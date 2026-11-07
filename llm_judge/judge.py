"""Etap 2 LLM-as-a-Judge: ocena zrzutów ekranu wg rubryki, agregacja i werdykt.

Uruchomienie:
    python -m llm_judge.judge                 # wszystkie widoki z screenshots/views.json
    python -m llm_judge.judge --view login    # jeden widok
    python -m llm_judge.judge --dry-run       # bez wywołań API: walidacja wejścia i podgląd żądania

Wymaga ANTHROPIC_API_KEY (lub profilu `ant auth login`).
"""
import argparse
import base64
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

HERE = Path(__file__).parent
RUBRIC = HERE / "prompts" / "judge_rubric.md"
SHOTS = HERE / "screenshots"
RESULTS = HERE / "results"

MODEL = "claude-opus-5-5"
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
    priority: Literal["wysoki", "średni", "niski"]
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
            raise ValueError("wymagane dokładnie 8 wymiarów rubryki, każdy raz")
        return v


def build_messages(view: dict) -> list[dict]:
    image = base64.standard_b64encode((SHOTS / view["screenshot"]).read_bytes()).decode()
    context = (f"Widok: {view['id']}\nURL: {view['url']}\nCel widoku: {view['purpose']}\n"
               f"Typowe zadanie użytkownika: {view['task']}\n"
               f"Viewport: {view['viewport'][0]}x{view['viewport'][1]}, użytkownik "
               f"{'zalogowany' if view['auth'] else 'niezalogowany'}.\n\n"
               "Oceń ten widok zgodnie z rubryką.")
    return [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image}},
        {"type": "text", "text": context},
    ]}]


def judge_once(client, system: str, view: dict) -> JudgeVerdict:
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
        raise RuntimeError(f"model odmówił oceny widoku {view['id']}: {response.stop_details}")
    if response.parsed_output is None:
        raise RuntimeError(f"brak poprawnej odpowiedzi JSON (stop_reason={response.stop_reason})")
    return response.parsed_output


def aggregate(view_id: str, runs: list[JudgeVerdict]) -> dict:
    per_dim = {}
    for dim in DIMENSIONS:
        scores = [next(d.score for d in r.dimensions if d.id == dim) for r in runs]
        per_dim[dim] = {"scores": scores, "median": statistics.median(scores),
                        "spread": max(scores) - min(scores)}
    medians = [d["median"] for d in per_dim.values()]
    mean = round(statistics.mean(medians), 2)
    verdict = "PASS" if mean >= PASS_MEAN and min(medians) >= MIN_DIMENSION else "FAIL"
    return {"view": view_id, "model": MODEL, "runs": len(runs), "dimensions": per_dim,
            "mean": mean, "max_spread": max(d["spread"] for d in per_dim.values()),
            "verdict": verdict}


def write_summary(aggregates: list[dict], details: dict[str, list[JudgeVerdict]]) -> None:
    lines = [f"# Wyniki LLM-as-a-Judge\n",
             f"Model: `{MODEL}`, przebiegi na widok: {RUNS}, "
             f"data: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC\n",
             f"Werdykt PASS: średnia median ≥ {PASS_MEAN} i żaden wymiar < {MIN_DIMENSION}.\n",
             "| Wymiar | " + " | ".join(a["view"] for a in aggregates) + " |",
             "|---|" + "---|" * len(aggregates)]
    for dim in DIMENSIONS:
        cells = [f"{a['dimensions'][dim]['median']:g} (±{a['dimensions'][dim]['spread']})" for a in aggregates]
        lines.append(f"| {dim} | " + " | ".join(cells) + " |")
    lines.append("| **średnia** | " + " | ".join(f"**{a['mean']}**" for a in aggregates) + " |")
    lines.append("| **werdykt** | " + " | ".join(f"**{a['verdict']}**" for a in aggregates) + " |\n")
    for a in aggregates:
        lines.append(f"## {a['view']}\n")
        first = details[a["view"]][0]
        lines += [f"- mocna strona: {s}" for s in first.strengths]
        lines += [f"- [{r.priority}] ({r.dimension}) {r.recommendation}" for r in first.recommendations]
        lines.append("")
    (RESULTS / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--view", action="append", help="identyfikator widoku (można powtórzyć)")
    ap.add_argument("--runs", type=int, default=RUNS)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    system = RUBRIC.read_text(encoding="utf-8")
    views = json.loads((SHOTS / "views.json").read_text(encoding="utf-8"))
    if args.view:
        views = [v for v in views if v["id"] in args.view]
    if not views:
        print("brak widoków - uruchom najpierw: python -m llm_judge.capture", file=sys.stderr)
        return 2

    if args.dry_run:
        for v in views:
            msg = build_messages(v)
            print(f"[dry-run] {v['id']}: obraz {len(msg[0]['content'][0]['source']['data']) // 1024} KiB (b64), "
                  f"kontekst {len(msg[0]['content'][1]['text'])} znaków, rubryka {len(system)} znaków, "
                  f"{args.runs} przebiegi -> {MODEL}")
        print(f"[dry-run] schemat odpowiedzi: {list(JudgeVerdict.model_json_schema()['properties'])}")
        return 0

    import anthropic
    client = anthropic.Anthropic()
    RESULTS.mkdir(exist_ok=True)
    aggregates, details = [], {}
    for v in views:
        runs = []
        for i in range(args.runs):
            print(f"{v['id']}: przebieg {i + 1}/{args.runs}")
            runs.append(judge_once(client, system, v))
        details[v["id"]] = runs
        agg = aggregate(v["id"], runs)
        aggregates.append(agg)
        (RESULTS / f"{v['id']}.json").write_text(json.dumps(
            {"aggregate": agg, "runs": [r.model_dump() for r in runs]}, indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"{v['id']}: średnia {agg['mean']}, werdykt {agg['verdict']}")
    write_summary(aggregates, details)
    return 0 if all(a["verdict"] == "PASS" for a in aggregates) else 1


if __name__ == "__main__":
    sys.exit(main())
