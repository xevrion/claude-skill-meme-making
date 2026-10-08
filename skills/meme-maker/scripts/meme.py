# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10", "pyyaml>=6"]
# ///
"""Render memes from templates or from any image.

Run with `uv run meme.py ...` (installs Pillow on the fly) or plain `python3 meme.py ...`
when Pillow is already installed. Every render command prints the output path.
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageSequence
except ImportError:
    sys.exit("Pillow is missing. Run this script with `uv run`, or `pip install pillow`.")

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "assets" / "fonts"
FONT_FILES = {
    "anton": FONTS / "Anton-Regular.ttf",
    "arimo": FONTS / "Arimo.ttf",
    "thick": FONTS / "TitilliumWeb-Black.ttf",
    "thin": FONTS / "TitilliumWeb-SemiBold.ttf",
}
LINE_HEIGHT = {"anton": 1.12, "arimo": 1.22, "thick": 1.1, "thin": 1.15}
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "meme-maker"
MEMEGEN = "https://api.memegen.link"
# memegen is MIT licensed; its repo holds each template's image and text-box config
MEMEGEN_RAW = "https://raw.githubusercontent.com/jacebrowning/memegen/main/templates"
# memegen font names mapped to the bundled fonts; Impact and Segoe are not redistributable
MEMEGEN_FONTS = {"thick": "thick", "titilliumweb": "thick", "thin": "thin",
                 "titilliumweb-thin": "thin", "impact": "anton"}
IMGFLIP = "https://api.imgflip.com/get_memes"
UA = {"User-Agent": "meme-maker-skill/1.0"}
CATALOGUE_TTL = 7 * 24 * 3600


# ---------- network and catalogues ----------

def fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def catalogue(name, url):
    """Template list from a meme API, cached for a week so search works offline."""
    path = CACHE / f"{name}.json"
    if path.exists() and time.time() - path.stat().st_mtime < CATALOGUE_TTL:
        return json.loads(path.read_text())
    try:
        raw = json.loads(fetch(url))
    except Exception as e:
        if path.exists():
            return json.loads(path.read_text())
        print(f"warning: could not load {name} catalogue: {e}", file=sys.stderr)
        return []
    items = raw if name == "memegen" else raw.get("data", {}).get("memes", [])
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items))
    return items


def memegen_templates():
    seen, out = set(), []
    for t in catalogue("memegen", f"{MEMEGEN}/templates/"):
        if t["id"] not in seen:
            seen.add(t["id"])
            out.append(t)
    return out


def imgflip_templates():
    return catalogue("imgflip", IMGFLIP)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def search(query):
    q = norm(query)
    words = q.split()
    hits = []
    for t in memegen_templates():
        hay = norm(" ".join([t["id"], t["name"], *t.get("keywords", [])]))
        if q == norm(t["id"]) or all(w in hay for w in words):
            hits.append(("memegen", t["id"], t["name"], f"{t['lines']} lines"))
    for t in imgflip_templates():
        if all(w in norm(t["name"]) for w in words):
            hits.append(("imgflip", t["id"], t["name"], f"{t['box_count']} boxes, blank only"))
    return hits


def search_imgflip_site(query, pages=1):
    """imgflip's own template search, which covers its whole user-uploaded library."""
    seen, hits = set(), []
    for page in range(1, pages + 1):
        url = "https://imgflip.com/memesearch?" + urllib.parse.urlencode({"q": query, "page": page})
        html = fetch(url, headers={"User-Agent": "Mozilla/5.0 (meme-maker-skill)"}).decode("utf-8", "replace")
        found = re.findall(r'href="/meme/(\d+)/([^"]+)"', html)
        if not found:
            break
        for tid, slug in found:
            if tid not in seen:
                seen.add(tid)
                hits.append((tid, urllib.parse.unquote(slug).replace("-", " ")))
    return hits


def base36(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while n:
        n, r = divmod(n, 36)
        out = digits[r] + out
    return out or "0"


def imgflip_blank_url(tid):
    # imgflip serves every template's blank image at its id written in base 36
    code = base36(int(tid))
    for ext in ("jpg", "png", "gif"):
        url = f"https://i.imgflip.com/{code}.{ext}"
        try:
            urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA), timeout=15)
            return url
        except urllib.error.HTTPError:
            continue
    raise FileNotFoundError(f"no blank image found for imgflip template {tid}")


# ---------- image io ----------

def load(src):
    if re.match(r"https?://", src):
        return Image.open(io.BytesIO(fetch(src)))
    return Image.open(src)


