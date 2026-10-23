# Blog handover: cunninghamshane.com

Last updated 2026-10-23, 1:40 am CT.

**Overnight (1:00 to 1:20 am):**
- **Old internal links fixed:** 8 links in 7 posts pointed to pre-migration URLs. They now point to `/posts/<slug>/`, and none of the 2,233 internal links are broken. Live in commit `6ef4763`.
- **Demo post restored:** I deleted the archie theme's demo post by mistake. It's back, unchanged and still a draft (commit `cd0dae3`).
- **Rule going forward:** nothing gets deleted, whether posts, branches or files.

## Where things stand

The site is live at https://cunninghamshane.com on the new **mono-pop** theme, deployed by GitHub Actions from `main`.

- **Repo:** `shanecunningham/shanecunningham.github.io`. The default branch is `main`, and the github-pages environment allows deploys from `main` only.
- **CI:** `.github/workflows/hugo.yaml` deploys on push to `main` and runs a build-only check on pull requests. Hugo is pinned to 0.168.0, the latest release as of Oct 13.
- **Posts:** all 85 old posts are converted from WordPress HTML to Markdown under `content/posts/`, at `/posts/<slug>/`. 81 are marked `archived: true` and show an "Archived" note. No posts were deleted.
- **New post:** "Hello, world (again)" (`content/posts/hello-world-again.md`) shows kubectl + jq one-liners.
- **Home page:** shows the 2 newest posts, then "archive by year" and "all posts" links. The count is `params.homePosts` in `hugo.toml`.
- **Layout:** the column and type scale up on wide screens, with steps at 1440, 1920 and 2560px. These are the `--k` and `--wrap` variables in `themes/mono-pop/assets/css/main.css`.
- **About page:** one paragraph about the blog's history. No bio, and no GitHub link anywhere.
- **Security:** credentials and a personal email were redacted from old OpenStack and Tectonic code samples. The old values are still in git history; rotate anything that might still be live.

PRs and pushes so far: #35 (master to main), #36 (theme and post cleanup, merged), then direct pushes to `main` for the About page, the home-page post count and the hello-world post.

## Open decisions

1. **Colors.** The current site is still the violet and mint palette. Six no-purple, no-blue options are on the design canvas, in the bottom row ("D color options"):
   - E: rust + teal
   - F: forest + amber
   - G: neutral with a color per tag
   - H: coral + mustard + teal
   - I: ink + red
   - J: tangerine + sage

   Pick one, or a mix, and it gets applied to `main.css`. The tokens are at the top of the file: `--accent`, `--accent2`, `--hl`, `--chip`, and the `.chroma` syntax colors.

## To do

- [ ] **Recover images.** 39 images in 13 posts point to dead hosts. Run on the PC, from the repo root: `python tools/recover_images.py --dry-run`, then without `--dry-run`. It pulls archived copies from the Wayback Machine into page bundles, and replaces missing ones with a short note. Commit and push.
- [ ] **Sync the local repo.** The local clone is on `cleanup` and behind `main`: `git switch main; git pull`.
- [ ] **Old branches.** There are 14 old branches on GitHub, all merged into `main` except `test` (one commit, "test 2"). Keep them or tidy them later; your call.
- [ ] **Match local Hugo to CI.** `winget upgrade Hugo.Hugo.Extended` gets it to 0.168.
- [ ] **Test the one-liners.** Run the hello-world one-liners against a real cluster once. They were tested against sample `kubectl` JSON, not a live cluster.

## Ideas parked

- Pagefind site search (static, works on Pages)
- A link checker in CI (lychee or htmltest), since the old posts link to many dead vendor pages
- A favicon and a default social image (there's no `static/` folder yet)

## How to work on it

- **Preview:** `hugo server -D`, then open http://localhost:1313/.
- **New post:** `hugo new content posts/my-post.md`, then remove `draft: true` to publish.
- **Conventions:** front matter is YAML with `title`, `date`, `description` (one sentence), `tags` (1 to 3 from the list in `CLAUDE.md`), and optionally `archived`, `draft` or `toc`.
- **Code blocks:** fenced with a language (`sh`, `console`, `text`, `yaml`, and so on). Add `{title="path"}` when a block is a file's contents.
- **Repo docs:** full conventions are in the repo's `CLAUDE.md`, the run instructions in `README.md`.
- **Pushing:** pushes via PR get the build check. Small fixes can go straight to `main`.

## Links

- Live site: https://cunninghamshane.com
- Repo: https://github.com/shanecunningham/shanecunningham.github.io
- Theme PR: https://github.com/shanecunningham/shanecunningham.github.io/pull/36
- Design canvas (mockups A to D, color options E to J): https://claude.ai/artifact/DANoHh9NQayEyEuTWbmVnk
- Migration plan doc: https://claude.ai/artifact/9eKWzkVT6A6F2oFU2twp5g
