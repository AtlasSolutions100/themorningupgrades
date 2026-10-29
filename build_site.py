#!/usr/bin/env python3
"""Builds the themorningupgrades.com pages from shared chrome. Run: python3 build_site.py"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))

NAV = """
<nav class="nav" aria-label="Main"><div class="wrap">
  <a class="brand" href="/"><img src="/img/mark.jpg" alt=""><b>The Morning Upgrade</b></a>
  <button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu">Menu</button>
  <div class="menu" id="menu">
    <a href="/shop.html">Shop</a>
    <a href="/ingredients.html">Ingredients</a>
    <a href="/start.html">7-day swap</a>
    <a href="/faq.html">FAQ</a>
    <a href="/share.html">Share &amp; earn</a>
    <a class="btn sm" href="/shop.html">Get CoreJava</a>
  </div>
</div></nav>
"""

FOOTER = """
<footer aria-label="Footer"><div class="wrap">
  <div class="cols">
    <div>
      <h2 class="fh">The Morning Upgrade</h2>
      <p>Instant coffee with MCT powder, natural caffeine and L-theanine. One scoop, hot water, 30 servings a bag. Sold by Rector &amp; Stull LLC, Independent ISR of MarketPlace Global products and services.</p>
      <p>hello@themorningupgrades.com</p>
    </div>
    <div>
      <h2 class="fh">Shop</h2>
      <a href="/shop.html">CoreJava coffee</a>
      <a href="/ingredients.html">What's in it</a>
      <a href="/faq.html">Questions</a>
      <a href="/shipping-returns.html">Shipping &amp; returns</a>
      <a href="/guides.html">Guides &amp; recipes</a>
      <a href="https://billing.stripe.com/p/login/3cIbJ3fEv6XIbtk8iw4wM00" rel="noopener">Manage subscription</a>
    </div>
    <div>
      <h2 class="fh">Company</h2>
      <a href="/about.html">About us</a>
      <a href="/share.html">Share &amp; earn</a>
      <a href="/partner.html">Build with us</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/terms.html">Terms</a>
    </div>
  </div>
  <p>These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease. Consult a physician before use if you are pregnant, nursing, taking medication, or have a medical condition. Contains caffeine.</p>
  <p>CoreJava is a product of MarketPlace Global. Rector &amp; Stull LLC is an Independent Sales Representative (ISR) of MarketPlace Global, not the manufacturer, and not MarketPlace Global itself. We earn income on the products we sell and on sales made by partners we introduce.</p>
  <p>&copy; <span class="yr"></span> Rector &amp; Stull LLC &middot; 30 N Gould St Ste R, Sheridan, WY 82801</p>
</div></footer>
"""

SITE = "https://themorningupgrades.com"
# Bing Webmaster Tools: paste the content="..." value of its msvalidate.01 meta tag here and
# rebuild. Empty = no tag. (Bing can also import the site from Google Search Console.)
BING_VERIFICATION = ""
import json as _json, html as _html

def url_for(fn):
    return SITE + "/" if fn == "index.html" else f"{SITE}/{fn}"

def _strip(h):
    return _html.unescape(re.sub(r"<[^>]+>", "", h)).strip()

# Questions left out of FAQ rich results on purpose: the label claim, the AI
# presenters, and the one that names the maker stay on the page but aren't
# promoted as search snippets. Search-facing text (titles, descriptions,
# structured data) never uses the product or company trademark names.
FAQ_SKIP = {"What does it do?", "Who are the people in your videos?", "Who am I buying from?"}

# Answer-style guides: (published, modified). Guides get Article + FAQPage
# markup from their visible questions, and og:type article.
GUIDE_META = {
    "what-is-mct-coffee.html": ("2026-10-28", "2026-10-28"),
    "how-to-make-mct-instant-coffee.html": ("2026-10-28", "2026-10-28"),
    "l-theanine-and-caffeine.html": ("2026-10-25", "2026-10-28"),
    "mct-coffee-vs-butter-coffee.html": ("2026-10-25", "2026-10-28"),
    "iced-instant-coffee-recipes.html": ("2026-10-25", "2026-10-25"),
}

# The one product, as the shop page states it. Named descriptively: search-facing
# text stays free of the maker's trademarks (see note above FAQ_SKIP). No rating markup
# until the page shows real, attributable customer feedback.
def product_ld():
    ship = {"@type": "OfferShippingDetails",
            "shippingRate": {"@type": "MonetaryAmount", "value": "8.95", "currency": "USD"},
            "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "US"},
            "deliveryTime": {"@type": "ShippingDeliveryTime",
                             "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 2, "unitCode": "DAY"},
                             "transitTime": {"@type": "QuantitativeValue", "minValue": 3, "maxValue": 6, "unitCode": "DAY"}}}
    returns = {"@type": "MerchantReturnPolicy", "applicableCountry": "US",
               "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 90,
               "returnMethod": "https://schema.org/ReturnByMail", "returnFees": "https://schema.org/ReturnShippingFees",
               "itemCondition": "https://schema.org/NewCondition"}
    def offer(name, price, extra=None):
        o = {"@type": "Offer", "name": name, "price": price, "priceCurrency": "USD",
             "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition",
             "url": SITE + "/shop.html", "seller": {"@id": SITE + "/#org"},
             "shippingDetails": ship, "hasMerchantReturnPolicy": returns}
        o.update(extra or {})
        return o
    return {"@type": "Product", "@id": SITE + "/shop.html#product",
            "name": "MCT Instant Coffee with L-Theanine, 30 Servings",
            "description": "Medium-roast instant coffee with MCT powder from coconut, natural caffeine and L-theanine. "
                           "One level scoop (about 6.8 g) in 8 fl oz of hot water. 30 servings per 7.2 oz (204 g) bag. Contains caffeine.",
            "image": [SITE + "/img/hero_breakfast.jpg", SITE + "/img/flatlay.jpg", SITE + "/img/scoop.jpg"],
            "category": "Instant coffee",
            "weight": {"@type": "QuantitativeValue", "value": 204, "unitCode": "GRM"},
            "offers": [offer("One bag (30 servings)", "79.95"),
                       offer("Subscribe & Save: one bag every 30 days", "69.95",
                             {"priceSpecification": {"@type": "UnitPriceSpecification", "price": "69.95", "priceCurrency": "USD",
                                                     "billingDuration": {"@type": "QuantitativeValue", "value": 30, "unitCode": "DAY"}}})]}

def structured_data(fn, title, desc, body, og_image):
    org = {"@type": "Organization", "@id": SITE + "/#org", "name": "The Morning Upgrade",
           "legalName": "Rector & Stull LLC", "url": SITE + "/", "logo": SITE + "/img/mark.jpg",
           "email": "hello@themorningupgrades.com",
           "sameAs": ["https://www.tiktok.com/@themorningupgrade", "https://www.instagram.com/themorningupgrade/",
                      "https://www.youtube.com/@themorningupgrade"],
           "address": {"@type": "PostalAddress", "streetAddress": "30 N Gould St Ste R", "addressLocality": "Sheridan",
                       "addressRegion": "WY", "postalCode": "82801", "addressCountry": "US"}}
    graph = [org]
    if fn == "index.html":
        graph.append({"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "The Morning Upgrade",
                      "description": "Instant coffee with MCT powder, natural caffeine and L-theanine, plus plain-language guides.",
                      "inLanguage": "en-US", "publisher": {"@id": SITE + "/#org"}})
    if fn == "shop.html":
        graph.append(product_ld())
    if fn in GUIDE_META:
        pub, mod = GUIDE_META[fn]
        graph.append({"@type": "Article", "@id": url_for(fn) + "#article", "headline": title.split(" | ")[0],
                      "description": desc, "url": url_for(fn), "mainEntityOfPage": url_for(fn),
                      "image": SITE + og_image, "datePublished": pub, "dateModified": mod, "inLanguage": "en-US",
                      "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"}})
    qa = re.findall(r"<details><summary>(.*?)</summary>(.*?)</details>", body, re.S)
    qa = [(_strip(q), _strip(a)) for q, a in qa if _strip(q) not in FAQ_SKIP]
    qa = [(q, a) for q, a in qa if not re.search(r"corejava|marketplace\s*global|\bmpg\b", q + " " + a, re.I)]
    if (fn == "faq.html" or fn in GUIDE_META) and qa:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                      "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    if fn != "index.html":
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": title.split(" — ")[0].split(" | ")[0], "item": url_for(fn)}]})
    return '<script type="application/ld+json">' + _json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")) + "</script>"

def sticky_bar(mode):
    """buy = checkout for the picked plan (follows the picker); shop = a plain link to the shop
    page (guides, 404: a searcher shouldn't land in Stripe for a product they haven't seen)."""
    if mode == "buy":
        return f'<aside class="sticky" aria-label="Quick buy"><div><b>CoreJava &middot; 30 servings</b><span data-sticky-price>{PLAN_STICKY["subscribe"]}</span></div><a class="btn" data-buy="subscribe" href="#">Checkout</a></aside>'
    if mode == "shop":
        return '<aside class="sticky" aria-label="See the coffee"><div><b>Our instant MCT coffee</b><span>30 servings &middot; from $69.95/mo</span></div><a class="btn" href="/shop.html">See the coffee &rarr;</a></aside>'
    return ""

def page(title, desc, body, og_image="/img/flatlay.jpg", noindex=False, extra_head="", nav=True, fn="index.html", sticky="buy"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="icon" href="/img/mark.jpg">
<link rel="apple-touch-icon" href="/img/mark.jpg">
{'' if noindex else f'<link rel="canonical" href="{url_for(fn)}">'}
<meta name="theme-color" content="#1b130e">
{'<meta name="google-site-verification" content="7jyn0E7TYq9A_Ug0PhqrwoI0ssqQj0Z9mrlBYkPK4dw"><meta name="facebook-domain-verification" content="fplr4vshxvflcgysu4cu6j0cpwtbco">' if fn == "index.html" else ''}{f'<meta name="msvalidate.01" content="{BING_VERIFICATION}">' if fn == "index.html" and BING_VERIFICATION else ''}
<meta property="og:type" content="{'article' if fn in GUIDE_META else 'website'}">
<meta property="og:site_name" content="The Morning Upgrade">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{url_for(fn)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://themorningupgrades.com{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://themorningupgrades.com{og_image}">
{'' if noindex else structured_data(fn, title, desc, body, og_image)}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js"></script>
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{NAV if nav is True else (MINI_NAV if nav == 'mini' else '')}
<main id="main">
{body}
</main>
{FOOTER}
{sticky_bar(sticky)}
</body>
</html>
"""

BENEFITS = """
<div class="marq"><div>
  <span>Smooth energy</span><span>Sharp focus</span><span>Creamy without the cream</span><span>Tastes like coffee</span><span>Ready in 30 seconds</span><span>30 mornings a bag</span>
  <span>Smooth energy</span><span>Sharp focus</span><span>Creamy without the cream</span><span>Tastes like coffee</span><span>Ready in 30 seconds</span><span>30 mornings a bag</span>
</div></div>
"""
CTA_BLOCK = """
<div class="ctab"><a class="btn" data-buy="subscribe" href="#">Subscribe &amp; Save &mdash; $69.95/mo</a><a class="btn ghost" data-buy="onetime" href="#">One bag &mdash; $79.95</a><p class="fine"><span data-ship="short">Ships to all 50 states</span> &middot; cancel anytime &middot; <span data-ship="checkout">secure checkout</span></p></div>
"""
COMPARE = """
<section><div class="wrap">
  <h2 style="text-align:center">The math on a month of mornings</h2>
  <p style="text-align:center;color:var(--muted);margin:0 0 26px">Same 30 mornings. Three ways to buy them.</p>
  <div class="cmp">
    <div class="cmp-h"><span></span><span>Caf&eacute; latte</span><span>Drip + second cup</span><span class="hl">CoreJava</span></div>
    <div><span>Per morning</span><span>$5&ndash;7</span><span>$1&ndash;2, twice</span><span class="hl">$2.33&ndash;2.67</span></div>
    <div><span>Per month</span><span>$150&ndash;210</span><span>$60&ndash;120</span><span class="hl">$69.95&ndash;79.95</span></div>
    <div><span>Time</span><span>A line and a drive</span><span>Grind, brew, clean</span><span class="hl">30 seconds</span></div>
    <div><span>What's in it</span><span>Caffeine, sugar, milk</span><span>Caffeine</span><span class="hl">Caffeine + L-theanine + 5 more</span></div>
  </div>
  <p class="fine" style="text-align:center;margin-top:14px">Caf&eacute; and drip costs are typical US prices; yours will vary. CoreJava prices are ours, before shipping and tax.</p>
</div></section>
"""
FOUNDER = """
<section class="alt"><div class="wrap split">
  <div class="frame p45"><img src="/img/desk.jpg" alt="Laptop, mug and a bag of CoreJava on a desk" loading="lazy"></div>
  <div>
    <p class="eyebrow">A note from the two of us</p>
    <h2>We're new. Here's who you're buying from.</h2>
    <p>We're Rector &amp; Stull, two partners, one in Idaho and one in Texas, both of whom run on coffee and spend afternoons on calls. We drank CoreJava for a while before we decided to sell it. The reason is simple: it's the cup we kept making.</p>
    <p>We're new, so there's no wall of star ratings here yet. We have a bag we drink every morning, a label we quote instead of embellish, and an email a real person answers. If it's not for you, say so and we'll make it right.</p>
    <p style="font-family:Helvetica,Arial,sans-serif;font-size:14px;color:var(--muted)">&mdash; Koby &amp; the Rector &amp; Stull team &middot; hello@themorningupgrades.com</p>
  </div>
</div></section>
"""


