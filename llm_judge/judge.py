"""LLM-as-a-Judge, step 2: score screenshots against the rubric, aggregate runs, give a verdict.

Usage:
    python -m llm_judge.judge                    # all views from screenshots/views.json
    python -m llm_judge.judge --view login       # a single view
    python -m llm_judge.judge --backend cli      # force the Claude Code backend
    python -m llm_judge.judge --dry-run          # no model calls: validate inputs, preview requests

Backends:
    api  - Anthropic SDK (Messages API, structured outputs); needs ANTHROPIC_API_KEY
    cli  - headless Claude Code (`claude -p`) using the logged-in Claude Code account;
           the model reads the screenshot with its Read tool, output is constrained by --json-schema
    auto - api when ANTHROPIC_API_KEY is set, otherwise cli (default)

Configuration is read from the environment and from an optional `.env` file in the repo root
(see `.env.example`): ANTHROPIC_API_KEY, JUDGE_MODEL, JUDGE_BACKEND, CLAUDE_BIN.
"""
import argparse
import base64
import glob
import json
import os
import shutil
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

HERE = Path(__file__).parent
ROOT = HERE.parent
RUBRIC = HERE / "prompts" / "judge_rubric.md"
SHOTS = HERE / "screenshots"
RESULTS = HERE / "results"

load_dotenv(ROOT / ".env")

MODEL = os.getenv("JUDGE_MODEL") or "claude-opus-5-5"
RUNS = 3
DIMENSIONS = ["visual_hierarchy", "consistency", "system_status", "language_clarity",
              "error_prevention", "efficiency", "minimalism", "accessibility"]
PASS_MEAN, MIN_DIMENSION = 3.5, 2


class DimensionScore(BaseModel):
    id: Literal["visual_hierarchy", "consistency", "system_status", "language_clarity",
                "error_prevention", "efficiency", "minimalism", "accessibility"]
    score: int = Field(ge=1, le=5)
    evidence: str
    justification: str


class Recommendation(BaseModel):
    priority: Literal["high", "medium", "low"]
    dimension: str
    recommendation: str


class JudgeVerdict(BaseModel):
    view: str
    dimensions: list[DimensionScore]
    strengths: list[str]
    recommendations: list[Recommendation]

    @field_validator("dimensions")
    @classmethod
    def all_dimensions_once(cls, v):
        if sorted(d.id for d in v) != sorted(DIMENSIONS):
            raise ValueError("exactly the 8 rubric dimensions are required, each once")
        return v


def view_context(view: dict) -> str:
    return (f"View: {view['id']}\nURL: {view['url']}\nPurpose of the view: {view['purpose']}\n"
            f"Typical user task: {view['task']}\n"
            f"Viewport: {view['viewport'][0]}x{view['viewport'][1]}, user "
            f"{'logged in' if view['auth'] else 'not logged in'}.\n\n"
            "Evaluate this view according to the rubric.")


# --- backend: Anthropic SDK -------------------------------------------------------------

def build_messages(view: dict) -> list[dict]:
    image = base64.standard_b64encode((SHOTS / view["screenshot"]).read_bytes()).decode()
    return [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image}},
        {"type": "text", "text": view_context(view)},
    ]}]


def judge_once_api(client, system: str, view: dict) -> JudgeVerdict:
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=build_messages(view),
        output_format=JudgeVerdict,
        output_config={"effort": "high"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"model refused to evaluate view {view['id']}: {response.stop_details}")
    if response.parsed_output is None:
        raise RuntimeError(f"no valid JSON response (stop_reason={response.stop_reason})")
    return response.parsed_output


# --- backend: headless Claude Code ------------------------------------------------------

def find_claude() -> str:
    candidates = [os.getenv("CLAUDE_BIN"), shutil.which("claude")]
    pattern = Path.home() / ".vscode" / "extensions" / "anthropic.claude-code-*" / "resources" / "native-binary" / "claude*"
    candidates += sorted(glob.glob(str(pattern)), reverse=True)
    for c in candidates:
        if c and Path(c).is_file():
            return c
    raise RuntimeError("Claude Code CLI not found - set CLAUDE_BIN or install `claude`")


