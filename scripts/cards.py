"""Generate the repository cards as static SVG.

Self-hosted rather than pulled from a pin service, for a boring reason: the
public instance of that service was returning 503 on every retry, which would
have put broken images in the middle of the page. Owning the file also means
owning the layout instead of accepting a widget's.

    python scripts/cards.py
"""

from __future__ import annotations

import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"

INK = "#21211D"
SURFACE_TOP = "#20201C"
SURFACE_BOTTOM = "#171713"
FOREST = "#28332D"
ACCENT = "#CDC733"
SAGE = "#8ec7a8"
ICE = "#F9F9F9"

W, H = 500, 200
FONT = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

# Decorative line art, drawn at very low opacity on the right of each card. It
# is the only ornament here: the rest of the surface earns its interest from the
# gradient and the edge highlight rather than from clip art.
MOTIFS = {
    # Many strokes converging into one — the burst being merged.
    "burstq": """
      <path d="M300,40 C352,44 386,58 404,84" />
      <path d="M296,64 C350,66 384,76 404,94" />
      <path d="M300,88 C352,88 386,92 404,100" />
      <path d="M296,112 C350,110 384,106 404,104" />
      <path d="M300,136 C352,132 386,120 404,110" />
      <circle cx="412" cy="100" r="7" />
    """,
    # A gate: two posts, a barrier, and the check that lets a build through.
    "replaygate": """
      <path d="M316,44 V156" />
      <path d="M420,44 V156" />
      <path d="M316,66 H420" />
      <path d="M316,90 H420" />
      <path d="M316,114 H420" />
      <path d="M340,132 l14,14 l30,-32" />
    """,
}

CARDS = [
    {
        "file": "burstq.svg",
        "motif": "burstq",
        "title": "burstq",
        "slug": "github.com/Dowgg18/debounced-webhook-pipeline",
        "lines": [
            "One ordered unit of work per conversation,",
            "out of a storm of chat webhooks.",
        ],
        "tags": [("Python", ACCENT), ("Redis Streams", SAGE)],
    },
    {
        "file": "replaygate.svg",
        "motif": "replaygate",
        "title": "replaygate",
        "slug": "github.com/Dowgg18/agent-replay-gate",
        "lines": [
            "A pre-deploy regression gate for LLM agents.",
            "Seal every I/O boundary, then fail the build.",
        ],
        "tags": [("Python", ACCENT), ("LLM testing", SAGE)],
    },
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(card: dict) -> str:
    tags = ""
    x = 34
    for label, colour in card["tags"]:
        tags += (
            f'<circle cx="{x}" cy="160" r="4.5" fill="{colour}"/>'
            f'<text x="{x + 12}" y="164.5" font-family="{FONT}" font-size="12.5" '
            f'fill="{ICE}" opacity="0.7">{esc(label)}</text>'
        )
        x += 26 + int(len(label) * 7.0)

    uid = card["title"]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img" aria-label="{esc(card['title'])}">
  <defs>
    <linearGradient id="surface-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{SURFACE_TOP}"/>
      <stop offset="100%" stop-color="{SURFACE_BOTTOM}"/>
    </linearGradient>
    <linearGradient id="spine-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{ACCENT}"/>
      <stop offset="70%" stop-color="{FOREST}"/>
      <stop offset="100%" stop-color="{FOREST}" stop-opacity="0.3"/>
    </linearGradient>
    <!-- A light source at the top edge. One highlight does more for depth than
         any drop shadow, and it survives both GitHub themes. -->
    <linearGradient id="edge-{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset="28%" stop-color="{ACCENT}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow-{uid}" cx="0.82" cy="0.12" r="0.6">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="clip-{uid}">
      <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="15"/>
    </clipPath>
  </defs>

  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="15"
        fill="url(#surface-{uid})" stroke="{ICE}" stroke-opacity="0.09"/>

  <g clip-path="url(#clip-{uid})">
    <rect width="{W}" height="{H}" fill="url(#glow-{uid})"/>
    <g stroke="{ACCENT}" stroke-opacity="0.075" stroke-width="1.6" fill="none"
       stroke-linecap="round" stroke-linejoin="round">{MOTIFS[card['motif']]}</g>
    <rect x="14" y="22" width="3" height="{H - 44}" rx="1.5" fill="url(#spine-{uid})"/>
    <rect x="1" y="1" width="{W - 2}" height="1" fill="url(#edge-{uid})"/>
  </g>

  <text x="34" y="62" font-family="{FONT}" font-size="25" font-weight="700"
        fill="{ACCENT}" letter-spacing="-0.4">{esc(card['title'])}</text>

  <text x="34" y="98" font-family="{FONT}" font-size="14" fill="{ICE}"
        opacity="0.87">{esc(card['lines'][0])}</text>
  <text x="34" y="120" font-family="{FONT}" font-size="14" fill="{ICE}"
        opacity="0.87">{esc(card['lines'][1])}</text>

  {tags}

  <text x="{W - 26}" y="164.5" text-anchor="end" font-family="{MONO}" font-size="10.5"
        fill="{ICE}" opacity="0.3">{esc(card['slug'])}</text>
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for card in CARDS:
        path = OUT / card["file"]
        path.write_text(build(card), encoding="utf-8")
        print(f"  {card['file']}  ({path.stat().st_size} bytes)")
    stale = OUT / "proven.svg"
    if stale.exists():
        stale.unlink()
        print("  removed proven.svg (now a text line, not a card)")


if __name__ == "__main__":
    main()