ICON_TRUCK = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="17" r="1.6"/><circle cx="17" cy="17" r="1.6"/></svg>'
ICON_SHIELD = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg>'
ICON_LOOP = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12a8 8 0 0 1-14.5 4.6M4 12a8 8 0 0 1 14.5-4.6"/><path d="M20 4v4h-4M4 20v-4h4"/></svg>'
ICON_LOCK = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'
ICON_SCOOP = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a6 6 0 0 0 12 0v-2H4z"/><path d="M16 12l5-6"/></svg>'
ICON_LEAF = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19C5 9 11 4 20 4c0 9-5 15-15 15z"/><path d="M5 19l8-8"/></svg>'
ICON_COCO = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><path d="M12 4v4M4 12h4"/></svg>'

ICON_BEAN = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 6.5a7 7 0 0 1 11 11 7 7 0 0 1-11-11z"/><path d="M8 16c3-1 4-4 4-8 0-1.5.5-3 1.5-4"/></svg>'
ICON_BAG = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 4h10l1 4H6z"/><path d="M6 8v11a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V8"/><path d="M9 13h6"/></svg>'
ICON_GLOBE = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>'

def trust_row(dark=False):
    return f"""<div class="trustbar{' on-dark' if dark else ''}">
  <span>{ICON_TRUCK}<span><b>Ships from Minnesota</b><i>in 2 business days</i></span></span>
  <span>{ICON_LOCK}<span><b data-ship="checkout">Secure checkout</b><i>90-day guarantee on unopened bags</i></span></span>
  <span>{ICON_GLOBE}<span><b>Made by MarketPlace Global</b><i>sold by Rector &amp; Stull, an independent ISR</i></span></span>
</div>"""

_PICKERS = [0]
PLAN_CTA = {"subscribe": "Checkout &mdash; $69.95/mo", "onetime": "Checkout &mdash; $79.95"}
PLAN_STICKY = {"subscribe": "$69.95/mo &middot; $2.33 a morning", "onetime": "$79.95 one bag &middot; $2.67 a morning"}
SHIP_NOTE = "+ shipping &amp; tax at checkout"

def picker(note=True):
    _PICKERS[0] += 1
    name = f"plan{_PICKERS[0]}"
    return f"""<fieldset class="picker" data-picker><legend class="sr">Choose a plan</legend>
  <label class="opt on"><input type="radio" name="{name}" value="subscribe" checked data-cta="{_html.unescape(PLAN_CTA['subscribe'])}" data-sticky="{_html.unescape(PLAN_STICKY['subscribe'])}"><span class="radio"></span>
    <span class="ptxt"><em>Best value &middot; $10 off every bag</em><b>Subscribe &amp; Save</b><span class="pp">$69.95<small>/mo &middot; $2.33 a morning</small></span><span class="pfine">A bag every 30 days. Pause, skip or cancel from your receipt.</span></span></label>
  <label class="opt"><input type="radio" name="{name}" value="onetime" data-cta="{_html.unescape(PLAN_CTA['onetime'])}" data-sticky="{_html.unescape(PLAN_STICKY['onetime'])}"><span class="radio"></span>
    <span class="ptxt"><b>One bag</b><span class="pp">$79.95<small> &middot; $2.67 a morning</small></span><span class="pfine">30 servings. No commitment.</span></span></label>
  <a class="btn big" data-buy="subscribe" data-picker-btn href="#"><span data-cta>{PLAN_CTA['subscribe']}</span> <span aria-hidden="true">&rarr;</span></a>
  {f'<p class="fine pnote">{SHIP_NOTE} &middot; 90-day guarantee on unopened bags &middot; pause or cancel anytime</p>' if note else ''}
</fieldset>"""

INGCARDS = f"""<div class="ingcards">
  <div>{ICON_COCO}<div><h2>MCT powder</h2><p>The creamy part. From coconut, and the first thing on the label.</p></div></div>
  <div>{ICON_LEAF}<div><h2>Natural caffeine + L-theanine</h2><p>Coffee-bean caffeine with the amino acid in green tea. Focus without the edge.</p></div></div>
  <div>{ICON_SCOOP}<div><h2>30 servings. One scoop.</h2><p>Hot water, 30 seconds, no machine. A month of mornings in one bag.</p></div></div>
</div>"""

CALLOUTS = f"""<div class="callouts-wrap">
  <div class="bagstage">
    <img src="/img/hero_props.png" width="1300" height="1300" alt="CoreJava bag with coconut, MCT powder, coffee beans, green tea leaves and matcha" fetchpriority="high" decoding="async">
    <svg class="leads" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      <path d="M24 30 L27 30 L30 65.5" /><circle cx="30.2" cy="67.5" r="1"/>
      <path d="M76 30 L73 30 L72.4 61" /><circle cx="72.3" cy="63" r="1"/>
      <path d="M24 88 L27 88 L42 85.7" /><circle cx="43.5" cy="85.4" r="1"/>
      <path d="M76 92 L73 92 L56.6 79.8" /><circle cx="55.4" cy="78.8" r="1"/>
    </svg>
    <span class="chip c1"><i>{ICON_COCO}</i><span><b>MCT powder</b>the creamy part</span></span>
    <span class="chip c2"><i>{ICON_LEAF}</i><span><b>L-theanine</b>focus without the edge</span></span>
    <span class="chip c3"><i>{ICON_BEAN}</i><span><b>Natural caffeine</b>about one cup's worth</span></span>
    <span class="chip c4"><i>{ICON_BAG}</i><span><b>30 servings</b>one scoop a morning</span></span>
  </div>
</div>"""

def hero_c(h1="One scoop. Steady energy, sharp focus.", strip=("Steady energy","Sharp focus","30 mornings a bag"), video=True, variants=False):
    striphtml = " <i>/</i> ".join(f"<span>{t}</span>" for t in strip)
    pick = ""
    if variants:
        pick = ("<script>(function(){var V=" + _json.dumps({k: [h, list(st)] for k, (h, st) in LANDING_VARIANTS.items()}, ensure_ascii=False)
                + ";var c='';try{c=(new URLSearchParams(location.search).get('utm_content')||'').toLowerCase().split(/[_\\-.]/)[0];}catch(e){}"
                + "var v=V[c];if(!v)return;var h=document.getElementById('lp-h1'),st=document.getElementById('lp-strip');h.textContent=v[0];"
                + "st.querySelectorAll('span:not(.rule)').forEach(function(e,i){if(v[1][i])e.textContent=v[1][i];});"
                + "document.documentElement.setAttribute('data-variant',c);})();</script>")
    return f"""
<div class="heroC"><div class="wrap">
  <h1 class="h1c{' lp' if variants else ''}" id="lp-h1">{h1}</h1>
  <p class="stripc" id="lp-strip"><span class="rule"></span>{striphtml}<span class="rule"></span></p>{pick}
  <div class="heroC-grid">
    <div class="heroC-left">{CALLOUTS}</div>
    <div class="heroC-right">
      <p class="sr">CoreJava instant coffee: natural caffeine, L-theanine and MCT powder. One scoop, hot water, 30 seconds. Made for a focused, steady morning.</p>
      {picker()}
    </div>
  </div>
  {trust_row(dark=False)}
</div></div>
"""

# ---------- HOME ----------
HOME = """
""" + hero_c() + """
"""+"""

<section class="alt"><div class="wrap">
  <h2>Three mornings, three problems</h2>
  <div class="grid3">
    <div class="card"><h3>The 2pm slide</h3><p>A big cup hits fast and leaves fast. By the afternoon meeting your focus has gone home without you.</p></div>
    <div class="card"><h3>The second-cup habit</h3><p>So you pour another, then another. The coffee is running the schedule instead of the other way round.</p></div>
    <div class="card"><h3>The $6 habit</h3><p>A latte on the way in, a cold brew after lunch. Two stops, two lines, twelve dollars.</p></div>
  </div>
</div></section>

<section><div class="wrap split">
  <div class="frame phone"><video muted loop playsinline preload="metadata" data-autoplay poster="/media/ritual.jpg"><source src="/media/ritual.mp4" type="video/mp4"></video></div>
  <div>
    <p class="eyebrow">How it works</p>
    <h2>One scoop. Hot water. That's the whole ritual.</h2>
    <ul class="clean">
      <li>One level scoop into 8 oz of hot water, stir. No machine, no grounds, no filter.</li>
      <li>Medium roast. Black is fine, creamer is fine, over ice is fine.</li>
      <li>30 servings a bag: one scoop every morning for a month.</li>
    </ul>
    <p><a class="btn" href="/shop.html">Buy CoreJava</a></p>
  </div>
</div></section>
""" + FOUNDER + """
<section class="dark"><div class="wrap split">
  <div>
    <p class="eyebrow">What's in it</p>
    <h2>Seven things, one scoop.</h2>
    <p>MCT powder, for a creamy cup. Natural caffeine from coffee beans. L-theanine, the amino acid in green tea. ChromeMate, a patented chromium. Paradoxine, grains of paradise extract. Garcinia Cambogia fruit extract. Saffr'Activ saffron extract. One scoop, hot water, and you've got your morning cup.</p>
    <p><a class="btn" href="/ingredients.html">See every ingredient</a></p>
  </div>
  <div class="frame phone"><video muted loop playsinline preload="metadata" data-autoplay poster="/media/ingredients.jpg"><source src="/media/ingredients.mp4" type="video/mp4"></video></div>
</div></section>

<section class="alt"><div class="wrap">""" + INGCARDS.replace("ingcards","ingcards light") + """</div></section>
""" + COMPARE + """
<section class="alt" id="quiz"><div class="wrap">
  <h2 style="text-align:center">Not sure yet? Which morning are you?</h2>
  <p style="text-align:center;color:var(--muted);margin:0 0 26px">Three quick questions, then the free <em>7 Mornings</em> guide is yours.</p>
  <div class="quiz">
    <div class="q on" data-q="1">
      <div class="prog">Question 1 of 3</div>
      <h3>When does your energy actually drop off?</h3>
      <button class="opt" data-v="crash">Early afternoon. 2pm is a wall.</button>
      <button class="opt" data-v="jitters">It doesn't drop so much as spike. I get wired, then flat.</button>
      <button class="opt" data-v="parent">By the time the kids are back it's gone.</button>
      <button class="opt" data-v="desk">Mid-morning, right when the real work starts.</button>
    </div>
    <div class="q" data-q="2">
      <div class="prog">Question 2 of 3</div>
      <h3>How many cups does it take to get through a day?</h3>
      <button class="opt" data-v="1">One, and I'm hanging on.</button>
      <button class="opt" data-v="2">Two. The second one is damage control.</button>
      <button class="opt" data-v="3">Three or more. I've stopped counting.</button>
    </div>
    <div class="q" data-q="3">
      <div class="prog">Question 3 of 3</div>
      <h3>What would you want from a better cup?</h3>
      <button class="opt" data-v="focus">Focus that lasts into the afternoon.</button>
      <button class="opt" data-v="smooth">Energy without the shaky edge.</button>
      <button class="opt" data-v="simple">Something simple I'll actually stick with.</button>
    </div>
    <div class="q" data-q="4">
      <div class="prog">Your result</div>
      <div class="result"><b id="r-label">Result</b><span id="r-text"></span></div>
      <h3>Get the 7 Mornings guide</h3>
      <form id="tmu-form" novalidate>
        <label for="q-first">First name</label><input id="q-first" type="text" name="first_name" autocomplete="given-name">
        <label for="q-email">Email</label><input id="q-email" type="email" name="email" required autocomplete="email">
        <input type="hidden" name="quiz_result"><input type="hidden" name="cups"><input type="hidden" name="want">
        <p style="margin:16px 0 8px"><button class="btn" type="submit">Send me the guide</button></p>
        <p class="fine">You'll get the guide right away and a short series of notes after it. Unsubscribe in one click.</p>
        <p id="tmu-msg" class="fine" role="status" style="color:var(--copper2)"></p>
      </form>
    </div>
  </div>
</div></section>

""" + """
<section><div class="wrap split">
  <div>
    <h2>Questions, answered plainly</h2>
    <details><summary>Does it taste like coffee?</summary><p>Yes. Medium roast, a little smoother than drip. Black is fine; creamer is fine.</p></details>
    <details><summary>Is it one cup or two?</summary><p>One scoop is the serving on the label.</p></details>
    <details><summary>What if I drink coffee all day?</summary><p>Swap the first cup only for a week, and keep everything else the same.</p></details>
    <details><summary>Can I cancel the subscription?</summary><p>Any time. Use the link in your receipt, or <a href="https://billing.stripe.com/p/login/3cIbJ3fEv6XIbtk8iw4wM00">manage your subscription here</a>: pause a month, cancel, or update your card. No calls, no forms.</p></details>
    <p><a class="btn ghost" href="/faq.html">All questions</a></p>
  </div>
  <div class="frame p45"><img src="/img/patio_iced.jpg" alt="Iced CoreJava on a sunny patio" loading="lazy"></div>
</div></section>
<section class="alt"><div class="wrap split">
  <div>
    <p class="eyebrow">Share &amp; earn</p>
    <h2>Your coffee, paid for by the friends who steal a cup.</h2>
    <p>Tell people about it anyway? MarketPlace Global pays a bonus on every order a friend places through your link. Three levels, explained without the hype.</p>
    <p><a class="btn ghost" href="/share.html">How it works</a></p>
  </div>
  <div class="frame p45"><img src="/img/scoop.jpg" alt="A scoop of CoreJava" loading="lazy"></div>
</div></section>
<section class="dark" style="text-align:center"><div class="wrap">
  <h2>Tomorrow's first cup.</h2>
  <p>One scoop, hot water, thirty seconds. Thirty mornings a bag.</p>
""" + CTA_BLOCK + """
</div></section>

<script>
(function(){
  var ans={}, f=document.getElementById('tmu-form'), msg=document.getElementById('tmu-msg');
  var results={
    crash:['The 2 PM slide','Your first cup does its work early and the afternoon is on its own. The guide starts with the one-cup swap.'],
    jitters:['Sharp, not shaky','More coffee isn\\u2019t the only option. Day 1 of the guide explains why caffeine and L-theanine are paired.'],
    parent:['The 3pm pickup','Your day has a second shift. The guide is built around one cup that\\u2019s still working when it starts.'],
    desk:['Mid-morning fade','The slump arrives before lunch. The guide starts with when you drink the first cup.']
  };
  function show(n){document.querySelectorAll('.q').forEach(function(q){q.classList.toggle('on',q.dataset.q==String(n))});document.getElementById('quiz').scrollIntoView({behavior:'smooth',block:'start'});}
  document.querySelectorAll('.q[data-q="1"] .opt').forEach(function(b){b.onclick=function(){ans.quiz_result=b.dataset.v;show(2)}});
  document.querySelectorAll('.q[data-q="2"] .opt').forEach(function(b){b.onclick=function(){ans.cups=b.dataset.v;show(3)}});
  document.querySelectorAll('.q[data-q="3"] .opt').forEach(function(b){b.onclick=function(){ans.want=b.dataset.v;
    var r=results[ans.quiz_result]||results.crash; document.getElementById('r-label').textContent=r[0]; document.getElementById('r-text').textContent=r[1];
    f.quiz_result.value=ans.quiz_result; f.cups.value=ans.cups; f.want.value=ans.want; show(4); track('QuizComplete',{result:ans.quiz_result});}});
  var q=new URLSearchParams(location.search);
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var email=f.email.value.trim(); if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)){msg.textContent='Check the email address.';return;}
    var btn=f.querySelector('button'); btn.disabled=true; msg.textContent='Sending\\u2026';
    klaviyoSubscribe(TMU.KLAVIYO_LIST_QUIZ, email, f.first_name.value.trim(), {quiz_result:f.quiz_result.value||'none',cups:f.cups.value,want:f.want.value,lead_magnet:'7 Mornings guide',utm_source:q.get('utm_source')||'',utm_medium:q.get('utm_medium')||'',utm_campaign:q.get('utm_campaign')||'',utm_content:q.get('utm_content')||''}, 'themorningupgrades.com quiz')
    .then(function(r){ if(r.status===202){ track('Lead'); location.href='/thanks.html?r='+encodeURIComponent(f.quiz_result.value||''); } else { throw new Error(r.status); } })
    .catch(function(){ msg.textContent='Something went wrong. Try again in a moment.'; btn.disabled=false; });
  });
})();
</script>
"""

