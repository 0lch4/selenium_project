"""Converts the test design documents (Markdown) into LaTeX fragments included by the report.

Supported subset: ##/### headings, tables, paragraphs, **bold**, `code`, [link](url).
The generated text stays in Polish - the report is written for a Polish course.
Usage:  python scripts/md_to_tex.py   ->  docs/report/generated/*.tex
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


BOLD_ON, BOLD_OFF = "\x01", "\x02"


def inline(text: str) -> str:
    # bold first: a bold span may contain inline code, so it cannot be handled per part
    text = re.sub(r"\*\*(.+?)\*\*", BOLD_ON + r"\1" + BOLD_OFF, text)
    parts = re.split(r"(`[^`]+`)", text)
    res = []
    for p in parts:
        if p.startswith("`") and p.endswith("`"):
            # allow line breaks after slashes so long paths fit in narrow table cells
            res.append(r"\texttt{" + escape(p[1:-1]).replace("/", r"/\allowbreak{}") + "}")
        else:
            p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
            res.append(escape(p))
    return "".join(res).replace(BOLD_ON, r"\textbf{").replace(BOLD_OFF, "}")


# Column widths for tables whose content is uneven across columns, keyed by the header row
WIDTHS = {
    ("ID", "Funkcja", "Opis", "MoSCoW", "Uzasadnienie"): [0.07, 0.19, 0.34, 0.11, 0.29],
    ("ID", "Tytuł", "Priorytet", "Technika", "Poziom", "Funkcje", "Automatyzacja", "Wynik"):
        [0.08, 0.18, 0.09, 0.15, 0.11, 0.11, 0.14, 0.14],
    ("ID", "Tytuł", "Wykryty przez", "Ważność", "Priorytet", "Status"): [0.09, 0.45, 0.13, 0.1, 0.1, 0.13],
    ("ID", "Wynik", "Czas [s]", "Uwagi"): [0.1, 0.24, 0.09, 0.57],
    ("Grupa", "Wykonania", "Zaliczone", "Niezaliczone", "Oczekiwane niepowodzenie (xfail)", "Czas [s]"):
        [0.3, 0.12, 0.12, 0.13, 0.21, 0.12],
}
SHORT_TABLE = 12  # rows; longer tables use longtable and may break across pages


def table(rows: list[list[str]], small: bool = False, widths: list[float] | None = None) -> str:
    """A longtable; `widths` are column width fractions (summing to 1)."""
    header, body = rows[0], rows[1:]
    n = len(header)
    if widths is None:
        widths = WIDTHS.get(tuple(h.strip() for h in header))
    if widths is None:
        if n == 2:
            widths = [0.27, 0.73]
        elif n == 3 and header[0].strip() == "#":
            widths = [0.05, 0.48, 0.47]
        elif n > 8:
            widths = [0.13] + [0.87 / (n - 1)] * (n - 1)
        else:
            widths = [1 / n] * n
    # column width minus the inter-column padding so the table fits within the margins
    # ragged-right cells: justified text in narrow columns leaves wide gaps between words
    spec = "".join(rf">{{\raggedright\arraybackslash}}p{{\dimexpr {w:.3f}\linewidth-2\tabcolsep\relax}}"
                   for w in widths)
    size = r"\scriptsize\setlength{\tabcolsep}{3pt}" if small or n >= 8 else r"\small"
    head = " & ".join(r"\textbf{" + inline(h) + "}" for h in header) + r" \\"
    rows_tex = [" & ".join(inline(c) for c in r) + r" \\" for r in body]
    if len(body) <= SHORT_TABLE:
        # short tables never break: a longtable right after a heading at a page break prints
        # its header above the heading
        return "\n".join([r"{" + size, r"\par\smallskip\noindent\begin{tabular}{" + spec + "}", r"\toprule",
                          head, r"\midrule", *rows_tex, r"\bottomrule", r"\end{tabular}\par\smallskip", "}"])
    lines = [r"{" + size, r"\begin{longtable}{" + spec + "}", r"\toprule", head, r"\midrule", r"\endhead",
             *rows_tex, r"\bottomrule", r"\end{longtable}", "}"]
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
            title = inline(m.group(2))
            cmd = {2: r"\subsection", 3: r"\subsubsection"}.get(depth)
            # keep a heading together with the start of its content; deeper levels become a bold
            # line of their own (\paragraph is run-in and a following longtable jumps ahead of it)
            out.append(r"\needspace{8\baselineskip}" +
                       (cmd + "{" + title + "}" if cmd else r"\par\medskip\noindent\textbf{" + title + r"}\par"))
        elif line.strip() in ("", "---"):
            continue
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out) + "\n"


def llm_results() -> str:
    """Table of medians from the LLM-as-a-Judge results and the high-priority recommendations."""
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
    out.append(table(rec, widths=[0.15, 0.2, 0.65]) + "}")
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
