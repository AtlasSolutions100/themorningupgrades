#!/usr/bin/env python3
"""Behaviour tests for individual pages (Playwright, local, nothing is sent anywhere: the Klaviyo
endpoint is answered by the test itself).

    python3 tools/test_pages.py
"""
import json
import sys
from playwright.sync_api import sync_playwright
from testlib import serve

FAIL = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def context(b, base, w=390, h=844, klaviyo=None):
    ctx = b.new_context(viewport={"width": w, "height": h})
    ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}")

    def route(r):
        u = r.request.url
        if u.startswith(base):
            return r.continue_()
        if klaviyo is not None and u.startswith("https://a.klaviyo.com/client/subscriptions/"):
            klaviyo.append(json.loads(r.request.post_data or "{}"))
            return r.fulfill(status=202, body="")
        return r.abort()
    ctx.route("**/*", route)
    return ctx


def start_tests(b, base):
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("bs_variants", os.path.join(os.path.dirname(__file__), "..", "build_site.py"))
    # read LANDING_VARIANTS without running the build: parse the dict literal
    src = open(os.path.join(os.path.dirname(__file__), "..", "build_site.py")).read()
    block = src[src.index("LANDING_VARIANTS = {"):]
    block = block[:block.index("\n}\n") + 3]
    ns = {}
    exec(block, ns)
    V = ns["LANDING_VARIANTS"]
    ctx = context(b, base); pg = ctx.new_page()
    for content, key in [("", "default"), ("ritual_a", "ritual"), ("swap-2", "swap"), ("label", "label"), ("COST_b", "cost"), ("day3", "default")]:
        pg.goto(base + "/start.html" + (f"?utm_source=tiktok&utm_medium=paid&utm_content={content}" if content else ""))
        h1 = pg.locator("h1").text_content().strip()
        strip = [t.strip() for t in pg.locator("#lp-strip span:not(.rule)").all_text_contents()]
        check(h1 == V[key][0] and strip == list(V[key][1]), f"/start utm_content={content or '(none)'} -> {key} headline")
        check(pg.locator("h1").count() == 1, f"/start has one h1 ({content or 'none'})")
    check(pg.locator("header.nav.mini .brand").count() == 1 and pg.locator("header.nav.mini a[href='/faq.html']").count() == 1,
          "/start has the mini header with a Questions link")
    check(pg.locator(".burger").count() == 0, "/start has no menu")
    check(pg.locator(".ingcards").count() == 0, "/start no longer repeats the ingredient cards")
    ctx.close()
    # capture form posts to the quiz list with source=start and goes to /thanks
    sent = []
    ctx = context(b, base, klaviyo=sent); pg = ctx.new_page()
    pg.goto(base + "/start.html?utm_source=snap&utm_medium=paid&utm_campaign=t1&utm_content=ritual_a")
    pg.fill("#cap-start-email", "not-an-email")
    pg.click("#cap-start button[type=submit]")
    check(pg.locator("#cap-start [data-capmsg]").inner_text().startswith("Check the email"), "capture rejects a bad email")
    pg.fill("#cap-start-email", "test@example.com")
    with pg.expect_navigation():
        pg.click("#cap-start button[type=submit]")
    check(pg.url.endswith("/thanks.html?r=start"), "capture goes to /thanks after Klaviyo 202")
    ok = bool(sent) and sent[0]["data"]["relationships"]["list"]["data"]["id"] == "WgctGT"
    props = sent[0]["data"]["attributes"]["profile"]["data"]["attributes"]["properties"] if sent else {}
    check(ok and props.get("source") == "start" and props.get("lead_magnet") == "7 Mornings guide" and props.get("utm_content") == "ritual_a",
          "capture posts email to list WgctGT with source=start and UTMs")
    ctx.close()


