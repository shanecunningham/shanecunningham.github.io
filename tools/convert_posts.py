#!/usr/bin/env python3
"""Convert WordPress/Ghost-era posts (TOML front matter, mixed HTML + Markdown)
into clean Markdown with YAML front matter for the mono-pop Hugo theme.

Usage: convert_posts.py <posts_dir> [--check-only]

Guarantees checked per post (any failure is reported and the post is left untouched):
  * every code block's text survives (after entity decoding and tag stripping)
  * no raw HTML tags remain outside code
"""
import html
import json
import re
import sys
import tomllib
from pathlib import Path

PH = "\u0000PH{}\u0000"          # placeholder for protected spans
PH_RE = re.compile("\u0000PH(\\d+)\u0000")

TAG_MAP = {
    "rackspace": "rackspace", "nagios": "nagios", "kubernetes": "kubernetes",
    "esxi": "esxi", "pfsense": "pfsense", "xenserver": "xenserver",
    "windows server": "windows", "rdo": "openstack", "mysql": "mysql",
    "lamp": "lamp", "hyper-v": "hyper-v", "coreos": "coreos", "ceph": "ceph",
    "saltstack": "saltstack", "docker": "docker", "openstack": "openstack",
    "openstack-ansible": "openstack-ansible",
}

SHELL_WORDS = re.compile(
    r"^(sudo|apt-get|apt|yum|dnf|cd|git|pip|pip3|curl|wget|nova|neutron|glance|cinder|openstack|keystone|"
    r"swift|heat|magnum|trove|ssh|scp|mount|umount|cp|mv|mkdir|rm|ls|vi|vim|nano|cat|echo|export|kubectl|"
    r"docker|systemctl|service|chkconfig|ansible|ansible-playbook|openstack-ansible|lxc-\w+|tar|make|"
    r"chmod|chown|ln|ip|ifconfig|brctl|ovs-vsctl|xe|xl|esxcli|vmkfstools|zfs|zpool|terraform|salt|"
    r"salt-cloud|salt-key|hdiutil|diskutil|dd|fdisk|parted|mkfs\.\w+|modprobe|lsmod|lspci|uname|"
    r"grep|sed|awk|tail|head|find|locate|updatedb|crontab|htpasswd|a2ensite|a2enmod|nginx|apachectl|"
    r"mysql|mysqldump|mysqladmin|pvcreate|vgcreate|lvcreate|losetup|rabbitmqctl|uuencode|mail|"
    r"touch|source|\.|python|python3|bash|sh|npm|go|brew|port|hostnamectl|netstat|ss|ping|"
    r"telnet|nc|dig|nslookup|openssl|ssh-keygen|useradd|passwd|su|reboot|shutdown|"
    r"extlinux|xenstore-\w+|gem|bundle|rake|virsh|qemu-img|lvm|cfdisk|swapon|sysctl)\b"
)
PROMPT = re.compile(r"^(\$ |# |\[?[\w.-]+@[\w.-]+[^\n]*?[#$] |root@)")


def guess_lang(code: str) -> str:
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return "text"
    first = lines[0].strip()
    if sum(1 for l in lines if PROMPT.match(l.strip())) >= 1 and PROMPT.match(first):
        return "console"
    if first.startswith(("{", "[")) and code.strip().endswith(("}", "]")):
        try:
            json.loads(code)
            return "json"
        except Exception:
            pass
    if re.match(r"^#!.*\b(bash|sh)\b", first):
        return "sh"
    if re.match(r"^#!.*python", first) or re.match(r"^(import |from \S+ import |def |class )", first):
        return "python"
    if re.match(r"^(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|USE|SHOW|FLUSH)\b", first, re.I) \
            and not SHELL_WORDS.match(first):
        return "sql"
    if re.match(r"^<\?php", first):
        return "php"
    if re.match(r"^<(\?xml|[a-zA-Z][\w:-]*[ >])", first):
        return "xml"
    if re.match(r"^(server|location|upstream|http)\s*\{", first) or re.search(r"^\s*(listen|server_name|proxy_pass)\s", code, re.M):
        return "nginx"
    if re.match(r"^<(VirtualHost|Directory)", first, re.I):
        return "apache"
    yamlish = sum(1 for l in lines if re.match(r"^\s*(- )?[\w.\-]+:(\s|$)", l))
    if lines[0].strip() == "---" or (yamlish >= max(2, len(lines) * 0.6) and not SHELL_WORDS.match(first)):
        return "yaml"
    if re.match(r"^\[[\w .:-]+\]$", first) and sum(1 for l in lines if "=" in l) >= 1:
        return "ini"
    shellish = sum(1 for l in lines if SHELL_WORDS.match(l.strip()))
    if shellish >= max(1, len(lines) * 0.5):
        return "sh"
    return "text"