def judge_once_cli(claude: str, system: str, view: dict) -> JudgeVerdict:
    shot = (SHOTS / view["screenshot"]).resolve()
    prompt = (f"{view_context(view)}\n\nThe screenshot is the file {shot}. Read it with the Read tool, "
              "evaluate it and return only the JSON object required by the schema.")
    proc = subprocess.run(
        [claude, "-p", "--model", MODEL, "--output-format", "json",
         "--json-schema", json.dumps(JudgeVerdict.model_json_schema()),
         "--tools", "Read", "--allowedTools", "Read", "--no-session-persistence",
         "--system-prompt", system],
        input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=900,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited with {proc.returncode}: {proc.stderr[-500:]}")
    out = json.loads(proc.stdout)
    if out.get("is_error"):
        raise RuntimeError(f"claude reported an error: {out.get('subtype')} {out.get('result', '')[:300]}")
    payload = out.get("structured_output") or json.loads(out["result"])
    return JudgeVerdict.model_validate(payload)


# --- aggregation and reporting ----------------------------------------------------------

def aggregate(view_id: str, runs: list[JudgeVerdict], backend: str) -> dict:
    per_dim = {}
    for dim in DIMENSIONS:
        scores = [next(d.score for d in r.dimensions if d.id == dim) for r in runs]
        per_dim[dim] = {"scores": scores, "median": statistics.median(scores),
                        "spread": max(scores) - min(scores)}
    medians = [d["median"] for d in per_dim.values()]
    mean = round(statistics.mean(medians), 2)
    verdict = "PASS" if mean >= PASS_MEAN and min(medians) >= MIN_DIMENSION else "FAIL"
    return {"view": view_id, "backend": backend, "model": MODEL, "runs": len(runs),
            "dimensions": per_dim, "mean": mean,
            "max_spread": max(d["spread"] for d in per_dim.values()), "verdict": verdict}


def write_summary(aggregates: list[dict], details: dict[str, list[JudgeVerdict]], backend: str,
                  out_dir: Path) -> None:
    lines = ["# LLM-as-a-Judge results\n",
             f"Backend: `{backend}`, model: `{MODEL}`, runs per view: {aggregates[0]['runs']}, "
             f"date: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC\n",
             f"PASS verdict: mean of medians ≥ {PASS_MEAN} and no dimension < {MIN_DIMENSION}. "
             "Cells: median (± spread = max − min across runs).\n",
             "| Dimension | " + " | ".join(a["view"] for a in aggregates) + " |",
             "|---|" + "---|" * len(aggregates)]
    for dim in DIMENSIONS:
        cells = [f"{a['dimensions'][dim]['median']:g} (±{a['dimensions'][dim]['spread']})" for a in aggregates]
        lines.append(f"| {dim} | " + " | ".join(cells) + " |")
    lines.append("| **mean** | " + " | ".join(f"**{a['mean']}**" for a in aggregates) + " |")
    lines.append("| **verdict** | " + " | ".join(f"**{a['verdict']}**" for a in aggregates) + " |\n")
    for a in aggregates:
        lines.append(f"## {a['view']}\n")
        first = details[a["view"]][0]
        lines += [f"- strength: {s}" for s in first.strengths]
        lines += [f"- [{r.priority}] ({r.dimension}) {r.recommendation}" for r in first.recommendations]
        lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def resolve_backend(choice: str) -> str:
    if choice == "auto":
        key = os.getenv("ANTHROPIC_API_KEY", "")
        # a Claude Code OAuth token (claude setup-token) is not accepted by the Messages API
        if key.startswith("sk-ant-oat"):
            os.environ.setdefault("CLAUDE_CODE_OAUTH_TOKEN", key)
            del os.environ["ANTHROPIC_API_KEY"]
            return "cli"
        return "api" if key else "cli"
    return choice


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--view", action="append", help="view id (repeatable)")
    ap.add_argument("--runs", type=int, default=RUNS)
    ap.add_argument("--backend", choices=["auto", "api", "cli"], default=os.getenv("JUDGE_BACKEND") or "auto")
    ap.add_argument("--results-dir", type=Path, default=RESULTS, help="where to write JSON and summary.md")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    backend = resolve_backend(args.backend)
    system = RUBRIC.read_text(encoding="utf-8")
    views = json.loads((SHOTS / "views.json").read_text(encoding="utf-8"))
    if args.view:
        views = [v for v in views if v["id"] in args.view]
    if not views:
        print("no views - run first: python -m llm_judge.capture", file=sys.stderr)
        return 2

    if args.dry_run:
        for v in views:
            msg = build_messages(v)
            print(f"[dry-run] {v['id']}: image {len(msg[0]['content'][0]['source']['data']) // 1024} KiB (b64), "
                  f"context {len(msg[0]['content'][1]['text'])} chars, rubric {len(system)} chars, "
                  f"{args.runs} runs -> {MODEL} via {backend}")
        print(f"[dry-run] response schema: {list(JudgeVerdict.model_json_schema()['properties'])}")
        return 0

    if backend == "api":
        import anthropic
        client = anthropic.Anthropic()
        judge = lambda v: judge_once_api(client, system, v)  # noqa: E731
    else:
        claude = find_claude()
        judge = lambda v: judge_once_cli(claude, system, v)  # noqa: E731

    out_dir = args.results_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    aggregates, details = [], {}
    for v in views:
        runs = []
        for i in range(args.runs):
            print(f"{v['id']}: run {i + 1}/{args.runs} ({backend})", flush=True)
            runs.append(judge(v))
        details[v["id"]] = runs
        agg = aggregate(v["id"], runs, backend)
        aggregates.append(agg)
        (out_dir / f"{v['id']}.json").write_text(json.dumps(
            {"aggregate": agg, "runs": [r.model_dump() for r in runs]}, indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"{v['id']}: mean {agg['mean']}, verdict {agg['verdict']}", flush=True)
    write_summary(aggregates, details, backend, out_dir)
    return 0 if all(a["verdict"] == "PASS" for a in aggregates) else 1


if __name__ == "__main__":
    sys.exit(main())
