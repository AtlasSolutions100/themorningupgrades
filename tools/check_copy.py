#!/usr/bin/env python3
"""Compliance check for every word the site publishes. Stdlib only.

Scans build_site.py, every generated *.html (including /c/), llms.txt and the strings in
assets/site.js. Exits 1 and prints file:line plus context for each hit.

What it guards (owner rules):
  - no weight / appetite / metabolism / fat-burning / slimming language anywhere, including
    alt text, schema and file names;
  - no invented proof or implied results ("most people", "no 2 PM crash", star ratings, "reviews");
  - bare "fat" only where a guide defines MCTs as a type of fat (flagged next to burn/lose/body...).
  - no "medium roast" (or medium-dark): the bag says Dark Roast.

Edit BANNED_WORDS / BANNED_PHRASES / ALLOW below; keep them as plain regexes.

    python3 tools/check_copy.py            # check the repo
    python3 tools/check_copy.py --drift    # also fail if a rebuild changes any committed HTML
    python3 tools/check_copy.py --selftest
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Whole-word, case-insensitive.
BANNED_WORDS = (
    r"weight", r"weight[- ]loss", r"lose weight", r"appetite\w*", r"metabolism", r"metabolic",
    r"fat[- ]?burn\w*", r"burn(s|ing)? fat", r"body fat", r"belly fat", r"slim\w*", r"burn\w*",
    r"thermogenic", r"suppress\w*", r"craving\w*", r"calorie\w*", r"diet", r"keto", r"detox",
    r"cleanse", r"satiety", r"fullness",
)
# Implied results and invented proof. Case-insensitive substrings/regexes.
BANNED_PHRASES = (
    r"most popular", r"most people", r"usually where", r"no 2 ?pm crash", r"\bcrash\w*", r"\bjitter\w*",
    r"guaranteed results", r"★", r"&#9733;", r"\breviews\b", r"\brated\b", r"\btestimonial",
    r"clinically (proven|shown)", r"doctor[- ]recommended",
    r"medium[- ]?(dark[- ]?)?roast\w*", r"medium[- ]dark",                 # the bag says Dark Roast
)
# "fat" is a word the MCT guides need ("MCTs are a type of fat"). Flag it only near these.
FAT_NEAR = r"burn\w*|los[es]\w*|loss|body|belly|melt\w*|shed\w*|reduc\w*|torch\w*"

# Exact contexts stripped before testing. Keep each one narrow.
ALLOW = (
    r'"weight":\s*\{\s*"@type":\s*"QuantitativeValue"',             # Product schema net weight key
    r"\bnet (wt\.?|weight)\b[^<\n]{0,24}?\d",                       # "net wt 7.2 oz"
    r"\d[\d.,]*\s*(oz|g|lb)\b[^<\n]{0,12}?\bnet (wt\.?|weight)\b",
    r"\bshipping weight\b[^<\n]{0,24}?\d",
    r"assets/ads/[\w./-]+",                                         # ad file paths
    r'data-v="(crash|jitters)"',                                    # quiz answer keys (Klaviyo values)
    r"\b(crash|jitters):\s*\[",                                     # quiz result map keys
    r'"(crash|jitters)":\s*\[',                                    # same keys as JSON
    r'\("(crash|jitters)",',                                        # same keys in the QUIZ table
    r"results\.crash",
    r"most participants earn little|most people earn little",       # required income disclosure
)

SKIP_DIRS = {".git", "node_modules", "tools", "img", "media", "assets"}


def files():
    yield os.path.join(ROOT, "build_site.py")
    yield os.path.join(ROOT, "llms.txt")
    yield os.path.join(ROOT, "assets", "site.js")
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if f.endswith(".html"):
                yield os.path.join(d, f)


def js_strings(text):
    """Only the string literals of a JS file (keeps comments and identifiers out)."""
    out = []
    for m in re.finditer(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"", text):
        out.append((text.count("\n", 0, m.start()) + 1, m.group(0)))
    return out


def scan_text(text):
    """Returns [(offset, match_text, rule)] for one blob of text."""
    hits = []
    masked = text
    for a in ALLOW:
        masked = re.sub(a, lambda m: " " * len(m.group(0)), masked, flags=re.I)
    for w in BANNED_WORDS:
        for m in re.finditer(r"\b(?:" + w + r")\b", masked, re.I):
            hits.append((m.start(), m.group(0), "banned word"))
    for p in BANNED_PHRASES:
        for m in re.finditer(p, masked, re.I):
            hits.append((m.start(), m.group(0), "banned phrase"))
    for m in re.finditer(r"\bfat\b", masked, re.I):
        lo = masked[max(0, m.start() - 40):m.end() + 40]
        words = re.findall(r"[A-Za-z-]+", lo)
        # within 3 words either side
        before = re.findall(r"[A-Za-z-]+", masked[max(0, m.start() - 60):m.start()])[-3:]
        after = re.findall(r"[A-Za-z-]+", masked[m.end():m.end() + 60])[:3]
        if any(re.fullmatch(FAT_NEAR, w, re.I) for w in before + after):
            hits.append((m.start(), m.group(0), "fat near " + "/".join(before + after)))
    return sorted(set(hits))


def check(paths):
    problems = []
    for path in paths:
        rel = os.path.relpath(path, ROOT)
        # file names count too
        for h in scan_text(re.sub(r"[_./-]", " ", rel)):
            problems.append(f"{rel}: file name: {h[1]!r} ({h[2]})")
        try:
            text = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            continue
        chunks = js_strings(text) if path.endswith(".js") else [(1, text)]
        for base_line, chunk in chunks:
            for off, word, rule in scan_text(chunk):
                line = base_line + chunk.count("\n", 0, off)
                ctx = chunk[max(0, off - 40):off + 40].replace("\n", " ")
                problems.append(f"{rel}:{line}: {word!r} ({rule}) ... {ctx} ...")
    # image / media file names
    for sub in ("img", "media", "assets"):
        for d, _, fs in os.walk(os.path.join(ROOT, sub)):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), ROOT)
                for h in scan_text(re.sub(r"[_./-]", " ", rel)):
                    problems.append(f"{rel}: file name: {h[1]!r} ({h[2]})")
    return problems


def drift():
    """Rebuild and fail if any committed generated file changes (HTML edited by hand, or the
    generator changed without a rebuild). llms.txt's date line is the one allowed difference."""
    subprocess.run([sys.executable, os.path.join(ROOT, "build_site.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
    bad = []
    for line in filter(None, out):
        path = line[3:]
        if path == "llms.txt":
            diff = subprocess.run(["git", "diff", "-U0", "--", "llms.txt"], cwd=ROOT, capture_output=True, text=True).stdout
            changed = [l for l in diff.split("\n") if l[:1] in ("+", "-") and not l.startswith(("+++", "---"))]
            if all("Facts as stated on the site (updated" in l for l in changed):
                continue
        if path == "sitemap.xml":
            diff = subprocess.run(["git", "diff", "-U0", "--", "sitemap.xml"], cwd=ROOT, capture_output=True, text=True).stdout
            changed = [l for l in diff.split("\n") if l[:1] in ("+", "-") and not l.startswith(("+++", "---"))]
            if all("<lastmod>" in l for l in changed):
                continue
        bad.append(line)
    return bad


def selftest():
    ok = True
    must_pass = ['"weight":{"@type":"QuantitativeValue","value":204}', "Net Wt 7.2 oz (204 g)", "net weight 204 g",
                 "MCTs are a type of fat, usually made from coconut", "assets/ads/tmu_flatlay_4x5.jpg",
                 "a dietary supplement", 'data-v="crash"', '{"crash": ["The 2 PM slide"', '[("crash", "Early afternoon', "Most participants earn little",
                 "A 2022 review in the journal", "the fat content is real: read the nutrition panel",
                 "Dark roast, a little smoother", "medium heat", "medium-chain triglycerides"]
    must_fail = ["supports weight loss", "Weight control coffee", "healthy appetite control", "boosts metabolism",
                 "fat burning", "burns fat", "slimming", "Most popular", "No 2 PM crash", "the jitters",
                 "Most people stop", "★★★★★", "500 reviews", "helps you lose fat",
                 "keto friendly", "curbs cravings", "weight",
                 "Medium roast", "medium-roast instant coffee", "a medium-dark roast"]
    for s in must_pass:
        if scan_text(s):
            print("selftest FAIL (should pass):", s, scan_text(s)); ok = False
    for s in must_fail:
        if not scan_text(s):
            print("selftest FAIL (should flag):", s); ok = False
    print("selftest", "ok" if ok else "FAILED")
    return ok


def main(argv):
    if "--selftest" in argv:
        return 0 if selftest() else 1
    if not selftest():
        return 1
    problems = check(sorted(set(files())))
    if "--drift" in argv:
        problems += [f"drift: {l} (generated file differs from build_site.py output; edit build_site.py and rebuild)" for l in drift()]
    for p in problems:
        print(p)
    print(f"check_copy: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
