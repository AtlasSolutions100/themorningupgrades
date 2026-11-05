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


# Seen-and-closed pop-up state, so the email pop-up stays out of the way of the other tests.
NO_POPUP_JS = "try{if(!localStorage.getItem('tmu_pop'))localStorage.setItem('tmu_pop',JSON.stringify({s:'closed',t:Date.now()}))}catch(e){}"


def context(b, base, w=390, h=844, klaviyo=None, popup=False, status=202):
    ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce" if popup else None)
    ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}")
    if not popup:
        ctx.add_init_script(NO_POPUP_JS)

    def route(r):
        u = r.request.url
        if u.startswith(base):
            return r.continue_()
        if klaviyo is not None and u.startswith(("https://a.klaviyo.com/client/subscriptions/", "https://a.klaviyo.com/client/profiles/")):
            klaviyo.append(json.loads(r.request.post_data or "{}"))
            return r.fulfill(status=status, body="")
        return r.abort()
    ctx.route("**/*", route)
    return ctx


def start_tests(b, base):
    import importlib.util, os, re
    spec = importlib.util.spec_from_file_location("bs_variants", os.path.join(os.path.dirname(__file__), "..", "build_site.py"))
    # read LANDING_VARIANTS without running the build: parse the dict literal
    src = open(os.path.join(os.path.dirname(__file__), "..", "build_site.py")).read()
    block = src[src.index("LANDING_VARIANTS = {"):]
    block = block[:block.index("\n}\n") + 3]
    ns = {"LP_SUB": re.search(r'^LP_SUB = "(.*)"$', src, re.M).group(1)}
    exec(block, ns)
    V = ns["LANDING_VARIANTS"]
    ctx = context(b, base); pg = ctx.new_page()
    for content, key in [("", "default"), ("ritual_a", "ritual"), ("swap-2", "swap"), ("label", "label"), ("COST_b", "cost"), ("day3", "default")]:
        pg.goto(base + "/start.html" + (f"?utm_source=tiktok&utm_medium=paid&utm_content={content}" if content else ""))
        h1 = pg.locator("h1").text_content().strip()
        sub = pg.locator("#lp-sub").text_content().strip()
        check(h1 == V[key][0] and sub == V[key][1], f"/start utm_content={content or '(none)'} -> {key} headline")
        check(pg.locator("h1").count() == 1, f"/start has one h1 ({content or 'none'})")
        strip = [t.strip() for t in pg.locator("#lp-strip span:not(.rule)").all_text_contents()]
        check(strip == ["30 servings a bag", "Ships in about 2 days", "90-day guarantee on unopened bags"], f"/start trust strip ({content or 'none'})")
        # paid visits start on 1 bag; the button follows; the eyebrow is the label line
        want_plan = "onetime" if content else "subscribe"
        btn = pg.locator(".lphero [data-picker-btn]")
        check(pg.locator(".lphero [data-picker] input:checked").get_attribute("value") == want_plan and btn.get_attribute("data-buy") == want_plan
              and btn.text_content().strip() == ("Try 1 bag, $79.95" if content else "Start Subscribe & Save, $69.95 a month"),
              f"/start picker defaults to {want_plan} ({'paid' if content else 'organic'}) and the button says so")
    check(pg.locator(".lphero .eyebrow").text_content().strip() == "Instant coffee with MCT powder and L\u2011theanine", "/start eyebrow is the label line")
    check(pg.locator(".lphero .terms li").count() == 4 and pg.locator(".lphero .terms li").first.inner_text().strip() == "Scoop included in every bag." and pg.locator(".lphero .bonus-hero img").count() == 1, "/start: 4 terms lines (scoop first) and the Recipe Pack cover in the hero")
    check(pg.locator(".sticky").count() == 0 and pg.locator("body[data-popup=off]").count() == 1, "/start: no sticky bar, no pop-up")
    check(pg.locator("main h2").nth(0).inner_text().strip() == "The latte math", "/start: the latte math is section 2")
    check(pg.locator(".who-text").count() == 1 and pg.locator(".who-text img").count() == 0, "/start: founder block without a photo")
    n_faq = pg.locator(".closing-grid details").count()
    check(9 <= n_faq <= 11, f"/start: {n_faq} FAQ items (9 to 11)")
    pg.evaluate("() => localStorage.removeItem('tmu_ut')")
    pg.goto(base + "/start.html")
    check(pg.locator(".lphero [data-picker] input:checked").get_attribute("value") == "subscribe", "/start organic visit keeps Subscribe & Save first")
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
    nav = [a.strip() for a in pg.locator("nav.nav .menu .ddb").all_text_contents()] + [a.strip() for a in pg.locator("nav.nav .menu > a:visible").all_text_contents()]
    check(nav == ["Shop", "Learn", "FAQ", "Shop"] and pg.locator("nav.nav .menu > a.btn").get_attribute("href") == "/shop.html",
          f"top nav is Shop/Learn/FAQ and a Shop button to /shop ({nav})")
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
    pg.goto(base + "/corejava.html")
    y = pg.evaluate("() => document.querySelector('[data-picker-btn]').getBoundingClientRect().top + scrollY")
    check(y < 900, f"/corejava first checkout button within about 800 px at 390px (top {int(y)}px)")
    check(pg.locator("h1").inner_text().startswith("Instant coffee with MCT powder and L"), "/corejava H1 is the label line")
    check(pg.locator(".shop-buy .terms li").count() == 4 and pg.locator(".shop-buy .bonus-hero img").count() == 1, "/corejava: 4 terms lines and the Recipe Pack cover next to the button")
    pg.evaluate("() => document.querySelector('[data-picker-btn]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(500)
    check(pg.evaluate("() => document.querySelector('.sticky').getBoundingClientRect().top >= innerHeight - 1"), "/corejava: no sticky bar while the picker button is on screen")
    pg.evaluate("() => document.querySelector('.specs').scrollIntoView()"); pg.wait_for_timeout(500)
    check(pg.evaluate("() => document.querySelector('.sticky').getBoundingClientRect().top < innerHeight"), "/corejava: sticky bar back once the picker is off screen")
    footer = [a.strip() for a in pg.locator("footer a").all_text_contents()]
    check("Build with us" not in footer and "Share with friends" not in footer, "footer has no partner or share links")
    for fn in ("partner.html", "share.html"):
        pg.goto(base + "/" + fn)
        check(pg.locator("meta[name=robots][content=noindex]").count() == 1 and pg.locator("h1").count() == 1 and "income disclosure" in pg.content().lower(), f"/{fn} is noindex, still served with its disclosure")
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
        rel = re.findall(r'<li><a href="/([a-z0-9-]+\.html)">', h.split("Related guides")[1].split("</ul>")[0])
        check(3 <= len(rel) <= 5 and all(os.path.exists(os.path.join(root, r)) for r in rel) and fn not in rel, f"{fn}: 3 to 5 related pages, all existing ({len(rel)})")
    for fn, recipe in (("iced-instant-coffee-recipes.html", "iced-instant-coffee-recipe.html"), ("how-to-make-mct-instant-coffee.html", "instant-coffee-latte.html")):
        h = open(os.path.join(root, fn)).read()
        check(f'<li><a href="/{recipe}">' in h.split("Related guides")[1], f"{fn}: related list links the {recipe} recipe")
    new = ["how-much-caffeine-in-instant-coffee.html", "how-to-make-instant-coffee-taste-better.html", "does-instant-coffee-go-bad.html",
           "instant-coffee-for-travel-camping-dorm.html", "what-is-mct-powder.html", "natural-caffeine-vs-synthetic.html",
           "caffeine-and-l-theanine-ratio.html", "instant-coffee-vs-drip-cost-per-cup.html",
           "what-is-functional-coffee.html", "mushroom-coffee-vs-mct-coffee.html"]
    for fn in new:
        h = open(os.path.join(root, fn)).read()
        n = h.count("<details><summary>")
        check(4 <= n <= 5 and 'class="frame gphoto"' in h and "benefit" not in h.lower(), f"{fn}: {n} FAQs, a photo, no 'benefits' framing")
    # functional coffee guides: sourced, linked both ways, label facts only for our product
    for fn, other in (("what-is-functional-coffee.html", "mushroom-coffee-vs-mct-coffee.html"), ("mushroom-coffee-vs-mct-coffee.html", "what-is-functional-coffee.html")):
        h = open(os.path.join(root, fn)).read()
        rel = h.split("Related guides")[1].split("</ul>")[0]
        check(f'href="/{other}"' in rel and h.count('<ol class="fine src">') == 1, f"{fn}: links {other} in related guides and lists sources")
        check("150 mg caffeine" in _h.unescape(h) and "no mushrooms on the label" in h, f"{fn}: our product described by label facts")
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/instant-coffee-vs-drip-cost-per-cup.html")
    check("$2.33 a cup" in pg.locator(".calc-out").inner_text(), "cost calculator shows $2.33 a cup for 69.95 / 30")
    pg.fill("#c-price", "12"); pg.fill("#c-cups", "60")
    check("$0.20 a cup" in pg.locator(".calc-out").inner_text(), "cost calculator recalculates ($12 / 60 = $0.20)")
    ctx.close()


def notice_tests(b, base):
    ctx = b.new_context(viewport={"width": 390, "height": 844})
    ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    pg = ctx.new_page(); pg.goto(base + "/corejava.html"); pg.wait_for_timeout(100)
    n = pg.locator(".notice")
    box = n.bounding_box()
    check(n.count() == 1 and box and box["height"] <= 70 and box["y"] + box["height"] <= 844 - 70, f"analytics notice is a short toast above the sticky bar ({box})")
    pg.mouse.wheel(0, 200); pg.wait_for_timeout(200)
    check(pg.locator(".notice").count() == 0 and pg.evaluate("() => localStorage.getItem('tmu_notice')") == "1", "notice gone on the first scroll and remembered")
    pg.evaluate("() => localStorage.removeItem('tmu_notice')"); pg.goto(base + "/faq.html"); pg.wait_for_timeout(100)
    pg.mouse.click(200, 300); pg.wait_for_timeout(100)
    check(pg.locator(".notice").count() == 0, "notice gone on the first tap")
    ctx.close()


def quiz_tests(b, base):
    for path, want, plan in [("/quiz.html", "simple", "subscribe"), ("/quiz.html", "focus", "onetime")]:   # the quiz left home (Nov 5 2026)
        sent = []
        ctx = context(b, base, klaviyo=sent); pg = ctx.new_page()
        pg.goto(base + path)
        pg.click('#quiz .q[data-q="1"] .opt[data-v="jitters"]')
        pg.click('#quiz .q[data-q="2"] .opt[data-v="2"]')
        pg.click(f'#quiz .q[data-q="3"] .opt[data-v="{want}"]')
        check(pg.locator("#r-label").text_content() == "Dark and smooth", f"{path}: result uses Q1")
        check("first one only" in pg.locator("#r-cups").text_content(), f"{path}: result uses Q2")
        check(pg.locator("#r-guide").get_attribute("href") == "/l-theanine-and-caffeine.html", f"{path}: result links the matching guide")
        checked = pg.locator("#quiz .qpick input:checked").get_attribute("value")
        btn = pg.locator("#quiz .qpick [data-picker-btn]").get_attribute("data-buy")
        check(checked == plan and btn == plan, f"{path}: Q3={want} preselects {plan} in a working picker ({checked}/{btn})")
        form_first = pg.evaluate("() => document.getElementById('r-form').compareDocumentPosition(document.querySelector('#quiz .qsuggest')) & Node.DOCUMENT_POSITION_FOLLOWING")
        check(bool(form_first) == (want != "simple"), f"{path}: email form {'above' if want != 'simple' else 'below'} the picker for Q3={want}")
        check(pg.locator("#tmu-form input:not([type=hidden])").count() == 1, f"{path}: email is the only field")
        check("$2.33" in pg.locator("#r-text").text_content() and "L-theanine" in pg.locator("#r-text").text_content(), f"{path}: result restates the scoop and the latte math")
        steps = pg.evaluate("() => (window.dataLayer||[]).map(a=>Array.from(a)).filter(x=>x[0]==='event'&&x[1]==='QuizStep').map(x=>x[2].step)")
        check(steps == [1, 2, 3, 4], f"{path}: QuizStep events 1-4 ({steps})")
        pg.fill("#q-email", "test@example.com")
        pg.click("#tmu-form button[type=submit]")
        pg.wait_for_selector("#tmu-done:not([hidden])")
        check(pg.locator("#tmu-done a").get_attribute("href").endswith(".pdf"), f"{path}: after submit the guide link shows in the result step")
        props = sent[0]["data"]["attributes"]["profile"]["data"]["attributes"]["properties"] if sent else {}
        check(props.get("quiz_result") == "jitters" and props.get("cups") == "2" and props.get("want") == want, f"{path}: Klaviyo gets all three answers")
        ctx.close()


def order_tests(b, base):
    for qs, stored, sub, one in [("?session_id=cs_test_ord1&plan=onetime", None, False, True),
                                 ("?session_id=cs_test_ord2&plan=subscribe", None, True, False),
                                 ("?session_id=cs_test_ord3", "onetime", False, True),
                                 ("?session_id=cs_test_ord4", None, False, False)]:
        ctx = context(b, base); pg = ctx.new_page()
        pg.goto(base + "/shop.html")
        pg.evaluate("s => { localStorage.clear(); if (s) localStorage.setItem('tmu_plan', s); }", stored)
        pg.goto(base + "/order-complete.html" + qs)
        vis = lambda sel: pg.locator(sel).is_visible()
        check(vis(".plan-sub") == sub and vis(".plan-one") == one, f"order page {qs} stored={stored}: subscription block {sub}, next-bag block {one}")
        if one:
            check((pg.locator(".plan-one a[data-buy=subscribe]").get_attribute("href") or "").startswith("https://buy.stripe.com/"), "next-bag button goes to Subscribe & Save checkout")
        ctx.close()
    sent = []
    ctx = context(b, base, klaviyo=sent); pg = ctx.new_page()
    pg.goto(base + "/order-complete.html?session_id=cs_test_sms1&plan=subscribe")
    check(not pg.locator("#sms-form input[name=consent]").is_checked(), "SMS consent box is unchecked by default")
    pg.fill("#s-email", "test@example.com"); pg.fill("#s-phone", "(555) 555-0123")
    pg.click("#sms-form button[type=submit]")
    check("Tick the box" in pg.locator("#sms-msg").inner_text() and not sent, "no consent, nothing sent")
    pg.check("#sms-form input[name=consent]")
    pg.click("#sms-form button[type=submit]")
    pg.wait_for_selector("#sms-form >> text=Saved")
    pr = sent[0]["data"]["attributes"]["properties"] if sent else {}
    check(pr.get("sms_refill_consent") is True and pr.get("sms_consent_phone") == "+15555550123" and "Reply STOP" in pr.get("sms_consent_text", "")
          and pr.get("sms_consent_at"), "consent record (phone E.164, exact text, time) goes to the Klaviyo profile")
    ctx.close()
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/thanks.html")
    check(pg.locator("[data-picker] [data-picker-btn]").count() == 1, "thanks page has the plan picker inline")
    pg.goto(base + "/90-mornings.html")
    check(pg.locator("meta[name=robots][content=noindex]").count() == 1 and pg.locator("[data-picker]").count() == 1, "90 Mornings shell is noindex with a picker")
    ctx.close()


HOUSE_LINKS = {"cupofjoe": "https://buy.stripe.com/4gMeVffEv5TEfJA42g4wM02", "mushroom": "https://buy.stripe.com/00w5kF77Z1Do9lccyM4wM03"}
HEALTH_WORDS = r"\b(focus\w*|immun\w*|energ\w*|adaptogen\w*|brain\w*|calm\w*|nootropic\w*|cognit\w*|stress\w*|wellness|boost\w*|health\w*|benefit\w*)\b"


def house_tests(b, base):
    """House coffee product pages (/cup-of-joe, /mushroom-coffee-blend): buy buttons go to their own Payment Links
    with the same creator/ad credit as CoreJava's; no health words, no Roastify, none of CoreJava's terms (the
    CoreJava name only on its "You might also like" card); the order page knows the plans."""
    import re
    PAGES_H = {"cupofjoe": "/cup-of-joe.html", "mushroom": "/mushroom-coffee-blend.html"}
    for k, path in PAGES_H.items():
        ctx = context(b, base, w=390, h=844); pg = ctx.new_page()
        r = pg.goto(base + path)
        check(r.status == 200 and pg.locator("h1").count() == 1, f"{path} exists with one h1")
        main_btn = pg.locator(f"main a[data-buy={k}][data-buy-main]")
        href = main_btn.get_attribute("href") or ""
        check(main_btn.count() == 1 and href.startswith(HOUSE_LINKS[k] + "?utm_source=site") and "client_reference_id" not in href,
              f"{path}: buy button -> its Payment Link with utm tags ({href[:70]})")
        main = pg.locator("main").inner_text()
        body = re.sub(r"\s+", " ", pg.locator("main").evaluate("m => { const c = m.cloneNode(true); c.querySelectorAll('.xsell').forEach(e => e.remove()); return c.innerText; }"))
        check(not re.search(HEALTH_WORDS, main, re.I), f"{path}: no health or function words: " + str(re.findall(HEALTH_WORDS, main, re.I)))
        check("roastify" not in pg.content().lower(), f"{path}: never names Roastify")
        low = main.lower()
        check(all(w not in low for w in ("90-day", "guarantee", "marketplace global", "minnesota", "supplement facts", "food and drug")),
              f"{path}: no CoreJava terms (guarantee, MarketPlace Global, Minnesota, supplement panel, FDA line) in the page body")
        check("corejava" not in body.lower(), f"{path}: CoreJava named only on its 'You might also like' card")
        check(all(w in main for w in ("+ $5.95 flat US shipping", "No returns on opened coffee", "Roasted to order")), f"{path}: price shipping and house terms in the buy box")
        check(pg.locator("[data-picker]").count() == 0 and pg.locator(".sticky a[data-buy]").get_attribute("data-buy") == k, f"{path}: no CoreJava picker; the sticky bar buys this coffee")
        check(pg.locator("body[data-popup=off]").count() == 1, f"{path}: no CoreJava pop-up")
        ld = " ".join(pg.locator("script[type='application/ld+json']").all_text_contents())
        check(ld.count('"@type":"Product"') == 1 and "AggregateRating" not in ld and f'"url":"https://themorningupgrades.com{path}"' in ld, f"{path}: 1 Product entry with its own URL, no ratings")
        ctx.close()
    ctx = context(b, base, w=1280, h=900); pg = ctx.new_page()
    pg.goto(base + "/cup-of-joe.html")
    main = pg.locator("main").inner_text()
    check(all(w in main for w in ("$27.95", "Light", "Medium (Colombia)", "Dark", "confirm your roast at checkout")), "Cup of Joe: price, 3 roasts, roast confirmed at checkout")
    pg.locator(".ropt", has_text="Dark").click()
    check(pg.locator("[data-roast-notes]").inner_text().startswith("Deep body") and pg.locator("[data-gallery-stage]").get_attribute("data-current") == "2",
          "Cup of Joe: picking Dark shows its notes and its bag")
    pg.locator(".pthumb[data-i='1']").click()
    check(pg.locator(".roastpick input[value=light]").is_checked() and pg.locator("[data-roast-notes]").inner_text().startswith("Fresh fruit"), "Cup of Joe: the Light thumb selects Light")
    pg.goto(base + "/mushroom-coffee-blend.html")
    main = pg.locator("main").inner_text()
    check(all(w in main for w in ("$33.95", "Full ingredient list coming soon", "Dark chocolate, nougat, mild acidity", "Medium roast coffee with mushroom powder")), "Mushroom blend: price, notes, placeholder ingredient line")
    ctx.close()
    # creator and paid-ad credit ride along exactly like the CoreJava buttons
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/cup-of-joe.html?ref=kasey&utm_source=creator&utm_medium=influencer")
    for k, path in PAGES_H.items():
        pg.goto(base + path)
        href = pg.locator(f"main a[data-buy={k}][data-buy-main]").get_attribute("href") or ""
        check(href.startswith(HOUSE_LINKS[k] + "?") and href.endswith("&client_reference_id=cr_kasey"), f"house {k}: creator credit cr_kasey rides to Stripe")
    pg.goto(base + "/corejava.html")
    core = pg.locator("[data-picker-btn]").first.get_attribute("href") or ""
    check(core.endswith("&client_reference_id=cr_kasey"), "CoreJava button carries the same creator credit")
    ctx.close()
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/mushroom-coffee-blend.html?utm_source=tiktok&utm_medium=paid&utm_campaign=hc&utm_content=v1")
    href = pg.locator("main a[data-buy=mushroom][data-buy-main]").get_attribute("href") or ""
    check(href.endswith("&client_reference_id=ut__tiktok__hc__v1"), f"house mushroom: paid-ad credit rides to Stripe ({href[-40:]})")
    nav = []
    def stripe(r):
        nav.append(r.request.url); r.fulfill(status=200, content_type="text/html", body="<html><body>checkout</body></html>")
    ctx.route("https://buy.stripe.com/**", stripe)
    pg.goto(base + "/cup-of-joe.html")
    with pg.expect_navigation(url="https://buy.stripe.com/**"):
        pg.locator("main a[data-buy=cupofjoe][data-buy-main]").click()
    check(nav and nav[0].startswith(HOUSE_LINKS["cupofjoe"]), "clicking Buy Cup of Joe opens its Stripe Payment Link")
    pg.goto(base + "/cup-of-joe.html")
    check(pg.evaluate("() => localStorage.getItem('tmu_plan')") == "cupofjoe", "Buy Cup of Joe remembers plan cupofjoe")
    ctx.close()
    ctx = context(b, base, w=1440, h=900); pg = ctx.new_page()
    pg.goto(base + "/corejava.html")
    low = pg.locator("main").evaluate("m => { const c = m.cloneNode(true); c.querySelectorAll('.xsell').forEach(e => e.remove()); return c.innerText; }").lower()
    check(all(w not in low for w in ("roasting partner", "$5.95", "roasted to order", "opened coffee", "cup of joe", "mushroom")), "/corejava: no house coffee terms outside its 'You might also like' cards")
    pg.goto(base + "/start.html")
    check("house" not in pg.locator("main").inner_html().lower() and "cup-of-joe" not in pg.locator("main").inner_html(), "/start doesn't mention house coffee (site chrome aside)")
    for fn in ("shipping-returns.html", "faq.html", "terms.html", "privacy.html"):
        pg.goto(base + "/" + fn)
        c = (pg.locator("main").text_content() or "").lower()
        check("house coffee" in c and "roasting partner" in c and "roastify" not in c, f"/{fn} has a house coffee section (roasting partner, not named)")
    ctx.close()
    # order page: house coffee thank-you, none of CoreJava's account/bonus/refill text
    for plan, name in (("cupofjoe", "Cup of Joe Everyday Coffee"), ("mushroom", "Mushroom Coffee Blend")):
        ctx = context(b, base); pg = ctx.new_page()
        pg.goto(base + f"/order-complete.html?session_id=cs_test_hc_{plan}&plan={plan}")
        vis = pg.locator("main").inner_text()
        check(name in vis and "roasting partner" in vis and "MarketPlace Global" not in vis and "Recipe Pack" not in vis
              and not pg.locator("#sms-form").is_visible() and not pg.locator(".plan-one").is_visible() and not pg.locator(".plan-sub").is_visible(),
              f"order page plan={plan}: house coffee thank-you only")
        ctx.close()
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/order-complete.html?session_id=cs_test_hc_core&plan=onetime")
    vis = pg.locator("main").inner_text()
    check("MarketPlace Global" in vis and "roasting partner" not in vis, "order page plan=onetime: CoreJava text, no house coffee text")
    ctx.close()


PRODUCT_PAGES = {"corejava.html": ("CoreJava", "subscribe", "https://buy.stripe.com/8x228t3VN2Hsapg56k4wM01"),
                 "cup-of-joe.html": ("Cup of Joe Everyday Coffee", "cupofjoe", "https://buy.stripe.com/4gMeVffEv5TEfJA42g4wM02"),
                 "mushroom-coffee-blend.html": ("Mushroom Coffee Blend", "mushroom", "https://buy.stripe.com/00w5kF77Z1Do9lccyM4wM03")}


def shop_ia_tests(b, base):
    """Shop pass (Nov 2026): /shop lists the 3 coffees with working buy links; each product page has breadcrumbs,
    Product JSON-LD, its buy mapping and cards for the other 2; /house-coffee redirects; every page's nav reaches all 3."""
    import os, re, glob
    root = os.path.join(os.path.dirname(__file__), "..")
    ctx = context(b, base, w=1280, h=900); pg = ctx.new_page()
    pg.goto(base + "/shop.html")
    cards = pg.locator("main .pcard")
    check(cards.count() == 5 and pg.locator("h1").inner_text().strip() == "Shop our coffee", "/shop lists 5 product cards (3 coffees, 2 bundles)")
    for fn, (name, key, link) in PRODUCT_PAGES.items():
        c = pg.locator(f"main #pc-{fn[:-5]}:has(a[href='/{fn}'])")   # by id: the bundle cards link the product pages too
        href = c.locator(f"a[data-buy={key}]").get_attribute("href") or ""
        check(c.count() == 1 and href.startswith(link + "?"), f"/shop card for {fn}: View link and quick Buy -> {key} checkout")
    check((pg.locator("main a[data-buy=onetime]").get_attribute("href") or "").startswith("https://buy.stripe.com/3cIbJ3fEv6XIbtk8iw4wM00"), "/shop CoreJava card also offers 1 bag")
    check(pg.locator("#house").count() == 1 and pg.locator("#bundles").count() == 1 and pg.locator(".cmp3 tbody tr").count() == 6, "/shop has the #house and #bundles groups and a 6-row comparison")
    check(pg.locator(".sticky").count() == 0, "/shop has no sticky CoreJava checkout bar")
    ctx.close()
    for fn, (name, key, link) in PRODUCT_PAGES.items():
        ctx = context(b, base, w=390, h=844); pg = ctx.new_page()
        pg.goto(base + "/" + fn)
        crumbs = [t.strip() for t in pg.locator("nav.crumbs a, nav.crumbs [aria-current]").all_text_contents()]
        check(crumbs[:2] == ["Home", "Shop"] and len(crumbs) == 3, f"/{fn}: breadcrumb Home > Shop > product ({crumbs})")
        ld = [json.loads(j) for j in pg.locator("script[type='application/ld+json']").all_text_contents()]
        graph = [g for d in ld for g in d["@graph"]]
        bc = [g for g in graph if g["@type"] == "BreadcrumbList"]
        check(any(g["@type"] == "Product" for g in graph) and bc and [i["name"] for i in bc[0]["itemListElement"]][:2] == ["Home", "Shop"], f"/{fn}: Product and BreadcrumbList JSON-LD")
        og = pg.locator("meta[property='og:image']").get_attribute("content") or ""
        check(og.startswith("https://themorningupgrades.com/img/"), f"/{fn}: og:image")
        btn = pg.locator("main [data-picker-btn], main a[data-buy-main]").first
        check((btn.get_attribute("href") or "").startswith(link + "?") and btn.get_attribute("data-buy") == key, f"/{fn}: main buy button -> {key}")
        others = [f for f in PRODUCT_PAGES if f != fn]
        x = pg.locator(".xsell")
        check(x.locator(".pcard").count() == 2 and all(x.locator(f"a[href='/{o}']").count() >= 1 for o in others), f"/{fn}: 'You might also like' shows the other 2")
        check(pg.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 1, f"/{fn}: no horizontal overflow at 390")
        ctx.close()
    # old URL: /house-coffee.html redirects (noindex, canonical, meta refresh, JS), anchors go to the product page
    raw = open(os.path.join(root, "house-coffee.html")).read()
    check('name="robots" content="noindex"' in raw and 'rel="canonical" href="https://themorningupgrades.com/shop.html"' in raw
          and 'http-equiv="refresh"' in raw and "location.replace" in raw, "/house-coffee.html is a noindex redirect page")
    ctx = context(b, base); pg = ctx.new_page()
    for frm, to in (("/house-coffee.html", "/shop.html#house"), ("/house-coffee.html#cup-of-joe", "/cup-of-joe.html"),
                    ("/house-coffee.html#mushroom-blend", "/mushroom-coffee-blend.html"), ("/house-coffee.html?utm_source=x", "/shop.html?utm_source=x#house")):
        pg.goto(base + frm); pg.wait_for_url("**" + to.split("#")[0].split("?")[0] + "*")
        check(pg.url.endswith(to), f"{frm} -> {to} ({pg.url[len(base):]})")
    ctx.close()
    sm = open(os.path.join(root, "sitemap.xml")).read()
    llms = open(os.path.join(root, "llms.txt")).read()
    check(all(f"/{f}" in sm and f"/{f}" in llms for f in PRODUCT_PAGES) and "house-coffee.html" not in sm, "sitemap and llms.txt list the 3 product pages, not the redirect")
    # every page's nav and footer reach /shop and all 3 products
    for path in sorted(glob.glob(os.path.join(root, "*.html"))):
        h = open(path).read()
        if 'http-equiv="refresh"' in h:
            continue
        fn = os.path.basename(path)
        nav = h.split('<nav class="nav"')[1].split("</nav>")[0] if '<nav class="nav"' in h else ""
        foot = h.split("<footer")[1]
        if fn in ("start.html", "quiz.html"):   # mini header (ad landing page, quiz): the footer has the links
            check(all(f'href="/{f}"' in foot for f in list(PRODUCT_PAGES) + ["shop.html"]), f"{fn}: footer links all products")
            continue
        check(all(f'href="/{f}"' in nav and f'href="/{f}"' in foot for f in list(PRODUCT_PAGES) + ["shop.html"]), f"{fn}: nav and footer link /shop and all 3 products")
    # header menus: keyboard and Esc (desktop), the grouped list (phone)
    ctx = context(b, base, w=1280, h=900); pg = ctx.new_page(); pg.goto(base + "/faq.html")
    bt = pg.locator(".dd .ddb").first
    bt.focus(); pg.keyboard.press("Enter")
    check(bt.get_attribute("aria-expanded") == "true" and pg.locator("#dd-shop").is_visible(), "Shop menu opens with Enter (aria-expanded true)")
    pg.keyboard.press("Tab")
    check(pg.evaluate("() => document.activeElement.getAttribute('href')") == "/shop.html", "Tab moves into the Shop menu")
    pg.keyboard.press("Escape")
    check(bt.get_attribute("aria-expanded") == "false" and not pg.locator("#dd-shop").is_visible() and pg.evaluate("() => document.activeElement.classList.contains('ddb')"),
          "Esc closes the Shop menu and returns focus to its button")
    bt.click(); pg.mouse.click(40, 600)
    check(not pg.locator("#dd-shop").is_visible(), "a click outside closes the menu")
    ctx.close()
    ctx = context(b, base); pg = ctx.new_page(); pg.goto(base + "/guides.html")
    pg.click(".burger")
    links = [a.strip().split("\n")[0] for a in pg.locator(".menu a:visible").all_inner_texts()]
    check(links[:4] == ["All coffees", "CoreJava", "Cup of Joe", "Mushroom Coffee Blend"] and "Shipping & returns" in links and "Manage subscription" in links,
          f"phone menu: Shop > the 3 products, then Learn, FAQ, Shipping & returns, Manage subscription ({links[:4]})")
    pg.keyboard.press("Escape")
    check(not pg.locator(".menu").is_visible() and pg.locator(".burger").get_attribute("aria-expanded") == "false", "Esc closes the phone menu")
    ctx.close()


BUNDLE_LINKS = {"bundle_cupofjoe": "https://buy.stripe.com/cNi9AV2RJ5TEcxodCQ4wM04", "bundle_mushroom": "https://buy.stripe.com/5kQaEZeArci22WOeGU4wM05"}
# Price order, low to high (owner, Nov 5 2026): /shop cards and the home row
SHOP_ORDER = ["pc-cup-of-joe", "pc-mushroom-coffee-blend", "pc-corejava", "pc-bundle-cupofjoe", "pc-bundle-mushroom"]


def bundle_tests(b, base):
    """Home lists the 3 coffees with one call to action, Shop; /shop has the 2 bundles in price order with their
    own Payment Links (same creator/ad credit); site.js maps the keys; the order page knows the bundles."""
    import os, re
    root = os.path.join(os.path.dirname(__file__), "..")
    js = open(os.path.join(root, "assets", "site.js")).read()
    for k, cfg in (("bundle_cupofjoe", "STRIPE_BUNDLE_CUPOFJOE"), ("bundle_mushroom", "STRIPE_BUNDLE_MUSHROOM")):
        m = re.search(cfg + r': "([^"]*)"', js)
        check(bool(m) and m.group(1) == BUNDLE_LINKS[k] and re.search(k + r":\{[^}]*link:'" + cfg + "'", js), f"site.js maps {k} -> {BUNDLE_LINKS[k]}")
    check("bundle_cupofjoe:89.95" in js and "bundle_mushroom:94.95" in js, "site.js prices the bundles at 89.95 and 94.95")
    # home: the 3 coffees in price order, linked to their pages; no checkout anywhere; every button says Shop
    raw = open(os.path.join(root, "index.html")).read()
    check("data-buy" not in raw and "buy.stripe.com" not in raw and "data-picker" not in raw and 'id="quiz"' not in raw, "home HTML has no data-buy, Stripe link, plan picker or quiz")
    for w, h in ((390, 844), (1280, 900)):
        ctx = context(b, base, w, h); pg = ctx.new_page(); pg.goto(base + "/")
        ids = pg.eval_on_selector_all(".ourc .pcard", "els => els.map(e => e.id)")
        check(ids == SHOP_ORDER[:3], f"home at {w}: 3 coffees in price order ({ids})")
        for i, fn in enumerate(("cup-of-joe.html", "mushroom-coffee-blend.html", "corejava.html")):
            check(pg.locator(".ourc .pcard").nth(i).locator(f"h3 a[href='/{fn}']").count() == 1, f"home at {w}: card {i + 1} links /{fn}")
        if w == 1280:
            xs = [pg.locator(f"#{i}").bounding_box()["x"] for i in ids]
            check(xs == sorted(xs) and len(set(round(x) for x in xs)) == 3, f"home at 1280: coffees left to right in price order ({[round(x) for x in xs]})")
        btns = pg.eval_on_selector_all(".btn:visible, a[data-buy], button.btn", "els => els.map(e => [e.textContent.trim(), e.getAttribute('href')])")
        check(btns and all(t == "Shop" and h == "/shop.html" for t, h in btns), f"home at {w}: every button is Shop -> /shop.html ({btns})")
        check(pg.locator(".hero2 .btn").count() == 1 and pg.locator(".ourc .btn").count() == 1 and pg.locator(".ourc .pc-acts").count() == 0,
              f"home at {w}: one Shop button in the hero, one under the coffees, no per-card buttons")
        hrefs = pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
        check(not any("buy.stripe.com" in u for u in hrefs), f"home at {w}: no link goes to Stripe")
        check(pg.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 1, f"home at {w}: no horizontal overflow")
        ctx.close()
    # /shop: price order, bundle cards, their buttons
    for w, h in ((390, 844), (1280, 900)):
        ctx = context(b, base, w, h); pg = ctx.new_page(); pg.goto(base + "/shop.html")
        ids = pg.eval_on_selector_all("main .pcard", "els => els.map(e => e.id)")
        check(ids == SHOP_ORDER, f"/shop at {w}: cards in price order ({ids})")
        boxes = [pg.locator(f"#{i}").bounding_box() for i in SHOP_ORDER]
        if w == 1280:
            row1 = [bx["x"] for bx in boxes[:3]]
            check(row1 == sorted(row1) and len({round(bx["y"]) for bx in boxes[:3]}) == 1, f"/shop at 1280: Cup of Joe, Mushroom, CoreJava left to right in 1 row ({[round(x) for x in row1]})")
            check(boxes[3]["y"] > boxes[2]["y"] + boxes[2]["height"] - 1 and boxes[3]["x"] < boxes[4]["x"] and round(boxes[3]["y"]) == round(boxes[4]["y"]),
                  "/shop at 1280: the 2 bundles in the next row, $89.95 then $94.95")
        else:
            ys = [bx["y"] for bx in boxes]
            check(ys == sorted(ys), "/shop at 390: cards stack in price order")
        check(pg.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 1, f"/shop at {w}: no horizontal overflow")
        ctx.close()
    ctx = context(b, base, 1280, 900); pg = ctx.new_page(); pg.goto(base + "/shop.html")
    for k, name, price, house, extra in (("bundle_cupofjoe", "CoreJava + Cup of Joe", "$89.95", "cup-of-joe.html", "Choose light, medium or dark at checkout"),
                                         ("bundle_mushroom", "CoreJava + Mushroom Coffee Blend", "$94.95", "mushroom-coffee-blend.html", "Mushroom Coffee Blend")):
        c = pg.locator(f"#pc-{k.replace('_', '-')}")
        t = c.inner_text()
        btn = c.locator(f"a[data-buy={k}]")
        href = btn.get_attribute("href") or ""
        check(btn.count() == 1 and href.startswith(BUNDLE_LINKS[k] + "?utm_source=site"), f"/shop {name}: Buy -> its Payment Link ({href[:60]})")
        check(name in t and price in t and "+ $8.95 shipping" in t and "Ships in 2 packages." in t and "1 bag CoreJava, 30 servings" in t and extra in t,
              f"/shop {name}: name, price, $8.95 shipping, 2 packages, what's included")
        check(c.locator("a[href='/corejava.html']").count() == 1 and c.locator(f"a[href='/{house}']").count() == 1 and c.locator("img").count() == 1,
              f"/shop {name}: links both product pages and has 1 image")
        low = t.lower()
        # savings (Koby, Nov 5 2026): separate prices (CoreJava 1 bag + the house coffee, shipping excluded) minus the bundle price
        from decimal import Decimal as D
        house_price = D(re.search(r"cupofjoe:([\d.]+)" if "cupofjoe" in k else r"mushroom:([\d.]+)", js.split("var PRICE=")[1]).group(1))
        one_bag = D(re.search(r"onetime:([\d.]+)", js.split("var PRICE=")[1]).group(1))
        house_card = D(re.search(r"\$([\d.]+)", pg.locator(f"#pc-{house[:-5]} .pc-price b").inner_text()).group(1))
        sep, bundle = one_bag + house_price, D(price[1:])
        was = c.locator("s.bc-was").inner_text().strip()
        save = c.locator(".bc-save").inner_text().strip()
        check(house_card == house_price and was == f"${sep}" and save == f"Save ${sep - bundle} vs buying separately",
              f"/shop {name}: struck separate total {was} = $79.95 + ${house_price}; '{save}' = separate minus {price}")
        check(c.locator("s, del, strike").count() == 1 and not re.search(r"discount|% off|\bfree\b", low), f"/shop {name}: 1 struck price, no discount or free wording")
        check(not re.search(HEALTH_WORDS, t, re.I) and "roastify" not in low and "\u2014" not in t and "\u2013" not in t, f"/shop {name}: no health words, no Roastify, no em/en dashes")
    # outside the 2 bundle cards: no price-saving or discount wording and no struck price (CoreJava cards, picker, house cards)
    rest = re.sub(r"Subscribe\s*&\s*Save", "", pg.locator("main").evaluate("m => { const c = m.cloneNode(true); c.querySelectorAll('.bcard').forEach(e => e.remove()); return c.innerText; }"))
    check(not re.search(r"\bsav(e|es|ing|ings)\b|discount|% off|\$[\d.]+ off", rest, re.I)
          and pg.locator("main s:not(.bcard s), main del, main strike").count() == 0, "/shop: save/discount wording and struck prices only inside the bundle cards")
    ld = " ".join(pg.locator("script[type='application/ld+json']").all_text_contents())
    il = [g for d in [json.loads(x) for x in pg.locator("script[type='application/ld+json']").all_text_contents()] for g in d["@graph"] if g["@type"] == "ItemList"]
    names = [i["name"] for i in il[0]["itemListElement"]] if il else []
    check(names[:2] == ["Cup of Joe Everyday Coffee", "The Morning Upgrade Mushroom Coffee Blend"] and names[3:] == ["CoreJava + Cup of Joe", "CoreJava + Mushroom Coffee Blend"] and "AggregateRating" not in ld,
          f"/shop ItemList in price order with the bundles, no ratings ({names})")
    ctx.close()
    # creator credit rides along; clicking Buy opens the bundle's Payment Link and remembers the plan
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/shop.html?ref=kasey&utm_source=creator&utm_medium=influencer")
    pg.goto(base + "/shop.html")
    for k in BUNDLE_LINKS:
        href = pg.locator(f"a[data-buy={k}]").get_attribute("href") or ""
        check(href.startswith(BUNDLE_LINKS[k] + "?") and href.endswith("&client_reference_id=cr_kasey"), f"{k}: creator credit cr_kasey rides to Stripe")
    nav = []
    def stripe(r):
        nav.append(r.request.url); r.fulfill(status=200, content_type="text/html", body="<html><body>checkout</body></html>")
    ctx.route("https://buy.stripe.com/**", stripe)
    for k in BUNDLE_LINKS:
        pg.goto(base + "/shop.html")
        with pg.expect_navigation(url="https://buy.stripe.com/**"):
            pg.locator(f"a[data-buy={k}]").click()
        check(nav and nav[-1].startswith(BUNDLE_LINKS[k] + "?"), f"clicking Buy on {k} opens {BUNDLE_LINKS[k]}")
        pg.goto(base + "/shop.html")
        check(pg.evaluate("() => localStorage.getItem('tmu_plan')") == k, f"Buy {k} remembers plan {k}")
    ctx.close()
    ctx = context(b, base); pg = ctx.new_page()
    pg.goto(base + "/shop.html?utm_source=tiktok&utm_medium=paid&utm_campaign=bd&utm_content=v1")
    href = pg.locator("a[data-buy=bundle_mushroom]").get_attribute("href") or ""
    check(href.endswith("&client_reference_id=ut__tiktok__bd__v1"), f"bundle_mushroom: paid-ad credit rides to Stripe ({href[-40:]})")
    ctx.close()
    # order page: the bundle thank-you (2 packages), none of the single-product blocks
    for plan, name, house in (("bundle_cupofjoe", "CoreJava + Cup of Joe bundle", "Cup of Joe Everyday Coffee"),
                              ("bundle_mushroom", "CoreJava + Mushroom Coffee Blend bundle", "The Morning Upgrade Mushroom Coffee Blend")):
        ctx = context(b, base); pg = ctx.new_page()
        pg.goto(base + f"/order-complete.html?session_id=cs_test_bd_{plan}&plan={plan}")
        vis = pg.locator("main").inner_text()
        check(name in vis and house in vis and "2 packages" in vis and "roasting partner" in vis and "MarketPlace Global" in vis
              and not pg.locator(".plan-one").is_visible() and not pg.locator(".plan-sub").is_visible() and not pg.locator("#sms-form").is_visible()
              and not pg.locator("[data-line=house]").is_visible() and not pg.locator("[data-line=corejava]").is_visible(),
              f"order page plan={plan}: bundle thank-you, ships in 2 packages")
        ctx.close()
    # every generated page: price-saving/discount wording and struck prices only inside the bundle cards
    import glob, importlib.util
    spec = importlib.util.spec_from_file_location("check_copy", os.path.join(os.path.dirname(__file__), "check_copy.py"))
    cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
    pages = sorted(glob.glob(os.path.join(root, "*.html")) + glob.glob(os.path.join(root, "c", "**", "*.html"), recursive=True))
    bad = {os.path.relpath(f, root): [h[1] for h in cc.promo_scan(open(f).read())] for f in pages}
    bad = {k: v for k, v in bad.items() if v}
    check(not bad, f"no save/discount wording or struck price outside the bundle cards, on any page ({bad})")
    shop = open(os.path.join(root, "shop.html")).read()
    cards = re.findall(r'<article class="pcard bcard[\s\S]*?</article>', shop)
    check(len(cards) == 2 and all("Save $" in c and "<s " in c for c in cards) and shop.count("Save $") == 2 and shop.count("<s ") == 2,
          "/shop: the 2 save lines and 2 struck prices are inside the 2 bundle cards")
    for fn in ("corejava.html", "index.html", "start.html", "cup-of-joe.html", "mushroom-coffee-blend.html", "corejava-coffee.html"):
        h = open(os.path.join(root, fn)).read()
        check("Save $" not in h and "<s " not in h and "<s>" not in h and "bcard" not in h, f"/{fn}: no bundle savings, no struck price")
    # /start stays as it was: no bundles, no Shop button, its own picker
    st = open(os.path.join(root, "start.html")).read()
    check("bundle" not in st.lower() and 'class="btn sm" href="/shop.html"' not in st and st.count("data-picker-btn") == 2, "/start unchanged: no bundles, mini header, its 2 pickers")


def popup_tests(b, base):
    """Email pop-up: when it opens, where it never opens, keyboard and focus, the Klaviyo sign-up and
    the success state, and the Subscribe & Save note afterwards. Timers run on Playwright's clock."""
    SUB = "https://buy.stripe.com/8x228t3VN2Hsapg56k4wM01"
    def is_open(pg):
        return pg.locator(".tmu-pop .tp-panel[role=dialog]").count() == 1 and pg.locator(".tmu-pop .tp-panel").is_visible()
    def wait10(pg):
        pg.clock.run_for(11000); pg.wait_for_timeout(50)

    # opens after 10 s on the home page (desktop), not before; focus lands in the email field
    sent = []
    ctx = context(b, base, 1440, 900, klaviyo=sent, popup=True); pg = ctx.new_page(); pg.clock.install()
    pg.goto(base + "/")
    pg.clock.run_for(5000); pg.wait_for_timeout(50)
    check(not is_open(pg), "pop-up: not open at 5 s")
    wait10(pg)
    check(is_open(pg), "pop-up: opens after 10 s on the home page")
    check(pg.evaluate("() => document.activeElement && document.activeElement.id") == "tp-email", "pop-up: focus starts in the email field (desktop)")
    check(pg.locator(".tp-panel").get_attribute("aria-modal") == "true" and pg.locator("#tp-h").count() == 1
          and pg.locator("label[for=tp-email]").count() == 1 and pg.locator("label[for=tp-first]").count() == 1, "pop-up: modal dialog with a heading and labelled fields")
    txt = pg.locator(".tp-panel").inner_text()
    for must in ("Recipe Pack", "$69.95 a month", "$79.95", "Subscribe & Save", "Pause, skip or cancel anytime", "By signing up you agree to emails from The Morning Upgrade. Unsubscribe anytime."):
        check(must in txt, f"pop-up says {must!r}")
    check("MORNING10" not in txt and "code" not in txt.lower(), "pop-up mentions no promo code")
    check("$10" not in txt and " off" not in txt.lower() and "discount" not in txt.lower(), "pop-up states the 2 prices, no 'off' or discount wording")
    check(pg.locator(".tp-panel a[href='/privacy.html']").count() == 1, "pop-up links the privacy page")
    inside = []
    for _ in range(12):
        pg.keyboard.press("Tab")
        inside.append(pg.evaluate("() => !!document.activeElement.closest('.tp-panel')"))
    pg.keyboard.press("Shift+Tab"); inside.append(pg.evaluate("() => !!document.activeElement.closest('.tp-panel')"))
    check(all(inside), "pop-up: Tab and Shift+Tab stay inside the dialog")
    # submit: bad email, then a good one
    pg.fill("#tp-email", "nope"); pg.click(".tp-form button[type=submit]")
    check(pg.locator("#tp-msg").inner_text().startswith("Check the email") and not sent, "pop-up: rejects a bad email, sends nothing")
    pg.fill("#tp-first", "Sam"); pg.fill("#tp-email", "test@example.com"); pg.click(".tp-form button[type=submit]")
    pg.wait_for_selector('.tmu-pop [data-step="done"]:not([hidden])')
    a = sent[0]["data"] if sent else {}
    props = a.get("attributes", {}).get("profile", {}).get("data", {}).get("attributes", {}).get("properties", {}) if a else {}
    check(bool(a) and a["relationships"]["list"]["data"]["id"] == "WgctGT" and a["attributes"]["custom_source"] == "popup"
          and props.get("offer") == "recipe_pack_plus_autoship10" and props.get("source") == "popup"
          and a["attributes"]["profile"]["data"]["attributes"]["first_name"] == "Sam", "pop-up: subscribes to list WgctGT, source popup, offer recipe_pack_plus_autoship10")
    lead = pg.evaluate("() => (window.dataLayer||[]).map(a=>Array.from(a)).filter(x=>x[0]==='event'&&x[1]==='Lead').map(x=>x[2].source)")
    check(lead == ["popup"], f"pop-up: Lead fires once with source popup ({lead})")
    dl = pg.locator(".tmu-pop .tp-dl")
    check(dl.get_attribute("href") == "/assets/recipe-pack.pdf" and dl.get_attribute("download") is not None and dl.is_visible(), "pop-up success: Download the Recipe Pack")
    use = pg.locator(".tmu-pop .tp-use")
    href = use.get_attribute("href") or ""
    check(use.is_visible() and "Start Subscribe & Save, $69.95 a month" in use.text_content() and href.startswith(SUB + "?") and "promo" not in href,
          f"pop-up success: Start Subscribe & Save goes to the plain Subscribe & Save checkout ({href[:70]})")
    check(pg.evaluate("() => document.activeElement.id") == "tp-h2", "pop-up success: focus moves to the success heading")
    pg.keyboard.press("Escape")
    check(not is_open(pg) and pg.evaluate("() => JSON.parse(localStorage.getItem('tmu_pop')).s") == "signed", "pop-up: Escape closes; sign-up remembered")
    pg.goto(base + "/"); wait10(pg)
    check(not is_open(pg), "pop-up: never again after sign-up")
    pg.goto(base + "/corejava.html")   # home has no picker since Nov 5 2026: the note shows next to CoreJava's
    note = pg.locator(".shop-buy [data-picker] .promo-note")
    check(note.count() == 1 and note.is_visible() and note.inner_text() == "Subscribe & Save is $69.95 a month; 1 bag is $79.95 \u00b7 Cancel anytime", "after sign-up: note under the Subscribe & Save button")
    pg.locator(".shop-buy [data-picker] input[value=onetime]").locator("xpath=..").click()
    check(not note.is_visible(), "after sign-up: no note while 1 bag is picked")
    hrefs = pg.eval_on_selector_all("a[data-buy]", "els => els.map(e => e.href)")
    check(hrefs and not any("promo" in h for h in hrefs), "no checkout link carries a promo code")
    ctx.close()

    # close (backdrop) snoozes for 14 days; after that it can show again
    ctx = context(b, base, 1440, 900, popup=True); pg = ctx.new_page(); pg.clock.install()
    pg.goto(base + "/shop.html"); wait10(pg)
    check(is_open(pg), "pop-up: opens on /shop")
    pg.mouse.click(30, 30)
    check(not is_open(pg), "pop-up: backdrop click closes it")
    pg.goto(base + "/faq.html"); wait10(pg)
    check(not is_open(pg), "pop-up: snoozed after closing")
    pg.evaluate("() => localStorage.setItem('tmu_pop', JSON.stringify({s:'closed',t:Date.now()-15*864e5}))")
    pg.goto(base + "/faq.html"); wait10(pg)
    check(is_open(pg), "pop-up: shows again after 14 days")
    pg.click(".tp-x")
    check(not is_open(pg), "pop-up: the close button closes it")
    ctx.close()

    # exit intent (desktop) and failure message
    ctx = context(b, base, 1440, 900, klaviyo=[], popup=True, status=500); pg = ctx.new_page(); pg.clock.install()
    pg.goto(base + "/ingredients.html"); pg.clock.run_for(3000)
    pg.evaluate("() => document.dispatchEvent(new MouseEvent('mouseout',{clientY:-2,relatedTarget:null,bubbles:true}))")
    check(is_open(pg), "pop-up: opens on desktop exit intent")
    pg.fill("#tp-email", "test@example.com"); pg.click(".tp-form button[type=submit]")
    pg.wait_for_selector("#tp-msg:has-text('try again')")
    check(pg.locator(".tp-form").is_visible() and pg.locator(".tp-form button[type=submit]").is_enabled()
          and pg.locator('[data-step="done"]').is_hidden(), "pop-up: a failed sign-up shows a friendly error and keeps the form")
    ctx.close()

    # never on these pages, never over the quiz
    ctx = context(b, base, 1440, 900, popup=True); pg = ctx.new_page(); pg.clock.install()
    for path in ("/quiz.html", "/order-complete.html", "/thanks.html", "/partner.html", "/share.html", "/no-such-page", "/start.html",
                 "/shop.html?utm_source=tiktok&utm_medium=paid&utm_campaign=t1"):
        pg.goto(base + path); wait10(pg)
        pg.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(50)
        check(not is_open(pg), f"pop-up: never on {path}")
    pg.goto(base + "/faq.html"); wait10(pg)
    check(not is_open(pg), "pop-up: still closed on the next page after a paid visit (tmu_ut flag)")
    pg.evaluate("() => localStorage.removeItem('tmu_ut')")
    pg.evaluate("() => localStorage.setItem('tmu_purchased', JSON.stringify(['cs_test_x']))")
    pg.goto(base + "/"); wait10(pg)
    check(not is_open(pg), "pop-up: not after an order from this browser")
    ctx.close()

    # phones: 50% scroll opens it as a bottom sheet with the photo hidden
    ctx = context(b, base, 390, 844, popup=True); pg = ctx.new_page()
    pg.goto(base + "/shop.html")
    pg.evaluate("() => window.scrollTo(0, (document.documentElement.scrollHeight - innerHeight) * 0.55)")
    pg.wait_for_selector(".tmu-pop .tp-panel", timeout=3000)
    box = pg.locator(".tp-panel").bounding_box()
    check(abs(box["y"] + box["height"] - 844) < 2 and box["width"] == 390 and pg.locator(".tp-media").is_hidden(), f"pop-up: 50% scroll opens a bottom sheet on phones ({box})")
    check(pg.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 1, "pop-up: no horizontal overflow on phones")
    ctx.close()


def seo_tests(b, base):
    """Static checks on the generated HTML: titles/descriptions, canonicals, sitemap, structured data,
    and the CoreJava page (brand searches) with its internal links."""
    import os, re, glob, html as _h
    root = os.path.join(os.path.dirname(__file__), "..")
    site = "https://themorningupgrades.com"
    home = open(os.path.join(root, "index.html")).read()
    check('<meta name="msvalidate.01" content="97386D3157EE9C0604AE6D8A368F083C" />' in home.split("</head>")[0], "index.html head carries the Bing msvalidate.01 tag")
    org = [g for d in re.findall(r'<script type="application/ld\+json">(.*?)</script>', home, re.S) for g in json.loads(d)["@graph"] if g["@type"] == "Organization"]
    check(org and "https://www.facebook.com/profile.php?id=61595873313798" in org[0].get("sameAs", []), "Organization sameAs lists the Facebook page")
    titles, descs, indexable = {}, {}, set()
    for path in sorted(glob.glob(os.path.join(root, "*.html"))):
        fn = os.path.basename(path)
        h = open(path).read()
        if 'name="robots" content="noindex"' in h:
            check("application/ld+json" not in h, f"{fn}: noindex page carries no structured data")
            continue
        indexable.add(fn)
        url = site + "/" if fn == "index.html" else f"{site}/{fn}"
        t = _h.unescape(re.search(r"<title>(.*?)</title>", h).group(1))
        d = _h.unescape(re.search(r'<meta name="description" content="(.*?)"', h).group(1))
        titles.setdefault(t, []).append(fn); descs.setdefault(d, []).append(fn)
        check(len(t) <= 60 and 50 <= len(d) <= 160, f"{fn}: title {len(t)} <= 60, description {len(d)} in 50-160")
        check(f'<link rel="canonical" href="{url}">' in h, f"{fn}: canonical is its own URL")
        og = re.search(r'<meta property="og:image" content="https://themorningupgrades.com(/[^"]+)"', h)
        check(bool(og) and os.path.exists(os.path.join(root, og.group(1).lstrip("/"))), f"{fn}: og:image exists ({og and og.group(1)})")
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        try:
            graph = [g for j in lds for g in json.loads(j)["@graph"]]
        except Exception as e:
            graph = []; check(False, f"{fn}: JSON-LD parses ({e})")
        types = [g["@type"] for g in graph]
        check("AggregateRating" not in h and '"Review"' not in h and "ratingValue" not in h, f"{fn}: no rating or review markup")
        if fn != "index.html":
            bc = [g for g in graph if g["@type"] == "BreadcrumbList"]
            names = [i["name"] for i in bc[0]["itemListElement"]] if bc else []
            check(bool(bc) and names[0] == "Home" and bc[0]["itemListElement"][-1]["item"] == url and all(len(n) <= 60 for n in names),
                  f"{fn}: BreadcrumbList ends at the page with short names ({names})")
        for g in graph:
            if g["@type"] == "Product" and fn in ("cup-of-joe.html", "mushroom-coffee-blend.html"):
                o = g["offers"]
                check(g["brand"]["name"] == "The Morning Upgrade" and "manufacturer" not in g and o["price"] in ("27.95", "33.95") and o["priceCurrency"] == "USD"
                      and o["shippingDetails"]["shippingRate"]["value"] == "5.95" and "hasMerchantReturnPolicy" not in o and "aggregateRating" not in g,
                      f"{fn}: house Product {g['name']}: own brand, no MarketPlace Global, $5.95 shipping, no CoreJava return policy")
                continue
            if g["@type"] == "Product":
                offers = g["offers"]
                ok = g["brand"]["name"] == "CoreJava" and g["manufacturer"]["name"] == "MarketPlace Global" and len(offers) == 2 and all(
                    o["price"] in ("79.95", "69.95") and o["priceCurrency"] == "USD" and o["availability"].endswith("InStock") for o in offers)
                check(ok and "aggregateRating" not in g and "review" not in g, f"{fn}: Product brand CoreJava, maker MarketPlace Global, two in-stock USD offers")
    for t, fns in titles.items():
        check(len(fns) == 1, f"title unique: {t!r} ({fns})")
    for d, fns in descs.items():
        check(len(fns) == 1, f"description unique ({fns})")
    sm = set(re.findall(r"<loc>(.*?)</loc>", open(os.path.join(root, "sitemap.xml")).read()))
    want = {site + "/" if f == "index.html" else f"{site}/{f}" for f in indexable}
    check(sm == want, f"sitemap lists exactly the {len(want)} indexable pages (missing {sorted(want - sm)}, extra {sorted(sm - want)})")
    # the CoreJava page: label facts, disclosure, no claims, and linked from the pages that matter
    h = open(os.path.join(root, "corejava-coffee.html")).read()
    txt = _h.unescape(re.sub(r"<[^>]+>", " ", h))
    for must in ("150 mg per scoop in total", "1,500 mg MCTs from coconut", "7.5 oz (213 g)", "1 level scoop (7 g)", "$79.95", "$69.95", "Independent ISR of MarketPlace Global",
                 "not an independent review", "Dark Roast Colombian Instant Coffee", "400 mg"):
        check(must in txt, f"corejava-coffee.html says {must!r}")
    check('"@type":"Product"' in h and '"@type":"FAQPage"' in h, "corejava-coffee.html has Product and FAQPage markup")
    for page in ("index.html", "corejava.html", "ingredients.html", "guides.html", "faq.html"):
        check('href="/corejava-coffee.html"' in open(os.path.join(root, page)).read(), f"{page} links /corejava-coffee.html")
    ing = open(os.path.join(root, "ingredients.html")).read()
    check('id="panel-text"' in ing and "L-Theanine" in ing and "400 mg" in ing, "ingredients.html has the Supplement Facts panel as text")
    llms = open(os.path.join(root, "llms.txt")).read()
    check("corejava-coffee.html" in llms and "L-Theanine 400 mg" in llms, "llms.txt lists the CoreJava page and the panel")
    # the current bag (Koby's photos, Nov 4 2026): no page may carry the old label's figures
    every = sorted(glob.glob(os.path.join(root, "*.html")) + glob.glob(os.path.join(root, "c", "**", "*.html"), recursive=True))
    for path in every + [os.path.join(root, "llms.txt")]:
        txt = _h.unescape(open(path, encoding="utf-8").read())
        for old in ("100 mg natural caffeine", "100 mg of added natural caffeine", "6.8 g", "7.2 oz", "204 g", "1,700%"):
            check(old not in txt, f"{os.path.relpath(path, root)}: no old-label figure {old!r}")
    for must in ("Medium-Chain Triglycerides (Coconut MCT Oil and Acacia Fiber)", "1710%", "Caffeine (from Dark Roast Colombian Instant Coffee",
                 "Serving size: 1 level scoop (7 g)", "Natural Flavors, Silicon Dioxide", "Contains:</strong> tree nuts (coconut)"):
        check(must in ing, f"ingredients.html panel text has {must!r}")
    # the bag's printed statements (owner, Koby, Nov 4 2026): quoted on the 2 info pages only, with the FDA notice
    quotes = ("WEIGHT CONTROL COFFEE&dagger;", "SUPPORTS HEALTHY APPETITE CONTROL | FOCUS | ENERGY&dagger;", "HELPS BOOST METABOLISM, ENERGY &amp; FOCUS&dagger;")
    fda = "These statements have not been evaluated by the Food and Drug Administration."
    for path in every + [os.path.join(root, "llms.txt")]:
        rel = os.path.relpath(path, root); raw = open(path, encoding="utf-8").read()
        has = [q for q in quotes if q in raw or _h.unescape(q) in _h.unescape(re.sub(r"<[^>]+>", " ", raw))]
        if rel in ("ingredients.html", "corejava-coffee.html"):
            sec = raw.split('id="label-says"')[1].split("</div>")[0] if 'id="label-says"' in raw else ""
            check(len(has) == 3 and all(q in sec for q in quotes) and fda in sec and "quoted as printed" in sec,
                  f"{rel}: 'What the label says' quotes the 3 label statements with the FDA notice")
        else:
            check(not has, f"{rel}: no label benefit quotes ({has})")
    for page in ("start.html", "shop.html", "corejava.html", "index.html", "cup-of-joe.html", "mushroom-coffee-blend.html"):
        check('id="label-says"' not in open(os.path.join(root, page)).read(), f"{page}: no 'What the label says' section")


def klaviyo_checkout_tests(b, base):
    """Started Checkout / Placed Order to Klaviyo: only for a visitor this browser knows (signed up here, or a
    Klaviyo _kx link), never with a privacy signal, never with an email in a URL. Stripe is answered locally."""
    SUB = "https://buy.stripe.com/8x228t3VN2Hsapg56k4wM01"
    ONE = "https://buy.stripe.com/3cIbJ3fEv6XIbtk8iw4wM00"

    def kctx(init=""):
        events, nav = [], []
        ctx = b.new_context(viewport={"width": 390, "height": 844})
        ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}")
        ctx.add_init_script(NO_POPUP_JS)
        if init:
            ctx.add_init_script(init)

        def route(r):
            u = r.request.url
            if u.startswith(base):
                return r.continue_()
            if u.startswith("https://a.klaviyo.com/client/subscriptions/"):
                return r.fulfill(status=202, body="")
            if u.startswith("https://a.klaviyo.com/client/events/"):
                events.append({"url": u, "body": json.loads(r.request.post_data or "{}"), "rev": r.request.headers.get("revision")})
                return r.fulfill(status=202, body="")
            if u.startswith("https://buy.stripe.com/"):
                nav.append(u)
                return r.fulfill(status=200, content_type="text/html", body="<html><body>checkout</body></html>")
            return r.abort()
        ctx.route("**/*", route)
        return ctx, events, nav

    def buy(pg, plan=None):
        pg.goto(base + "/corejava.html")
        if plan == "onetime":
            pg.locator("[data-picker] input[value=onetime]").first.locator("xpath=..").click()
        with pg.expect_navigation(url="https://buy.stripe.com/**"):
            pg.locator("[data-picker-btn]").first.click()

    def settle(pg, events, n, ms=2000):
        for _ in range(ms // 50):
            if len(events) >= n:
                break
            pg.wait_for_timeout(50)
        pg.wait_for_timeout(150)

    def attrs(e):
        return e["body"]["data"]["attributes"]

    # not signed up on this browser: checkout works, nothing goes to Klaviyo
    ctx, events, nav = kctx(); pg = ctx.new_page()
    buy(pg); settle(pg, events, 1, 600)
    check(not events and nav and nav[0].startswith(SUB), "Started Checkout: nothing sent for an unknown visitor, checkout still opens")
    ctx.close()

    # signed up through the guide capture, then Buy: Started Checkout with plan, value and the checkout URL
    ctx, events, nav = kctx(); pg = ctx.new_page()
    pg.goto(base + "/start.html")
    f = pg.locator("form[data-capture]").first
    f.locator("input[type=email]").fill("buyer@example.com")
    with pg.expect_navigation():
        f.locator("button[type=submit]").click()
    buy(pg); settle(pg, events, 1)
    a = attrs(events[0]) if events else {}
    pr = a.get("properties", {})
    check(len(events) == 1 and a["metric"]["data"]["attributes"]["name"] == "Started Checkout"
          and a["profile"]["data"]["attributes"] == {"email": "buyer@example.com"}, "Started Checkout sent for a signed-up visitor, email in the body")
    check(pr.get("plan") == "subscribe" and pr.get("value") == 69.95 and a.get("value") == 69.95 and pr.get("currency") == "USD"
          and pr.get("CheckoutURL", "").startswith(SUB + "?utm_source=klaviyo&utm_medium=email") and pr.get("clicked_url", "").startswith(SUB),
          "Started Checkout (subscribe): plan, $69.95, Stripe checkout URL")
    check(events and events[0]["rev"] == "2025-01-15" and "company_id=Ucdz59" in events[0]["url"], "Started Checkout uses the public site key and the site's API revision")
    urls = " ".join([e["url"] for e in events] + nav + [pr.get("CheckoutURL", ""), pr.get("clicked_url", "")])
    check("@" not in urls and "%40" not in urls.upper() and "example.com" not in urls, "no email in any URL (Klaviyo request, checkout links)")
    buy(pg, "onetime"); settle(pg, events, 2)
    pr = attrs(events[1])["properties"] if len(events) > 1 else {}
    check(pr.get("plan") == "onetime" and pr.get("value") == 79.95 and pr.get("CheckoutURL", "").startswith(ONE + "?"), "Started Checkout (1 bag): plan, $79.95, Stripe checkout URL")
    # the order page tells Klaviyo the order happened, once per Stripe session
    pg.goto(base + "/order-complete.html?session_id=cs_test_kl1&plan=onetime"); settle(pg, events, 3)
    pg.reload(); pg.wait_for_timeout(300)
    po = [attrs(e) for e in events if attrs(e)["metric"]["data"]["attributes"]["name"] == "Placed Order"]
    check(len(po) == 1 and po[0].get("unique_id") == "cs_test_kl1" and po[0].get("value") == 79.95, "Placed Order once per session, with the plan's value")
    # the partner list never sets the remembered email
    pg.evaluate("() => localStorage.removeItem('tmu_kl')")
    pg.evaluate("() => klaviyoSubscribe(TMU.KLAVIYO_LIST_PARTNERS, 'partner@example.com', '', {}, 'test')")
    pg.wait_for_timeout(200)
    check(pg.evaluate("() => localStorage.getItem('tmu_kl')") is None, "partner-form sign-ups are not used for Started Checkout")
    ctx.close()

    # Global Privacy Control or Do Not Track: nothing sent, checkout still opens
    known = "try{localStorage.setItem('tmu_kl',JSON.stringify({e:'gpc@example.com',t:Date.now()}))}catch(e){}"
    for label, sig in (("GPC", "Object.defineProperty(Navigator.prototype,'globalPrivacyControl',{get:function(){return true}});"),
                       ("DNT", "Object.defineProperty(Navigator.prototype,'doNotTrack',{get:function(){return '1'}});")):
        ctx, events, nav = kctx(known + sig); pg = ctx.new_page()
        buy(pg); settle(pg, events, 1, 600)
        check(not events and len(nav) == 1, f"{label}: no Klaviyo event, checkout still opens")
        ctx.close()

    # arrived from a Klaviyo email link (_kx): identified by that id, and _kx never rides to Stripe
    ctx, events, nav = kctx(); pg = ctx.new_page()
    pg.goto(base + "/?_kx=KXtest123")
    buy(pg); settle(pg, events, 1)
    check(len(events) == 1 and attrs(events[0])["profile"]["data"]["attributes"] == {"_kx": "KXtest123"} and "_kx" not in nav[0],
          "Started Checkout from a Klaviyo email visit uses _kx, not forwarded to Stripe")
    ctx.close()


def start_video_tests(b, base):
    """/start hero: the explainer video in the left column, muted/inline with a poster, the poster
    preloaded (not the video), a text version for screen readers, reduced motion keeps it still,
    and no star rating or Trustpilot score anywhere on the page."""
    import re
    ctx = context(b, base, 1280, 900); pg = ctx.new_page()
    pg.goto(base + "/start.html")
    v = pg.locator(".lphero .hero2-media video")
    check(v.count() == 1, "/start hero has 1 video in the media column")
    a = v.evaluate("v => ({muted: v.muted, inline: v.hasAttribute('playsinline'), loop: v.loop, poster: v.getAttribute('poster'), "
                   "w: v.getAttribute('width'), h: v.getAttribute('height'), pre: v.getAttribute('preload'), "
                   "desc: v.getAttribute('aria-describedby'), label: v.getAttribute('aria-label'), "
                   "srcs: [...v.querySelectorAll('source')].map(s => s.getAttribute('src'))})")
    check(a["muted"] and a["inline"] and a["loop"], "/start video is muted, playsinline and loops")
    check(bool(a["poster"]) and a["w"] == "1080" and a["h"] == "1350", "/start video has a poster and width/height")
    check(a["pre"] in ("metadata", "none"), "/start video is not fully preloaded")
    check(bool(a["label"]) and pg.locator("#" + a["desc"]).count() == 1 and "Supplement Facts" in pg.locator("#" + a["desc"]).text_content(),
          "/start video has a label and a text version")
    check(all(pg.request.get(base + u).ok for u in a["srcs"] + [a["poster"]]), "/start video sources and poster exist")
    html = pg.content()
    check(f'rel="preload" as="image" type="image/webp" href="{a["poster"]}"' in html and 'as="video"' not in html,
          "/start preloads the poster, not the video")
    check(pg.locator(".lphero .hero2-media picture").count() == 0, "/start hero photo replaced by the video")
    text = pg.locator("body").inner_text()
    check(not re.search(r"trustpilot|\u2605|\bstars?\b|\d(\.\d)? out of 5", text + html, re.I), "/start has no Trustpilot or star rating")
    ctx.close()
    # reduced motion: no autoplay, poster stays; the button can still start it
    ctx = b.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce"); pg = ctx.new_page()
    ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}"); ctx.add_init_script(NO_POPUP_JS)
    pg.goto(base + "/start.html"); pg.wait_for_timeout(600)
    st = pg.evaluate("() => {var v=document.getElementById('lp-video'); return {paused: v.paused, auto: v.hasAttribute('autoplay')}}")
    check(st["paused"] and not st["auto"], "/start video does not autoplay with reduced motion")
    check(pg.locator(".lpvid .vbtn").text_content().strip() == "Play", "/start video button offers Play when paused")
    ctx.close()