def norm_code(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.rstrip() for l in s.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def decode_code(raw: str) -> str:
    """Inner HTML of a <pre>/<code> block -> plain code text."""
    s = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    s = re.sub(r"</?(code|span|strong|b|em|i|tt|font)\b[^>]*>", "", s, flags=re.I)
    s = html.unescape(s).replace(" ", " ")
    # curly quotes and dashes never belong in code
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                                   "–": "--", "—": "--"}))
    return norm_code(s)


def fence(code: str, lang: str) -> str:
    ticks = "```"
    while ticks in code:
        ticks += "`"
    return f"{ticks}{lang}\n{code}\n{ticks}"


class Converter:
    def __init__(self):
        self.store = []

    def protect(self, text: str) -> str:
        self.store.append(text)
        return PH.format(len(self.store) - 1)

    def block(self, text: str) -> str:
        # block-level placeholder on its own paragraph
        return "\n\n" + self.protect(text) + "\n\n"

    def restore(self, s: str) -> str:
        for _ in range(5):
            s2 = PH_RE.sub(lambda m: self.store[int(m.group(1))], s)
            if s2 == s:
                break
            s = s2
        return s


def inline_html(s: str) -> str:
    """Convert inline HTML (no code here) to Markdown."""
    # images (optionally wrapped in a link)
    def img(m):
        tag = m.group(0)
        src = re.search(r'src=["\']?([^"\'\s>]+)', tag)
        alt = re.search(r'alt=["\']([^"\']*)', tag)
        title = re.search(r'title=["\']([^"\']*)', tag)
        a = (alt.group(1) if alt else "") or (title.group(1) if title else "")
        return f"![{a.strip()}]({src.group(1) if src else ''})"
    s = re.sub(r"<a\b[^>]*>\s*(<img\b[^>]*>)\s*</a>", lambda m: img(re.match(r".*", m.group(1))), s, flags=re.I | re.S)
    s = re.sub(r"<img\b[^>]*>", img, s, flags=re.I)

    # emphasis (move inner edge whitespace outside the markers)
    def emph(marker):
        def f(m):
            inner = m.group(2)
            if not inner.strip():
                return inner
            lead = inner[: len(inner) - len(inner.lstrip())]
            trail = inner[len(inner.rstrip()):]
            return f"{lead}{marker}{inner.strip()}{marker}{trail}"
        return f
    s = re.sub(r"<(strong|b)\b[^>]*>(.*?)</\1>", emph("**"), s, flags=re.I | re.S)
    s = re.sub(r"<(em|i)\b[^>]*>(.*?)</\1>", emph("*"), s, flags=re.I | re.S)

    # links
    def link(m):
        attrs, text = m.group(1), m.group(2)
        href = re.search(r'href=["\']([^"\']*)', attrs)
        text = re.sub(r"\s+", " ", text).strip()
        if not href:
            return text
        url = href.group(1).replace(" ", "%20")
        return f"[{text or url}]({url})"
    s = re.sub(r"<a\b([^>]*)>(.*?)</a>", link, s, flags=re.I | re.S)
    s = re.sub(r"<a\b[^>]*name=[^>]*>\s*</a>|<a\s+name=[^>]*>", "", s, flags=re.I)

    # presentational wrappers
    s = re.sub(r"</?(span|font|div|center|u)\b[^>]*>", "", s, flags=re.I)
    return s


