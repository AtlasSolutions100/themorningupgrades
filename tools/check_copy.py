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
  - no slump / energy-drop / before-and-after framing.

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
    r"\bslump\w*", r"\benergy (drop|dip|crash)\w*", r"\bafternoon (dip|wall)\b",   # no energy-dip framing
    r"before[- ]and[- ]after", r"\bbefore ?/ ?after\b",
)
# "fat" is a word the MCT guides need ("MCTs are a type of fat"). Flag it only near these.
FAT_NEAR = r"burn\w*|los[es]\w*|loss|body|belly|melt\w*|shed\w*|reduc\w*|torch\w*"

# Exact contexts stripped before testing. Keep each one narrow.
ALLOW = (
    r'"weight":\s*\{\s*"@type":\s*"QuantitativeValue"',             # Product schema net weight key
    r"\bnet (wt\.?|weight)\b[^<\n]{0,24}?\d",                       # "net wt 7.5 oz"
    r"\d[\d.,]*\s*(oz|g|lb)\b[^<\n]{0,12}?\bnet (wt\.?|weight)\b",
    r"\bshipping weight\b[^<\n]{0,24}?\d",
    r"assets/ads/[\w./-]+",                                         # ad file paths
    r'data-v="(crash|jitters)"',                                    # quiz answer keys (Klaviyo values)
    r"\b(crash|jitters):\s*\[",                                     # quiz result map keys
    r'"(crash|jitters)":\s*\[',                                    # same keys as JSON
    r'\("(crash|jitters)",',                                        # same keys in the QUIZ table
    r"results\.crash",
    r"most participants earn little|most people earn little",       # required income disclosure
    # The Subscribe & Save plan tag (owner, Nov 4 2026: it is the plan most customers choose). Only this exact tag.
    r'<span class="ptag">Most popular</span>',
    # The FAQ about the bag's printed name (owner, Nov 2026): the name is quoted once, and the answer
    # says we make no such claims. Nothing else may use the word.
    r"The bag says Weight Control Coffee\. Is that what this is\?",
    r"we make no weight claims",
    # House coffee (owner, Nov 4 2026): the Mushroom Coffee Blend bag says "Medium roast coffee with mushroom
    # powder", and that is the only way the site describes it. Only this exact phrase; CoreJava stays Dark Roast.
    r"medium roast coffee with mushroom powder",
    # The bag's own printed statements (owner, Koby, Nov 4 2026: verbatim label quotes allowed on info pages,
    # never on ad landing pages). Exact strings only, capitals as printed, case-sensitive; tools/test_pages.py
    # checks they appear only on /ingredients and /corejava-coffee. Everything else stays banned.
    r"(?-i:WEIGHT CONTROL COFFEE&dagger;)",
    r"(?-i:SUPPORTS HEALTHY APPETITE CONTROL \| FOCUS \| ENERGY&dagger;)",
    r"(?-i:HELPS BOOST METABOLISM, ENERGY &amp; FOCUS&dagger;)",
    # The Supplement Facts panel transcribed as printed (Nov 4 2026 bag): its Calories row and its
    # Daily Value footnote. Only these exact forms.
    r'(?-i:\("Calories", "25", ""\))',
    r"(?-i:<td>Calories</td><td>25</td>)",
    r"(?-i:Calories 25)",
    r"(?-i:\* Percent Daily Values are based on a 2,000 calorie diet\.)",
)

# No discounts (owner): no price-saving or discount wording and no struck-through prices anywhere, including
# CoreJava's pages, cards and the plan picker. "Subscribe & Save" is the plan's name, not a saving claim.
# The one exception (owner, Koby, Nov 5 2026): the 2 bundle cards on /shop may say "Save $X vs buying
# separately" and strike the separate total, computed from the price constants in build_site.py. The exception
# is scoped to the bundle card markup (<article class="pcard bcard ...">...</article>) and, in build_site.py, to
# the bundle_card() function that writes it. Everything else stays banned.
PROMO = (
    r"\bsav(e|es|ing|ings)\s+(up to\s+|over\s+)?(\$|\d)",                # "save $17.95", "saves 20"
    r"\bsav(e|es|ing|ings)\b[^<\n]{0,30}?\b(vs\.?|versus|separately|off)\b", # "save vs buying separately"
    r"\bsavings?\s+of\b", r"\byou save\b",
    r"\d+\s*%\s*off\b", r"\$[\d.,]+\s+off\b",
    r"\bdiscount(s|ed)?\b",
    r"<(s|del|strike)[\s>]", r"line-through",
)
PROMO_ALLOW = (
    r"Subscribe(&nbsp;|\s)*(&amp;|&|and)(&nbsp;|\s)*Save",              # the plan's name
    r"not the headline discount",                                       # the subscription guide's advice, no offer
    r'<article class="pcard bcard[^"]*"[\s\S]*?</article>',            # the bundle cards (Koby, Nov 5 2026)
    r"\ndef bundle_card\([\s\S]*?\n(?=def )",                         # the function that writes them
)


