# APPLY – Library Update 2.0 (tabs) into the production generators

Built 13/14 Nov 2026 on branch `library/tabs-2-0` (base: main `368155e`). Nothing is live until the PR is merged.

## Which file goes where

`generators-final/` mirrors the production generator folder (`/workspace/geothermie/library/`). Copy these into it:

| File in `generators-final/` | Goes to | Change vs. production |
|---|---|---|
| `build_site.py` | `library/build_site.py` | Header note; if `site/index.html` already carries the tabs shell (`data-ss-tabs="2.0"`), it takes `tabs/pretabs/index.html` as its base (live head, body tag, footer). |
| `tabs/tabs.py` | `library/tabs/tabs.py` (new) | The tabs stage. Changes vs. the Designer's interim state: `--restore` mode, sha guard (`tabs/pretabs/tabs-out.json`), operating-plants count = `TL.operating.length` (28). |
| `tabs/assets/spudsignal.css`, `ss-url.js`, `library.js` | `library/tabs/assets/` (new) | Shared stylesheet (prototype v2.1 plus §14 tap-target fixes), URL filters, Library search/expired toggle. Copied to `site/assets/` on every tabs run. |
| `tabs/pretabs/*` | `library/tabs/pretabs/` (new) | Pre-tabs copies of `/`, `/tenders/`, `/map/`, `/projects/` from main `368155e`, plus `tabs-out.json`, `tabs-log.json`, `home-deadlines.json`. Needed for `--restore` and for re-runs. |
| everything else | unchanged | `data.py`, `build.py`, `build_styled.py`, `build_map.py`, `check.py`, `tenders/*` are byte-identical to `generators/`. |

## Weekly build order (from `library/`)

```bash
python3 tabs/tabs.py --restore site     # 1. put the pre-tabs pages back (refuses a page edited after the last tabs run)
python3 build.py && python3 build_styled.py && python3 build_site.py
python3 tenders/build_tenders.py
node site/audience/apply.mjs
python3 tenders/slim.py
python3 tabs/tabs.py site               # 2. LAST: tab bar, shared CSS, footer, glossary, /whats-new/
```

`build_map.py` only writes `map/data.js` / `data.geojson` and can run anywhere before step 2.

Why the restore step: `apply.mjs`, `slim.py` and the tenders count in `build_tenders.py` edit pages in place. Run on a tabbed page they would either fail or have their edit dropped, because `tabs.py` rebuilds a tabbed page from its stored pre-tabs copy. `tabs.py` now stops with an error instead of dropping an edit silently.

Tested here: fresh run on main = prototype v2.1 output (byte-identical apart from the items below); restore gives back main's pages byte-for-byte; a changed Library entry in `data.py` shows up after restore → generators → tabs; a second tabs run changes nothing.

## Differences to the prototype (intended)
- No preview switches: `?pins=b` (map option B), `?hdr=b` (Tenders header option B) and `?past=show` are not built. Daniel chose pin option A and expired entries hidden by default.
- Toggle label "Operating plants (28)" (prototype: 27), per the Kartograf.
- §14 in `spudsignal.css`: tap targets ≥ 44 px for the Tenders intro summary and feed links, map zoom buttons, footer links and the /projects/ CTA.
- `<html data-ss-tabs="2.0">` marker on the four generated pages.
- Library script is served as `/assets/library.js` (prototype: `library-v2.js`).

## Open before go-live
- The Update 2.0 date on `/whats-new/` reads "set at go-live". Set it in `tabs/tabs.py` (`ENT`) at go-live and rebuild.
- Merging this PR also publishes the `handoff/` folder under library.spudsignal.com/handoff/ (GitHub Pages serves the whole repo). Decide whether that folder should stay in main.