def ia_tests(b, base):
    import re, os
    src = open(os.path.join(os.path.dirname(__file__), "..", "build_site.py")).read()
    block = src[src.index("GUIDE_LINKS = {"):]
    guides = re.findall(r'"([a-z0-9-]+\.html)":', block[:block.index("\n}\n")])
    ctx = context(b, base, w=1440, h=900); pg = ctx.new_page()
    pg.goto(base + "/")
    nav = [a.strip() for a in pg.locator("nav.nav .menu a").all_text_contents()]
    check(nav == ["Shop", "Ingredients", "Guides", "FAQ", "Get CoreJava"], f"top nav is Shop/Ingredients/Guides/FAQ/Get CoreJava ({nav})")
    home_links = set(pg.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))"))
    pg.goto(base + "/guides.html")
    idx_links = set(pg.eval_on_selector_all("main a[href]", "els => els.map(e => e.getAttribute('href'))"))
    for g in guides:
        two = ("/" + g) in home_links or ("/guides.html" in home_links and ("/" + g) in idx_links)
        check(two, f"{g} reachable in <=2 clicks from home")
    for g in guides:
        pg.goto(base + "/" + g)
        crumbs = pg.locator("nav.crumbs a").all_text_contents()
        check(crumbs == ["Home", "Guides"], f"{g} shows Home > Guides breadcrumbs")
        check(pg.locator(".byline a[rel=author]").count() == 1, f"{g} has a named author byline")
    ctx.close()
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/shop.html")
    y = pg.evaluate("() => document.querySelector('[data-picker-btn]').getBoundingClientRect().top + scrollY")
    check(y < 2 * 844, f"/shop first checkout button within 2 screens at 390px (top {int(y)}px)")
    ctx.close()


def recipe_tests(b, base):
    import os, re, glob, html as _h
    root = os.path.join(os.path.dirname(__file__), "..")
    src = open(os.path.join(root, "build_site.py")).read()
    ns = {}
    exec("import re\nimport html as _html\n" + src[src.index("RECIPE_DATE ="):src.index("RECIPE_BY =")], ns)
    R = ns["RECIPES"]
    check(len(R) >= 10, f"{len(R)} recipe pages (>= 10)")
    idx = open(os.path.join(root, "recipes.html")).read()
    for r in R:
        fn = r["slug"] + ".html"
        h = open(os.path.join(root, fn)).read()
        words = len(re.findall(r"[A-Za-z0-9']+", _h.unescape(" ".join([r["lede"]] + r["ingredients"] + r["steps"] + r["tips"] + [q + " " + a for q, a in r["faq"]]))))
        check(words >= 250, f"{fn}: {words} words of recipe-specific text")
        ld = [json.loads(j) for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)]
        rec = [g for d in ld for g in d["@graph"] if g["@type"] == "Recipe"]
        ok = rec and all(rec[0].get(k) for k in ("name", "image", "recipeIngredient", "recipeInstructions", "prepTime", "totalTime", "recipeYield", "author"))
        check(bool(ok), f"{fn}: Recipe schema with the required fields")
        check(f'href="/{fn}"' in idx and 'href="/recipes.html"' in h, f"{fn}: linked from /recipes and links back")
        check("Contains caffeine" in h and "any instant coffee" in h, f"{fn}: caffeine + any-instant-coffee lines")
        check(len(_h.unescape(re.search(r"<title>(.*?)</title>", h).group(1))) <= 60, f"{fn}: title <= 60 chars")