def frames_of(img):
    """Frames plus per-frame durations, so animated GIFs keep their animation."""
    if getattr(img, "is_animated", False):
        frames, durations = [], []
        for f in ImageSequence.Iterator(img):
            frames.append(f.convert("RGBA"))
            durations.append(f.info.get("duration", 80))
        return frames, durations
    return [img.convert("RGBA")], None


def default_output(stem, animated):
    out_dir = Path.cwd() / "memes"
    out_dir.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")[:48] or "meme"
    path = out_dir / f"{slug}.{'gif' if animated else 'png'}"
    n = 2
    while path.exists():
        path = out_dir / f"{slug}-{n}.{path.suffix[1:]}"
        n += 1
    return path


def save(frames, durations, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if durations and len(frames) > 1:
        if out.suffix.lower() != ".gif":
            out = out.with_suffix(".gif")
        frames[0].save(out, save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, disposal=2)
    elif out.suffix.lower() in (".jpg", ".jpeg"):
        frames[0].convert("RGB").save(out, quality=92)
    else:
        frames[0].save(out)
    print(out)
    return out


def render(src, draw_fn, out, stem):
    frames, durations = frames_of(load(src))
    done = [draw_fn(f) for f in frames]
    save(done, durations, out or default_output(stem, bool(durations)))


# ---------- text layout ----------

def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONT_FILES[name]), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def wrap(text, fnt, max_w, draw, broken=None):
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=fnt) <= max_w:
                line = trial
                continue
            if line:
                lines.append(line)
            line = word
            # a single word wider than the box gets split by characters
            while draw.textlength(line, font=fnt) > max_w and len(line) > 1:
                if broken is not None:
                    broken.append(word)
                cut = len(line) - 1
                while cut > 1 and draw.textlength(line[:cut], font=fnt) > max_w:
                    cut -= 1
                lines.append(line[:cut])
                line = line[cut:]
        lines.append(line)
    return lines


def line_height(font_name, size, spacing=0.0):
    # font metrics include accent room that leaves visible gaps between all-caps lines
    return int(size * LINE_HEIGHT[font_name] * (1 + spacing))


def fit(text, font_name, max_w, max_h, start, minimum=10, weight=None, spacing=0.0, stroke=0.0):
    """Largest size whose wrapped text fits the box; returns (font, lines, line_height)."""
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    size = max(int(start), minimum)
    while True:
        fnt = font(font_name, size, weight)
        pad = int(size * stroke) * 2
        broken = []
        lines = wrap(text, fnt, max_w - pad, probe, broken)
        lh = line_height(font_name, size, spacing)
        widest = max((probe.textlength(l, font=fnt) for l in lines), default=0)
        fits = lh * len(lines) + pad <= max_h and widest + pad <= max_w and not broken
        if fits or size <= minimum:
            return fnt, balance(text, lines, fnt, max_w - pad, probe), lh
        size = max(minimum, int(size * 0.92))


def balance(text, lines, fnt, max_w, probe):
    """Narrow the wrap width while the line count holds, so no line ends with one lonely word."""
    if len(lines) < 2:
        return lines
    width = max_w
    while True:
        broken = []
        trial = wrap(text, fnt, width * 0.95, probe, broken)
        if len(trial) != len(lines) or broken:
            return lines
        lines, width = trial, width * 0.95


def draw_block(draw, lines, fnt, lh, x, top, fill, stroke_w=0, stroke_fill="black", align="center"):
    anchor = {"center": "ma", "left": "la", "right": "ra"}[align]
    for i, line in enumerate(lines):
        draw.text((x, top + i * lh), line, font=fnt, fill=fill, anchor=anchor,
                  stroke_width=stroke_w, stroke_fill=stroke_fill)


# ---------- memegen templates rendered locally ----------

def template_files(tid, style):
    """Config and image for a memegen template, fetched from its repo once and cached."""
    import yaml

    folder = CACHE / "templates" / tid
    folder.mkdir(parents=True, exist_ok=True)
    cfg_path = folder / "config.yml"
    if not cfg_path.exists():
        cfg_path.write_bytes(fetch(f"{MEMEGEN_RAW}/{tid}/config.yml"))
    name = style or "default"
    for ext in ("png", "jpg", "gif", "jpeg", "webp"):
        img_path = folder / f"{name}.{ext}"
        if img_path.exists():
            break
    else:
        for ext in ("png", "jpg", "gif", "jpeg", "webp"):
            try:
                data = fetch(f"{MEMEGEN_RAW}/{tid}/{name}.{ext}")
            except urllib.error.HTTPError:
                continue
            img_path = folder / f"{name}.{ext}"
            img_path.write_bytes(data)
            break
        else:
            raise FileNotFoundError(f"no image for style '{name}' of template '{tid}'")
    return yaml.safe_load(cfg_path.read_text()), img_path


