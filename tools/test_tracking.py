#!/usr/bin/env python3
"""Phase T tracking tests (Playwright, local only, third-party requests blocked).

Checks: ViewContent on the product pages only; Purchase value follows ?plan=, then tmu_plan,
then 69.95; Purchase fires once per Stripe session_id and never without one; GA4 gets a standard
`purchase` with transaction_id; Buy clicks remember the plan; tmu_ut accepts the paid mediums; the first-party
funnel events for R&S HQ (lp_view, quiz_start, lead, buy_click) carry the visitor id and first touch, never an email.

    python3 tools/test_tracking.py
"""
import json
import sys
from playwright.sync_api import sync_playwright
from testlib import serve, block_third_party

FAIL = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


EVENTS_JS = """() => {
  const out = {ga: [], fb: [], tt: [], snap: []};
  (window.dataLayer || []).forEach(a => { const x = Array.from(a); if (x[0] === 'event') out.ga.push([x[1], x[2] || {}]); });
  ((window.fbq && window.fbq.queue) || []).forEach(a => { const x = Array.from(a); if (x[0] === 'track' || x[0] === 'trackCustom') out.fb.push([x[1], x[2] || {}, x[3] || {}]); });
  (Array.isArray(window.ttq) ? window.ttq : []).forEach(a => { const x = Array.from(a); if (x[0] === 'track') out.tt.push([x[1], x[2] || {}, x[3] || {}]); });
  ((window.snaptr && window.snaptr.queue) || []).forEach(a => { const x = Array.from(a); if (x[0] === 'track') out.snap.push([x[1], x[2] || {}]); });
  return out;
}"""


def events(page):
    page.wait_for_load_state("domcontentloaded")
    return page.evaluate(EVENTS_JS)


def names(evts, key):
    return [e[0] for e in evts[key]]


COLLECT = "https://dashboard.rectorandstull.com/collect/tmu"