# ---------- SHOP ----------
SHOP = """
<section style="padding-top:36px"><div class="wrap split" style="align-items:start">
  <div>
    <div class="frame p45"><img src="/img/hero_breakfast.jpg" alt="CoreJava coffee bag on a breakfast table in morning light" loading="lazy" decoding="async"></div>
    <div class="gallery">
      <div class="frame" style="aspect-ratio:9/16"><video muted loop playsinline preload="metadata" data-autoplay poster="/media/product_callouts_v2.jpg"><source src="/media/product_callouts_v2.mp4" type="video/mp4"></video></div>
      <div class="frame" style="aspect-ratio:9/16"><img src="/img/kitchen_pour.jpg" alt="Pouring hot water next to a CoreJava bag" loading="lazy"></div>
      <div class="frame" style="aspect-ratio:9/16"><video muted loop playsinline preload="metadata" data-autoplay poster="/media/iced.jpg"><source src="/media/iced.mp4" type="video/mp4"></video></div>
    </div>
  </div>
  <div>
    <p class="eyebrow">CoreJava &middot; performance coffee</p>
    <h1 style="font-size:clamp(34px,4.4vw,52px)">CoreJava Coffee, 30 servings.</h1>
    <p class="lead">Medium-roast instant coffee built around natural caffeine and L-theanine, with ChromeMate, Paradoxine, Garcinia Cambogia and Saffr'Activ. Made for focus and steady energy. One level scoop in 8 oz of hot water.</p>
    """ + picker() + """
    <p class="bonus" data-bonus hidden><strong>Free with your first order:</strong> the Recipe Pack, 12 ways to drink it plus a 30-morning tracker (PDF).</p>
    <p class="fine"><span data-ship="long">Ships to all 50 states.</span> Cancel anytime &middot; <span data-ship="checkout">secure checkout</span> &middot; <span data-ship="damage">made right if it arrives damaged</span>. Questions before you buy: hello@themorningupgrades.com.</p>
    <h2 style="margin-top:30px;font-size:22px">Details</h2>
    <ul class="clean">
      <li><strong>Serving:</strong> 1 level scoop (about 6.8 g) in 8 fl oz hot water. 30 servings per 7.2 oz (204 g) bag.</li>
      <li><strong>Ingredients:</strong> MCT powder, natural caffeine, L-theanine, ChromeMate&reg; chromium, Paradoxine&reg; grains of paradise extract, Garcinia Cambogia extract, Saffr'Activ&reg; saffron extract. <a href="/ingredients.html">Full breakdown</a>.</li>
      <li><strong>Taste:</strong> medium roast, smooth. Works black, with creamer, or over ice.</li>
      <li><strong>Who it's for:</strong> adults who drink coffee daily and want a steadier morning. Not for children, or if you're pregnant or nursing. Contains caffeine.</li>
      <li><strong>Made by:</strong> MarketPlace Global. Sold by Rector &amp; Stull LLC, Independent MarketPlace Global ISR.</li>
    </ul>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <h2>How a week with it goes</h2>
  <div class="steps">
    <div><h3>Days 1&ndash;2</h3><p>Swap your first cup only. Same mug, same time. Notice the afternoon.</p></div>
    <div><h3>Days 3&ndash;5</h3><p>Notice whether you still want a second cup. Write it down.</p></div>
    <div><h3>Days 6&ndash;7</h3><p>Decide. If you like the cup, Subscribe &amp; Save keeps it coming for $2.33 a morning.</p></div>
  </div>
</div></section>
""" + COMPARE + FOUNDER + """
<section class="dark" style="text-align:center"><div class="wrap"><h2>Start tomorrow.</h2>""" + CTA_BLOCK + """</div></section>
"""

# ---------- INGREDIENTS ----------
ING = """
<section class="tight"><div class="wrap split" style="align-items:center">
  """ + CALLOUTS + """
  <div>
    <p class="eyebrow">What's in it</p>
    <h1 style="font-size:clamp(34px,4.4vw,56px)">Seven ingredients. Nothing hidden behind a blend.</h1>
    <p class="lead">We'll tell you where each one comes from. We describe the cup by what's in it: natural caffeine for energy, L-theanine alongside it, MCT powder for a creamy texture. We don't make health claims beyond the label.</p>
  </div>
</div></section>
<section class="alt"><div class="wrap">
  <h2 class="sr">The seven ingredients</h2>
  <div class="ing">
    <div class="card"><b>MCT powder</b><h3>First on the label</h3><p>Medium-chain triglycerides, usually from coconut oil, in powder form. It&rsquo;s what gives the cup body and a creamy texture without adding cream.</p></div>
    <div class="card"><b>Natural caffeine</b><h3>From coffee beans</h3><p>The same caffeine you already drink, from coffee, not synthesized. About the amount in a strong cup.</p></div>
    <div class="card"><b>L-theanine</b><h3>The amino acid in green tea</h3><p>Found naturally in tea leaves. Commonly paired with caffeine; many people describe the pairing as smoother than coffee alone.</p></div>
    <div class="card"><b>ChromeMate&reg;</b><h3>A patented chromium</h3><p>A branded form of the mineral chromium, bound to niacin. Chromium is an essential trace mineral.</p></div>
    <div class="card"><b>Paradoxine&reg;</b><h3>Grains of paradise extract</h3><p>A standardized extract of <em>Aframomum melegueta</em>, a West African seed in the ginger family.</p></div>
    <div class="card"><b>Garcinia Cambogia</b><h3>Fruit extract</h3><p>Extract of the rind of a small tropical fruit, standardized for hydroxycitric acid.</p></div>
    <div class="card"><b>Saffr'Activ&reg;</b><h3>Saffron extract</h3><p>A standardized extract of saffron stigmas, the same spice used in cooking.</p></div>
    <div class="card claim"><b>What we say about it</b><h3>Natural caffeine and L-theanine for focus and steady energy.</h3><p>That's the whole pitch. It's a dietary supplement, not a medicine, and we don't claim more than what's in the bag.</p></div>
  </div>
  <p class="fine" style="margin-top:22px;text-align:center">Full Supplement Facts, including amounts per serving and other ingredients, are printed on the bag. Trademarks belong to their respective ingredient suppliers.</p>
</div></section>
<section><div class="wrap" style="text-align:center">
  <h2>One scoop has all seven.</h2>
  <p style="color:var(--muted)">$79.95 a bag, or $69.95 a month on Subscribe &amp; Save.</p>
""" + CTA_BLOCK + """
</div></section>
"""

# ---------- FAQ ----------
FAQ = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">FAQ</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Questions, answered plainly.</h1>
  <h2>The coffee</h2>
  <details><summary>Does it taste like coffee?</summary><p>Yes. Medium roast, a little smoother than drip. Black is fine; creamer is fine; over ice is fine.</p></details>
  <details><summary>How much caffeine is in a serving?</summary><p>About the same as a strong cup of coffee. The exact amount is on the Supplement Facts panel on the bag. It contains caffeine, so skip it late in the day if you're sensitive.</p></details>
  <details><summary>Is it one cup or two?</summary><p>One scoop is the serving on the label.</p></details>
  <details><summary>What does it do?</summary><p>It's instant coffee with natural caffeine, L-theanine and MCT powder, made for focus and steady energy. It's a dietary supplement, not a medicine, and it hasn't been evaluated by the FDA.</p></details>
  <details><summary>Who shouldn't take it?</summary><p>Children, and anyone pregnant or nursing. If you take medication or have a medical condition, ask your physician first.</p></details>
  <h2>Ordering</h2>
  <details><summary>How does Subscribe &amp; Save work?</summary><p>A bag ships every 30 days at $69.95, $10 less than a single bag, plus shipping and tax. Pause a month, cancel, or update your card any time from the link in your receipt or at <a href="https://billing.stripe.com/p/login/3cIbJ3fEv6XIbtk8iw4wM00">the subscription portal</a>. No calls.</p></details>
  <details><summary>Where does it ship from, how fast, and what does shipping cost?</summary><p><span data-ship="policy">Orders are fulfilled by the maker, MarketPlace Global, from Maple Grove, Minnesota, usually within two business days, then 3&ndash;6 days in transit. US shipping is a flat $8.95 a bag.</span> US addresses only for now. Tracking arrives by email.</p></details>
  <details><summary>Returns?</summary><p>If a bag arrives damaged or wrong, email hello@themorningupgrades.com within 30 days of delivery and we'll replace it or refund it. Unopened bags are covered by a 90-day money-back guarantee. Full policy on the <a href="/shipping-returns.html">Shipping &amp; returns</a> page.</p></details>
  <details><summary>Who am I buying from?</summary><p>Rector &amp; Stull LLC, Independent ISR of MarketPlace Global products and services. MarketPlace Global makes CoreJava; we sell it.</p></details>
  <h2>The business</h2>
  <details><summary>Who are the people in your videos?</summary><p>AI presenters we make for the brand. We say so here and in the platform AI labels. They show the coffee, the scoop and the label; they never claim results, because they haven't used it. Real answers come from a real inbox: hello@themorningupgrades.com.</p></details>
</div></section>
"""

# ---------- PARTNER ----------
PARTNER = """
<section style="padding-top:36px"><div class="wrap split">
  <div>
    <p class="eyebrow">Build track</p>
    <h1 style="font-size:clamp(30px,4vw,46px)">Sell the coffee you already drink. We'll show you exactly how we do it.</h1>
    <p class="lead">Rector &amp; Stull is a small team of Independent Sales Representatives (ISRs) for MarketPlace Global. We sell CoreJava online with short videos, a simple website and an email list. If you join our team, we show you how we do it and meet weekly to go over what&rsquo;s working.</p>
    <p><a class="btn" data-enroll data-fallback="Ask about joining" href="#apply">Join our team</a> &nbsp; <a class="btn ghost" href="#how">How it works</a></p>
    <p class="fine" style="margin-top:14px">Independent Sales Representative (ISR) opportunity with MarketPlace Global. Compensation is based on sales of MarketPlace Global products and on sponsoring other ISRs who sell them; no compensation is paid for recruiting. Success can be achieved only through substantial independent effort, and most participants earn little or nothing. Read the <a data-disclosure href="#">income disclosure statement</a>, the <a href="https://cdn.raveretailer.com/4450703AD7/2024/12/GSR_6751b39409eb32803571733411236.pdf" rel="noopener">Policies &amp; Procedures</a> and the <a href="https://cdn.raveretailer.com/4450703AD7/2026/09/GSR_6a99a5994071e2714841788457897.pdf" rel="noopener">Compensation Plan</a> before you decide.</p>
  </div>
  <div class="frame phone"><video muted loop playsinline preload="metadata" data-autoplay poster="/media/ambient.jpg"><source src="/media/ambient.mp4" type="video/mp4"></video></div>
