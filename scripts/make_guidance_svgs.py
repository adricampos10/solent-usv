"""Generates the README diagrams for the guidance law: a static map of the
whole law at the boat, and three self-animating SVGs for its trigonometry:
arcsin (course to steer), arctan (line-of-sight guidance) and atan2
(directions).

GitHub strips scripts from READMEs, but SVG animations (SMIL) still play when
the SVG is shown as an image, so each frame's geometry is precomputed here and
written as <animate> value lists. All diagrams use a dark background.

    python3 scripts/make_guidance_svgs.py [OUTPUT_DIR]    # default docs/img
"""
import math
import re
import sys
from pathlib import Path

N = 72            # frames per loop
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

STYLE = f"""<style>
  text {{ font-family: {FONT}; font-size: 13px; fill: #e8e6dc; }}
  .h {{ font-size: 15px; font-weight: 600; }}
  .m {{ fill: #a8a69e; }}
  .bad {{ fill: #ff7b6b; }}
  .grid {{ stroke: #5f5e5a; }}
  .bg {{ fill: #1f1f1e; }}
</style>"""

def arrow_defs(body):
    """One arrowhead marker per colour used in the body. Each marker has its
    colour written out: context-stroke would be shorter, but Safari and
    older browsers draw it invisible."""
    colours = sorted(set(re.findall(r'url\(#a([0-9A-Fa-f]{6})\)', body)))
    marks = "".join(
        f'<marker id="a{c}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#{c}" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round"/></marker>' for c in colours)
    return f"<defs>{marks}</defs>"


def mark(colour):
    return f'marker-end="url(#a{colour.lstrip("#")})"'


TEAL, BLUE, AMBER, CORAL, PURPLE, RED = "#1D9E75", "#378ADD", "#BA7517", "#D85A30", "#7F77DD", "#E24B4A"
# Lighter shades of the same hues, for coloured text on the dark background.
TEAL_T, BLUE_T, CORAL_T, AMBER_T = "#5DCAA5", "#85B7EB", "#F0997B", "#EF9F27"


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f'{STYLE}\n{arrow_defs(body)}\n<rect class="bg" width="{w}" height="{h}" rx="10"/>\n{body}\n</svg>\n')


def anim(attr, values, dur):
    vals = ";".join(f"{v:.1f}" if isinstance(v, float) else str(v) for v in values + values[:1])
    return f'<animate attributeName="{attr}" values="{vals}" dur="{dur}s" repeatCount="indefinite"/>'


