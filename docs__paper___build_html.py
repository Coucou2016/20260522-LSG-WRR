"""Build self-contained manuscript.html from manuscript.md + SciencePlots SVGs."""
from __future__ import annotations

import base64
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
MD_PATH = ROOT / "docs" / "paper" / "manuscript.md"
OUT_PATH = ROOT / "docs" / "paper" / "manuscript.html"
FIG_DIR = ROOT / "outputs" / "figures"

FIGURES = [
    (
        # Internal file IDs (fig02–fig09) follow generation order in make_figures.py.
        # Display numbering is sequential: the study-domain footprint figure was
        # removed, so the extent maps open as Figure 1.
        "fig2a",
        "fig02_extent_hit_miss_carlisle_E1.svg",
        "Figure 1a. Carlisle event E1 inundation-extent classification at τ = 0.03 m, comparing "
        "(a) the low-fidelity (LF) simulation with the HF reference and (b) the LSG-Max H-LSG "
        "prediction with HF. Blue indicates hits, red misses, gold false alarms, and grey cells "
        "dry in both.",
    ),
    (
        "fig2b",
        "fig02_extent_hit_miss_chowilla_E1.svg",
        "Figure 1b. Chowilla event E1 inundation-extent classification at τ = 0.03 m, comparing "
        "(a) the LF simulation with the HF reference and (b) the LSG-Max H-LSG prediction with HF. "
        "Blue indicates hits, red misses, gold false alarms, and grey cells dry in both. The dashed "
        "outline marks the training wet domain. Chowilla event E1 is the Group 1 held-out event; its "
        "inundation extent (84,667 wet cells) substantially exceeds the 36,124-cell training wet "
        "domain, so many of the widespread misses in panel (b) occur outside that footprint and "
        "correspond to the all-cells-versus-wet-domain score difference reported in Section 4.5.",
    ),
    (
        "fig2c",
        "fig02_extent_hit_miss_burnett_E1.svg",
        "Figure 1c. Burnett event E1 inundation-extent classification at τ = 0.03 m, comparing "
        "(a) the LF simulation with the HF reference and (b) the LSG-Max H-LSG prediction with HF. "
        "Blue indicates hits, red misses, gold false alarms, and grey cells dry in both.",
    ),
    (
        "fig3a",
        "fig03_peak_depth_error_carlisle_E1.svg",
        "Figure 2a. Carlisle event E1 peak-depth errors (m), shown for (a) the LF simulation and "
        "(b) the LSG-Max H-LSG prediction relative to the HF reference; each panel uses an "
        "independent color scale spanning its own 99th-percentile absolute error "
        "(q<sub>99</sub>(|e|)), so color saturation is not comparable across panels. The dashed outline "
        "marks the training wet domain. Positive errors indicate overprediction and negative "
        "errors indicate underprediction.",
    ),
    (
        "fig3b",
        "fig03_peak_depth_error_chowilla_E1.svg",
        "Figure 2b. Chowilla event E1 peak-depth errors (m), shown for (a) the LF simulation and "
        "(b) the LSG-Max H-LSG prediction relative to the HF reference; each panel uses an "
        "independent color scale spanning its own 99th-percentile absolute error "
        "(q<sub>99</sub>(|e|) ≈ 1 m for LF and ≈ 12 m for LSG-Max), so color saturation is not "
        "comparable across panels. The dashed outline marks the training wet domain. The large "
        "negative errors in panel (b) are EXT-gated zeros outside that domain where HF depths "
        "reach ≈ 15 m; inside the wet domain the same LSG prediction has RMSE 0.093 m "
        "(Section 4.5). Positive errors indicate overprediction and negative errors indicate "
        "underprediction.",
    ),
    (
        "fig3c",
        "fig03_peak_depth_error_burnett_E1.svg",
        "Figure 2c. Burnett event E1 peak-depth errors (m), shown for (a) the LF simulation and "
        "(b) the LSG-Max H-LSG prediction relative to the HF reference; each panel uses an "
        "independent color scale spanning its own 99th-percentile absolute error "
        "(q<sub>99</sub>(|e|)), so color saturation is not comparable across panels. The dashed outline "
        "marks the training wet domain. Positive errors indicate overprediction and negative "
        "errors indicate underprediction.",
    ),
    (
        "fig4a",
        "fig04_pwet_carlisle_E1.svg",
        "Figure 3a. Carlisle event E1 LSG-Max H-LSG inundation probability *P*(*h* ≥ 0.03 m), "
        "reconstructed from the probabilistic WSE pathway conditional on the deterministic EXT gate.",
    ),
    (
        "fig4b",
        "fig04_pwet_chowilla_E1.svg",
        "Figure 3b. Chowilla event E1 LSG-Max H-LSG inundation probability *P*(*h* ≥ 0.03 m), "
        "reconstructed from the probabilistic WSE pathway conditional on the deterministic EXT gate. The "
        "near-zero probability region beyond the trained extent reflects extent-gate extrapolation "
        "outside the training wet domain (Section 4.5).",
    ),
    (
        "fig4c",
        "fig04_pwet_burnett_E1.svg",
        "Figure 3c. Burnett event E1 LSG-Max H-LSG inundation probability *P*(*h* ≥ 0.03 m), "
        "reconstructed from the probabilistic WSE pathway conditional on the deterministic EXT gate.",
    ),
    (
        "fig5",
        "fig05_cross_case_csi_rmse_wet_train.svg",
        "Figure 4. Critical success index (CSI) and root-mean-square error (RMSE; m) on the Group 1 "
        "training wet-domain scoring mask for LF-only, LSG-Max H-LSG, and (Carlisle only) LSG-TS "
        "maximum-surface predictions across Carlisle, Chowilla, and Burnett.",
    ),
    (
        "fig6",
        "fig06_error_budget_o1o4.svg",
        "Figure 5. O1–O4 depth RMSE (m) for the Group 1 train and test splits, scored on the "
        "training wet domain. Panels: (a) Carlisle LSG-Max H-LSG, (b) Carlisle LSG-TS H-LSG, "
        "(c) Chowilla LSG-Max H-LSG, (d) Burnett LSG-Max H-LSG. Each panel uses an independent "
        "y-axis limit so that the small O1/O2 bars remain visible alongside the larger O3 values; "
        "bars should not be compared across panels by height.",
    ),
    (
        "fig7",
        "fig07_global_vs_hlsg_ab.svg",
        "Figure 6. Native-capacity wet-domain depth RMSE (m) for the Group 1 maximum-surface "
        "evaluations of Carlisle, Chowilla, and Burnett. Bars compare the native global model with "
        "residual H-LSG; for Carlisle, H-LSG denotes the SGPR configuration used for the reported "
        "maximum-surface results (0.094 m). Wet-domain CSI is essentially unchanged "
        "across the two models (0.974–0.976) because the extent gate is shared and global, so it is "
        "reported in Section 4.3 rather than plotted.",
    ),
    (
        "fig9",
        "fig09_zoning_wet_correlation_ab.svg",
        "Figure 7. Chowilla Group 1 maximum-surface zoning sensitivity comparing the global model, "
        "residual-response *k*-means zoning, and wet-correlation zoning. Bars show wet-domain CSI "
        "(left axis) and depth RMSE (right axis, m); bar heights should not be compared between the "
        "two metrics because they use different axes.",
    ),
    (
        "fig8",
        "fig08_uq_calibration_crps_scale.svg",
        "Figure 8. CRPS-based variance calibration and its spatial diagnostics. "
        "(a) Carlisle LSG-Max H-LSG reliability diagram before and after variance calibration. "
        "(b) Spatial distribution of Carlisle cells with 0.5 ≤ *P*(*h* ≥ τ) < 0.95 relative to the "
        "HF wet–dry pattern. (c) Carlisle all-cell and active-cell 90% coverage before and after "
        "calibration. (d) CRPS (m) before and after calibration for Carlisle, Chowilla, and Burnett, "
        "evaluated over all retained cells including dry cells on a logarithmic axis. Because CRPS is "
        "evaluated over all retained cells including dry cells, it should not be compared directly "
        "with the wet-domain RMSE values (Table 9).",
    ),
]


