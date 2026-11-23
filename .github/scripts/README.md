# Site and map checks

- `check_site.py`: published files, placeholders, counts, links, legal footer. Runs in CI (`site-checks`).
- `browser_check.mjs`: headless browser at 390 px and 1280 px, with and without JavaScript. Runs in CI.
- `check_map_issue.py`: the **map gate**. Runs in CI as a separate check run, `map-issue-gate`.

## Map gate: run it after every send

After each SpudSignal issue goes out and its Library "Featured in" links are on main, run:

```bash
python3 .github/scripts/check_map_issue.py .            # repo-local, no network
python3 .github/scripts/check_map_issue.py . --online   # also reads the beehiiv sitemap (fail-safe)
```

You can also run it on GitHub: Actions → Site checks → Run workflow.

The gate **fails** in these cases:
- No pin or side-panel row in `map/data.js` carries the latest issue (no "Read in SpudSignal #N" link).
- A pin's `issue_url` doesn't match the Library's URL for that issue.
- `map/data.js` still shows an ID listed under "old" in `map/superseded-tenders.json`.

It only **warns** about tender pins whose deadline has passed and about a successor notice that is not on the map.

- **Where "latest issue" comes from:** the highest issue number linked from the Library pages (`index.html`, `tenders/index.html`, `whats-new/index.html`). CI never fetches beehiiv. `--online` adds the beehiiv sitemap. If the sitemap can't be reached, the gate warns and keeps the repo-local result.
- **When a map update replaces a notice** (same procedure, new notice number), add an old → new pair with its source to `map/superseded-tenders.json`. Never remove pairs.
- **When an issue has nothing mappable** (for example policy only), add `{"issue": N, "reason": "..."}` under `issues_without_map_items`.
- **In CI:** the gate is strict on pushes to main, on manual runs, and on PRs that touch `map/data.js`, `map/superseded-tenders.json` or the gate. On all other PRs it is advisory (warnings only), so the weekly tender refresh and the featured-links PR are never blocked.

## Read-in rule (which issue a pin links to)

A pin's "Read in SpudSignal #N" points to the **earliest issue whose web version links the pin's own source URL** (`source_url`). Lines in "Closing soon" (email-only) never count. Later mentions, such as On-the-radar lines in newer issues, don't move the link. This is the same rule the Library uses for "Featured in #N", which lists every issue that links the source. For the newest issue, the gate checks only that at least one map item carries it.
