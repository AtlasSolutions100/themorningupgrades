#!/bin/bash
# Everything CI runs before a deploy. Run locally the same way: bash tools/ci.sh
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/check_copy.py --drift   # banned words/phrases + generated HTML matches build_site.py
python3 tools/test_tracking.py        # Phase T event tests
python3 tools/smoke.py                # layout, alt text, contrast, links at 390 and 1440
