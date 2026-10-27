#!/usr/bin/env python3
"""Monthly creator commission report (15% for life on customers a creator brought in).

How attribution works: a creator link (/c/<code>) makes the site add client_reference_id=cr_<code>
to the Stripe Payment Link. The first completed checkout carrying a creator code ties that customer
to the creator for good; every later paid order from the same customer (subscription renewals,
repeat one-time orders) earns the creator 15%.

Commission base = what the customer paid for coffee: subtotal before tax, minus shipping.
Refunds are not netted automatically; subtract them by hand if a refunded order shows up.

    STRIPE_SECRET_KEY=rk_live_... python3 tools/creator_commissions.py 2026-11
    (a restricted key with read access to Checkout Sessions, Invoices and Customers is enough)

Only needs the Python standard library.
"""
import base64
import calendar
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict

RATE = 0.15
API = "https://api.stripe.com/v1/"


def get(path, **params):
    key = os.environ["STRIPE_SECRET_KEY"]
    url = API + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": "Basic " + base64.b64encode((key + ":").encode()).decode()})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def each(path, **params):
    after = None
    while True:
        p = dict(params, limit=100)
        if after:
            p["starting_after"] = after
        page = get(path, **p)
        for obj in page["data"]:
            yield obj
        if not page.get("has_more"):
            return
        after = page["data"][-1]["id"]


def month_bounds(ym):
    y, m = map(int, ym.split("-"))
    start = dt.datetime(y, m, 1, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(days=calendar.monthrange(y, m)[1])
    return int(start.timestamp()), int(end.timestamp())


def attribute(sessions):
    """customer key -> creator code, earliest creator checkout wins. Key = Stripe customer id, else email."""
    owner = {}
    for s in sorted(sessions, key=lambda s: s["created"]):
        ref = s.get("client_reference_id") or ""
        if s.get("status") != "complete" or not ref.startswith("cr_"):
            continue
        email = ((s.get("customer_details") or {}).get("email") or "").lower()
        for k in filter(None, [s.get("customer"), email]):
            owner.setdefault(k, ref[3:])
    return owner


def report(sessions, invoices, start, end):
    owner = attribute(sessions)
    rows = defaultdict(lambda: {"orders": 0, "base": 0})
    # one-time orders: the checkout session is the order
    for s in sessions:
        if s.get("mode") != "payment" or s.get("status") != "complete" or s.get("payment_status") != "paid":
            continue
        if not (start <= s["created"] < end):
            continue
        email = ((s.get("customer_details") or {}).get("email") or "").lower()
        code = owner.get(s.get("customer")) or owner.get(email)
        if code:
            # a session's amount_subtotal is the items only: shipping and tax are added on top
            rows[code]["orders"] += 1
            rows[code]["base"] += s.get("amount_subtotal") or 0
    # subscription orders: every paid invoice (first month and renewals)
    for inv in invoices:
        if inv.get("status") != "paid" or not inv.get("amount_paid"):
            continue
        t = (inv.get("status_transitions") or {}).get("paid_at") or inv["created"]
        if not (start <= t < end):
            continue
        email = (inv.get("customer_email") or "").lower()
        code = owner.get(inv.get("customer")) or owner.get(email)
        if code:
            ship = ((inv.get("shipping_cost") or {}).get("amount_subtotal") or 0)
            rows[code]["orders"] += 1
            rows[code]["base"] += max(0, (inv.get("subtotal") or 0) - ship)
    return {c: dict(r, commission=int(r["base"] * RATE + 0.5)) for c, r in rows.items()}


def main():
    ym = sys.argv[1] if len(sys.argv) > 1 else (dt.date.today().replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    start, end = month_bounds(ym)
    sessions = list(each("checkout/sessions"))
    invoices = list(each("invoices", **{"created[gte]": start - 40 * 86400, "created[lt]": end}))
    rows = report(sessions, invoices, start, end)
    print(f"Creator commissions for {ym} ({int(RATE * 100)}% of coffee subtotal, before tax and shipping)")
    if not rows:
        print("  no creator orders this month")
    for code, r in sorted(rows.items()):
        print(f"  {code:<12} {r['orders']:>3} orders   base ${r['base'] / 100:>9.2f}   owed ${r['commission'] / 100:>8.2f}")


if __name__ == "__main__":
    main()