def stylize(text, style):
    if style == "upper":
        return text.upper()
    if style == "lower":
        return text.lower()
    if style == "mock":
        return "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
    if style == "none":
        return text
    text = re.sub(r"\bi\b", "I", text)
    return text[:1].upper() + text[1:] if text.islower() else text


def draw_slot(im, spec, text, font_override):
    w, h = im.size
    angle = float(spec.get("angle") or 0)
    bx, by = float(spec.get("anchor_x", 0)) * w, float(spec.get("anchor_y", 0)) * h
    bw, bh = float(spec.get("scale_x", 1)) * w, float(spec.get("scale_y", 0.2)) * h
    name = MEMEGEN_FONTS.get(font_override or spec.get("font") or "thick", "arimo")
    color = spec.get("color") or "white"
    plain = color == "black"
    fnt, lines, lh = fit(stylize(text, spec.get("style", "upper")), name, bw, bh,
                         start=h / (4 if angle else 9), minimum=8,
                         weight=700 if name == "arimo" else None,
                         stroke=0 if plain else 0.06)
    sw = 0 if plain else max(1, round(fnt.size * 0.06))
    align = spec.get("align") or "center"
    x = {"center": bw / 2, "left": 0, "right": bw}.get(align, bw / 2)
    # pad the layer so descenders and outlines are not clipped at the box edge
    pad = fnt.size
    top = (bh - lh * len(lines)) / 2
    layer = Image.new("RGBA", (int(bw) + 2 * pad, int(bh) + 2 * pad), (0, 0, 0, 0))
    draw_block(ImageDraw.Draw(layer), lines, fnt, lh, x + pad, top + pad, color, sw, "black",
               align if align in ("left", "right") else "center")
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    cx, cy = bx + bw / 2, by + bh / 2
    im.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def render_template_local(a):
    cfg, img_path = template_files(a.id, a.style)
    img = Image.open(img_path)
    frames, durations = frames_of(img)
    if not a.animated:
        frames, durations = frames[:1], None
    slots = cfg.get("text") or []
    if len(a.text) > len(slots):
        print(f"warning: {a.id} has {len(slots)} slots, extra text ignored", file=sys.stderr)
    done = []
    for f in frames:
        for spec, text in zip(slots, a.text):
            if text.strip():
                draw_slot(f, spec, text, a.font)
        if a.width:
            f = f.resize((a.width, round(f.height * a.width / f.width)), Image.LANCZOS)
        done.append(f)
    stem = " ".join(a.text) or a.id
    save(done, durations, a.output or default_output(stem, bool(durations)))


# ---------- commands ----------

def cmd_search(a):
    query = " ".join(a.query)
    hits = search(query)
    for src, tid, name, extra in hits[:40]:
        print(f"{src:8} {tid:24} {name}  ({extra})")
    if a.local:
        return
    known = {h[1] for h in hits}
    try:
        site = [h for h in search_imgflip_site(query, a.pages) if h[0] not in known]
    except Exception as e:
        print(f"(imgflip site search failed: {e})", file=sys.stderr)
        site = []
    for tid, name in site:
        print(f"{'imgflip+':8} {tid:24} {name}  (blank only, from imgflip's full library)")
    if not hits and not site:
        print("no matches; try a shorter or different word")


def cmd_list(a):
    for t in memegen_templates():
        print(f"{t['id']:24} {t['lines']} lines  {t['name']}")


def cmd_template(a):
    ids = {t["id"] for t in memegen_templates()}
    if ids and a.id not in ids:
        sys.exit(f"unknown memegen template '{a.id}'. Use `search` to find the id, or "
                 f"`blank` + `label` for formats memegen does not have.")
    if not a.hosted:
        try:
            return render_template_local(a)
        except ImportError:
            print("warning: pyyaml missing, using the hosted renderer", file=sys.stderr)
        except Exception as e:
            print(f"warning: local render failed ({e}), using the hosted renderer",
                  file=sys.stderr)
    body = {"template_id": a.id, "text": [t if t.strip() else " " for t in a.text],
            "extension": "gif" if a.animated else "png"}
    if a.style:
        body["style"] = a.style
    if a.font:
        body["font"] = a.font
    res = json.loads(fetch(f"{MEMEGEN}/images", data=json.dumps(body).encode(),
                           headers={"Content-Type": "application/json"}))
    url = res["url"]
    if a.width:
        url += ("&" if "?" in url else "?") + f"width={a.width}"
    data = fetch(url)
    out = Path(a.output) if a.output else default_output(" ".join(a.text) or a.id, a.animated)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(out)