def line(frames, dur, color, width=2.5, dash=None, marker=True):
    """frames: list of (x1, y1, x2, y2)."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f" {mark(color)}" if marker else ""
    a = "".join(anim(k, [f[i] for f in frames], dur) for i, k in enumerate(("x1", "y1", "x2", "y2")))
    return f'<line stroke="{color}" stroke-width="{width}" stroke-linecap="round"{d}{m}>{a}</line>'


def texts(x, y, strings, dur, cls=""):
    """One text per frame, shown only during its frame (discrete opacity).
    Consecutive equal strings share one element to keep the file small."""
    out, i = [], 0
    while i < len(strings):
        j = i
        while j + 1 < len(strings) and strings[j + 1] == strings[i]:
            j += 1
        vals = ["1" if i <= k <= j else "0" for k in range(len(strings))]
        times = ";".join(f"{k / len(strings):.4f}" for k in range(len(strings)))
        c = f' class="{cls(strings[i]) if callable(cls) else cls}"' if cls else ""
        out.append(f'<text x="{x}" y="{y}"{c} opacity="{vals[0]}">{strings[i]}'
                   f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{times}" '
                   f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/></text>')
        i = j + 1
    return "\n".join(out)


def ping_pong(lo, hi):
    """N values going lo -> hi -> lo, easing at the ends."""
    return [lo + (hi - lo) * (1 - math.cos(2 * math.pi * k / N)) / 2 for k in range(N)]


def arcsin_svg():
    dur, U, k, ox, oy = 14, 3.0, 45, 70, 230
    currents = ping_pong(0.0, 3.5)
    u_f, c_f, g_f, readout = [], [], [], []
    for c in currents:
        ok = c < U
        b = math.asin(c / U) if ok else math.pi / 2
        ux, uy = ox + U * k * math.cos(b), oy - U * k * math.sin(b)
        gy = uy + c * k
        u_f.append((ox, oy, ux, uy))
        c_f.append((ux, uy, ux, gy))
        g_f.append((ox, oy, ux, gy))
        readout.append(f"v⊥ / U = {c:.1f} / {U:.0f} = {c / U:.2f}  →  β = arcsin({c / U:.2f}) = {math.degrees(b):.1f}°"
                       if ok else f"v⊥ / U = {c / U:.2f} ≥ 1: arcsin doesn't exist, no heading holds the track")
    body = [
        '<text x="20" y="30" class="h">arcsin: the course to steer</text>',
        '<text x="20" y="50" class="m">You know the hypotenuse (boat speed U) and the side to cancel (cross current v⊥)</text>',
        f'<line x1="40" y1="{oy}" x2="400" y2="{oy}" class="grid" stroke-width="1" stroke-dasharray="6 5"/>',
        f'<text x="400" y="{oy + 20}" text-anchor="end" class="m">track</text>',
        line(u_f, dur, TEAL), line(c_f, dur, BLUE), line(g_f, dur, AMBER),
        f'<line x1="430" y1="110" x2="460" y2="110" stroke="{TEAL}" stroke-width="2.5"/><text x="470" y="114">U: boat through the water</text>',
        f'<line x1="430" y1="138" x2="460" y2="138" stroke="{BLUE}" stroke-width="2.5"/><text x="470" y="142">v⊥: cross current</text>',
        f'<line x1="430" y1="166" x2="460" y2="166" stroke="{AMBER}" stroke-width="2.5"/><text x="470" y="170">over the ground</text>',
        texts(20, 290, readout, dur, cls=lambda s: "bad" if "doesn't" in s else ""),
    ]
    return svg(680, 310, "\n".join(body))


def arctan_svg():
    dur, D, k, bx, ty, r = 14, 40, 1.6, 110, 270, 34
    errors = ping_pong(12.0, 120.0)
    px = bx + D * k
    los_f, top_f, side_f, ahead_f, boat_y, arc_d, th_y, d_y, e_y, readout = ([] for _ in range(10))
    for e in errors:
        by = ty - e * k
        th = math.atan(e / D)
        L = math.hypot(D * k, e * k)
        los_f.append((bx + (px - bx) * 9 / L, by + (ty - by) * 9 / L, px - (px - bx) * 8 / L, ty - (ty - by) * 8 / L))
        top_f.append((bx, by, px, by))
        side_f.append((px, by, px, ty))
        ahead_f.append((px, by, px + 120, by))
        boat_y.append(by)
        arc_d.append(f"M{bx + r:.1f} {by:.1f} A{r} {r} 0 0 1 {bx + r * math.cos(th):.1f} {by + r * math.sin(th):.1f}")
        th_y.append(by + r * math.sin(th / 2) + 5)
        d_y.append(by - 8)
        e_y.append((by + ty) / 2 + 4)
        readout.append(f"e = {e:.0f} m  →  θ = arctan({e:.0f} / 40) = {math.degrees(th):.0f}°")
    body = [
        '<text x="20" y="30" class="h">arctan: back to the track (line-of-sight guidance)</text>',
        '<text x="20" y="50" class="m">The boat aims at a point on the track, always Δ = 40 m ahead</text>',
        f'<line x1="30" y1="{ty}" x2="380" y2="{ty}" class="grid" stroke-width="1.5"/>',
        f'<text x="380" y="{ty + 20}" text-anchor="end" class="m">track →</text>',
        line(ahead_f, dur, "#888780", 1, "5 4", False),
        line(top_f, dur, BLUE, 1.8, None, False),
        line(side_f, dur, BLUE, 1.8, None, False),
        line(los_f, dur, CORAL),
        f'<path fill="none" stroke="{AMBER}" stroke-width="2.5"><animate attributeName="d" values="{";".join(arc_d + arc_d[:1])}" dur="{dur}s" repeatCount="indefinite"/></path>',
        f'<text x="{bx + r + 8}" class="h" style="fill:{AMBER}">θ{anim("y", th_y, dur)}</text>',
        f'<text x="{(bx + px) / 2 - 6}" style="fill:{BLUE}">Δ{anim("y", d_y, dur)}</text>',
        f'<text x="{px + 8}" style="fill:{BLUE}">e{anim("y", e_y, dur)}</text>',
        f'<circle cx="{px}" cy="{ty}" r="5" fill="{CORAL}"/>',
        f'<circle cx="{bx}" cy="{ty}" r="7" fill="{TEAL}">{anim("cy", boat_y, dur)}</circle>',
        f'<circle cx="430" cy="100" r="6" fill="{TEAL}"/><text x="450" y="104">boat</text>',
        f'<circle cx="430" cy="126" r="5" fill="{CORAL}"/><text x="450" y="130">aim point on the track</text>',
        f'<line x1="416" y1="152" x2="444" y2="152" stroke="{AMBER}" stroke-width="2.5"/><text x="450" y="156">θ: how much to turn</text>',
        f'<line x1="416" y1="178" x2="444" y2="178" stroke="#888780" stroke-width="1" stroke-dasharray="5 4"/><text x="450" y="182">straight ahead (0°)</text>',
        texts(416, 232, readout, dur),
        '<text x="416" y="262" class="m">Far from the track it turns a lot;</text>',
        '<text x="416" y="280" class="m">close to it, hardly at all, so it joins smoothly</text>',
    ]
    return svg(680, 310, "\n".join(body))


def atan2_svg():
    dur, cx, cy, R = 16, 180, 195, 100
    angles = [360 * k / N for k in range(N)]
    v_f, w_f, t1, t2, t3 = [], [], [], [], []
    for a in angles:
        r = math.radians(a)
        dx, dy = math.cos(r), math.sin(r)
        at = math.atan(dy / dx) if abs(dx) > 1e-9 else math.copysign(math.pi / 2, dy)
        v_f.append((cx, cy, cx + R * dx, cy - R * dy))
        w_f.append((cx, cy, cx + (R - 16) * math.cos(at), cy - (R - 16) * math.sin(at)))
        t1.append(f"atan2(Δy, Δx) = {round(a) % 360}°")
        t2.append(f"arctan(Δy / Δx) = {round(math.degrees(at))}°")
        t3.append("same answer: B is to the east" if dx > 1e-9 else "wrong half: Δy/Δx can't tell west from east")
    body = [
        '<text x="20" y="30" class="h">atan2: the right angle all the way round</text>',
        '<text x="20" y="50" class="m">Direction from A to B, as a maths angle (0° = east, counter-clockwise)</text>',
        f'<circle cx="{cx}" cy="{cy}" r="{R + 8}" fill="none" class="grid" stroke-width="0.8"/>',
        f'<line x1="{cx - R - 20}" y1="{cy}" x2="{cx + R + 20}" y2="{cy}" class="grid" stroke-width="0.8"/>',
        f'<line x1="{cx}" y1="{cy - R - 20}" x2="{cx}" y2="{cy + R + 20}" class="grid" stroke-width="0.8"/>',
        f'<text x="{cx + R + 26}" y="{cy + 4}" class="m">E</text><text x="{cx - 4}" y="{cy - R - 24}" class="m">N</text>',
        f'<text x="{cx - R - 38}" y="{cy + 4}" class="m">W</text><text x="{cx - 4}" y="{cy + R + 36}" class="m">S</text>',
        line(w_f, dur, RED, 2, "5 4"),
        line(v_f, dur, PURPLE),
        f'<circle cx="{cx}" cy="{cy}" r="4" fill="#888780"/><text x="{cx - 18}" y="{cy + 20}" class="m">A</text>',
        f'<line x1="360" y1="110" x2="390" y2="110" stroke="{PURPLE}" stroke-width="2.5"/><text x="400" y="114">atan2: always right</text>',
        f'<line x1="360" y1="138" x2="390" y2="138" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/><text x="400" y="142">plain arctan</text>',
        texts(360, 215, t1, dur),
        texts(360, 239, t2, dur),
        texts(360, 269, t3, dur, cls=lambda s: "bad" if "wrong" in s else "m"),
    ]
    return svg(680, 340, "\n".join(body))


def full_svg():
    """Static map of the whole guidance law at one moment (the README's
    worked example): track 090°, 1 m/s stream setting south, U = 3 m/s,
    boat 10 m off the line (not to scale), look-ahead 40 m."""
    bx, by, L = 200, 190, 260
    theta, beta = math.atan(10 / 40), math.asin(1 / 3)

    def ray(angle, length):        # angle above the track direction, in radians
        return bx + length * math.cos(angle), by - length * math.sin(angle)

    def arc(a0, a1, r):
        (x0, y0), (x1, y1) = ray(a0, r), ray(a1, r)
        return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 0 0 {x1:.1f} {y1:.1f}"

    cx, cy = ray(theta, L)
    hx, hy = ray(theta + beta, L - 40)
    tx, ty = ray(theta / 2, 82)
    gx, gy = ray(theta + beta / 2, 122)
    body = [
        '<text x="20" y="30" class="h">The whole guidance law at the boat</text>',
        '<text x="20" y="50" class="m">Track 090°, 1 m/s stream setting south, boat at 3 m/s, 10 m off the line (not to scale)</text>',
        f'<line x1="40" y1="110" x2="640" y2="110" class="grid" stroke-width="1.5" {mark("#5f5e5a")}/>',
        f'<circle cx="40" cy="110" r="4" fill="#888780"/><text x="36" y="98" class="m">A</text><text x="626" y="98" class="m">B</text>',
        '<text x="420" y="98" class="m">track A → B: 090° (atan2)</text>',
        f'<line x1="{bx}" y1="{by - 8}" x2="{bx}" y2="114" stroke="#888780" stroke-width="0.8" stroke-dasharray="3 3"/>',
        f'<text x="{bx - 22}" y="152" class="m">e</text>',
        f'<line x1="150" y1="168" x2="150" y2="236" stroke="{BLUE}" stroke-width="2.5" {mark(BLUE)}/>',
        f'<text x="60" y="262" style="fill:{BLUE_T}">tidal stream 1 m/s</text>',
        f'<line x1="{bx}" y1="{by}" x2="480" y2="{by}" stroke="#888780" stroke-width="1" stroke-dasharray="6 5"/>',
        f'<text x="488" y="{by + 4}" class="m">along the track</text>',
        f'<line x1="{bx}" y1="{by}" x2="{cx:.1f}" y2="{cy:.1f}" stroke="{CORAL}" stroke-width="2" {mark(CORAL)}/>',
        f'<text x="{cx + 8:.1f}" y="{cy + 4:.1f}" style="fill:{CORAL_T}">course over ground</text>',
        f'<line x1="{bx}" y1="{by}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{TEAL}" stroke-width="2.5" {mark(TEAL)}/>',
        f'<text x="{hx + 8:.1f}" y="{hy:.1f}" style="fill:{TEAL_T}">heading 056.5°</text>',
        f'<path d="{arc(0, theta, 70)}" fill="none" stroke="{CORAL}" stroke-width="2.5"/>',
        f'<text x="{tx:.1f}" y="{ty + 5:.1f}" class="h" style="fill:{CORAL_T}">θ</text>',
        f'<path d="{arc(theta, theta + beta, 110)}" fill="none" stroke="{TEAL}" stroke-width="2.5"/>',
        f'<text x="{gx:.1f}" y="{gy + 5:.1f}" class="h" style="fill:{TEAL_T}">β</text>',
        f'<circle cx="{bx}" cy="{by}" r="8" fill="{TEAL}"/><text x="{bx - 14}" y="{by + 24}" class="m">boat</text>',
        '<text x="40" y="296">heading = 090° − β − θ = 090° − 19.5° − 14° = 056.5°</text>',
        '<text x="40" y="320" class="m">θ = arctan(10 / 40) = 14°, back to the line  ·  β = arcsin(1 / 3) = 19.5°, into the current</text>',
    ]
    return svg(680, 340, "\n".join(body))


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "docs" / "img")
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("guidance_law", full_svg), ("guidance_arcsin", arcsin_svg),
                     ("guidance_arctan", arctan_svg), ("guidance_atan2", atan2_svg)):
        (out / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print(out / f"{name}.svg")