def block_html(s: str) -> str:
    # headings: body h1 -> h2 (the post title is the page h1)
    for lvl, md in (("1", "##"), ("2", "##"), ("3", "###"), ("4", "####")):
        s = re.sub(rf"<h{lvl}\b[^>]*>(.*?)</h{lvl}>", lambda m, md=md: f"\n\n{md} {re.sub(r'\s+', ' ', m.group(1)).strip()}\n\n",
                   s, flags=re.I | re.S)

    # lists
    def ul(m, ordered=False):
        items = re.findall(r"<li\b[^>]*>(.*?)</li>", m.group(1), flags=re.I | re.S)
        out = []
        for n, it in enumerate(items, 1):
            it = re.sub(r"\s*\n\s*", " ", it.strip())
            out.append(f"{n}. {it}" if ordered else f"- {it}")
        return "\n\n" + "\n".join(out) + "\n\n"
    s = re.sub(r"<ul\b[^>]*>(.*?)</ul>", ul, s, flags=re.I | re.S)
    s = re.sub(r"<ol\b[^>]*>(.*?)</ol>", lambda m: ul(m, True), s, flags=re.I | re.S)

    # blockquote
    s = re.sub(r"<blockquote\b[^>]*>(.*?)</blockquote>",
               lambda m: "\n\n" + "\n".join("> " + l.strip() for l in m.group(1).strip().splitlines() if l.strip()) + "\n\n",
               s, flags=re.I | re.S)

    # paragraphs and breaks
    s = re.sub(r"<p\b[^>]*>", "\n\n", s, flags=re.I)
    s = re.sub(r"</p>", "\n\n", s, flags=re.I)
    s = re.sub(r"<br\s*/?>\s*", "\n", s, flags=re.I)
    s = re.sub(r"<hr\s*/?>", "\n\n---\n\n", s, flags=re.I)
    return s


STRUCT = re.compile(r"^(\s*([-*+] |\d+\. |>|#{1,6} |\||---\s*$|!\[)|\u0000PH)")


def hard_breaks(s: str) -> str:
    """WordPress and Ghost turned single newlines into <br>. Keep those breaks
    explicitly (CommonMark backslash hard break) between consecutive prose lines."""
    lines = s.split("\n")
    out = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if (line.strip() and nxt.strip()
                and not STRUCT.match(line) and not STRUCT.match(nxt)
                and not line.rstrip().endswith("\\")):
            out.append(line.rstrip() + "\\")
        else:
            out.append(line)
    return "\n".join(out)