def find_blank(name):
    """Image source for a template given a memegen id, an imgflip id, or a name."""
    key = norm(name)
    for t in memegen_templates():
        if key in (norm(t["id"]), norm(t["name"])):
            return str(template_files(t["id"], None)[1])
    for t in imgflip_templates():
        if key in (norm(t["id"]), norm(t["name"])):
            return t["url"]
    if name.isdigit():
        return imgflip_blank_url(name)
    hits = search(name)
    if hits:
        src, tid, title = hits[0][:3]
        print(f"using closest match: {title}", file=sys.stderr)
        return find_blank(tid)
    site = search_imgflip_site(name)
    if not site:
        sys.exit(f"no template matches '{name}'")
    print(f"using closest imgflip match: {site[0][1]} ({site[0][0]})", file=sys.stderr)
    return imgflip_blank_url(site[0][0])


def cmd_blank(a):
    img = load(find_blank(a.name))
    out = a.output or default_output(f"blank-{a.name}", False)
    img.convert("RGB").save(out)
    print(out)


def cmd_classic(a):
    def draw_fn(im):
        w, h = im.size
        d = ImageDraw.Draw(im)
        box_w, box_h = w * 0.94, h * 0.26
        for text, at_top in ((a.top, True), (a.bottom, False)):
            if not text:
                continue
            text = text.upper()
            fnt, lines, lh = fit(text, "anton", box_w, box_h, start=h / 7, stroke=0.08)
            sw = max(2, int(fnt.size * 0.08))
            block = lh * len(lines)
            top = h * 0.025 if at_top else h - h * 0.03 - block
            draw_block(d, lines, fnt, lh, w / 2, top, "white", sw, "black")
        return im
    render(a.image, draw_fn, a.output, a.top or a.bottom or "meme")


def cmd_caption(a):
    def draw_fn(im):
        w, h = im.size
        pad = int(w * 0.05)
        name = a.font
        weight = 500 if name == "arimo" else None
        start = w / 13 if name == "arimo" else w / 10
        fnt, lines, lh = fit(a.text, name, w - 2 * pad, h * 1.2, start=start, weight=weight)
        bar = lh * len(lines) + 2 * pad - int(lh * 0.1)
        canvas = Image.new("RGBA", (w, h + bar), "white")
        canvas.paste(im, (0, bar))
        d = ImageDraw.Draw(canvas)
        if a.align == "left":
            draw_block(d, lines, fnt, lh, pad, pad, "black", align="left")
        else:
            draw_block(d, lines, fnt, lh, w / 2, pad, "black")
        return canvas
    render(a.image, draw_fn, a.output, a.text)


NUM = r"\s*([0-9.]+)\s*"
LABEL_RE = re.compile(rf"^{NUM},{NUM}(?:,{NUM})?(?:,{NUM})?:(.*)$", re.S)


def cmd_label(a):
    labels = []
    for spec in a.label:
        m = LABEL_RE.match(spec)
        if not m:
            sys.exit(f"bad label '{spec}'. Format: X,Y[,W[,H]]:text, all fractions 0-1")
        x, y = float(m[1]), float(m[2])
        bw = float(m[3]) if m[3] else 0.4
        bh = float(m[4]) if m[4] else 0.2
        labels.append((x, y, bw, bh, m[5].strip()))

    def draw_fn(im):
        w, h = im.size
        d = ImageDraw.Draw(im)
        for x, y, bw, bh, text in labels:
            if a.style == "impact":
                fnt, lines, lh = fit(text.upper(), "anton", w * bw, h * bh,
                                     start=a.size or h / 12, stroke=0.08, minimum=a.min_size)
                fill, sw, sf = "white", max(2, int(fnt.size * 0.08)), "black"
            else:
                fnt, lines, lh = fit(text, "arimo", w * bw, h * bh, start=a.size or h / 16,
                                     weight=700, minimum=a.min_size)
                fill, sw, sf = ("white" if a.style == "plain-white" else "black"), 0, None
            top = y * h - lh * len(lines) / 2
            draw_block(d, lines, fnt, lh, x * w, top, fill, sw, sf)
        return im
    render(a.image, draw_fn, a.output, labels[0][3] if labels else "label")