</div></section>

<section class="alt" id="how"><div class="wrap">
  <h2>How it works</h2>
  <div class="steps">
    <div><h3>Enroll with MarketPlace Global</h3><p>You sign up as an Independent Sales Representative under our team. MarketPlace Global handles product, shipping, payments and commissions.</p></div>
    <div><h3>Learn how we do it</h3><p>MarketPlace Global provides the training, tools and approved materials. We add a weekly call where we walk through what we post, what we say, and the compliance rules that keep it clean.</p></div>
    <div><h3>Sell, then teach</h3><p>You earn on the coffee you sell. If you introduce partners, you earn on what they sell too. We meet weekly to go over what's working.</p></div>
  </div>
</div></section>

<section><div class="wrap split">
  <div class="frame p45"><img src="/img/desk.jpg" alt="Laptop, mug and coffee bag on a desk" loading="lazy"></div>
  <div>
    <h2>Who this is for</h2>
    <ul class="clean">
      <li>You drink coffee every day and you'd rather sell one thing you use than ten you don't.</li>
      <li>You're comfortable posting short videos, or willing to learn with templates that do most of the work.</li>
      <li>You're fine with honest numbers. We'll show you ours.</li>
    </ul>
    <h2 style="margin-top:28px">Who it isn't for</h2>
    <p style="color:var(--muted)">Anyone who needs income this month. Anyone who wants to recruit before they've sold a bag. Anyone who'd rather not identify themselves as an independent MarketPlace Global ISR in everything they post.</p>
  </div>
</div></section>

<section class="dark"><div class="wrap">
  <h2>The honest part</h2>
  <div class="grid3">
    <div class="card"><h3>It costs money to start</h3><p>MarketPlace Global charges an enrollment fee and you'll want product to try. We'll tell you the current numbers before you sign anything.</p></div>
    <div class="card"><h3>Most people earn little</h3><p>That's true of every direct-sales company, and the income disclosure statement shows it. We'd rather you read it first than hear it later.</p></div>
    <div class="card"><h3>Results take work</h3><p>Our system shortens the learning curve. It does not remove the work: posting, replying, following up, every week.</p></div>
  </div>
  <p class="fine" style="margin-top:22px">Rector &amp; Stull LLC does not guarantee any level of income. MarketPlace Global&rsquo;s own income disclosure projects average annual gross revenue for ISRs of roughly $500 to $2,000 before expenses, which can exceed commissions. Compensation is based solely on product sales, not recruiting, and requires substantial independent effort. See the <a data-disclosure href="#" style="color:#C9C2B6">MarketPlace Global income disclosure statement</a>, <a href="https://cdn.raveretailer.com/4450703AD7/2024/12/GSR_6751b39409eb32803571733411236.pdf" rel="noopener" style="color:#C9C2B6">Policies &amp; Procedures</a> and <a href="https://cdn.raveretailer.com/4450703AD7/2026/09/GSR_6a99a5994071e2714841788457897.pdf" rel="noopener" style="color:#C9C2B6">Compensation Plan</a>.</p>
</div></section>

<section class="alt" id="apply"><div class="wrap">
  <div class="quiz" style="max-width:640px">
    <h3>Tell us a little about you</h3>
    <p class="fine" style="margin:0 0 10px">We'll reply within one business day with the enrollment details and the current costs. No pressure, no scripts.</p>
    <form id="partner-form" novalidate>
      <label for="q-first">First name</label><input id="q-first" type="text" name="first_name" autocomplete="given-name">
      <label for="q-email">Email</label><input id="q-email" type="email" name="email" required autocomplete="email">
      <label for="f-phone">Phone (optional)</label><input id="f-phone" type="tel" name="phone" autocomplete="tel">
      <label for="f-experience">Where are you starting from?</label><select id="f-experience" name="experience">
        <option value="new">New to selling online</option>
        <option value="social">I post on social already</option>
        <option value="sales">I've done sales or direct sales before</option>
        <option value="mpg">I'm already a MarketPlace Global ISR</option>
      </select>
      <p class="fine" style="margin:6px 0 0">If you already have a MarketPlace Global ISR agreement, we can&rsquo;t enroll you under a different sponsor (MPG policy 3.6) &mdash; but we&rsquo;re happy to compare notes.</p>
      <label for="f-note">Anything you want us to know?</label><textarea id="f-note" name="note"></textarea>
      <p style="margin:16px 0 8px"><button class="btn" type="submit">Send</button></p>
      <p class="fine">You'll hear from a real person at Rector &amp; Stull. We never add partner inquiries to our customer emails.</p>
      <p id="p-msg" class="fine" role="status" style="color:var(--copper2)"></p>
    </form>
  </div>
</div></section>

<script>
(function(){
  var f=document.getElementById('partner-form'), msg=document.getElementById('p-msg'); var q=new URLSearchParams(location.search);
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var email=f.email.value.trim(); if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)){msg.textContent='Check the email address.';return;}
    if(!TMU.KLAVIYO_LIST_PARTNERS){ location.href='mailto:hello@themorningupgrades.com?subject=Partner%20inquiry&body='+encodeURIComponent('Name: '+f.first_name.value+'\\nEmail: '+email+'\\nPhone: '+f.phone.value+'\\nStarting from: '+f.experience.value+'\\n\\n'+f.note.value); return; }
    var btn=f.querySelector('button'); btn.disabled=true; msg.textContent='Sending\\u2026';
    klaviyoSubscribe(TMU.KLAVIYO_LIST_PARTNERS, email, f.first_name.value.trim(), {phone:f.phone.value,experience:f.experience.value,note:f.note.value,utm_source:q.get('utm_source')||'',utm_campaign:q.get('utm_campaign')||''}, 'themorningupgrades.com partner form')
    .then(function(r){ if(r.status===202){ track('PartnerLead'); msg.textContent='Got it. We\\u2019ll be in touch within one business day.'; f.reset(); } else { throw new Error(r.status); } })
    .catch(function(){ msg.textContent='Something went wrong. Email us at hello@themorningupgrades.com.'; btn.disabled=false; });
  });
})();
</script>
"""


SHARE = """
<section style="padding-top:36px"><div class="wrap split">
  <div>
    <p class="eyebrow">Share &amp; earn</p>
    <h1 style="font-size:clamp(32px,4.4vw,50px)">Your coffee, paid for by the friends who steal a cup.</h1>
    <p class="lead">You already tell people about the coffee that got you through the afternoon. With MarketPlace Global&rsquo;s referral program you get paid every time one of them orders. Three levels. Start wherever you like.</p>
    <p><a class="btn" href="#levels">See the three levels</a> &nbsp; <a class="btn ghost" href="#honest">What this actually is</a></p>
    <p class="fine" style="margin-top:14px">Independent Sales Representative (ISR) program of MarketPlace Global. Paid on product sales only. Most participants earn little; see the <a data-disclosure href="#">income disclosure</a>.</p>
  </div>
  <div class="frame phone"><img src="/img/gym.jpg" alt="Woman on a yoga mat holding a CoreJava bag and a mug" loading="lazy" decoding="async"></div>
</div></section>

<section class="alt" id="levels"><div class="wrap">
  <h2 style="text-align:center">Three levels. No pressure to climb.</h2>
  <div class="levels">
    <div class="lvl">
      <span class="num">1</span>
      <h3>Sip</h3>
      <p class="tag2">Just drink it</p>
      <p>One bag, or Subscribe &amp; Save. Enjoy your mornings. That&rsquo;s it; you can stay right here, and that&rsquo;s fine.</p>
      <a class="btn ghost sm" href="/shop.html">Get the coffee</a>
    </div>
    <div class="lvl best">
      <span class="num">2</span>
      <h3>Share</h3>
      <p class="tag2">Get your bag covered</p>
      <p>Become an MPG referral rep and get your own link. Friends order through it, you earn a bonus on every order and re-order. <span class="math" hidden>At <b class="pct"></b> back, <b class="n3"></b> friends on Subscribe &amp; Save covers your own bag every month.</span></p>
      <div class="ladder" hidden>
        <div><i>1 friend</i><b class="l1"></b><em>/mo</em></div>
        <div><i>3 friends</i><b class="l3"></b><em>/mo</em></div>
        <div><i>5 friends</i><b class="l5"></b><em>/mo</em></div>
        <div><i>10 friends</i><b class="l10"></b><em>/mo</em></div>
      </div>
      <a class="btn sm" data-enroll href="#">Start sharing</a>
    </div>
    <div class="lvl">
      <span class="num">3</span>
      <h3>Build</h3>
      <p class="tag2">Take it seriously</p>
      <p>You like the selling part. We hand you everything we use: the video system, the site, the email flows, the weekly call. You bring the work.</p>
      <a class="btn ghost sm" href="/partner.html">See the Build track</a>
    </div>
  </div>
  <p class="fine" style="text-align:center;margin-top:18px">Ladder figures are illustrative, based on friends ordering one bag a month at the current Subscribe &amp; Save price, before any expenses. They are not projections of what you will earn.</p>
</div></section>

<section id="honest"><div class="wrap" style="max-width:820px">
  <p class="eyebrow">In plain language</p>
  <h2>What &ldquo;Share&rdquo; actually is</h2>
  <div class="card" style="padding:28px">
    <ul class="clean" style="margin:0">
      <li><strong>It&rsquo;s MarketPlace Global&rsquo;s Independent Sales Representative program.</strong> MPG is the direct-sales company that makes CoreJava. We&rsquo;re ISRs too; if you join through us, we&rsquo;re your sponsor and the people on the weekly call.</li>
      <li><strong>It costs money to start.</strong> The CoreJava Starter Kit is $179.90 (two bags plus two 6-day experience packs) and the Builder Kit is $229.90 (three of each). Both include the $29.95 annual membership. Plus shipping and tax.</li>
      <li><strong>You earn on product sales, not on signing people up.</strong> A Retail Customer Bonus every time someone you referred orders, and a Fast Start Bonus if someone you introduce enrolls with a kit. MPG pays weekly.</li>
      <li><strong>To stay eligible for team commissions you keep 50 QV a month,</strong> which is roughly one bag of your own or one customer order. In the Share level you can do this by drinking the coffee you were already buying.</li>
      <li><strong>Most participants earn little.</strong> MPG&rsquo;s own disclosure projects average annual gross revenue of roughly $500 to $2,000 before expenses, which can exceed what you earn. Read it: <a data-disclosure href="#">income disclosure statement</a>. Also read the <a href="https://cdn.raveretailer.com/4450703AD7/2024/12/GSR_6751b39409eb32803571733411236.pdf" rel="noopener">Policies &amp; Procedures</a> and <a href="https://cdn.raveretailer.com/4450703AD7/2026/09/GSR_6a99a5994071e2714841788457897.pdf" rel="noopener">Compensation Plan</a>.</li>
      <li><strong>You can stop whenever.</strong> Don&rsquo;t renew the membership and it lapses. 30-day money-back on unopened product bought as an ISR.</li>
    </ul>
  </div>
  <p style="margin-top:22px">If that all sounds fine and you mostly want your coffee covered, Share is for you. If you read it and thought &ldquo;I could do more than three friends,&rdquo; look at <a href="/partner.html">Build</a>.</p>
  <p><a class="btn" data-enroll href="#">Start sharing</a></p>
</div></section>

<section class="alt"><div class="wrap split">
  <div class="frame p45"><img src="/img/desk.jpg" alt="Laptop, mug and a bag of CoreJava on a desk" loading="lazy"></div>
  <div>
    <h2>Questions people ask before they share</h2>
    <details><summary>Do I have to recruit anyone?</summary><p>No. The Share level is customers only: friends who buy coffee. Nobody is paid for recruiting at any level; compensation is on product sales.</p></details>
    <details><summary>Is this an MLM?</summary><p>MarketPlace Global is a direct-sales company whose compensation plan includes sponsoring other reps, so yes, it&rsquo;s in that category. We&rsquo;d rather you know that on this page than find out later.</p></details>
    <details><summary>What do my friends pay?</summary><p>The same prices as anyone else: $79.95 a bag or $69.95 a month on Subscribe &amp; Save, plus shipping. Your link doesn&rsquo;t change their price.</p></details>
    <details><summary>What if I already have an MPG account?</summary><p>Then you already have a sponsor and MPG policy doesn&rsquo;t allow switching. Keep sharing through your own link; we&rsquo;re happy to compare notes.</p></details>
    <details><summary>Do I need to buy inventory?</summary><p>No. Friends order from MPG directly through your link and MPG ships to them. The kit is the only purchase.</p></details>
  </div>
</div></section>