def shop_gallery_tests(b, base):
    """/corejava gallery: 6 thumb buttons (5 photos + the video), clicking or arrow keys swap the stage,
    the video has no src until chosen, never autoplays, plays from the click and pauses on leaving.
    Home and /shop lead with the pack shot (img/bag.png on a drawn backdrop); lux-still is gone."""
    ctx = context(b, base, 1280, 900); pg = ctx.new_page()
    pg.goto(base + "/corejava.html")
    thumbs = pg.locator("[data-gallery-thumbs] button.pthumb")
    slides = pg.locator("[data-gallery-stage] .pslide")
    check(thumbs.count() == 6 and slides.count() == 6, "/corejava gallery has 6 thumb buttons and 6 slides")
    vis = lambda: [i for i in range(slides.count()) if slides.nth(i).is_visible()]
    pressed = lambda: [i for i in range(thumbs.count()) if thumbs.nth(i).get_attribute("aria-pressed") == "true"]
    check(vis() == [0] and pressed() == [0], "/corejava stage starts on the first slide, first thumb pressed")
    first = slides.nth(0).locator("img")
    check("/img/opt/hero-scene-" in (first.get_attribute("src") or "") and first.get_attribute("fetchpriority") == "high"
          and first.get_attribute("loading") != "lazy", "/corejava stage leads with the eager hero scene (real bag)")
    v = pg.locator("#shop-video")
    st = v.evaluate("v => ({pre: v.getAttribute('preload'), auto: v.hasAttribute('autoplay') || v.autoplay, src: v.currentSrc, "
                    "srcs: [...v.querySelectorAll('source')].filter(s => s.getAttribute('src')).length, desc: v.getAttribute('aria-describedby'), ctl: v.controls})")
    check(st["pre"] == "none" and not st["auto"] and st["srcs"] == 0 and not st["src"] and st["ctl"],
          "/corejava video: preload none, no autoplay, no src until chosen, has controls")
    check(pg.locator("#" + st["desc"]).count() == 1 and "Supplement Facts" in pg.locator("#" + st["desc"]).text_content(),
          "/corejava video has the screen-reader text version")
    for i in range(5):
        thumbs.nth(i).click()
        check(vis() == [i] and pressed() == [i], f"/corejava thumb {i + 1} swaps the stage")
    thumbs.nth(5).click(); pg.wait_for_timeout(800)
    st = v.evaluate("v => ({paused: v.paused, src: v.currentSrc, muted: v.muted})")
    check(vis() == [5] and pressed() == [5] and "corejava-inside-v3" in st["src"], "/corejava video thumb shows the video and loads it")
    check(not st["paused"], "/corejava video plays from the click")
    thumbs.nth(0).click()
    check(v.evaluate("v => v.paused") and vis() == [0], "/corejava video pauses when another thumb is chosen")
    thumbs.nth(0).focus(); pg.keyboard.press("ArrowRight")
    check(vis() == [1] and pg.evaluate("document.activeElement.dataset.i") == "1", "/corejava ArrowRight moves to the next thumb and slide")
    pg.keyboard.press("ArrowLeft"); pg.keyboard.press("ArrowLeft")
    check(vis() == [5], "/corejava ArrowLeft wraps to the video thumb")
    check(v.evaluate("v => v.paused"), "/corejava arrow keys never start the video")
    html = pg.content()
    check("lux-still" not in html and "lux-pattern" not in html and 'imagesrcset="/img/opt/hero-scene-' in html, "/corejava preloads the hero scene; old bag renders are gone")
    ctx.close()
    # phone: swipe on the stage
    ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, reduced_motion="reduce"); pg = ctx.new_page()
    ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}"); ctx.add_init_script(NO_POPUP_JS)
    pg.goto(base + "/corejava.html")
    stage = pg.locator("[data-gallery-stage]")
    bb = stage.bounding_box()
    sw = lambda x0, x1: stage.evaluate("""(s, a) => { const y = a[2]; const mk = (t, x) => s.dispatchEvent(new PointerEvent(t, {bubbles: true, pointerType: 'touch', clientX: x, clientY: y}));
        mk('pointerdown', a[0]); mk('pointerup', a[1]); }""", [x0, x1, bb["y"] + bb["height"] / 2])
    sw(bb["x"] + 300, bb["x"] + 80)
    check(stage.get_attribute("data-current") == "1", "/corejava swipe left on the stage shows the next slide")
    sw(bb["x"] + 80, bb["x"] + 300)
    check(stage.get_attribute("data-current") == "0", "/corejava swipe right goes back")
    check(pg.locator("#shop-video").evaluate("v => v.paused && !v.autoplay"), "/corejava video does not autoplay (reduced motion)")
    ctx.close()
    # home: the real bag in the generated scene is the hero
    ctx = context(b, base, 1280, 900); pg = ctx.new_page(); pg.goto(base + "/")
    img = pg.locator(".hero2-media img")
    html = pg.content()
    check("/img/opt/hero-scene-" in (img.get_attribute("src") or "") and "lux-still" not in html
          and 'imagesrcset="/img/opt/hero-scene-' in html, "home hero is the bag scene (preloaded); lux-still is gone")
    ctx.close()


def main():
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        start_tests(b, base)
        start_video_tests(b, base)
        shop_gallery_tests(b, base)
        ia_tests(b, base)
        recipe_tests(b, base)
        guide_tests(b, base)
        notice_tests(b, base)
        quiz_tests(b, base)
        order_tests(b, base)
        house_tests(b, base)
        shop_ia_tests(b, base)
        bundle_tests(b, base)
        popup_tests(b, base)
        klaviyo_checkout_tests(b, base)
        seo_tests(b, base)
        b.close()
    print(f"\n{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