def cmd_stack(a):
    imgs = [load(p).convert("RGBA") for p in a.images]
    width = min(im.width for im in imgs) if a.width is None else a.width
    scaled = [im.resize((width, round(im.height * width / im.width)), Image.LANCZOS) for im in imgs]
    gap = a.gap
    if a.horizontal:
        height = min(im.height for im in scaled)
        scaled = [im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
                  for im in scaled]
        canvas = Image.new("RGBA", (sum(im.width for im in scaled) + gap * (len(scaled) - 1),
                                    height), "black")
        x = 0
        for im in scaled:
            canvas.paste(im, (x, 0))
            x += im.width + gap
    else:
        canvas = Image.new("RGBA", (width, sum(im.height for im in scaled) + gap * (len(scaled) - 1)),
                           "black")
        y = 0
        for im in scaled:
            canvas.paste(im, (0, y))
            y += im.height + gap
    save([canvas], None, a.output or default_output("stack", False))


def cmd_grid(a):
    im = load(a.image).convert("RGBA")
    w, h = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fnt = font("arimo", max(10, min(w, h) // 40), 700)
    for i in range(1, 10):
        x, y = w * i / 10, h * i / 10
        d.line([(x, 0), (x, h)], fill=(255, 0, 80, 160), width=1)
        d.line([(0, y), (w, y)], fill=(255, 0, 80, 160), width=1)
        d.text((x + 3, 3), f".{i}", font=fnt, fill=(255, 0, 80, 255),
               stroke_width=2, stroke_fill="white")
        d.text((3, y + 3), f".{i}", font=fnt, fill=(255, 0, 80, 255),
               stroke_width=2, stroke_fill="white")
    out = a.output or default_output("grid", False)
    Image.alpha_composite(im, overlay).save(out)
    print(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="find a template id by name or keyword")
    s.add_argument("query", nargs="+")
    s.add_argument("--pages", type=int, default=1,
                   help="pages of imgflip's full-library results, about 20 per page")
    s.add_argument("--local", action="store_true",
                   help="only the cached memegen and imgflip top-100 catalogues")
    s.set_defaults(fn=cmd_search)

    s = sub.add_parser("list", help="list every memegen template id")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("template", help="render a memegen template with correct text placement")
    s.add_argument("id")
    s.add_argument("text", nargs="*", help="one argument per text slot, '' to leave a slot empty")
    s.add_argument("--style", help="template style variant, see `search` output on memegen.link")
    s.add_argument("--font", help="memegen font id: thick (default), thin, impact")
    s.add_argument("--width", type=int)
    s.add_argument("--animated", action="store_true", help="gif output for animated templates")
    s.add_argument("--hosted", action="store_true",
                   help="render on memegen.link instead of locally (adds its watermark)")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_template)

    s = sub.add_parser("blank", help="download a blank template image (memegen or imgflip)")
    s.add_argument("name")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_blank)

    s = sub.add_parser("classic", help="white impact top/bottom text on any image")
    s.add_argument("image")
    s.add_argument("--top", default="")
    s.add_argument("--bottom", default="")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_classic)

    s = sub.add_parser("caption", help="modern caption: black text on a white bar above the image")
    s.add_argument("image")
    s.add_argument("text")
    s.add_argument("--font", choices=["arimo", "anton"], default="arimo")
    s.add_argument("--align", choices=["center", "left"], default="center")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_caption)

    s = sub.add_parser("label", help="place text at fractional coordinates on an image")
    s.add_argument("image")
    s.add_argument("label", nargs="+",
                   help="X,Y[,W[,H]]:text. X,Y is the label centre, W,H the box it must fit in, "
                        "all fractions of the image (default box 0.4 x 0.2)")
    s.add_argument("--style", choices=["impact", "plain", "plain-white"], default="impact")
    s.add_argument("--size", type=int, help="starting font size in px; still shrinks to fit")
    s.add_argument("--min-size", type=int, default=12)
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_label)

    s = sub.add_parser("stack", help="join images into one multi-panel image")
    s.add_argument("images", nargs="+")
    s.add_argument("--horizontal", action="store_true")
    s.add_argument("--width", type=int)
    s.add_argument("--gap", type=int, default=0)
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_stack)

    s = sub.add_parser("grid", help="overlay a 10%% coordinate grid to plan label positions")
    s.add_argument("image")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_grid)

    a = p.parse_args()
    try:
        a.fn(a)
    except urllib.error.URLError as e:
        sys.exit(f"network error: {e}. Local commands (classic, caption, label, stack) still work.")


if __name__ == "__main__":
    main()
