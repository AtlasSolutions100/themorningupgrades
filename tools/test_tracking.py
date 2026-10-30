#!/usr/bin/env python3
"""Phase T tracking tests (Playwright, local only, third-party requests blocked).

Checks: ViewContent on the product pages only; Purchase value follows ?plan=, then tmu_plan,
then 69.95; Purchase fires once per Stripe session_id and never without one; GA4 gets a standard
`purchase` with transaction_id; Buy clicks remember the plan; tmu_ut accepts the paid mediums.

    python3 tools/test_tracking.py
"""
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


def main():
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()

        def fresh():
            ctx = b.new_context()
            block_third_party(ctx, base)
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
                 ("?session_id=cs_test_a1b2c3d9&plan=bogus", None, 69.95)]
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
                  and ga_p[0][1].get("items", [{}])[0].get("item_id") == "CL805", f"GA4 purchase {value} once, transaction_id=session_id ({label})")
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
        b.close()
    print(f"\n{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
