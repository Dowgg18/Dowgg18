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
DURATION = 48.0  # seconds for one full crossing — a chameleon is not in a hurry
EAT_FADE = 0.35  # how long a square takes to dim after being eaten

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
    """Boustrophedon by ROW: left to right along one row, right to left along the
    next. Every square is visited and the walk never teleports.

    Row-major rather than column-major for one reason that only shows up once you
    look at it: the sprite is drawn in profile, so it has to travel horizontally.
    Walking it down a column made a side-view animal slide vertically like a lift,
    and flipping it to face the other way turned it upside down.
    """
    path: list[tuple[int, int]] = []
    for row in range(ROWS):
        cols = range(columns) if row % 2 == 0 else range(columns - 1, -1, -1)
        path.extend((col, row) for col in cols)
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

        # Face the direction of travel. scaleX, never scaleY: mirroring a profile
        # sprite vertically walks it on its back.
        facing = 1 if row % 2 == 0 else -1
        flip_frames.append(f"{at:.4f}%{{transform:scaleX({facing})}}")

    last_col = columns - 1 if (ROWS - 1) % 2 == 0 else 0
    move_frames.append(
        f"100%{{transform:translate({PAD_X + last_col * PITCH + CELL / 2:.1f}px,"
        f"{PAD_Y + (ROWS - 1) * PITCH + CELL / 2:.1f}px)}}"
    )

    # Drawn facing right with the MOUTH at the local origin, so the outer
    # translate puts the mouth exactly on the square being eaten and the body
    # trails behind it. Everything else is measured back from there.
    chameleon = f"""
  <g class="cham">
    <g class="cham-flip">
      <!-- curled tail, springing from the hip -->
      <path class="tail" d="M-18.2,1.4 c-3.8,0.6 -5.8,3 -5,5.2 c0.7,1.9 3.2,2.4 4.5,0.9
                            c1.1,-1.3 0.3,-3.1 -1.2,-3 c-1,0.1 -1.5,0.9 -1.3,1.7"
            fill="none" stroke-width="1.7" stroke-linecap="round"/>
      <!-- hind leg, drawn before the body so it reads as the far side -->
      <path class="leg far" d="M-13.4,4.2 c-0.6,1.9 -0.6,3 0.2,3.9 M-13.2,8.1 l-1.8,0.8
                               M-13.2,8.1 l1.5,1"
            fill="none" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- dorsal crest -->
      <path class="body" d="M-4.4,-5.2 L-5.6,-8.1 L-7.2,-5.9 L-8.8,-8.5 L-10.4,-6.2
                            L-12,-8.1 L-13.4,-5.4 C-10.4,-6.4 -7.2,-6.2 -4.4,-5.2 Z"/>
      <!-- body -->
      <path class="body" d="M0,0 C-1.4,-2.6 -2.2,-4.2 -4.6,-5.2 C-8,-6.6 -12.4,-6.2 -15.4,-4.2
                            C-17.4,-2.9 -18.3,-1.3 -18.4,0.5 C-18.5,2.4 -17,3.8 -14.4,4.5
                            C-10,5.7 -4.8,5.2 -1.6,2.9 C-0.5,2.1 0.2,1 0,0 Z"/>
      <!-- fore leg -->
      <path class="leg" d="M-5.2,4.4 c0.6,1.9 0.5,3 -0.3,3.9 M-5.5,8.3 l-1.9,0.8
                           M-5.5,8.3 l1.5,1.1"
            fill="none" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- turret eye: a cone of skin with a very small pupil -->
      <circle class="body" cx="-4.2" cy="-2" r="3"/>
      <circle class="eye-white" cx="-3.9" cy="-2" r="1.5"/>
      <circle class="eye" cx="-3.5" cy="-2" r="0.85"/>
      <!-- jaw -->
      <path class="jaw" d="M0,0 c-1.5,0.9 -2.9,1.5 -4.4,1.7" fill="none" stroke-width="0.8"/>
      <!-- tongue -->
      <g class="tongue">
        <path d="M0.5,0.7 h7" fill="none" stroke-width="1.3" stroke-linecap="round"/>
        <circle cx="8.1" cy="0.7" r="1.3" stroke="none"/>
      </g>
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
    /* steps(1) so the turn is a flick, not a squash through zero width.
       Origin at the mouth, which is the local origin, so the head stays on the
       square it is eating while the body swings round behind it. */
    .cham-flip {{ animation: cham-face {DURATION}s steps(1) infinite;
                  transform-origin: 0px 0px }}
    .body, .tail, .leg {{ animation: cham-tint {DURATION}s linear infinite }}
    .body {{ stroke: none }}
    .tail, .leg {{ stroke: currentColor; fill: none }}
    .leg.far {{ opacity: 0.55 }}
    .eye-white {{ fill: {ICE} }}
    .eye {{ fill: {INK} }}
    .jaw {{ stroke: {INK}; opacity: 0.35 }}
    .tongue {{ fill: #e0607e; stroke: #e0607e; opacity: 0;
               transform-origin: 0px 0px;
               animation: tongue {DURATION / 46:.3f}s ease-in-out infinite }}
    g.cham {{ color: {ACCENT} }}
    @keyframes tongue {{
      0%, 74% {{ opacity: 0; transform: scaleX(0.15) }}
      84% {{ opacity: 0.95; transform: scaleX(1) }}
      94%, 100% {{ opacity: 0; transform: scaleX(0.15) }}
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
