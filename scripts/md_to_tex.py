"""Konwertuje dokumenty projektu testów (Markdown) na fragmenty LaTeX dołączane do raportu.

Obsługiwany podzbiór: nagłówki ##/###, tabele, akapity, **pogrubienie**, `kod`, [link](url).
Uruchomienie:  python scripts/md_to_tex.py   ->  docs/report/generated/*.tex
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "report" / "generated"

SYMBOLS = {"≥": r"$\geq$", "≤": r"$\leq$", "→": r"$\rightarrow$", "↔": r"$\leftrightarrow$",
           "×": r"$\times$", "●": r"\textbullet", "…": r"\dots{}", "±": r"$\pm$", "−": r"$-$"}
SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
           "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def escape(text: str) -> str:
    out = "".join(SPECIAL.get(c, c) for c in text)
    for k, v in SYMBOLS.items():
        out = out.replace(k, v)
    return out


def inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    res = []
    for p in parts:
        if p.startswith("`") and p.endswith("`"):
            res.append(r"\texttt{" + escape(p[1:-1]) + "}")
        else:
            p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
            p = escape(p)
            p = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", p)
            res.append(p)
    return "".join(res)


def table(rows: list[list[str]], small: bool = False) -> str:
    header, body = rows[0], rows[1:]
    n = len(header)
    if n == 2:
        spec = r"p{0.25\linewidth}p{0.69\linewidth}"
    elif n == 3 and header[0].strip() == "#":
        spec = r"p{0.03\linewidth}p{0.45\linewidth}p{0.44\linewidth}"
    else:
        width = 0.94 / n
        spec = "".join(rf"p{{{width:.3f}\linewidth}}" for _ in range(n))
    size = r"\scriptsize" if small or n > 8 else r"\small"
    lines = [r"{" + size, r"\begin{longtable}{" + spec + "}", r"\toprule",
             " & ".join(r"\textbf{" + inline(h) + "}" for h in header) + r" \\", r"\midrule", r"\endhead"]
    lines += [" & ".join(inline(c) for c in r) + r" \\" for r in body]
    lines += [r"\bottomrule", r"\end{longtable}", "}"]
    return "\n".join(lines)


def convert(md: str, skip_until: str | None = None, stop_at: str | None = None,
            level_offset: int = 0) -> str:
    lines = md.splitlines()
    if skip_until:
        lines = lines[next(i for i, l in enumerate(lines) if l.startswith(skip_until)):]
    out, rows, para = [], [], []

    def flush():
        nonlocal rows, para
        if rows:
            out.append(table([r for r in rows if not re.fullmatch(r"[\s|:-]+", "|".join(r))]))
            rows = []
        if para:
            out.append(inline(" ".join(para)) + "\n")
            para = []

    for line in lines:
        if stop_at and line.startswith(stop_at):
            break
        if line.startswith("|"):
            if para:
                flush()
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        flush()
        m = re.match(r"^(#+) (.*)", line)
        if m:
            depth = len(m.group(1)) + level_offset
            cmd = {2: r"\subsection", 3: r"\subsubsection", 4: r"\paragraph"}.get(depth, r"\paragraph")
            out.append(cmd + "{" + inline(m.group(2)) + "}")
        elif line.strip() in ("", "---"):
            continue
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out) + "\n"


def llm_results() -> str:
    """Tabela median z wyników LLM-as-a-Judge i rekomendacje o wysokim priorytecie."""
    res = ROOT / "llm_judge" / "results"
    order = [v["id"] for v in json.loads((res / "input" / "views.json").read_text(encoding="utf-8"))]
    data = {v: json.loads((res / f"{v}.json").read_text(encoding="utf-8")) for v in order}
    first = data[order[0]]["aggregate"]
    rows = [["Wymiar"] + order]
    for dim in first["dimensions"]:
        rows.append([f"`{dim}`"] + [f"{data[v]['aggregate']['dimensions'][dim]['median']:g} "
                                    f"(±{data[v]['aggregate']['dimensions'][dim]['spread']})" for v in order])
    rows.append(["**średnia median**"] + [f"**{data[v]['aggregate']['mean']}**" for v in order])
    rows.append(["**werdykt**"] + [f"**{data[v]['aggregate']['verdict']}**" for v in order])
    out = [inline(f"Backend `{first['backend']}`, model `{first['model']}`, {first['runs']} przebiegi "
                  "na widok. Komórki: mediana (± rozrzut = max − min z przebiegów).") + "\n", table(rows)]
    rec = [["Widok", "Wymiar", "Rekomendacja (wysoki priorytet, przebieg 1)"]]
    for v in order:
        for r in data[v]["runs"][0]["recommendations"]:
            if r["priority"] == "high":
                rec.append([v, f"`{r['dimension']}`", r["recommendation"]])
    out.append(r"{\renewcommand{\arraystretch}{1.2}")
    out.append(table(rec).replace(r"p{0.313\linewidth}p{0.313\linewidth}p{0.313\linewidth}",
                                  r"p{0.13\linewidth}p{0.17\linewidth}p{0.62\linewidth}") + "}")
    return "\n".join(out) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = (DOCS / "test_cases.md").read_text(encoding="utf-8")
    (OUT / "test_cases.tex").write_text(
        convert(cases, skip_until="## Przypadki funkcjonalne", stop_at="## Macierz"), encoding="utf-8")
    (OUT / "traceability.tex").write_text(
        convert(cases, skip_until="## Macierz", level_offset=10), encoding="utf-8")
    features = (DOCS / "features.md").read_text(encoding="utf-8")
    (OUT / "features.tex").write_text(convert(features, skip_until="Priorytet"), encoding="utf-8")
    results = (DOCS / "results.md").read_text(encoding="utf-8")
    (OUT / "results.tex").write_text(convert(results, skip_until="## Podsumowanie", stop_at="## CI"),
                                     encoding="utf-8")
    defects = (DOCS / "defects.md").read_text(encoding="utf-8")
    (OUT / "defects.tex").write_text(convert(defects, skip_until="| ID", level_offset=1), encoding="utf-8")
    (OUT / "llm_results.tex").write_text(llm_results(), encoding="utf-8")
    print("\n".join(str(p.relative_to(ROOT)) for p in sorted(OUT.iterdir())))


if __name__ == "__main__":
    main()