<script>
(function(){
  var pct = (window.TMU && TMU.RETAIL_BONUS_PCT) || 0; if(!pct) return;
  var price = 69.95, bag = 69.95 + 8.95, per = price * pct / 100;
  var n3 = Math.ceil(bag / per);
  document.querySelectorAll('.math').forEach(function(e){ e.hidden=false; e.querySelector('.pct').textContent = pct + '%'; e.querySelector('.n3').textContent = n3; });
  document.querySelectorAll('.ladder').forEach(function(l){ l.hidden=false; [1,3,5,10].forEach(function(n){ l.querySelector('.l'+n).textContent = '$' + Math.round(per*n); }); });
})();
</script>
"""

# ---------- ABOUT ----------
ABOUT = """
<section style="padding-top:36px"><div class="wrap split">
  <div>
    <p class="eyebrow">About</p>
    <h1 style="font-size:clamp(30px,4vw,46px)">Two people, one bag of coffee, and a website that says what it is.</h1>
    <p class="lead">Rector &amp; Stull LLC is a small company run by two partners, one in Idaho and one in Texas. We're Independent Sales Representatives (ISRs) for MarketPlace Global, and CoreJava is the product we drink ourselves, which is why it's the one we sell.</p>
    <p>We started The Morning Upgrade because most coffee marketing is either a lifestyle fantasy or a wall of supplement jargon. We wanted a page that tells you what's in the bag, what it costs per cup, and how to find out in a week whether it's for you.</p>
    <p>Everything on this site that earns us money says so. The people in our videos are AI presenters; we say so here and in the platform AI labels. If something's unclear, email us and a human will answer: hello@themorningupgrades.com.</p>
    <p><a class="btn" href="/shop.html">Buy CoreJava</a> &nbsp; <a class="btn ghost" href="/partner.html">Partner with us</a></p>
  </div>
  <div class="frame p45"><img src="/img/bag_shadows.jpg" alt="CoreJava bag with leaf shadows" loading="lazy" decoding="async"></div>
  <p class="fine" style="margin-top:18px">The people in our videos are AI presenters we produce for the brand. They demonstrate the product; they never speak as customers or describe results.</p>
</div></section>
"""

# ---------- LEGAL ----------
SHIPPING = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">Policies</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Shipping &amp; returns</h1>
  <h2>Shipping</h2>
  <p>We ship to addresses in the United States. <span data-ship="policy">Orders are fulfilled by the maker, MarketPlace Global, from Maple Grove, Minnesota, usually within two business days, then 3&ndash;6 days in transit.</span> You'll get a tracking email when it leaves.</p>
  <h2>Subscribe &amp; Save</h2>
  <p>A new bag ships every 30 days and your card is charged $69.95 each time. You can pause a month or cancel from the link in any receipt, or at <a href="https://billing.stripe.com/p/login/3cIbJ3fEv6XIbtk8iw4wM00">the subscription portal</a>, up to the day before your next shipment. There are no cancellation fees.</p>
  <h2>Returns and refunds</h2>
  <p>MarketPlace Global, the maker, backs every customer order with a 90-day money-back guarantee on unopened product in resalable condition, and replaces anything that arrives damaged, defective or incorrect if you tell us within 30 calendar days of delivery. Email hello@themorningupgrades.com with your order number (and a photo if it&rsquo;s damaged) and we handle the return authorization for you. Return shipping on change-of-mind returns is paid by the customer; original shipping isn&rsquo;t refunded. Opened bags can&rsquo;t be returned for a change of mind, for food-safety reasons.</p>
  <h2>Questions</h2>
  <p>hello@themorningupgrades.com. A real person answers, usually the same business day.</p>
  <p class="fine">Rector &amp; Stull LLC, 30 N Gould St Ste R, Sheridan, WY 82801. Independent ISR of MarketPlace Global products and services. Last updated October 2026.</p>
</div></section>
"""

PRIVACY = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">Policies</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Privacy</h1>
  <p>This is the privacy policy for themorningupgrades.com, operated by Rector &amp; Stull LLC ("we"). It's written to be read.</p>
  <h2>What we collect</h2>
  <ul><li><strong>If you take the quiz:</strong> your answers, first name and email, so we can send you the guide and the follow-up emails.</li><li><strong>If you buy:</strong> your name, shipping address, email and phone. Payment details go to Stripe; we never see your card number. To fulfil your order we create a customer account for you with MarketPlace Global, the maker, and pass them your name, address, email and phone so they can ship to you and honor their guarantee. Their <a href="https://marketplaceglobal.com/rectorandstull/privacy-policy">privacy policy</a> covers what they do with it.</li><li><strong>If you ask about partnering:</strong> what you type into the form.</li><li><strong>Automatically:</strong> Google Analytics records pages viewed, where visitors came from, and button clicks, with IP addresses anonymized. TikTok, Meta, Snapchat and Google Ads tags record page views, sign-ups and purchases so we can measure which ads work.</li></ul>
  <h2>What we do with it</h2>
  <p>Fulfil orders, send the emails you signed up for, answer your questions, and measure which of our posts bring people here. We don't sell your data. We don't share it except with the services that make the site work: Stripe (payments), MarketPlace Global (the maker, who fulfils and ships orders), Klaviyo (email), GitHub (hosting), and analytics providers.</p>
  <h2>Your choices</h2>
  <p>Every email has an unsubscribe link. To see, correct or delete what we hold about you, email hello@themorningupgrades.com and we'll do it within 30 days.</p>
  <h2>Cookies</h2>
  <p>Google Analytics and the TikTok pixel set measurement cookies; you can block them with the <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">Google Analytics opt-out add-on</a> or your browser settings. Stripe and Klaviyo set the ones they need to work. TikTok&rsquo;s ad choices are at tiktok.com/legal/ads-and-your-data. The Meta pixel sets its own; you can opt out at facebook.com/ads/preferences. The Snap pixel sets its own too; Snapchat&rsquo;s ad preferences are in the app under Settings &gt; Ad Preferences.</p>
  <p class="fine">Rector &amp; Stull LLC, 30 N Gould St Ste R, Sheridan, WY 82801 &middot; hello@themorningupgrades.com. Last updated October 2026.</p>
</div></section>
"""

TERMS = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">Policies</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Terms of sale</h1>
  <p>By ordering from themorningupgrades.com you agree to these terms. The seller is Rector &amp; Stull LLC, Independent ISR of MarketPlace Global products and services. MarketPlace Global manufactures CoreJava; we are not the manufacturer.</p>
  <h2>Orders and prices</h2>
  <p>Prices are in US dollars. Any shipping charge is shown at checkout before you pay. We may change prices at any time; the price you pay is the one shown at checkout. If we can't fill an order we'll refund it in full.</p>
  <h2>Subscriptions</h2>
  <p>Subscribe &amp; Save renews every 30 days at the price shown until you cancel. Cancel any time from the link in your receipt, effective before the next shipment.</p>
  <h2>Use of the product</h2>
  <p>CoreJava is a dietary supplement containing caffeine, for adults. It is not intended to diagnose, treat, cure or prevent any disease. Read the label. Do not use if pregnant or nursing. Ask a physician if you take medication or have a medical condition. Keep out of reach of children.</p>
  <h2>Returns</h2>
  <p>See <a href="/shipping-returns.html">Shipping &amp; returns</a>.</p>
  <h2>Liability</h2>
  <p>To the extent the law allows, our liability for any order is limited to the amount you paid for it.</p>
  <h2>Partner opportunity</h2>
  <p>Information on the Partner page describes an Independent Sales Representative (ISR) opportunity with MarketPlace Global and is governed by MarketPlace Global's own agreement and policies, which you accept when you enroll with them. We make no guarantee of income.</p>
  <p class="fine">Rector &amp; Stull LLC, 30 N Gould St Ste R, Sheridan, WY 82801 &middot; hello@themorningupgrades.com. Governing law: Wyoming. Last updated October 2026.</p>
</div></section>
"""

ORDER_COMPLETE = """
<section style="padding-top:36px"><div class="wrap" style="max-width:720px">
  <div class="card" style="padding:34px 30px">
    <p class="eyebrow">Order received</p>
    <h1 style="font-size:clamp(30px,4vw,44px)">Your coffee is on its way.</h1>
    <p>Stripe has emailed your receipt. We set up your CoreJava customer account with MarketPlace Global, the maker, who ships from Maple Grove, Minnesota within about two business days; you'll get a tracking email when it leaves. If anything looks wrong, reply to the receipt or write hello@themorningupgrades.com.</p>
    <h3 style="margin-top:26px">While you wait</h3>
    <ul class="clean">
      <li>Morning 1: swap your <em>first</em> cup only. One level scoop, 8 oz hot water, stir.</li>
      <li>Notice the afternoon, not the first hour.</li>
      <li>Give it the full week before you decide.</li>
    </ul>
    <div class="card" style="margin-top:22px;padding:22px 22px;background:var(--tint);box-shadow:none">
      <p class="eyebrow" style="margin-bottom:6px">Your first-order bonus</p>
      <h3>The Recipe Pack</h3>
      <p>Twelve ways to drink it, hot, iced and blended, plus a 30-morning tracker for the fridge.</p>
      <p style="margin:0"><a class="btn" href="/assets/recipe-pack.pdf" download>Download the Recipe Pack (PDF)</a></p>
    </div>
    <p style="margin-top:22px"><a class="btn ghost" href="/">Back to the site</a></p>
  </div>
</div></section>
<script>tmuPurchase();</script>
"""

THANKS = """
<section style="padding-top:36px"><div class="wrap" style="max-width:720px">
  <div class="card" style="padding:34px 30px">
    <div class="frame" style="aspect-ratio:16/10;margin-bottom:22px;box-shadow:none"><img src="/img/desk.jpg" alt="A mug and a bag of coffee on a desk" loading="lazy" decoding="async"></div>
    <h1 style="font-size:clamp(30px,4vw,44px)">Your guide is on its way.</h1>
    <p>Check your inbox in the next minute or two (and the promotions tab, if you're on Gmail). If you'd rather not wait:</p>
    <p><a class="btn" href="https://d2ol7oe51mr4n9.cloudfront.net/user_3GvdxB9gfwtge4rv79iuyoXAckR/a857aef6-954a-4e8e-b256-41205db0097f.pdf" target="_blank" rel="noopener">Open the 7 Mornings guide</a></p>
    <div class="card" style="background:var(--cream2);margin:22px 0">
      <strong>What happens next</strong>
      <ol style="margin:8px 0 0;padding-left:20px"><li>Morning 1 starts tomorrow. It takes two minutes.</li><li>Over the next two weeks you'll get a handful of short notes: the why, the how-to, the cost math.</li><li>If you want to try the cup the guide is built around, it's below. One bag is 30 mornings.</li></ol>
    </div>
    <p><a class="btn" href="/start.html?utm_source=quiz">See the coffee</a> <a class="btn ghost" href="/">Back to the start</a></p>
  </div>
</div></section>
"""

# /start is the landing page for ads and creator links (noindex). The headline matches the ad:
# utm_content's first word (ritual_a -> "ritual") picks a variant; anything else gets the default.
# Every variant is label wording or plain facts, no results.
LANDING_VARIANTS = {
    "default": ("One scoop. Steady energy, sharp focus.", ("Steady energy", "Sharp focus", "30 mornings a bag")),
    "ritual":  ("One scoop. Hot water. That's it.", ("30 seconds", "No machine", "30 mornings a bag")),
    "swap":    ("Swap one cup for a week.", ("One scoop", "Hot water", "Seven mornings")),
    "label":   ("Seven things on the label. One scoop.", ("MCT powder", "Natural caffeine", "L-theanine")),
    "cost":    ("$2.33 a morning. One scoop.", ("Subscribe & Save", "$69.95/mo", "30 servings")),
}

MINI_NAV = """
<header class="nav mini" aria-label="The Morning Upgrade"><div class="wrap">
  <a class="brand" href="/"><img src="/img/mark.jpg" alt="" width="30" height="30"><b>The Morning Upgrade</b></a>
  <a class="minilink" href="/faq.html">Questions</a>
</div></header>
"""

GUAR = """<div class="guar">
    <div><b>Shipping</b><span data-ship="policy">Orders ship from Minnesota within about two business days, then 3&ndash;6 days in transit. US shipping is a flat $8.95 a bag.</span></div>
    <div><b>Guarantee</b><span>MarketPlace Global, the maker, backs every customer order with a 90-day money-back guarantee on unopened product in resalable condition (original shipping isn't refunded). Anything that arrives damaged or incorrect is replaced if you tell us within 30 days of delivery. We handle the return for you. <a href="/shipping-returns.html">The full policy</a>.</span></div>
    <div><b>Who you're buying from</b><span>Rector &amp; Stull LLC, Independent Sales Representative of MarketPlace Global. A real inbox answers: hello@themorningupgrades.com.</span></div>
  </div>"""

