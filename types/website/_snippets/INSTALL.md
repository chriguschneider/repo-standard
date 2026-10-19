## Development

Astro, built statically into `dist/` and served by Cloudflare Pages.

```bash
npm ci
npm run dev        # http://localhost:4321
npm run build      # astro check, astro build, link and CSP checks: what CI and Cloudflare run
npm run preview    # serve dist/ locally
CF_PAGES_BRANCH=@@BRANCH@@ npm run build   # build as a preview: banner, noindex
```

## From change to live

| Branch | Serves | Who writes |
|---|---|---|
| `@@BRANCH@@` (default) | [@@PREVIEW_URL@@](@@PREVIEW_URL@@): banner on every page, closed to search engines | PRs, by humans and agents |
| `@@PRODUCTION_BRANCH@@` | [@@SITE_URL@@](@@SITE_URL@@) | the owner only, by fast-forward |

Every change is a PR into `@@BRANCH@@`; Cloudflare Pages rebuilds the
preview a minute or two after each merge. Once the owner has checked the
preview, `@@PRODUCTION_BRANCH@@` is fast-forwarded to `@@BRANCH@@`
(`git push origin @@BRANCH@@:@@PRODUCTION_BRANCH@@`) and Pages deploys
production; `npm run deploy:status` confirms the commit is live. The full
procedure, and what counts as approval, is in
[`AGENTS.md`](AGENTS.md#release-procedure).

There are no version numbers, tags or changelog: the PR titles on `@@BRANCH@@`
and the deployment history in Cloudflare Pages are the record.