def convert_body(body: str, report: dict) -> tuple[str, list]:
    c = Converter()
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    codes = []

    # 1. existing Markdown fences
    def md_fence(m):
        lang = (m.group(2) or "").strip()
        code = norm_code(html.unescape(m.group(3)) if re.search(r"&(lt|gt|amp|quot|#\d+);", m.group(3)) else m.group(3))
        if lang in ("shell",):
            lang = "sh"
        lang = lang or guess_lang(code)
        codes.append(code)
        return c.block(fence(code, lang))
    body = re.sub(r"(?m)^([ \t]*)```[ \t]*([\w+-]*)[ \t]*\n(.*?)\n[ \t]*```[ \t]*$", md_fence, body, flags=re.S)

    # 2. <pre> blocks
    def pre(m):
        code = decode_code(m.group(1))
        codes.append(code)
        return c.block(fence(code, guess_lang(code)))
    body = re.sub(r"<pre\b[^>]*>(.*?)</pre>", pre, body, flags=re.I | re.S)
    # stray </pre> with no opener
    if re.search(r"</pre>", body, re.I):
        report.setdefault("notes", []).append("stray </pre> removed")
        body = re.sub(r"</pre>", "", body, flags=re.I)

    # 3. inline <code> (and multi-line <code> used as a block)
    def code_inline(m):
        code = decode_code(m.group(1))
        if "\n" in code:
            codes.append(code)
            return c.block(fence(code, guess_lang(code)))
        ticks = "``" if "`" in code else "`"
        pad = " " if code.startswith("`") or code.endswith("`") else ""
        return c.protect(f"{ticks}{pad}{code}{pad}{ticks}")
    body = re.sub(r"<code\b[^>]*>(.*?)</code>", code_inline, body, flags=re.I | re.S)

    # 4. existing inline Markdown code spans: protect from entity decoding
    body = re.sub(r"(?<!`)`[^`\n]+`(?!`)", lambda m: c.protect(m.group(0)), body)

    # 5. HTML -> Markdown
    body = inline_html(body)
    body = block_html(body)

    # 6. entities in prose: decode everything except the three that would turn into markup
    def ent(m):
        e = m.group(0)
        if e in ("&lt;", "&gt;", "&amp;"):
            return e
        return html.unescape(e)
    body = re.sub(r"&#?\w+;", ent, body)
    body = body.replace(" ", " ")

    # 7. headings need a space after the hashes; tidy whitespace
    body = re.sub(r"(?m)^(#{1,6})([^#\s])", r"\1 \2", body)
    body = re.sub(r"(?m)^# ", "## ", body)          # body h1 -> h2
    body = re.sub(r"[ \t]+$", "", body, flags=re.M)
    body = re.sub(r"(?m)^[ \t]+(?=\S)(?![-*+] |\d+\. )", "", body)  # WordPress indentation is not code
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    body = hard_breaks(body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    # placeholders sit on their own paragraph; restoring must not touch code whitespace
    body = c.restore(body).strip() + "\n"
    return body, codes


def original_codes(body: str) -> list:
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for m in re.finditer(r"(?m)^[ \t]*```[ \t]*[\w+-]*[ \t]*\n(.*?)\n[ \t]*```[ \t]*$", body, flags=re.S):
        raw = m.group(1)
        out.append(norm_code(html.unescape(raw) if re.search(r"&(lt|gt|amp|quot|#\d+);", raw) else raw))
    body = re.sub(r"(?m)^[ \t]*```.*?```[ \t]*$", "", body, flags=re.S)
    for m in re.finditer(r"<pre\b[^>]*>(.*?)</pre>", body, flags=re.I | re.S):
        out.append(decode_code(m.group(1)))
    body = re.sub(r"<pre\b[^>]*>.*?</pre>", "", body, flags=re.I | re.S)
    for m in re.finditer(r"<code\b[^>]*>(.*?)</code>", body, flags=re.I | re.S):
        d = decode_code(m.group(1))
        if "\n" in d:
            out.append(d)
    return out


def output_codes(md: str) -> list:
    return [norm_code(m.group(2)) for m in
            re.finditer(r"(?m)^(`{3,})[\w+-]*\n(.*?)\n\1$", md, flags=re.S)]


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def front_matter(fm: dict) -> str:
    tags = []
    for t in list(fm.get("categories", [])) + list(fm.get("tags", [])):
        k = TAG_MAP.get(t.strip().lower(), re.sub(r"[^a-z0-9]+", "-", t.strip().lower()).strip("-"))
        if k and k not in tags:
            tags.append(k)
    date = fm["date"]
    date = date.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(date, "strftime") else str(date)
    lines = ["---", f"title: {yaml_str(fm['title'].strip())}", f"date: {date}"]
    if fm.get("description"):
        lines.append(f"description: {yaml_str(fm['description'])}")
    lines.append("tags: [" + ", ".join(yaml_str(t) for t in tags) + "]")
    if fm.get("draft"):
        lines.append("draft: true")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def convert_file(path: Path, write: bool) -> dict:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    report = {"file": path.name}
    m = re.match(r"\+\+\+\n(.*?)\n\+\+\+\n(.*)", text, re.S)
    if not m:
        report["skipped"] = "not TOML front matter"
        return report
    fm = tomllib.loads(m.group(1))
    body_in = m.group(2)
    body, _ = convert_body(body_in, report)

    before = sorted(original_codes(body_in))
    after = sorted(output_codes(body))
    if before != after:
        missing = [b for b in before if b not in after]
        extra = [a for a in after if a not in before]
        report["code_mismatch"] = {"missing": [x[:120] for x in missing], "extra": [x[:120] for x in extra]}

    prose = re.sub(r"(?ms)^(`{3,})[\w+-]*\n.*?\n\1$", "", body)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    leftovers = sorted(set(re.findall(r"</?[a-zA-Z][a-zA-Z0-9]*\b[^>\n]*>", prose)))
    if leftovers:
        report["html_left"] = leftovers[:10]

    report["code_blocks"] = len(after)
    if write and "code_mismatch" not in report:
        path.write_text(front_matter(fm) + body, encoding="utf-8")
        report["written"] = True
    return report


def main():
    posts = Path(sys.argv[1])
    write = "--check-only" not in sys.argv
    results = [convert_file(p, write) for p in sorted(posts.glob("*.md"))]
    bad = [r for r in results if "code_mismatch" in r or "html_left" in r]
    print(json.dumps(bad, indent=1, ensure_ascii=False))
    print(f"converted {sum(1 for r in results if r.get('written'))} / {len(results)}; "
          f"code blocks {sum(r.get('code_blocks', 0) for r in results)}; "
          f"issues {len(bad)}; skipped {sum(1 for r in results if 'skipped' in r)}")


if __name__ == "__main__":
    main()
