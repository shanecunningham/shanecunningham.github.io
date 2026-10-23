# CLAUDE.md

Personal Hugo blog for cunninghamshane.com, deployed to GitHub Pages by `.github/workflows/hugo.yaml` on every push to `main`. Pull requests into `main` get a build-only check.

## Run it locally

1. Check for Hugo with `hugo version`. If it is missing, install it with `winget install Hugo.Hugo.Extended` and open a new shell. CI uses 0.168.0; anything 0.128 or newer works.
2. From the repo root, run `hugo server -D` in the background and open http://localhost:1313/.
3. A clean build (`hugo --gc --minify`) prints no warnings. Treat any warning as a bug.

## Layout

- `hugo.toml`: site config, personal details (`params`), nav (`menus.main`).
- `content/posts/`: every post. The filename is the URL slug (`/posts/<file>/`). A post with images is a page bundle: `content/posts/<slug>/index.md`, with the images next to it.
- `content/about.md`, `content/archive.md` (the by-year list, using `layout: archive`).
- `themes/mono-pop/`: the theme, vendored here and owned by this repo. The colors are CSS variables at the top of `assets/css/main.css`.
- `tools/convert_posts.py`: the one-time WordPress HTML to Markdown converter (kept for reference).
- `tools/recover_images.py`: restores images from the Wayback Machine (see below).

## Post conventions

- YAML front matter: `title`, `date`, `description` (one sentence), `tags` (1 to 3), and optionally `archived: true`, `draft: true` or `toc: false`.
- Tags come from a small fixed set: openstack, openstack-ansible, rackspace, kubernetes, docker, coreos, ceph, nagios, monitoring, esxi, vmware, xenserver, hyper-v, virtualization, zfs, storage, pfsense, networking, linux, windows, macos, mysql, lamp, apache, nginx, wordpress, saltstack, terraform, hardware, homelab, tools, meta. Add new ones sparingly.
- `archived: true` marks a post as historical. The theme shows an "Archived" note and badge. Archived posts are kept as written: never delete a post, and don't rewrite archived ones beyond fixing formatting.
- Code goes in fenced blocks with a language (`sh` for commands, `console` for prompts mixed with output, `text` for plain output, `yaml`, `ini` and so on). Add `{title="/path/to/file"}` when a block is the contents of a file.
- Never publish real credentials, tokens or personal email addresses in code samples. Use `<redacted>` or `you@example.com`.
- Raw HTML is not rendered (Goldmark's default). Write Markdown.

## Pending: recover images

39 images in 13 posts still point to hosts that no longer exist: the old WordPress uploads and a Rackspace CDN. To restore whatever the Wayback Machine has:

```sh
python tools/recover_images.py --dry-run   # see what is archived
python tools/recover_images.py             # download, make page bundles, rewrite links
hugo server -D                             # check the affected posts
```

Images with no archived copy are replaced with a short "(Image no longer available)" note. Commit the result.
