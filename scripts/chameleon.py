"""Generate an animated chameleon that walks the contribution graph and eats it.

Why a chameleon rather than the usual snake: a chameleon changes colour, and a
contribution graph is a grid of colours. The gimmick writes itself — the body
takes on the shade of whatever square it just ate, so the animation is a readable
summary of the year rather than decoration.

Output is a self-contained SVG with CSS keyframes. No JavaScript: GitHub strips
scripts from SVG, and the whole thing has to survive being served through a
caching image proxy.

    python scripts/chameleon.py --user Dowgg18 --out dist/chameleon.svg
    python scripts/chameleon.py --user Dowgg18 --out dist/chameleon-dark.svg --dark
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

# ── Geometry ──────────────────────────────────────────────────────────────────
CELL = 11
GAP = 3
PITCH = CELL + GAP
ROWS = 7
PAD_X = 18
PAD_Y = 26
DURATION = 22.0  # seconds for one full crossing
EAT_FADE = 0.55  # how long a square takes to dim after being eaten

# ── Palette (Kamo) ────────────────────────────────────────────────────────────
INK = "#21211D"
FOREST = "#28332D"
ACCENT = "#CDC733"
ICE = "#F9F9F9"

LEVELS_DARK = ["#1b1b18", "#2d3a2f", "#4d5f2c", "#8f9a2e", "#CDC733"]
LEVELS_LIGHT = ["#e9e9e0", "#cfd8c4", "#adba7a", "#d8d24a", "#CDC733"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


@dataclass(frozen=True, slots=True)
class Cell:
    col: int
    row: int
    count: int
    date: str

    @property
    def x(self) -> int:
        return PAD_X + self.col * PITCH

    @property
    def y(self) -> int:
        return PAD_Y + self.row * PITCH


def fetch(login: str, token: str) -> list[Cell]:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "chameleon-contrib",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        sys.exit(f"GitHub API returned {exc.code}: {exc.read()[:200]!r}")

    if "errors" in payload:
        sys.exit(f"GraphQL errors: {payload['errors']}")

    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    cells: list[Cell] = []
    for col, week in enumerate(weeks):
        for day in week["contributionDays"]:
            cells.append(
                Cell(col=col, row=day["weekday"], count=day["contributionCount"], date=day["date"])
            )
    return cells


def level(count: int, ceiling: int) -> int:
    """Bucket a day into one of five shades, scaled to the busiest day so a quiet
    year still shows contrast instead of a flat wall of the lowest colour."""
    if count <= 0:
        return 0
    if ceiling <= 1:
        return 4
    ratio = count / ceiling
    if ratio > 0.66:
        return 4
    if ratio > 0.33:
        return 3
    if ratio > 0.12:
        return 2
    return 1


def walk(columns: int) -> list[tuple[int, int]]:
    """Boustrophedon: down one column, up the next. Every square is visited, and
    the chameleon never teleports — which a naive left-to-right sweep does."""
    path: list[tuple[int, int]] = []
    for col in range(columns):
        rows = range(ROWS) if col % 2 == 0 else range(ROWS - 1, -1, -1)
        path.extend((col, row) for row in rows)
    return path


def build(cells: list[Cell], dark: bool) -> str:
    levels = LEVELS_DARK if dark else LEVELS_LIGHT
    empty = levels[0]
    columns = max(c.col for c in cells) + 1
    ceiling = max((c.count for c in cells), default=0)

    width = PAD_X * 2 + columns * PITCH
    height = PAD_Y * 2 + ROWS * PITCH + 14

    by_pos = {(c.col, c.row): c for c in cells}
    path = walk(columns)
    steps = len(path)
    step_pct = 100.0 / steps

    # ── squares ────────────────────────────────────────────────────────────
    rects: list[str] = []
    fades: list[str] = []
    for index, (col, row) in enumerate(path):
        cell = by_pos.get((col, row))
        if cell is None:
            continue
        lvl = level(cell.count, ceiling)
        fill = levels[lvl]
        cid = f"c{col}-{row}"
        rects.append(
            f'<rect id="{cid}" class="sq" x="{cell.x}" y="{cell.y}" '
            f'width="{CELL}" height="{CELL}" rx="2.5" fill="{fill}">'
            f"<title>{cell.date}: {cell.count}</title></rect>"
        )
        if lvl > 0:
            # Dim exactly when the chameleon arrives, then stay dim.
            at = index * step_pct
            fades.append(
                f"@keyframes eat-{cid}{{"
                f"0%,{at:.4f}%{{fill:{fill}}}"
                f"{min(100.0, at + EAT_FADE):.4f}%,100%{{fill:{empty}}}}}"
            )
            fades.append(
                f"#{cid}{{animation:eat-{cid} {DURATION}s linear infinite}}"
            )

    # ── chameleon path ─────────────────────────────────────────────────────
    move_frames: list[str] = []
    tint_frames: list[str] = []
    flip_frames: list[str] = []
    for index, (col, row) in enumerate(path):
        at = index * step_pct
        x = PAD_X + col * PITCH + CELL / 2
        y = PAD_Y + row * PITCH + CELL / 2
        move_frames.append(f"{at:.4f}%{{transform:translate({x:.1f}px,{y:.1f}px)}}")

        cell = by_pos.get((col, row))
        lvl = level(cell.count, ceiling) if cell else 0
        tint_frames.append(f"{at:.4f}%{{fill:{levels[max(lvl, 1)]}}}")

        # Face the direction of travel: even columns descend, odd ones climb.
        facing = 1 if col % 2 == 0 else -1
        flip_frames.append(f"{at:.4f}%{{transform:scaleY({facing})}}")

    move_frames.append(f"100%{{transform:translate({PAD_X + (columns - 1) * PITCH + CELL / 2:.1f}px,"
                       f"{PAD_Y + CELL / 2:.1f}px)}}")

    chameleon = f"""
  <g class="cham">
    <g class="cham-flip">
      <!-- curled tail -->
      <path class="tail" d="M6.5,1.5 c-4.2,0 -5.6,3.4 -3.6,5.2 c1.7,1.5 4.1,0.3 3.6,-1.7 c-0.3,-1.2 -1.9,-1.3 -2.3,-0.2"
            fill="none" stroke-width="1.8" stroke-linecap="round"/>
      <!-- body -->
      <path class="body" d="M6,2 c5.2,-2.6 11.6,-1.2 13.4,3.1 c1.5,3.6 -1.4,6.6 -5.6,6.6 c-4.6,0 -8.6,-2.4 -9.6,-5.4 c-0.6,-1.9 0.1,-3.4 1.8,-4.3 z"/>
      <!-- crest -->
      <path class="body" d="M15.6,0.6 c2.6,0.2 4.2,1.6 4.6,3.4 c-1.6,-1.2 -3.2,-1.7 -4.9,-1.6 z"/>
      <!-- legs -->
      <path class="leg" d="M9,10.6 l0.6,3.4 M9.6,14 l-1.5,1.1 M9.6,14 l1.6,0.9" fill="none"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path class="leg" d="M15.4,11 l0.4,3.2 M15.8,14.2 l-1.4,1.1 M15.8,14.2 l1.6,0.9" fill="none"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- eye -->
      <circle class="eye-white" cx="17.4" cy="5.4" r="2.5"/>
      <circle class="eye" cx="18.3" cy="5.4" r="1.1"/>
      <!-- tongue -->
      <path class="tongue" d="M20.6,7.4 h9" fill="none" stroke-width="1.4" stroke-linecap="round"/>
    </g>
  </g>"""

    grid_fill = INK if dark else "#ffffff"
    label = ICE if dark else INK
    total = sum(c.count for c in cells)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img"
     aria-label="A chameleon walking across {total} contributions">
  <style>
    .sq {{ shape-rendering: crispEdges }}
    .cham {{ animation: cham-walk {DURATION}s linear infinite }}
    .cham-flip {{ animation: cham-face {DURATION}s steps(1) infinite; transform-origin: 12px 8px }}
    .body, .tail, .leg {{ animation: cham-tint {DURATION}s linear infinite }}
    .tail, .leg {{ fill: none }}
    .body {{ stroke: none }}
    .tail, .leg {{ stroke: currentColor }}
    .eye-white {{ fill: {ICE} }}
    .eye {{ fill: {INK} }}
    .tongue {{ stroke: #e0607e; opacity: 0; animation: tongue {DURATION / 26:.3f}s ease-in-out infinite }}
    g.cham {{ color: {ACCENT} }}
    @keyframes tongue {{
      0%, 78% {{ opacity: 0; transform: scaleX(0.2) }}
      86% {{ opacity: 1; transform: scaleX(1) }}
      100% {{ opacity: 0; transform: scaleX(0.2) }}
    }}
    @keyframes cham-walk {{ {"".join(move_frames)} }}
    @keyframes cham-tint {{ {"".join(tint_frames)} }}
    @keyframes cham-face {{ {"".join(flip_frames)} }}
    {"".join(fades)}
    @media (prefers-reduced-motion: reduce) {{
      .cham, .cham-flip, .body, .tail, .leg, .tongue, .sq {{ animation: none }}
      .cham {{ opacity: 0 }}
    }}
  </style>

  <rect width="{width}" height="{height}" fill="{grid_fill}" rx="10"/>
  <text x="{PAD_X}" y="16" font-family="system-ui,-apple-system,'Segoe UI',sans-serif"
        font-size="11" fill="{label}" opacity="0.55">{total} contributions in the last year</text>

  {"".join(rects)}
  {chameleon}
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--dark", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("set GITHUB_TOKEN (needs no scopes beyond read:user)")

    cells = fetch(args.user, token)
    svg = build(cells, dark=args.dark)

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)

    active = sum(1 for c in cells if c.count > 0)
    print(f"wrote {out} ({len(svg)} bytes, {active} active days of {len(cells)})")
    if active < 10:
        print(
            "  note: the graph is nearly empty. Turn on Settings > Public profile >\n"
            "  'Include private contributions on my profile' to make a year of\n"
            "  private work visible without exposing any repository."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
