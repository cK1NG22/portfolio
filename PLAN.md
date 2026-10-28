# Plan — round 2

Written 2026-10-04. Branch `worktree-revamp`, worktree `.claude/worktrees/revamp`. Execute phases 1–5 in order; phase 6 is later.
Git in this worktree: use `/usr/bin/git` as single plain commands (the rtk hook breaks compound git commands).
Dev server: `npm --prefix <worktree> run dev -- --port 5173 --strictPort`.

## Status (2026-10-04)

Phases 1–5 are built on this branch. Phase 6 is not started.
A polish pass on the hero, activity section and project gallery was also done on 2026-10-04 (see the decisions below).

Still needed from Carter:

- [ ] X profile URL → `profile.links.x` in `src/content.ts` (the icon is hidden until set).
- [ ] LinkedIn and X post URLs → `media` in `src/content.ts` (the Media nav item is hidden until there is one).
- [ ] Screenshots for project covers (still generated gradients).
- [ ] Whether to make `mode-memory` public on GitHub.
- [x] Add Jan–Feb 2026 Claude Code activity from the other laptop. Done 2026-10-28 from the private `claude-backup` repo: its per-day counts are in `scripts/claude-other-machines.json`, and the Claude grid now starts 2026-01-13. To refresh: `python3 scripts/activity.py <other history.jsonl>`.
- [ ] Confirm the Eight Faces and venture fund pages are cleared with the client and Foundry before this branch goes live.

Decisions made while building (change if wrong):

- Activity squares show both sources behind a toggle. Refresh is a local script (`scripts/activity.py`); the scheduled GitHub Action was not added.
- Case pages built for: venture fund engagement (Topsail, client unnamed), Eight Faces, Companion, Balkanski, Locker. Shifts, AI LMS, and Knowledge Tree were not added.
- LinkedIn posts use the site's own card, not the LinkedIn iframe.
- Hero tagline is drawn with React Bits Tech Text. It sweeps left to right once in 5 seconds, parks on the period, follows the pointer on hover, then returns to the period.
- Activity shows GitHub and Claude Code combined by default (each square takes the higher of the two levels). The source picker is a logo-only Glide Select under the grid; its menu opens downward. The captions and totals lines were removed at Carter's request, so the page no longer says what is counted or the data dates.
- Lines of code, commits and repositories sit to the right of the grid, sized from the squares' height, right-aligned, all counting up.
- Project gallery uses React Bits Refine Frame: closed cards show the coarsest block stage, the open card refines to the sharp cover. The frame's status chip is off because it sits where the project title is.

Known and not fixed:

- The activity squares and the numbers beside them shrink as weeks are added through the year.
- The source picker's menu can run off the bottom of a short window.

## Phase 1 — Nav icons

- Replace the "GitHub" and "LinkedIn" text pills with logos; add X.
- `PillNavItem.label` is a string and is rendered in two stacked spans (rest and hover state). Add an optional `icon: ReactNode` to the item type in `src/components/reactbits/PillNav.tsx`; render it in both spans; keep `ariaLabel` as the accessible name. Same in the mobile menu, where icon + text label both show.
- Icons from `react-icons` (already installed). Check which brand marks exist before use (`SiGithub` exists; LinkedIn and X may need `react-icons/fa6`).
- Test: nav links have accessible names "GitHub", "LinkedIn", "X" and correct hrefs; axe still clean.

## Phase 2 — Tools: name on hover, click through to the site

- Keep Logo Loop (it already pauses on hover and supports `href` per logo). Add `href` for each tool in `src/pages/Home.tsx` and move the tool list into `src/content.ts`.
- Use Logo Loop's `renderItem` to wrap each logo with a label that appears on hover and keyboard focus. No React Bits tooltip exists.
- Gotcha: the loop clips overflow, so the label has to sit inside the track (reserve vertical padding) rather than float above it.
- Alternative considered: React Bits **Dock** has hover labels built in, but it is a static row, not a loop. Carter asked for the loop, so the loop stays unless he prefers Dock.
- Test: each tool link has the tool name and the right href; label visible on focus.

## Phase 3 — Activity squares

Data sources:

| Source | Where the data is | How it stays fresh |
|---|---|---|
| GitHub contributions | GitHub GraphQL `contributionsCalendar` | Can refresh with no Mac involved: a scheduled GitHub Action runs the query daily and commits `src/activity.json`. Default token shows public contributions; private-repo counts need a personal token stored as an Actions secret (never in the repo). |
| Claude Code activity | `~/.claude/stats-cache.json` → `dailyActivity` (messages, sessions, tool calls per day, from 2026-03-23) | Only on this Mac. A local script writes it into `src/activity.json`; it refreshes when the script is run (by hand, or from one of the scheduled shifts) and pushed. The cache itself was last computed 2026-10-01, so check what updates it. |

