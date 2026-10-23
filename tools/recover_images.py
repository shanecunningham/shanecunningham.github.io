#!/usr/bin/env python3
"""Recover images from dead hosts via the Wayback Machine.

For every Markdown image in content/posts/*.md that points at a dead host
(the old WordPress uploads on cunninghamshane.com, or the old Rackspace
Cloud Files CDN), this script:

  1. looks the URL up in the Wayback Machine (CDX API, any capture date),
  2. downloads the original bytes of the newest good capture,
  3. turns the post into a page bundle (posts/<slug>.md -> posts/<slug>/index.md)
     and saves the image next to it,
  4. rewrites the image link to the local file.

Images with no capture are replaced by a short italic note, so no post shows
a broken image.

Usage (from the repo root):
    python tools/recover_images.py --dry-run   # report only, change nothing
    python tools/recover_images.py             # do it

Standard library only; works on Windows, macOS and Linux.
"""
import argparse
import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DEAD_HOSTS = (
    "cunninghamshane.com/wp-content/",
    "www.cunninghamshane.com/wp-content/",
    "cdn.cunninghamshane.com/",
    ".rackcdn.com/",
)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
UA = {"User-Agent": "cunninghamshane.com image recovery (personal blog migration)"}


def is_dead(url: str) -> bool:
    return url.startswith("http") and any(h in url for h in DEAD_HOSTS)


def get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def find_capture(url: str):
    """Return (timestamp, original_url) of the newest 200 capture, or None."""
    bare = re.sub(r"^https?://", "", url)
    q = urllib.parse.urlencode({
        "url": bare, "output": "json", "filter": "statuscode:200",
        "fl": "timestamp,original,mimetype", "limit": "-5",
    })
    try:
        rows = json.loads(get(f"https://web.archive.org/cdx/search/cdx?{q}") or b"[]")
    except Exception as e:
        print(f"    cdx lookup failed: {e}")
        return None
    rows = [r for r in rows[1:] if r[2].startswith("image/")] if rows else []
    if not rows:
        return None
    ts, original, _ = rows[-1]
    return ts, original


def safe_name(url: str, used: set) -> str:
    name = Path(urllib.parse.urlparse(url).path).name or "image"
    name = re.sub(r"[^A-Za-z0-9._-]", "-", name)
    base, ext = (name.rsplit(".", 1) + [""])[:2]
    cand, n = name, 2
    while cand.lower() in used:
        cand = f"{base}-{n}.{ext}" if ext else f"{base}-{n}"
        n += 1
    used.add(cand.lower())
    return cand


def to_bundle(md: Path) -> Path:
    """posts/<slug>.md -> posts/<slug>/index.md (returns the new index.md path)."""
    if md.name == "index.md":
        return md
    bundle = md.with_suffix("")
    bundle.mkdir(exist_ok=True)
    target = bundle / "index.md"
    shutil.move(str(md), str(target))
    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--posts", default="content/posts")
    args = ap.parse_args()

    posts = Path(args.posts)
    if not posts.is_dir():
        sys.exit(f"{posts} not found; run from the repo root")

    found = missing = 0
    files = sorted(list(posts.glob("*.md")) + list(posts.glob("*/index.md")))
    for md in files:
        text = md.read_text(encoding="utf-8")
        dead = [(m.group(1), m.group(2)) for m in IMG_RE.finditer(text) if is_dead(m.group(2))]
        if not dead:
            continue
        print(f"{md}: {len(dead)} image(s)")
        replacements, downloads = {}, []
        used = set()
        for alt, url in dead:
            if url in replacements:
                continue
            cap = find_capture(url)
            time.sleep(1)  # be polite to archive.org
            if not cap:
                missing += 1
                print(f"    not archived: {url}")
                note = f"*(Image no longer available{': ' + alt if alt else ''}.)*"
                replacements[url] = ("note", note)
                continue
            ts, original = cap
            fname = safe_name(url, used)
            raw = f"https://web.archive.org/web/{ts}id_/{original}"
            found += 1
            print(f"    found {ts}: {fname}")
            replacements[url] = ("file", fname)
            downloads.append((raw, fname))

        if args.dry_run:
            continue

        has_files = any(kind == "file" for kind, _ in replacements.values())
        target = to_bundle(md) if has_files else md
        folder = target.parent
        ok = set()
        for raw, fname in downloads:
            try:
                data = get(raw, timeout=60)
                (folder / fname).write_bytes(data)
                ok.add(fname)
            except Exception as e:
                print(f"    download failed for {fname}: {e}")

        def repl(m):
            alt, url = m.group(1), m.group(2)
            if url not in replacements:
                return m.group(0)
            kind, val = replacements[url]
            if kind == "file" and val in ok:
                return f"![{alt}]({val})"
            if kind == "file":
                return f"*(Image no longer available{': ' + alt if alt else ''}.)*"
            return val

        target.write_text(IMG_RE.sub(repl, target.read_text(encoding="utf-8")), encoding="utf-8")

    print(f"\narchived copies found: {found}, not archived: {missing}"
          + (" (dry run, nothing changed)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