def capture(source, heading="Not ready to order? Get the 7 Mornings guide.", note="Seven short emails on how to swap one cup for a week, with the recipe pack. Unsubscribe in one click."):
    """Email-only capture for the 7 Mornings guide (Klaviyo quiz list), used on /start and guides."""
    fid = f"cap-{source}"
    return f"""<div class="capture" id="{fid}">
  <h2>{heading}</h2>
  <p>{note}</p>
  <form novalidate data-capture="{source}">
    <label for="{fid}-email" class="sr">Email</label>
    <div class="caprow"><input id="{fid}-email" type="email" name="email" required autocomplete="email" placeholder="you@example.com"><button class="btn" type="submit">Send me the guide</button></div>
    <p class="fine" role="status" data-capmsg></p>
  </form>
</div>
<script>
(function(){{
  var f=document.querySelector('[data-capture="{source}"]'), msg=f.querySelector('[data-capmsg]'), q=new URLSearchParams(location.search);
  f.addEventListener('submit',function(e){{
    e.preventDefault();
    var email=f.email.value.trim(); if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)){{msg.textContent='Check the email address.';return;}}
    var btn=f.querySelector('button'); btn.disabled=true; msg.textContent='Sending\\u2026';
    klaviyoSubscribe(TMU.KLAVIYO_LIST_QUIZ, email, '', {{lead_magnet:'7 Mornings guide',source:'{source}',quiz_result:'none',utm_source:q.get('utm_source')||'',utm_medium:q.get('utm_medium')||'',utm_campaign:q.get('utm_campaign')||'',utm_content:q.get('utm_content')||''}}, 'themorningupgrades.com {source}')
    .then(function(r){{ if(r.status===202){{ track('Lead',{{source:'{source}'}}); location.href='/thanks.html?r={source}'; }} else {{ throw new Error(r.status); }} }})
    .catch(function(){{ msg.textContent='Something went wrong. Try again in a moment.'; btn.disabled=false; }});
  }});
}})();
</script>"""

START = """
""" + hero_c(variants=True) + """
<section class="tight alt"><div class="wrap">
  """ + GUAR + """
</div></section>

<section><div class="wrap split" style="align-items:center">
  <div class="frame phone vid"><video muted loop playsinline preload="metadata" data-autoplay poster="/media/host_kitchen.jpg"><source src="/media/host_kitchen.mp4" type="video/mp4"></video><button class="unmute" type="button" data-unmute aria-label="Turn sound on">&#9654; Sound on</button></div>
  <div>
    <p class="eyebrow">One scoop. Seven things on the label.</p>
    <h2>Nothing hidden behind a blend.</h2>
    <p>MCT powder, natural caffeine, L-theanine, ChromeMate&reg; chromium, Paradoxine&reg; grains of paradise, Garcinia Cambogia and Saffr'Activ&reg; saffron extract. We describe it by what's in it and don't make health claims beyond the label.</p>
    <ul class="clean">
      <li>Medium roast, instant. Black is fine, creamer is fine, over ice is fine.</li>
      <li>One level scoop in 8 oz of hot water. Stir. Done.</li>
      <li>Made by MarketPlace Global in the US, shipped from Minnesota.</li>
    </ul>
    <p><a class="btn ghost sm" href="/ingredients.html">Every ingredient, explained</a></p>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <h2 style="text-align:center">The 7-day swap</h2>
  <p style="text-align:center;color:var(--muted);margin:0 0 26px">How we tell everyone to try it. Change one cup, watch one hour.</p>
  <div class="steps">
    <div><h3>Days 1&ndash;2</h3><p>Swap your first cup only. Same mug, same time. Change nothing else.</p></div>
    <div><h3>Days 3&ndash;5</h3><p>Pay attention around 2 PM. Are you reaching for the second cup, or not? Write it down.</p></div>
    <div><h3>Days 6&ndash;7</h3><p>Decide. If you like the cup, Subscribe &amp; Save keeps it coming for $2.33 a morning.</p></div>
  </div>
</div></section>

<section><div class="wrap" style="max-width:760px">""" + capture("start") + """</div></section>

<section class="alt"><div class="wrap split">
  <div>
    <h2>Questions, answered plainly</h2>
    <details><summary>Does it taste like coffee?</summary><p>Yes. Medium roast, a little smoother than drip. Black is fine; creamer is fine.</p></details>
    <details><summary>How much caffeine is in a scoop?</summary><p>About the same as a regular cup of coffee. One scoop is the serving on the label.</p></details>
    <details><summary>Is it one cup or two?</summary><p>One scoop is the serving on the label.</p></details>
    <details><summary>What if I drink coffee all day?</summary><p>Swap the first cup only for a week, and keep everything else the same.</p></details>
    <details><summary>Can I cancel the subscription?</summary><p>Any time, from the link in your receipt. Pause a month, skip, or cancel. No calls, no forms.</p></details>
    <details><summary>Who ships it, and who answers?</summary><p>MarketPlace Global, the maker, ships from Maple Grove, Minnesota, usually within two business days. You're buying from Rector &amp; Stull LLC, an independent sales representative, and a real person answers hello@themorningupgrades.com. <a href="/shipping-returns.html">Shipping &amp; returns</a>.</p></details>
  </div>
  <div>""" + picker() + """</div>
</div></section>

<section class="dark" style="text-align:center"><div class="wrap">
  <h2>Tomorrow's first cup.</h2>
  <p>One scoop, hot water, thirty seconds. Thirty mornings a bag.</p>
""" + CTA_BLOCK + """
</div></section>
"""


# ---------- GUIDES (search content: no maker/brand names, no claims past the label) ----------
# Answer-first: the lede is a direct 2-3 sentence answer to the question in the H1,
# then specifics, a visible FAQ (also FAQPage data), sources, and related guides.
# Keep it to label facts for the product (MCT powder from coconut, natural caffeine,
# L-theanine, 30 servings, one scoop + hot water). No health claims and nothing past the
# label (tools/check_copy.py enforces the word list); background cites sources and stays descriptive.
_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def _nice(d):
    y, m, dd = d.split("-")
    return f"{_MONTHS[int(m) - 1]} {int(dd)}, {y}"

GUIDE_LINKS = {
    "what-is-mct-coffee.html": "What is MCT coffee?",
    "how-to-make-mct-instant-coffee.html": "How to make instant MCT coffee",
    "l-theanine-and-caffeine.html": "L-theanine and caffeine: what the label means",
    "mct-coffee-vs-butter-coffee.html": "MCT coffee vs. butter coffee",
    "iced-instant-coffee-recipes.html": "Iced instant coffee without clumps",
}

def guide_page(eyebrow, h1, lede, body, fn=None, faq=(), sources=()):
    updated = ""
    if fn in GUIDE_META:
        mod = GUIDE_META[fn][1]
        updated = f'<p class="fine byline">Updated <time datetime="{mod}">{_nice(mod)}</time> &middot; The Morning Upgrade</p>'
    faq_html = ""
    if faq:
        faq_html = '<h2 id="questions">Questions</h2>\n  ' + "\n  ".join(
            f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faq)
    src_html = ""
    if sources:
        src_html = '<h2>Sources</h2>\n  <ol class="fine src">' + "".join(f"<li>{s}</li>" for s in sources) + "</ol>"
    rel = [(f, t) for f, t in GUIDE_LINKS.items() if f != fn]
    rel_html = '<h2>Related guides</h2>\n  <ul class="clean">' + "".join(f'<li><a href="/{f}">{t}</a></li>' for f, t in rel) + "</ul>"
    return f"""
<article><section style="padding-top:36px"><div class="wrap guide">
  <p class="eyebrow"><a href="/guides.html" style="text-decoration:none">Guides</a> &middot; {eyebrow}</p>
  <h1 style="font-size:clamp(32px,4.4vw,48px)">{h1}</h1>
  {updated}
  <p class="lead answer">{lede}</p>
  {body}
  {faq_html}
  {src_html}
  <div class="card" style="margin-top:34px;padding:24px;background:var(--tint);box-shadow:none">
    <h2 style="font-size:22px;margin:0 0 8px">Ours, if you want to skip the blender</h2>
    <p>An instant coffee with MCT powder from coconut, natural caffeine and L-theanine in one scoop. One level scoop in 8 oz of hot water, 30 servings a bag. <a href="/ingredients.html">See every ingredient</a>.</p>
    <p class="bonus" data-bonus hidden><strong>Free with your first order:</strong> the Recipe Pack, 12 ways to drink it plus a 30-morning tracker.</p>
    <p style="margin:0"><a class="btn" href="/shop.html">Shop the coffee</a></p>
  </div>
  {rel_html}
  <p class="fine" style="margin-top:24px">General information, not medical advice. Contains caffeine. Ask your physician before changing what you drink if you're pregnant, nursing, take medication or have a medical condition.</p>
</div></section></article>
"""

SRC_MCT = ('Jadhav HB, Annapure US. <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC9217113/" rel="noopener" target="_blank">'
           'Triglycerides of medium-chain fatty acids: a concise review</a>. <em>Journal of Food Science and Technology</em>. 2023;60(8):2143&ndash;2152 (published online 2022).')
SRC_SOHAIL = ('Sohail A, et al. <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC8794723/" rel="noopener" target="_blank">'
              'The Cognitive-Enhancing Outcomes of Caffeine and L-theanine: A Systematic Review</a>. <em>Cureus</em>. 2021;13(12):e20828.')
SRC_LI = ('Li M-Y, et al. <a href="https://www.frontiersin.org/articles/10.3389/fnut.2022.853846/full" rel="noopener" target="_blank">'
          'L-Theanine: A Unique Functional Amino Acid in Tea (Camellia sinensis L.)</a>. <em>Frontiers in Nutrition</em>. 2022;9:853846.')
SRC_FDA = ('U.S. Food and Drug Administration. <a href="https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much" rel="noopener" target="_blank">'
           'Spilling the Beans: How Much Caffeine is Too Much?</a> Consumer update, content current as of August 28, 2024.')

G_WHATMCT = guide_page("MCT coffee", "What is MCT coffee?",
  "MCT coffee is coffee with medium-chain triglycerides (MCTs) added. MCTs are a type of fat, usually made from coconut or palm kernel oil, and they come either as a clear oil you blend into brewed coffee or as a powder you stir into the cup. In the mug, the main thing you notice is texture: a smoother, creamier body without milk or cream.",
  """
  <h2>What &ldquo;MCT&rdquo; means</h2>
  <p>A triglyceride is three fatty acids attached to a glycerol backbone; it's the basic shape of most fats in food. In a <em>medium-chain</em> triglyceride those fatty acids are a medium length, six to twelve carbon atoms. A 2022 review in the <em>Journal of Food Science and Technology</em> lists them as caproic (C6), caprylic (C8), capric (C10) and lauric (C12) acid. Most of the fat in everyday food has longer chains than that.</p>
  <h2>Where MCTs come from</h2>
  <p>Coconut oil and palm kernel oil are the richest natural sources. The same review puts coconut oil at roughly 46&ndash;54% lauric acid, 5&ndash;10% caprylic acid and 5&ndash;8% capric acid; milk fat has small amounts too. Commercial MCT products separate the medium-chain fats out of those oils, so they're more concentrated than the oil they came from. Labels often name the chain lengths a product uses, such as C8 and C10.</p>
  <h2>MCT oil vs. MCT powder</h2>
  <div class="tbl"><table>
    <tr><th></th><th>MCT oil</th><th>MCT powder</th></tr>
    <tr><td>What it is</td><td>The fats as a clear, nearly flavorless liquid</td><td>MCT oil dried onto a carrier so it disperses in water</td></tr>
    <tr><td>How you use it</td><td>Blend or froth into brewed coffee</td><td>Stir into hot water or coffee</td></tr>
    <tr><td>Without a blender</td><td>Floats on top as an oily film</td><td>Dissolves with a spoon</td></tr>
    <tr><td>In the cup</td><td>Rich, frothy if blended</td><td>Smooth, lightly creamy</td></tr>
  </table></div>
  <p>Powders differ in what the carrier is and how much MCT a serving holds, so read the label of any powder you compare.</p>
  <h2>What's in ours</h2>
  <p>Ours is an instant MCT coffee: MCT powder from coconut is the first ingredient on the label, alongside natural caffeine and L-theanine, the amino acid found in tea leaves. One level scoop (about 6.8 g) in 8 fl oz of hot water makes a cup, and a bag holds 30 servings. <a href="/ingredients.html">Every ingredient is listed here</a>, and <a href="/how-to-make-mct-instant-coffee.html">here's how to make it</a>.</p>
  <h2>What MCT coffee isn't</h2>
  <p>It isn't butter coffee, though the two get mixed up: butter coffee is brewed coffee blended with butter or ghee, usually with MCT oil as well (<a href="/mct-coffee-vs-butter-coffee.html">how they compare</a>). And it's still coffee. It has whatever caffeine the coffee has, so count it the same way. MCTs are a fat, so the nutrition or Supplement Facts panel is the place to see what a serving adds.</p>
  """,
  fn="what-is-mct-coffee.html",
  faq=[
    ("Is MCT coffee the same as butter coffee?", "No. Butter coffee is brewed coffee blended with butter or ghee and usually MCT oil. MCT coffee has MCT oil or powder added and no butter. Butter coffee needs a blender; MCT powder coffee only needs a spoon."),
    ("Is MCT oil the same as coconut oil?", "No. MCT oil is made from coconut or palm kernel oil but keeps only the medium-chain fats, so it stays liquid and has almost no taste. Coconut oil is mostly lauric acid, tastes of coconut and turns solid in a cool kitchen."),
    ("Do I need a blender to make MCT coffee?", "Only with MCT oil, which otherwise floats on top. MCT powder is made to dissolve in hot water, so a spoon is enough."),
    ("Does MCT coffee have caffeine?", "Yes, unless it's made with decaf. Ours contains natural caffeine, about the same as a strong cup of coffee; the exact amount is on the Supplement Facts panel."),
    ("Can I make MCT coffee iced?", "Yes. Dissolve the powder in about 2 oz of hot water first, then pour it over ice and top up with cold water or milk. Cold water alone leaves clumps."),
  ],
  sources=[SRC_MCT])