def promo_scan(text):
    masked = text
    for a in PROMO_ALLOW:
        masked = re.sub(a, lambda m: re.sub(r"[^\n]", " ", m.group(0)), masked, flags=re.I)
    hits = []
    for p in PROMO:
        for m in re.finditer(p, masked, re.I):
            hits.append((m.start(), m.group(0), "price-saving, discount or strikethrough outside the bundle cards"))
    return hits


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
            for off, word, rule in sorted(set(scan_text(chunk) + promo_scan(chunk))):
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
    must_pass = ['"weight":{"@type":"QuantitativeValue","value":213}', "Net Wt 7.5 oz (213 g)", "net weight 213 g",
                 "MCTs are a type of fat, usually made from coconut", "assets/ads/tmu_flatlay_4x5.jpg",
                 "a dietary supplement", 'data-v="crash"', '{"crash": ["The 2 PM slide"', '[("crash", "Early afternoon', "Most participants earn little",
                 "A 2022 review in the journal", "the fat content is real: read the nutrition panel",
                 "Dark roast, a little smoother", "medium heat", "medium-chain triglycerides",
                 "steady energy", "before bed", "after lunch",
                 "The bag says Weight Control Coffee. Is that what this is?", "and we make no weight claims.",
                 "Medium roast coffee with mushroom powder.",
                 "&ldquo;WEIGHT CONTROL COFFEE&dagger;&rdquo;", "SUPPORTS HEALTHY APPETITE CONTROL | FOCUS | ENERGY&dagger;",
                 "HELPS BOOST METABOLISM, ENERGY &amp; FOCUS&dagger;", "<td>Calories</td><td>25</td>",
                 "* Percent Daily Values are based on a 2,000 calorie diet."]
    must_fail = ["supports weight loss", "Weight control coffee", "healthy appetite control", "boosts metabolism",
                 "fat burning", "burns fat", "slimming", "Most popular", "No 2 PM crash", "the jitters",
                 "Most people stop", "★★★★★", "500 reviews", "helps you lose fat",
                 "keto friendly", "curbs cravings", "weight",
                 "Medium roast", "medium-roast instant coffee", "a medium-dark roast",
                 "the afternoon slump", "no more energy drops", "before-and-after", "before/after",
                 "a medium roast coffee", "Medium roast coffee with MCT",
                 "WEIGHT CONTROL COFFEE", "Supports healthy appetite control | focus | energy&dagger;",
                 "helps boost metabolism, energy &amp; focus&dagger;", "HELPS BOOST METABOLISM", "low calorie", "Calories 30"]
    for s in must_pass:
        if scan_text(s):
            print("selftest FAIL (should pass):", s, scan_text(s)); ok = False
    for s in must_fail:
        if not scan_text(s):
            print("selftest FAIL (should flag):", s); ok = False
    promo_pass = ["Subscribe &amp; Save", "Subscribe&nbsp;&amp;&nbsp;Save is $69.95 a month", "Save my number", "A hand mixer saves your wrist: about 2 minutes",
                  "isn't a saving", "not the headline discount",
                  '<article class="pcard bcard cg-4" id="pc-bundle-cupofjoe"><s>$107.90</s> Save $17.95 vs buying separately</article>']
    promo_fail = ["Save $10", "save 20% today", "$10 off", "20% off", "a discount", "discounted price", "<s>$79.95</s>", "<del>$79.95</del>",
                  "you save", "Save vs buying separately", "savings of $5", "text-decoration:line-through",
                  '<article class="pcard" id="pc-corejava">Save $10 vs 1 bag</article>']
    for s in promo_pass:
        if promo_scan(s):
            print("selftest FAIL (promo should pass):", s, promo_scan(s)); ok = False
    for s in promo_fail:
        if not promo_scan(s):
            print("selftest FAIL (promo should flag):", s); ok = False
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
