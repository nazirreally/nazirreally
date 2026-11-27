# Obsidian Minimal — maintenance

The profile artwork is original SVG, with no external fonts or scripts. Project card charts and maps are illustrative, not actual observations or screenshots. Animation is optional and the static frames remain readable.

The initial intelligence card uses the 27 November 2026 connected repository audit (19 accessible public non-archived repositories, 12 with nonzero size, eight featured). Contribution intensity and language distribution are deliberately absent until retrieved successfully.

Run `python -m unittest discover -s scripts -v` and `python scripts/refresh_intelligence.py` from the repository root. The latter uses public GitHub REST endpoints and the public contribution calendar HTML. It excludes forks and archived repositories from refreshed inventory, aggregates GitHub-reported language bytes, and displays GitHub's own contribution intensity levels (not inferred commit counts). Public contribution calendars may include anonymous private activity totals if enabled on the account. Blank dates are missing, not zero. No private repository data is queried. Public REST rate limits and GitHub HTML changes can prevent refresh; failed retrieval preserves the previous dated asset. The workflow runs on main after merge and weekly or manually. It needs contents write permission to publish only the generated SVG. Pull requests run read-only validation.

Review: check light/dark and mobile/desktop rendering, actual dashboard URLs and current CI badge rendering before merging. No individual project repository is changed.