def guide_tests(b, base):
    import os, re, html as _h
    root = os.path.join(os.path.dirname(__file__), "..")
    src = open(os.path.join(root, "build_site.py")).read()
    block = src[src.index("GUIDE_META = {"):]
    guides = re.findall(r'"([a-z0-9-]+\.html)":', block[:block.index("\n}\n")])
    idx = open(os.path.join(root, "guides.html")).read()
    check(len(guides) >= 13, f"{len(guides)} guides")
    for fn in guides:
        h = open(os.path.join(root, fn)).read()
        t = _h.unescape(re.search(r"<title>(.*?)</title>", h).group(1))
        d = _h.unescape(re.search(r'<meta name="description" content="(.*?)"', h).group(1))
        lede = _h.unescape(re.sub("<[^>]+>", "", re.search(r'<p class="lead answer">(.*?)</p>', h, re.S).group(1)))
        check(len(t) <= 60 and len(d) <= 155, f"{fn}: title {len(t)} <= 60, description {len(d)} <= 155")
        if fn in ("iced-instant-coffee-recipes.html",):
            continue
        check(len(lede.split()) <= 62, f"{fn}: answer lede {len(lede.split())} words")
        check(f'href="/{fn}"' in idx, f"{fn}: on the guides index")
        check('href="/shop.html"' in h and ('data-capture="guide"' in h), f"{fn}: links the shop and has the guide capture")
    new = ["how-much-caffeine-in-instant-coffee.html", "how-to-make-instant-coffee-taste-better.html", "does-instant-coffee-go-bad.html",
           "instant-coffee-for-travel-camping-dorm.html", "what-is-mct-powder.html", "natural-caffeine-vs-synthetic.html",
           "caffeine-and-l-theanine-ratio.html", "instant-coffee-vs-drip-cost-per-cup.html"]
    for fn in new:
        h = open(os.path.join(root, fn)).read()
        n = h.count("<details><summary>")
        check(4 <= n <= 5 and 'class="frame gphoto"' in h and "benefit" not in h.lower(), f"{fn}: {n} FAQs, a photo, no 'benefits' framing")
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/instant-coffee-vs-drip-cost-per-cup.html")
    check("$2.33 a cup" in pg.locator(".calc-out").inner_text(), "cost calculator shows $2.33 a cup for 69.95 / 30")
    pg.fill("#c-price", "12"); pg.fill("#c-cups", "60")
    check("$0.20 a cup" in pg.locator(".calc-out").inner_text(), "cost calculator recalculates ($12 / 60 = $0.20)")
    ctx.close()


def quiz_tests(b, base):
    for path, want, plan in [("/quiz.html", "simple", "subscribe"), ("/", "focus", "onetime")]:
        sent = []
        ctx = context(b, base, klaviyo=sent); pg = ctx.new_page()
        pg.goto(base + path)
        pg.click('#quiz .q[data-q="1"] .opt[data-v="jitters"]')
        pg.click('#quiz .q[data-q="2"] .opt[data-v="2"]')
        pg.click(f'#quiz .q[data-q="3"] .opt[data-v="{want}"]')
        check(pg.locator("#r-label").text_content() == "Sharp, not shaky", f"{path}: result uses Q1")
        check("first one only" in pg.locator("#r-cups").text_content(), f"{path}: result uses Q2")
        check(pg.locator("#r-guide").get_attribute("href") == "/l-theanine-and-caffeine.html", f"{path}: result links the matching guide")
        checked = pg.locator("#quiz .qpick input:checked").get_attribute("value")
        btn = pg.locator("#quiz .qpick [data-picker-btn]").get_attribute("data-buy")
        check(checked == plan and btn == plan, f"{path}: Q3={want} preselects {plan} in a working picker ({checked}/{btn})")
        steps = pg.evaluate("() => (window.dataLayer||[]).map(a=>Array.from(a)).filter(x=>x[0]==='event'&&x[1]==='QuizStep').map(x=>x[2].step)")
        check(steps == [1, 2, 3, 4], f"{path}: QuizStep events 1-4 ({steps})")
        pg.fill("#q-email", "test@example.com")
        pg.click("#tmu-form button[type=submit]")
        pg.wait_for_selector("#tmu-done:not([hidden])")
        check(pg.locator("#tmu-done a").get_attribute("href").endswith(".pdf"), f"{path}: after submit the guide link shows in the result step")
        props = sent[0]["data"]["attributes"]["profile"]["data"]["attributes"]["properties"] if sent else {}
        check(props.get("quiz_result") == "jitters" and props.get("cups") == "2" and props.get("want") == want, f"{path}: Klaviyo gets all three answers")
        ctx.close()


def main():
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        start_tests(b, base)
        ia_tests(b, base)
        recipe_tests(b, base)
        guide_tests(b, base)
        quiz_tests(b, base)
        b.close()
    print(f"\n{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