G_HOWTO = guide_page("How-to", "How to make instant MCT coffee (one scoop, 30 seconds)",
  "Put one level scoop (about 6.8 g) in a mug, pour in 8 fl oz of hot water, and stir until no grains are left, about 15 seconds. That's one serving. Drink it black, add creamer, or dissolve it in a little hot water and pour it over ice.",
  """
  <h2>Step by step</h2>
  <ol class="howto">
    <li><strong>Scoop.</strong> One level scoop, leveled off against the edge of the bag. That's about 6.8 g, the serving size on the label.</li>
    <li><strong>Add hot water.</strong> 8 fl oz (one standard mug) from a kettle or hot-water tap. Hot water dissolves the powder completely; lukewarm water leaves grains.</li>
    <li><strong>Stir.</strong> About 15 seconds, until the surface is smooth.</li>
    <li><strong>Adjust.</strong> Add creamer, milk or sweetener if you like. It's a medium roast and works black.</li>
  </ol>
  <h2>Getting the strength right</h2>
  <p>Change the water, not the scoop. A little less water makes a bolder cup and a little more makes it milder. One scoop is the serving: a second scoop doubles the caffeine as well as the flavor.</p>
  <h2>Three ways to drink it</h2>
  <div class="tbl"><table>
    <tr><th>Style</th><th>How</th></tr>
    <tr><td>Hot</td><td>1 scoop + 8 fl oz hot water, stir.</td></tr>
    <tr><td>Iced</td><td>Dissolve 1 scoop in 2 fl oz hot water, pour over a full glass of ice, top with 6 fl oz cold water or milk. <a href="/iced-instant-coffee-recipes.html">Three iced recipes</a>.</td></tr>
    <tr><td>Latte-style</td><td>Dissolve 1 scoop in 2 fl oz hot water, then top with 6 fl oz steamed or frothed milk.</td></tr>
  </table></div>
  <h2>Habits that help</h2>
  <ul class="clean">
    <li>Have it in the morning. It contains caffeine.</li>
    <li>One scoop a day means a 30-serving bag is a month of mornings.</li>
    <li>Close the bag after each scoop and keep it somewhere dry; moisture makes any powder clump.</li>
  </ul>
  """,
  fn="how-to-make-mct-instant-coffee.html",
  faq=[
    ("Can I make it with cold water?", "Not directly; powders dissolve slowly in cold water and clump. Stir the scoop into about 2 oz of hot water first, then add ice and cold water."),
    ("Can I use milk instead of water?", "Yes. Heat the milk first, or dissolve the scoop in a splash of hot water and then add the milk, hot or cold."),
    ("How much caffeine is in a scoop?", "About the same as a strong cup of coffee. The exact amount is on the Supplement Facts panel on the bag."),
    ("Do I need a machine or a blender?", "No. A mug, hot water and a spoon. The MCT is already in powder form, so nothing needs blending."),
    ("How long does a bag last?", "A bag has 30 servings, so one scoop a day lasts 30 days."),
  ])

G_THEANINE = guide_page("L-theanine", "L-theanine and caffeine: what the pairing is, and what the label means",
  "L-theanine is an amino acid found naturally in tea leaves, and it's often added alongside caffeine because many people describe the combination as smoother than caffeine alone. On a label, &ldquo;caffeine + L-theanine&rdquo; means each serving contains both; the Supplement Facts panel says how much. The research on the pairing is real but small, so treat it as something to try, not a promise.",
  """
  <h2>What L-theanine is</h2>
  <p>L-theanine is an amino acid that occurs naturally in tea leaves. It's one reason a cup of tea can feel different from a cup of coffee with similar caffeine. A 2022 review in <em>Frontiers in Nutrition</em> reported average contents of about 6.6 mg per gram in green tea, 6.3 in white, 6.1 in oolong and 5.1 in black tea across 37 varieties. On its own it's sold as a supplement; more often you'll see it next to caffeine.</p>
  <h2>Why it's paired with caffeine</h2>
  <p>People who use the combination often describe it as smoother than caffeine alone. Researchers have looked at the pair mostly through short lab tests: reaction time, attention tasks, and how alert people say they feel.</p>
  <h2>What the studies actually say</h2>
  <p>A 2021 systematic review in <em>Cureus</em> (Sohail et al.) looked at five studies of caffeine and L-theanine together. Several reported faster reaction times or better scores on attention tasks with the combination. The review is also clear about the limits: the studies were very small (as few as five to twenty people), some included only men, and the authors called for more research.</p>
  <p>So the honest summary: the pairing is popular and has some encouraging small studies behind it. It is not a guarantee of how you'll feel, and it isn't a substitute for sleep.</p>
  <h2>Reading a &ldquo;caffeine + L-theanine&rdquo; label</h2>
  <ul class="clean">
    <li><strong>&ldquo;Natural caffeine&rdquo;</strong> means caffeine from a plant source, such as coffee beans, rather than made in a lab. It's the same molecule either way; the word tells you where it came from.</li>
    <li><strong>Amounts are per serving.</strong> The Supplement Facts panel lists them for one serving (on ours, one level scoop). If ingredients are grouped in a blend, you may see only the blend's total amount.</li>
    <li><strong>The FDA line.</strong> &ldquo;These statements have not been evaluated by the Food and Drug Administration&rdquo; appears on dietary supplements whose labels describe what the product supports. It means what it says: the FDA hasn't reviewed that wording.</li>
    <li><strong>&ldquo;Contains caffeine.&rdquo;</strong> L-theanine doesn't reduce the caffeine in a serving, so count it like any coffee.</li>
  </ul>
  <h2>Counting your caffeine</h2>
  <p>For most healthy adults, the FDA cites 400 mg a day as an amount not generally associated with negative effects, and lists a 12 oz cup of brewed coffee at roughly 113&ndash;247 mg. Sensitivity varies from person to person.</p>
  <h2>How to try it sensibly</h2>
  <ul class="clean">
    <li>Swap, don't stack. Replace a cup of coffee rather than adding caffeine on top.</li>
    <li>Have it in the morning. It still contains caffeine.</li>
    <li>Judge it over a week, not a single cup. Notice your afternoon, not the first hour.</li>
  </ul>
  """,
  fn="l-theanine-and-caffeine.html",
  faq=[
    ("Does L-theanine cancel out caffeine?", "No. Adding L-theanine doesn't lower the amount of caffeine in a serving. Count it the same as any other coffee."),
    ("Where does L-theanine come from?", "It occurs naturally in tea leaves. When it's listed as an ingredient, the product contains it as an added ingredient; the label shows how much per serving."),
    ("How much L-theanine is in a cup of tea?", "It varies with the tea, how much leaf you use and how long it steeps. A 2022 review averaged roughly 5 to 7 mg per gram of dry tea across 37 varieties."),
    ("Can I drink a caffeine + L-theanine coffee in the afternoon?", "It still contains caffeine. If caffeine late in the day affects your sleep, keep it to the morning."),
    ("What does &ldquo;natural caffeine&rdquo; mean on a label?", "Caffeine that comes from a plant, such as coffee beans, rather than being made synthetically. The molecule is the same; the term describes the source."),
  ],
  sources=[SRC_SOHAIL, SRC_LI, SRC_FDA])

G_MCT = guide_page("MCT coffee", "MCT coffee vs. butter coffee: what's the difference?",
  "Butter coffee is brewed coffee blended with butter or ghee, usually plus MCT oil; MCT coffee is coffee with MCT oil or MCT powder added and no butter. Butter coffee needs a blender and comes out thick and frothy. MCT powder coffee is stirred with a spoon and comes out smooth and lightly creamy.",
  """
  <h2>What butter coffee is</h2>
  <p>Butter coffee is brewed coffee blended with unsalted butter or ghee, and usually a spoonful of MCT oil. Blending matters: without it, the fat floats on top in a slick. Done right, you get a frothy, latte-like cup.</p>
  <h2>What MCTs are</h2>
  <p>MCT stands for medium-chain triglycerides: fats whose fatty-acid chains are a medium length, roughly 6 to 12 carbons. Commercial MCT oil is usually made from coconut or palm kernel oil. It's clear, nearly flavorless and stays liquid at room temperature. <a href="/what-is-mct-coffee.html">More on what MCT coffee is</a>.</p>
  <h2>Oil vs. powder</h2>
  <p>MCT <em>powder</em> is MCT oil that has been dried onto a carrier so it dissolves in water instead of sitting on top of it. That's the whole trick: no blender, no oily film, and it gives the cup a creamier body. Check the label of any powder for the carrier and serving size; they vary.</p>
  <h2>Side by side</h2>
  <div class="tbl"><table>
    <tr><th></th><th>Butter coffee</th><th>MCT powder coffee</th></tr>
    <tr><td>Prep</td><td>Brew, add butter and oil, blend 20&ndash;30 s</td><td>Stir a scoop into hot water</td></tr>
    <tr><td>Equipment</td><td>Blender or frother</td><td>A spoon</td></tr>
    <tr><td>Texture</td><td>Thick, frothy, rich</td><td>Smooth, lightly creamy</td></tr>
    <tr><td>Travel</td><td>Hard to make away from home</td><td>Works anywhere with hot water</td></tr>
    <tr><td>Clean-up</td><td>Blender jar, oily cup</td><td>One mug</td></tr>
  </table></div>
  <h2>Which one fits your mornings</h2>
  <p>If you like a weekend ritual and a rich, almost dessert-like cup, butter coffee is worth the blender. If your mornings are a race, a powder that dissolves in a stir is the one you'll actually keep making. Either way, the fat content is real: read the nutrition panel and decide what fits how you eat.</p>
  """,
  fn="mct-coffee-vs-butter-coffee.html",
  faq=[
    ("Can I use coconut oil instead of MCT oil in butter coffee?", "Yes. Coconut oil works but tastes of coconut and turns solid when it cools, so blend it well and drink it warm."),
    ("Do I need a blender for MCT powder?", "No. MCT powder is made to dissolve in hot water; a spoon is enough."),
    ("Which one has more fat?", "Usually butter coffee, since it combines butter and oil. Compare the nutrition panels of what you actually use."),
    ("Can either one be made iced?", "MCT powder can: dissolve it in a little hot water, then add ice. Butter coffee is best hot; the butter firms up in a cold drink."),
  ],
  sources=[SRC_MCT])

G_ICED = guide_page("Recipes", "How to make iced instant coffee without clumps (3 recipes)",
  "Instant coffee and ice water don't mix. One small trick fixes it, then three recipes worth keeping.",
  """
  <h2>The trick: dissolve hot, then go cold</h2>
  <p>Powders dissolve slowly in cold water and clump. Stir your scoop into about 2 oz of hot water first until it's fully dissolved, then pour it over ice and top up with cold water or milk. Thirty seconds, no lumps.</p>
  <h2>1. Iced classic</h2>
  <ul class="clean"><li>1 serving instant coffee, dissolved in 2 oz hot water</li><li>A full glass of ice</li><li>6 oz cold water</li></ul>
  <p>Iced coffee tastes stronger than hot, so add water to taste.</p>
  <h2>2. Iced oat vanilla</h2>
  <ul class="clean"><li>1 serving dissolved in 2 oz hot water</li><li>Ice and 6 oz oat milk</li><li>1 drop vanilla extract</li></ul>
  <p>One drop of vanilla. Two is a candle.</p>
  <h2>3. Blended frapp&eacute;</h2>
  <ul class="clean"><li>1 serving dissolved in 2 oz hot water</li><li>4 oz milk, 1 cup ice, 1 tsp honey</li></ul>
  <p>Blend until smooth and drink it before it separates.</p>
  <h2>A few more tips</h2>
  <ul class="clean"><li>Make coffee ice cubes from leftover coffee so melting ice doesn't water it down.</li><li>Sweeten while the base is hot: syrup and honey mix in better before the ice.</li><li>A handheld milk frother makes cold foam from cold milk in about 20 seconds.</li></ul>
  """,
  fn="iced-instant-coffee-recipes.html")

GUIDES_INDEX = """
<section style="padding-top:36px"><div class="wrap">
  <p class="eyebrow">Guides &amp; recipes</p>
  <h1 style="font-size:clamp(32px,4.4vw,48px)">Better mornings, plainly explained.</h1>
  <p class="lead">Short guides on what's in the cup and how to make it the way you like. Each one starts with the answer.</p>
  <div class="glist" style="margin-top:22px">
    <a href="/what-is-mct-coffee.html"><p class="eyebrow">MCT coffee</p><h2 style="font-size:21px;margin:6px 0">What is MCT coffee?</h2><p>What MCTs are, where they come from, and how oil and powder differ.</p></a>
    <a href="/how-to-make-mct-instant-coffee.html"><p class="eyebrow">How-to</p><h2 style="font-size:21px;margin:6px 0">How to make instant MCT coffee</h2><p>One scoop, hot water, 30 seconds. Plus iced and latte-style.</p></a>
    <a href="/l-theanine-and-caffeine.html"><p class="eyebrow">L-theanine</p><h2 style="font-size:21px;margin:6px 0">L-theanine and caffeine</h2><p>What the pairing is, how to read the label, and what the research does and doesn't say.</p></a>
    <a href="/mct-coffee-vs-butter-coffee.html"><p class="eyebrow">MCT coffee</p><h2 style="font-size:21px;margin:6px 0">MCT coffee vs. butter coffee</h2><p>Blender and butter, or a powder you stir in. How they compare.</p></a>
    <a href="/iced-instant-coffee-recipes.html"><p class="eyebrow">Recipes</p><h2 style="font-size:21px;margin:6px 0">Iced instant coffee without clumps</h2><p>One trick and three recipes worth keeping.</p></a>
  </div>
</div></section>
"""