def b64_data_uri(path: pathlib.Path) -> str:
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    if path.suffix.lower() == ".svg":
        return "data:image/svg+xml;base64," + b64
    return "data:image/png;base64," + b64


def inline_fmt(s: str) -> str:
    s = html.escape(s)
    # Restore explicit <sub>/<sup> tags that html.escape turned into entities so
    # subscripts/superscripts render instead of printing literal "<sub>N</sub>".
    s = s.replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>")
    s = s.replace("&lt;sup&gt;", "<sup>").replace("&lt;/sup&gt;", "</sup>")
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)

    # Italic only outside <code>...</code> so identifiers like coverage_*_active stay intact.
    parts = re.split(r"(<code>.*?</code>)", s)
    for i, part in enumerate(parts):
        if part.startswith("<code>"):
            continue
        parts[i] = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", part)
    s = "".join(parts)

    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    # Mark Chinese placeholder for font fallback styling
    s = s.replace("待补充", '<span class="dai-buchong">待补充</span>')
    s = s.replace("未运行", '<span class="dai-buchong">未运行</span>')
    return s


def flush_table(table_rows: list[str]) -> str:
    rows: list[list[str]] = []
    for r in table_rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) >= 2 and all(set(c) <= set("-: ") for c in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = rows[0], rows[1:]
    parts = [
        "<table>",
        "<thead><tr>" + "".join(f"<th>{inline_fmt(h)}</th>" for h in header) + "</tr></thead>",
        "<tbody>",
    ]
    for br in body:
        while len(br) < len(header):
            br.append("")
        parts.append(
            "<tr>"
            + "".join(f"<td>{inline_fmt(c)}</td>" for c in br[: len(header)])
            + "</tr>"
        )
    parts.append("</tbody></table>")
    return "\n".join(parts)


def md_to_body(md: str, fig_html: dict[str, str]) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_table = False
    table_rows: list[str] = []
    in_code = False
    code_buf: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                in_code = False
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
            i += 1
            continue
        if in_table:
            out.append(flush_table(table_rows))
            in_table = False
            table_rows = []

        if line.startswith("# "):
            out.append(f"<h1>{inline_fmt(line[2:])}</h1>")
        elif line.startswith("## "):
            title = line[3:].strip()
            out.append(f'<h2 id="{html.escape(title[:40])}">{inline_fmt(title)}</h2>')
        elif line.startswith("### "):
            title = line[4:].strip()
            out.append(f"<h3>{inline_fmt(title)}</h3>")
            if title.startswith("4.1"):
                out.append(fig_html["fig2a"])
                out.append(fig_html["fig2b"])
                out.append(fig_html["fig2c"])
                out.append(fig_html["fig3a"])
                out.append(fig_html["fig3b"])
                out.append(fig_html["fig3c"])
                out.append(fig_html["fig4a"])
                out.append(fig_html["fig4b"])
                out.append(fig_html["fig4c"])
                out.append(fig_html["fig5"])
            elif title.startswith("4.2"):
                out.append(fig_html["fig6"])
            elif title.startswith("4.3"):
                out.append(fig_html["fig7"])
            elif title.startswith("4.4"):
                out.append(fig_html["fig9"])
            elif title.startswith("4.6"):
                out.append(fig_html["fig8"])
        elif line.startswith("---"):
            out.append("<hr/>")
        elif line.strip().startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].rstrip()))
                i += 1
            out.append(
                '<p class="eq">' + "<br/>".join(inline_fmt(q) for q in quote_lines) + "</p>"
            )
            continue
        elif line.strip() == "":
            out.append("")
        elif line.strip().startswith("- ") or re.match(r"^\d+\. ", line.strip()):
            items: list[str] = []
            ordered = bool(re.match(r"^\d+\. ", line.strip()))
            while i < n and (
                lines[i].strip().startswith("- ") or re.match(r"^\d+\. ", lines[i].strip())
            ):
                it = re.sub(r"^(?:- |\d+\. )", "", lines[i].strip())
                items.append(f"<li>{inline_fmt(it)}</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        else:
            paras = [line]
            i += 1
            while (
                i < n
                and lines[i].strip()
                and not lines[i].startswith("#")
                and not lines[i].startswith("|")
                and not lines[i].startswith("---")
                and not lines[i].startswith("```")
                and not lines[i].strip().startswith(">")
                and not lines[i].strip().startswith("- ")
                and not re.match(r"^\d+\. ", lines[i].strip())
            ):
                paras.append(lines[i])
                i += 1
            text = " ".join(p.strip() for p in paras)
            out.append(f"<p>{inline_fmt(text)}</p>")
            continue
        i += 1

    if in_table:
        out.append(flush_table(table_rows))
    return "\n".join(out)


CSS = r"""
:root { --text:#111; --muted:#444; --rule:#ccc; --bg:#fff; --accent:#1a365d; }
* { box-sizing: border-box; }
html { font-size: 11pt; }
body {
  margin: 0 auto;
  max-width: 48rem;
  padding: 2.2rem 1.4rem 4rem;
  color: var(--text);
  background: var(--bg);
  font-family: "Times New Roman", Times, "Nimbus Roman", "Liberation Serif",
               "Microsoft YaHei", SimSun, "Songti SC", serif;
  line-height: 1.45;
}
h1 { font-size: 1.55rem; line-height: 1.25; margin: 0 0 0.8rem; color: var(--accent); }
h2 { font-size: 1.22rem; margin: 1.8rem 0 0.7rem; border-bottom: 1px solid var(--rule);
     padding-bottom: 0.25rem; page-break-after: avoid; }
h3 { font-size: 1.05rem; margin: 1.2rem 0 0.45rem; page-break-after: avoid; }
p { margin: 0.55rem 0; text-align: justify; hyphens: auto; }
ul, ol { margin: 0.4rem 0 0.7rem 1.3rem; }
li { margin: 0.2rem 0; }
code { font-family: Consolas, "Courier New", monospace; font-size: 0.92em; }
pre { background: #f7f7f7; padding: 0.7rem; overflow: auto; border: 1px solid var(--rule); }
table { width: 100%; border-collapse: collapse; margin: 0.8rem 0 1rem; font-size: 0.88rem;
        page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 0.28rem 0.35rem; vertical-align: top; }
th { background: #f0f3f7; text-align: left; }
figure { margin: 1.1rem 0 1.4rem; page-break-inside: avoid; }
figure img { width: 100%; height: auto; display: block; }
figcaption { font-size: 0.9rem; color: var(--muted); margin-top: 0.4rem; text-align: left; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 1.2rem 0; }
a { color: #0b3d91; text-decoration: none; }
.dai-buchong { font-family: "Microsoft YaHei", SimSun, "Songti SC", "Times New Roman", serif; }
.eq { display:block; text-align:center; margin: 0.85rem 0; font-style: italic; }
@media print {
  body { max-width: none; padding: 12mm 14mm; font-size: 10.5pt; }
  a { color: inherit; text-decoration: none; }
  h2, h3, figure, table { break-inside: avoid; page-break-inside: avoid; }
}
"""


def main() -> None:
    md = MD_PATH.read_text(encoding="utf-8")
    fig_html: dict[str, str] = {}
    for key, fname, caption in FIGURES:
        uri = b64_data_uri(FIG_DIR / fname)
        fig_html[key] = (
            f'<figure id="{key}">\n'
            f'  <img src="{uri}" alt="{html.escape(caption[:120].replace("*", ""))}" />\n'
            f"  <figcaption>{inline_fmt(caption)}</figcaption>\n"
            f"</figure>"
        )
    body = md_to_body(md, fig_html)
    doc = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
        "<title>Capacity-Controlled Evaluation of Residual Hierarchical Zoning in Multi-Fidelity Flood Inundation Surrogates</title>\n"
        f"<style>\n{CSS}\n</style>\n"
        "</head>\n"
        f"<body>\n{body}\n</body>\n"
        "</html>\n"
    )
    OUT_PATH.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    print(f"img tags: {doc.count('<img ')}")
    data_uri_marker = 'src="data:'
    print(f"data: URIs: {doc.count(data_uri_marker)}")


if __name__ == "__main__":
    main()
