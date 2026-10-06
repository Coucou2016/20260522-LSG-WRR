"""Build a COMPACT Round 6 prompt: tables + numbers-bearing sentences only.

Keeps the payload small enough for reliable chunked injection while retaining
every number and every claim that references one.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
MD = (ROOT / "docs" / "paper" / "manuscript.md").read_text(encoding="utf-8")
OUT = ROOT / "docs" / "paper" / "_round6_prompt_compact.txt"

lines = MD.splitlines()

def section(start_marker: str, end_markers: list[str]) -> str:
    i = next((k for k, ln in enumerate(lines) if start_marker in ln), None)
    if i is None:
        return ""
    j = len(lines)
    for k in range(i + 1, len(lines)):
        if any(m in lines[k] for m in end_markers):
            j = k
            break
    return "\n".join(lines[i:j]).strip()

header = """Round 6 of 6 - WRR manuscript review: numeric consistency + simulated reviewer pass

You reviewed Rounds 1-5 of this manuscript (innovation framing, methods/data logic, results/discussion logic, writing style, figures/tables/captions). All issues you raised there are fixed; do not re-flag them. FINAL round. Two tasks:

TASK A - Numeric consistency audit. Check EVERY number below for internal consistency: (1) abstract/key points vs tables vs body sentences; (2) arithmetic (each tabulated O2-O1 must equal O2 minus O1; capacity-matched statements must match Table 4/5/6); (3) units and decimal places; (4) any number appearing in two places must match or be explicitly reconciled. Report each discrepancy with exact locations. If consistent, say so explicitly.

TASK B - Simulated critical reviewer. Act as a skeptical Water Resources Research reviewer seeing only this text. SHORT report: max 8 points, each labeled [major] or [minor], each with a one-sentence fix. Focus on claims unsupported by the shown evidence, ambiguous statements a reader would misread, and anything a reviewer would demand before acceptance. Sentence-level fixes only; no structural rewrites.

COMPACT MANUSCRIPT EXTRACT (tables verbatim; prose limited to numbers-bearing and claim-bearing sentences):
"""

abstract = "\n".join(lines[:16])

tables = section("## 4. Results", ["## 5."])
# keep only table lines and table caption lines from Results
table_lines = []
for ln in tables.splitlines():
    s = ln.strip()
    if s.startswith("|") or s.startswith("**Table"):
        table_lines.append(ln)
tables_compact = "\n".join(table_lines)

num_re = re.compile(r"\d")
def numeric_sentences(text: str) -> str:
    out_lines = []
    for para in text.split("\n\n"):
        for sent in re.split(r"(?<=[.!?])\s+", para):
            if num_re.search(sent) and not sent.strip().startswith("|"):
                out_lines.append(sent.strip())
    return "\n".join(out_lines)

results = section("## 4. Results", ["## 5."])
discussion = section("## 5. Discussion", ["## 6."])
conclusions = section("## 6. Conclusions", ["## References"])

prompt = f"""{header}

=== KEY POINTS + ABSTRACT ===
{abstract}

=== ALL TABLES (verbatim, captions included) ===
{tables_compact}

=== RESULTS: every sentence containing a number ===
{numeric_sentences(results)}

=== DISCUSSION: every sentence containing a number ===
{numeric_sentences(discussion)}

=== CONCLUSIONS (full, short) ===
{conclusions}

End with a one-paragraph overall verdict: is this manuscript numerically sound and ready for submission after your listed fixes?
"""

OUT.write_text(prompt, encoding="utf-8")
print(f"wrote {OUT} ({len(prompt)} chars)")