NOT_FOUND = """
<section style="padding-top:48px"><div class="wrap" style="max-width:720px">
  <p class="eyebrow">Page not found</p>
  <h1 style="font-size:clamp(30px,4vw,44px)">That page isn&rsquo;t here.</h1>
  <p class="lead">The link may be old or have a typo. Here&rsquo;s where most things live:</p>
  <ul class="clean">
    <li><a href="/shop.html">The coffee</a>: instant coffee with MCT powder, natural caffeine and L-theanine, 30 servings a bag.</li>
    <li><a href="/ingredients.html">Every ingredient</a>, from the label.</li>
    <li><a href="/guides.html">Guides &amp; recipes</a>: MCT coffee, L-theanine, iced instant coffee.</li>
    <li><a href="/faq.html">Questions</a>: taste, caffeine, shipping, returns.</li>
  </ul>
  <p><a class="btn" href="/shop.html">See the coffee</a> &nbsp; <a class="btn ghost" href="/">Home</a></p>
  <p class="fine">Still stuck? hello@themorningupgrades.com</p>
</div></section>
"""

PAGES = {
  "404.html": ("Page not found — The Morning Upgrade", "That page isn't here. Try the shop, the ingredients, the guides or the FAQ.", NOT_FOUND, "/img/flatlay.jpg", True),
  "index.html": ("MCT Coffee with L-Theanine, One Scoop | The Morning Upgrade", "Instant coffee with MCT powder, natural caffeine and L-theanine. One scoop in hot water, 30 servings a bag. $69.95 a month or $79.95 a bag.", HOME, "/img/flatlay.jpg", False),
  "shop.html": ("Buy MCT Coffee: $69.95/mo or $79.95 a Bag | The Morning Upgrade", "Instant MCT coffee, 30 servings a bag. $79.95 for one bag or $69.95 a month on Subscribe & Save. Natural caffeine, L-theanine and four more actives.", SHOP, "/img/hero_breakfast.jpg", False),
  "ingredients.html": ("Ingredients: MCT Powder, Caffeine, L-Theanine | The Morning Upgrade", "Seven ingredients and what each one is: MCT powder, natural caffeine, L-theanine, ChromeMate, Paradoxine, Garcinia Cambogia, Saffr'Activ.", ING, "/media/ingredients.jpg", False),
  "faq.html": ("Coffee FAQ: Taste, Caffeine, Shipping | The Morning Upgrade", "How it tastes, how much caffeine is in a scoop, how Subscribe & Save works, shipping, returns, and who you're buying from.", FAQ, "/img/pour.jpg", False),
  "partner.html": ("Build with us — The Morning Upgrade", "Join our team and sell the coffee with the same videos, site and email system we use. Honest numbers first.", PARTNER, "/media/ambient.jpg", False),
  "share.html": ("Share & earn — The Morning Upgrade", "Get your coffee covered by the friends who steal a cup. The referral program, explained in plain language.", SHARE, "/media/ritual.jpg", False),
  "about.html": ("About — The Morning Upgrade", "The Morning Upgrade is run by Rector & Stull LLC, two partners in Idaho and Texas who sell one instant MCT coffee and say plainly what is in it.", ABOUT, "/img/flatlay.jpg", False),
  "shipping-returns.html": ("Shipping & returns — The Morning Upgrade", "$8.95 flat US shipping, Subscribe & Save terms, damaged-item replacement and the 90-day money-back guarantee on unopened bags.", SHIPPING, "/img/flatlay.jpg", False),
  "privacy.html": ("Privacy — The Morning Upgrade", "What we collect, what we do with it, and how to opt out.", PRIVACY, "/img/flatlay.jpg", False),
  "terms.html": ("Terms of sale — The Morning Upgrade", "Terms of sale for The Morning Upgrade: prices, Subscribe & Save renewals, use of the product, returns and liability.", TERMS, "/img/flatlay.jpg", False),
  "order-complete.html": ("Order received — The Morning Upgrade", "Thanks for your order.", ORDER_COMPLETE, "/img/flatlay.jpg", True),
  "start.html": ("One Scoop, Steady Energy | The Morning Upgrade", "Instant coffee with natural caffeine, L-theanine and MCT powder. $69.95 a month or $79.95 a bag, $8.95 flat US shipping, 90-day guarantee on unopened bags.", START, "/media/host_kitchen.jpg", True),
  "thanks.html": ("Your guide is on its way — The Morning Upgrade", "Check your inbox for the 7 Mornings guide.", THANKS, "/img/desk.jpg", True),
  "guides.html": ("Coffee Guides & Recipes | The Morning Upgrade", "Answer-first guides: what MCT coffee is, how to make instant MCT coffee, L-theanine with caffeine, MCT vs. butter coffee, and iced instant coffee recipes.", GUIDES_INDEX, "/img/kitchen_pour.jpg", False),
  "what-is-mct-coffee.html": ("What Is MCT Coffee? MCT Oil vs. Powder, Explained | The Morning Upgrade", "MCT coffee is coffee with medium-chain triglycerides added, as an oil you blend in or a powder you stir in. What MCTs are and how oil and powder differ.", G_WHATMCT, "/img/scoop.jpg", False),
  "how-to-make-mct-instant-coffee.html": ("How to Make Instant MCT Coffee: One Scoop, Hot Water | The Morning Upgrade", "One level scoop in 8 fl oz of hot water, stirred until dissolved. Step by step, plus iced and latte-style versions and how to adjust the strength.", G_HOWTO, "/img/kitchen_pour.jpg", False),
  "mct-coffee-vs-butter-coffee.html": ("MCT Coffee vs. Butter Coffee: What's the Difference? | The Morning Upgrade", "Butter coffee is coffee blended with butter and usually MCT oil; MCT coffee adds MCT oil or powder, no butter. How prep, texture and travel compare.", G_MCT, "/img/pour.jpg", False),
  "l-theanine-and-caffeine.html": ("L-Theanine and Caffeine: What the Label Means | The Morning Upgrade", "L-theanine is the amino acid in tea leaves, often paired with caffeine. What the pairing is, how to read the label, and what small studies found.", G_THEANINE, "/img/desk.jpg", False),
  "iced-instant-coffee-recipes.html": ("Iced Instant Coffee Without Clumps: 3 Recipes | The Morning Upgrade", "Dissolve hot, then go cold: the trick for smooth iced instant coffee, plus iced classic, iced oat vanilla and a blended frappé.", G_ICED, "/img/patio_iced.jpg", False),
}

# Sticky bar: checkout on the buy pages; a link to the shop on guides and the 404; none after a
# purchase or sign-up.
STICKY = {fn: "shop" for fn in list(GUIDE_META) + ["guides.html", "404.html", "about.html", "privacy.html", "terms.html"]}
STICKY.update({"order-complete.html": None, "thanks.html": None})

_changed = set()   # pages whose HTML changed in this build: their sitemap lastmod moves to today
for fn,(title,desc,body,og,noindex) in PAGES.items():
    html_out = page(title,desc,body,og,noindex,nav=("mini" if fn == "start.html" else True),fn=fn,sticky=STICKY.get(fn, "buy"))
    _path = os.path.join(HERE,fn)
    if not os.path.exists(_path) or open(_path).read() != html_out:
        _changed.add(fn)
    with open(_path,"w") as f: f.write(html_out)
    print("wrote",fn)

# ---------- creator links: /c/<code>/ ----------
# One line per creator with a deal (new offers: 15% of the coffee subtotal for 12 months; see README). The page remembers the creator
# (site.js keeps it 60 days, last creator link wins) and sends people to /start. Codes: a-z 0-9 _ -.
CREATORS = {
  "kasey":   "Kasey Loraine Eastland (@kceastlanddd)",
  "macy":    "Macy (@macyexists)",
  "kristen": "Kristen Carmean (@_kristencarmean, via Grail)",
  "emma":    "Emma Sturgeon (@emma_sturgeon, via Key Creative)",
  "laura":   "Laura (@lori_ilc, via Pearpop)",
}

def creator_page(code):
    dest = f"/start.html?ref={code}&utm_source=creator&utm_medium=influencer&utm_campaign={code}"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Morning Upgrade</title><meta name="robots" content="noindex">
<link rel="icon" href="/img/mark.jpg"><meta property="og:title" content="The Morning Upgrade">
<meta property="og:description" content="One scoop, hot water, 30 seconds. No machine, no pods.">
<meta property="og:image" content="https://themorningupgrades.com/media/host_kitchen.jpg">
<meta http-equiv="refresh" content="0; url={dest}">
<script>location.replace({_json.dumps(dest)});</script>
</head><body style="background:#1b130e;color:#f6efe6;font-family:system-ui,sans-serif;padding:24px">
<p><a style="color:#f6efe6" href="{dest}">Continue to The Morning Upgrade</a></p></body></html>
"""

import re as _re
for code in CREATORS:
    assert _re.fullmatch(r"[a-z0-9_-]{2,32}", code), code
    os.makedirs(os.path.join(HERE, "c", code), exist_ok=True)
    with open(os.path.join(HERE, "c", code, "index.html"), "w") as f: f.write(creator_page(code))
print("wrote creator links:", ", ".join(f"/c/{c}" for c in CREATORS))

# ---------- robots.txt + sitemap.xml + llms.txt ----------
import datetime as _dt
_today = _dt.date.today().isoformat()
_indexable = [fn for fn,(t,d,b,og,ni) in PAGES.items() if not ni]
_prio = {"index.html": "1.0", "shop.html": "0.9", "ingredients.html": "0.8", "faq.html": "0.7"}
_prio.update({fn: "0.6" for fn in GUIDE_META})
_old_lastmod = {}
if os.path.exists(os.path.join(HERE, "sitemap.xml")):
    for loc, lm in re.findall(r"<loc>(.*?)</loc><lastmod>(.*?)</lastmod>", open(os.path.join(HERE, "sitemap.xml")).read()):
        _old_lastmod[loc] = lm
with open(os.path.join(HERE, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for fn in _indexable:
        lm = _today if fn in _changed else _old_lastmod.get(url_for(fn), _today)
        f.write(f"  <url><loc>{url_for(fn)}</loc><lastmod>{lm}</lastmod><priority>{_prio.get(fn, '0.5')}</priority></url>\n")
    f.write("</urlset>\n")

# Search and AI crawlers are welcome everywhere public. A crawler that matches a named
# group ignores the * group, so the named group repeats the same rules.
AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
               "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot", "Bingbot", "Applebot",
               "Applebot-Extended", "DuckAssistBot"]
_rules = "Allow: /\nDisallow: /order-complete.html\nDisallow: /thanks.html\nDisallow: /c/\n"
with open(os.path.join(HERE, "robots.txt"), "w") as f:
    f.write("# Search engines and AI assistants may crawl and cite every public page.\n")
    f.write("".join(f"User-agent: {a}\n" for a in AI_CRAWLERS) + _rules + "\n")
    f.write("User-agent: *\n" + _rules + "\nSitemap: " + SITE + "/sitemap.xml\n")

# llms.txt (llmstxt.org): plain facts for AI assistants. Same rules as the rest of the
# search-facing text: label facts only, no maker trademarks, no claims past the label.
def _llm_link(fn):
    t, d = PAGES[fn][0], PAGES[fn][1]
    return f"- [{_html.unescape(t.split(' | ')[0].split(' — ')[0])}]({url_for(fn)}): {_html.unescape(d)}"
LLMS = f"""# The Morning Upgrade

> The Morning Upgrade (themorningupgrades.com) sells one product in the United States: a medium-roast instant coffee made with MCT powder from coconut, natural caffeine and L-theanine. One level scoop in 8 fl oz of hot water makes a cup, and a bag holds 30 servings. The site is run by Rector & Stull LLC, an independent sales representative (ISR) for the manufacturer; Rector & Stull is not the manufacturer.

Facts as stated on the site (updated {_today}):

- Price: $79.95 for one bag (30 servings), or $69.95 a month with Subscribe & Save (one bag every 30 days; pause, skip or cancel anytime from the receipt link).
- Serving: one level scoop, about 6.8 g, in 8 fl oz of hot water. 30 servings per 7.2 oz (204 g) bag. Medium roast; works black, with creamer or over ice.
- Shipping: US addresses only, flat $8.95 per bag. Orders ship from Minnesota within about two business days, then 3-6 days in transit.
- Returns: the maker's 90-day money-back guarantee on unopened bags; damaged or incorrect items are replaced if reported within 30 days of delivery.
- Contains caffeine. For adults; not for children or anyone pregnant or nursing. Ask a physician first if you take medication or have a medical condition.
- Product copy quotes the label rather than adding claims of its own. The guides are general information, not medical advice.
- People shown in the site's videos are AI presenters, and the site says so.
- Contact: hello@themorningupgrades.com. Rector & Stull LLC, 30 N Gould St Ste R, Sheridan, WY 82801.

## Product

{_llm_link("shop.html")}
{_llm_link("ingredients.html")}
{_llm_link("faq.html")}
{_llm_link("shipping-returns.html")}

## Guides

{chr(10).join(_llm_link(fn) for fn in GUIDE_LINKS)}

## Company

{_llm_link("about.html")}
{_llm_link("terms.html")}
{_llm_link("privacy.html")}
"""
with open(os.path.join(HERE, "llms.txt"), "w") as f:
    f.write(LLMS)
print("wrote sitemap.xml, robots.txt, llms.txt")
