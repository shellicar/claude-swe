"""Render the Fable 5 significance chart to fable-significance.svg:
each run's resolve rate as a point with its 95% Wilson CI, annotated with the
paired McNemar p. Dependency-free (matplotlib isn't installed); an SVG is text,
so it diffs cleanly and embeds in the markdown report.
"""
import json
import math
from math import comb

def load(dirn):
    res, uni = set(), set()
    for st in ("standard", "hard"):
        d = json.load(open(f"anthropic__claude-fable-5.runs_main_{dirn}_{st}.json"))
        r = set(d["resolved_ids"])
        res |= r
        uni |= r | set(d["unresolved_ids"])
    return res, uni

A, UA = load("fable-5")
B, UB = load("fable-5-high-2026-07-02")
n = len(UA | UB)

def wilson(x, n, z=1.96):
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h

rows = [("Fable 5 (original)", len(A), "#3b6ea5"),
        ("Fable 5 (2 Jul repeat)", len(B), "#c65d21")]
b, c = len(A - B), len(B - A)
k, nn = min(b, c), b + c
pval = min(1.0, 2 * sum(comb(nn, i) for i in range(k + 1)) / 2 ** nn)

W, H, L, R, T, Bm = 760, 300, 210, 40, 64, 70
pw, ph = W - L - R, H - T - Bm
xmin, xmax = 78, 100
X = lambda pct: L + (pct - xmin) / (xmax - xmin) * pw
ys = [T + ph * 0.35, T + ph * 0.72]
ay = T + ph + 24

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="-apple-system,Helvetica,Arial,sans-serif">',
     f'<rect width="{W}" height="{H}" fill="white"/>',
     f'<text x="{L}" y="32" font-size="17" font-weight="700">Claude Fable 5 \u2014 resolve rate with 95% CI (n={n})</text>',
     f'<line x1="{X(xmin):.1f}" y1="{ay}" x2="{X(xmax):.1f}" y2="{ay}" stroke="#999"/>']
for t in range(80, 101, 5):
    s.append(f'<line x1="{X(t):.1f}" y1="{ay}" x2="{X(t):.1f}" y2="{ay+5}" stroke="#999"/>')
    s.append(f'<text x="{X(t):.1f}" y="{ay+20}" font-size="12" fill="#555" text-anchor="middle">{t}%</text>')

for (label, x, col), y in zip(rows, ys):
    p, lo, hi = wilson(x, n)
    s.append(f'<text x="{L-14}" y="{y+4:.1f}" font-size="13" text-anchor="end">{label}</text>')
    s.append(f'<line x1="{X(lo*100):.1f}" y1="{y:.1f}" x2="{X(hi*100):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.5"/>')
    for e in (lo, hi):
        s.append(f'<line x1="{X(e*100):.1f}" y1="{y-7:.1f}" x2="{X(e*100):.1f}" y2="{y+7:.1f}" stroke="{col}" stroke-width="2.5"/>')
    s.append(f'<circle cx="{X(p*100):.1f}" cy="{y:.1f}" r="5.5" fill="{col}"/>')
    s.append(f'<text x="{X(p*100):.1f}" y="{y-14:.1f}" font-size="12" fill="#333" text-anchor="middle">{x}/{n} = {p*100:.1f}%  [{lo*100:.1f}, {hi*100:.1f}]</text>')

s.append(f'<text x="{L}" y="{H-16}" font-size="13" fill="#333">McNemar exact p = {pval:.2f} \u2014 not significant. Of {n} instances, {b+c} flipped ({c} gained, {b} lost); the rest agree.</text>')
s.append('</svg>')
open("fable-significance.svg", "w").write("\n".join(s))
print(f"wrote fable-significance.svg  (p={pval:.3f}, n={n})")