def first_party_tests(b, base):
    """tmuEvent beacons to R&S HQ: what each step sends, the first touch, and that no email ever leaves."""
    def ctx_with(popup=False):
        sent, kl = [], []
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}")
        if not popup:
            ctx.add_init_script("try{if(!localStorage.getItem('tmu_pop'))localStorage.setItem('tmu_pop',JSON.stringify({s:'closed',t:Date.now()}))}catch(e){}")

        def route(r):
            u = r.request.url
            if u.startswith(base):
                return r.continue_()
            if u == COLLECT and r.request.method == "POST":
                sent.append({"body": json.loads(r.request.post_data or "{}"),
                             "ctype": r.request.headers.get("content-type", "")})
                return r.fulfill(status=204, headers={"Access-Control-Allow-Origin": "*"})
            if u.startswith("https://a.klaviyo.com/client/subscriptions/"):
                kl.append(1)
                return r.fulfill(status=202, body="")
            return r.abort()
        ctx.route("**/*", route)
        return ctx, sent

    def wait(pg, sent, n, ms=3000):
        for _ in range(ms // 50):
            if len(sent) >= n:
                return
            pg.wait_for_timeout(50)

    def named(sent, name):
        return [x["body"] for x in sent if x["body"].get("name") == name]

    # landing from an organic link with a Google click id: lp_view with the visitor id and the first touch
    ctx, sent = ctx_with(); pg = ctx.new_page()
    pg.goto(base + "/start.html?utm_source=tiktok&utm_medium=organic&utm_campaign=bio&utm_content=pin1&gclid=G123&fbclid=F1")
    wait(pg, sent, 1)
    lv = named(sent, "lp_view")
    ft = lv[0]["ft"] if lv else {}
    vid = lv[0]["vid"] if lv else ""
    check(len(lv) == 1 and lv[0]["path"] == "/start.html" and lv[0]["detail"] is None, "lp_view on page load")
    check(bool(__import__("re").fullmatch(r"[a-z0-9]{8,40}", vid or "")) and ("tmu_vid=" + vid) in pg.evaluate("() => document.cookie"),
          f"anonymous visitor id in the tmu_vid cookie ({vid})")
    check((ft.get("utm_source"), ft.get("utm_medium"), ft.get("utm_campaign"), ft.get("utm_content"), ft.get("click_type"), ft.get("click_id"))
          == ("tiktok", "organic", "bio", "pin1", "gclid", "G123"), f"first touch: utm tags of any medium + click id ({ft})")
    check(pg.evaluate("() => localStorage.getItem('tmu_ut')") is None, "organic visit still sets no Stripe ut__ tag")
    check(all(x["ctype"].startswith("text/plain") for x in sent), "beacons go as text/plain (no CORS preflight)")
    # next page, no tags: same visitor, same first touch
    pg.goto(base + "/shop.html?utm_source=meta&utm_medium=paid&utm_campaign=later")
    wait(pg, sent, 2)
    lv = named(sent, "lp_view")
    check(len(lv) == 2 and lv[1]["vid"] == vid and lv[1]["ft"] == ft, "first touch never overwritten, same visitor id")
    check(pg.evaluate("() => !!localStorage.getItem('tmu_ut')"), "a later paid visit still sets the 30-day Stripe tag")
    # Buy clicks: checkout and plan
    pg.evaluate("() => document.addEventListener('click', e => e.preventDefault())")
    pg.locator("main a[data-buy='subscribe']").first.dispatch_event("click")
    pg.locator("main a[data-buy='onetime']").first.dispatch_event("click")
    wait(pg, sent, 4)
    check([x["detail"] for x in named(sent, "buy_click")] == ["stripe:subscribe", "stripe:onetime"], "buy_click: stripe + plan")
    # the newsletter capture on /start
    pg.goto(base + "/start.html")
    n0 = len(sent)
    f = pg.locator("form[data-capture]").first
    f.locator("input[type=email]").fill("reader@example.com")
    f.locator("button[type=submit]").click()
    pg.wait_for_url("**/thanks.html*")
    wait(pg, sent, n0 + 3)
    check([x["detail"] for x in named(sent, "lead")] == ["newsletter"], "lead: newsletter capture")
    ctx.close()

    # the quiz on the home page: quiz_start once, lead quiz
    ctx, sent = ctx_with(); pg = ctx.new_page()
    pg.goto(base + "/")
    wait(pg, sent, 1)
    pg.locator('.quiz .q[data-q="1"] .opt').first.click()
    pg.locator('.quiz .q[data-q="2"] .opt').first.click()
    pg.locator('.quiz .q[data-q="3"] .opt').first.click()
    pg.fill("#q-email", "quiz@example.com"); pg.click("#tmu-form button[type=submit]")
    pg.wait_for_selector("#tmu-done:not([hidden])")
    wait(pg, sent, 3)
    check(len(named(sent, "quiz_start")) == 1, "quiz_start once, on the first answer")
    check([x["detail"] for x in named(sent, "lead")] == ["quiz"], "lead: quiz")
    ctx.close()

    # the email pop-up: lead popup, then its Subscribe & Save button is a buy_click
    ctx, sent = ctx_with(popup=True); pg = ctx.new_page(); pg.clock.install()
    pg.goto(base + "/shop.html"); pg.clock.run_for(11000); pg.wait_for_timeout(50)
    pg.fill("#tp-email", "pop@example.com"); pg.click(".tp-form button[type=submit]")
    pg.wait_for_selector('.tmu-pop [data-step="done"]:not([hidden])')
    pg.evaluate("() => document.addEventListener('click', e => e.preventDefault())")
    pg.locator(".tmu-pop .tp-use").dispatch_event("click")
    pg.clock.run_for(500)
    wait(pg, sent, 3)
    check([x["detail"] for x in named(sent, "lead")] == ["popup"], "lead: pop-up")
    check([x["detail"] for x in named(sent, "buy_click")] == ["stripe:subscribe"], "pop-up Subscribe & Save: buy_click")
    allsent = json.dumps([x["body"] for x in sent])
    check("@" not in allsent and "example.com" not in allsent, "no email in any beacon")
    ctx.close()

    # MPG hand-off mode (no Stripe links): buy_click says mpg
    ctx, sent = ctx_with(); ctx.add_init_script("Object.defineProperty(window,'TMU',{configurable:true,set(v){v.STRIPE_ONETIME='';v.STRIPE_SUBSCRIBE='';Object.defineProperty(window,'TMU',{value:v,writable:true,configurable:true});},get(){return undefined;}})")
    pg = ctx.new_page(); pg.goto(base + "/shop.html")
    pg.evaluate("() => document.addEventListener('click', e => e.preventDefault())")
    pg.locator("main a[data-buy='onetime']").first.dispatch_event("click")
    wait(pg, sent, 2)
    check([x["detail"] for x in named(sent, "buy_click")] == ["mpg:onetime"], "buy_click: mpg in hand-off mode")
    ctx.close()


def main():
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()

        def fresh():
            ctx = b.new_context()
            block_third_party(ctx, base)
            ctx.add_init_script("try{localStorage.setItem('tmu_pop',JSON.stringify({s:'closed',t:Date.now()}))}catch(e){}")   # email pop-up off here
            return ctx, ctx.new_page()

        # 1. ViewContent on home/shop/start for the ad pixels, not on other pages, not to GA4
        for path, want in [("/", True), ("/index.html", True), ("/shop.html", True), ("/start.html", True),
                           ("/start?utm_source=tiktok", True), ("/shop", True), ("/faq", False),
                           ("/faq.html", False), ("/what-is-mct-coffee.html", False)]:
            ctx, pg = fresh(); pg.goto(base + path); e = events(pg)
            got = ("ViewContent" in names(e, "fb"), "ViewContent" in names(e, "tt"), "VIEW_CONTENT" in names(e, "snap"))
            check(got == (want,) * 3, f"ViewContent on {path}: {want} (meta/tiktok/snap = {got})")
            check("ViewContent" not in names(e, "ga"), f"no GA4 ViewContent custom event on {path}")
            ctx.close()

        # 2. Purchase value and dedupe
        cases = [("?session_id=cs_test_a1b2c3d4&plan=onetime", None, 79.95),
                 ("?session_id=cs_test_a1b2c3d5&plan=subscribe", "onetime", 69.95),
                 ("?session_id=cs_test_a1b2c3d6", "onetime", 79.95),
                 ("?session_id=cs_test_a1b2c3d7", "subscribe", 69.95),
                 ("?session_id=cs_test_a1b2c3d8", None, 69.95),
                 ("?session_id=cs_test_a1b2c3d9&plan=bogus", None, 69.95),
                 ("?session_id=cs_test_a1b2c3e1&plan=cupofjoe", None, 27.95),     # house coffees
                 ("?session_id=cs_test_a1b2c3e2&plan=mushroom", "onetime", 33.95)]
        SKUS = {27.95: "TMU-CUPOFJOE-12", 33.95: "TMU-MUSHROOM-12"}
        for qs, stored, value in cases:
            ctx, pg = fresh()
            pg.goto(base + "/shop.html")
            pg.evaluate("s => { localStorage.clear(); if (s) localStorage.setItem('tmu_plan', s); }", stored)
            pg.goto(base + "/order-complete.html" + qs); e = events(pg)
            sid = qs.split("session_id=")[1].split("&")[0]
            ga_p = [x for x in e["ga"] if x[0] == "purchase"]
            fb_p = [x for x in e["fb"] if x[0] == "Purchase"]
            tt_p = [x for x in e["tt"] if x[0] == "CompletePayment"]
            sn_p = [x for x in e["snap"] if x[0] == "PURCHASE"]
            ads = [x for x in e["ga"] if x[0] == "conversion"]
            label = f"{qs} stored={stored}"
            check(len(ga_p) == 1 and ga_p[0][1].get("value") == value and ga_p[0][1].get("transaction_id") == sid
                  and ga_p[0][1].get("items", [{}])[0].get("item_id") == SKUS.get(value, "CL805"), f"GA4 purchase {value} once, transaction_id=session_id ({label})")
            check(len(fb_p) == 1 and fb_p[0][1].get("value") == value and fb_p[0][2].get("eventID") == sid, f"Meta Purchase {value} with eventID ({label})")
            check(len(tt_p) == 1 and tt_p[0][1].get("value") == value and tt_p[0][2].get("event_id") == sid, f"TikTok CompletePayment {value} with event_id ({label})")
            check(len(sn_p) == 1 and sn_p[0][1].get("price") == value and sn_p[0][1].get("transaction_id") == sid, f"Snap PURCHASE {value} ({label})")
            check(len(ads) == 1 and ads[0][1].get("value") == value and ads[0][1].get("transaction_id") == sid, f"Google Ads conversion {value} ({label})")
            # refresh: nothing fires again
            pg.reload(); e2 = events(pg)
            again = [x for x in e2["ga"] if x[0] in ("purchase", "Purchase", "conversion")] + [x for x in e2["fb"] if x[0] == "Purchase"]
            check(not again, f"refresh does not re-fire Purchase ({label})")
            ctx.close()

        for qs in ["", "?plan=onetime", "?session_id=%7BCHECKOUT_SESSION_ID%7D"]:
            ctx, pg = fresh(); pg.goto(base + "/order-complete.html" + qs); e = events(pg)
            check(not [x for x in e["fb"] if x[0] == "Purchase"] and not [x for x in e["ga"] if x[0] in ("purchase", "Purchase")],
                  f"no Purchase without a Stripe session_id ({qs or 'no query'})")
            ctx.close()

        # 3. Buy clicks remember the plan; wire() still points at Stripe
        ctx, pg = fresh(); pg.goto(base + "/shop.html")
        pg.evaluate("() => document.addEventListener('click', e => e.preventDefault())")
        for kind in ("onetime", "subscribe"):
            a = pg.locator(f"main a[data-buy='{kind}']").first
            href = a.get_attribute("href") or ""
            check(href.startswith("https://buy.stripe.com/"), f"{kind} button still links to Stripe")
            a.dispatch_event("click")
            check(pg.evaluate("() => localStorage.getItem('tmu_plan')") == kind, f"click on {kind} sets tmu_plan={kind}")
            e = events(pg)
            ic = [x for x in e["fb"] if x[0] == "InitiateCheckout"]
            check(bool(ic) and ic[-1][1].get("value") == {"onetime": 79.95, "subscribe": 69.95}[kind], f"InitiateCheckout carries value for {kind}")
        ctx.close()

        # 4. tmu_ut accepts the paid mediums, ignores organic
        for med, want in [("paid", True), ("cpc", True), ("ppc", True), ("paid_social", True), ("social_paid", True), ("organic", False), ("", False)]:
            ctx, pg = fresh()
            pg.goto(base + f"/start.html?utm_source=tiktok&utm_medium={med}&utm_campaign=tt_test&utm_content=ritual_a")
            ut = pg.evaluate("() => localStorage.getItem('tmu_ut')")
            check(bool(ut) == want, f"tmu_ut stored for utm_medium={med or '(none)'}: {want}")
            ctx.close()
        # 5. Stripe links carry the page's utm tags once, and nothing else from the landing URL
        ctx, pg = fresh()
        pg.goto(base + "/shop.html?utm_source=tiktok&utm_medium=paid&utm_campaign=c1&client_reference_id=cr_evil&prefilled_promo_code=X&ttclid=T1")
        href = pg.locator("main a[data-buy='subscribe']").first.get_attribute("href") or ""
        qs = __import__("urllib.parse").parse.parse_qs(href.split("?", 1)[1])
        check(qs.get("utm_source") == ["tiktok"] and qs.get("utm_campaign") == ["c1"], f"Stripe link has the page's utm_source once ({qs.get('utm_source')})")
        check(qs.get("client_reference_id") == ["ut__tiktok__c1__"] and "prefilled_promo_code" not in qs and "ttclid" not in qs,
              f"landing URL can't inject Stripe params ({qs.get('client_reference_id')})")
        pg.goto(base + "/faq.html")
        href = pg.locator("a[data-buy]").first.get_attribute("href") or ""
        check("utm_source=site" in href, "no utm on the page: Stripe gets utm_source=site")
        ctx.close()

        # 6. Creator links keep the visitor's ad tags and click ids, and the creator code can't be swapped
        ctx, pg = fresh()
        pg.goto(base + "/c/kasey/?utm_source=tiktok&utm_medium=paid&utm_campaign=spark&ttclid=TT1&ref=macy")
        pg.wait_for_url("**/start.html*")
        u = pg.url
        check("ref=kasey" in u and "ttclid=TT1" in u and "utm_medium=paid" in u and "macy" not in u, f"creator redirect keeps ad params ({u.split('?')[1]})")
        href = pg.locator("main a[data-buy]").first.get_attribute("href") or ""
        check("client_reference_id=cr_kasey" in href, "creator still credited after a paid creator link")
        pg.goto(base + "/c/kasey/")
        pg.wait_for_url("**/start.html*")
        check(pg.url.endswith("/start.html?ref=kasey&utm_source=creator&utm_medium=influencer&utm_campaign=kasey"), "plain creator link lands as before")
        ctx.close()
        first_party_tests(b, base)
        b.close()
    print(f"\n{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