- Render with `react-activity-calendar` (fetch docs via `ctx7 docs /grubersjoe/react-activity-calendar` first). One component, two datasets, accent-colour theme.
- If both: a small toggle (GitHub / Claude Code) over one grid, or two stacked grids. Decide from how it looks.
- Script: `scripts/activity.py`, same pattern as `scripts/loc.py`. Only day + count leave the Mac; no prompts, paths, or project names.
- Caption states what is counted and the as-of date, like the lines-of-code figure.
- Test: grid renders with an accessible label; the JSON has the expected shape; axe clean (check colour contrast of the lowest level).

## Phase 4 — Media section

- New `/media` route and nav item. Data in `src/content.ts` as a list of `{ kind: 'x' | 'linkedin', url, ... }`.
- **X posts:** `react-tweet` (`ctx7 docs /vercel/react-tweet` for the Vite setup and how it fetches). Renders like a real post, dark theme, no X script.
- **LinkedIn posts:** no public API for static rendering. Two options:
  - Official iframe embed — exact LinkedIn look; loads LinkedIn's scripts and cookies, light theme only, fixed height, slower.
  - Own `PostCard` (avatar, name, date, text, link out) — matches the site, fast, dark; the post text is copied into `content.ts` by hand.
  - Starting point: own `PostCard`, because it keeps the page consistent and fast; swap to the iframe if exact fidelity matters more.
- Layout: CSS columns (masonry-style). React Bits **SpotlightCard** as the wrapper for the hover glow, if it accepts arbitrary children — check the source first. React Bits Masonry is image-oriented, so probably not it.
- Test: each post links to its source URL; axe clean (third-party embed markup may need a scoped exclusion — record any).

## Phase 5 — More projects

Private repos cannot link to GitHub, so each needs somewhere to land: a short case page at `/projects/:slug` (problem, what was built, status, stack, screenshot). Gallery items then link to the case page or the repo.

Candidates, with what each would show and what is in the way:

| Project | Why it could earn a place | In the way |
|---|---|---|
| Shifts (day / night / morning / dream) | Most distinctive thing in the files: an overnight agent loop with review gates; 159 commits; already on the Skills page | Private; needs a diagram instead of a screenshot |
| Agentic education / AI LMS | Largest codebase (~43k lines); connects to the AI-in-education writing | Status not verified; read its PROJECT.md first |
| Knowledge Tree | Visual, and has a live URL (knowledge-tree-seven.vercel.app) | Dormant since April; check the live site still works |
| Balkanski | Ties the languages and mission story to something built | Personal-use app, private repo |
| Locker | ~23k lines, 240+ tests, real architecture | Dormant since 2026-08-18; must be labelled as such |
| Companion | Actively pushed; calendar and goal tracking | Purpose and state not verified |
| mode-memory | Already on the Skills page as the plugin | Repo is private; make public to link |
| Topsail engagement | Strongest result on the resume | Client work: anonymised case page only, no code |
| eightfaces (Perry), velocity (Foundry) | Real client / org work | Not Carter's alone to publish; needs permission |

- Each card carries an honest status label (live / in progress / dormant / thesis).
- Replace generated gradient covers with real screenshots where a UI exists.
- Test: every gallery item resolves to a repo or a case page; case pages pass axe.

## Phase 6 — Q&A agent (later)

Not built until Carter says go. Shape:

- **Backend:** one serverless function (`api/chat`) on Vercel next to the static site, streaming. API key in Vercel env vars only.
- **Knowledge:** a single curated `profile.md` (experience, projects, approved facts) loaded into the prompt with prompt caching. Small enough that retrieval is unnecessary. This is the "wiki about myself" item from PROJECT.md.
- **Rules:** answer only from the file; say so when it doesn't know; no private details (client names, contact info) unless listed as approved.
- **Cost and abuse:** per-IP rate limit, max output length, monthly spend cap, small fast model by default.
- **Before building:** load the `claude-api` skill for current model ids and SDK usage; decide AI SDK vs Anthropic SDK.
- **Tests:** a hand-written question set with expected facts and expected refusals. This is business-rule testing no conformance suite covers.

## Testing

- Already in place: Playwright + axe-core (WCAG 2 A/AA) on every route. New routes get added to the loop in `tests/site.spec.ts`.
- Add: Lighthouse CI (`@lhci/cli`, one dev dependency + config) for performance, SEO and best-practice budgets. Embeds and the activity grid are the likely regressions.
- Neither can check: whether the copy and numbers are true, whether synced data is fresh, or (phase 6) whether the agent's answers are correct. Those stay hand-written tests and manual review.

## Carried over (unresolved)

- Who the site is for (consulting recruiters, founders and clients, or both).
- Colliers, Ironclad, Optimal AI, Sandbox dates — which are right.
- Merging to `main` switches Vercel to the Vite build and stops GitHub Pages updates.
- `PROJECT.md` in the main checkout still describes the Quarto site.
