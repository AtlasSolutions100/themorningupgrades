#!/usr/bin/env python3
"""Builds the themorningupgrades.com pages from shared chrome. Run: python3 build_site.py"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))

NAV = """
<nav class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/mark.jpg" alt=""><b>The Morning Upgrade</b></a>
  <button class="burger" aria-label="Menu">Menu</button>
  <div class="menu">
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
<footer><div class="wrap">
  <div class="cols">
    <div>
      <h4>The Morning Upgrade</h4>
      <p>Coffee that keeps up past lunch. One scoop, hot water, smooth energy and sharp focus. Sold by Rector &amp; Stull LLC, Independent ISR of MarketPlace Global products and services.</p>
      <p>hello@themorningupgrades.com</p>
    </div>
    <div>
      <h4>Shop</h4>
      <a href="/shop.html">CoreJava coffee</a>
      <a href="/ingredients.html">What's in it</a>
      <a href="/faq.html">Questions</a>
      <a href="/shipping-returns.html">Shipping &amp; returns</a>
      <a href="https://billing.stripe.com/p/login/3cIbJ3fEv6XIbtk8iw4wM00" rel="noopener">Manage subscription</a>
    </div>
    <div>
      <h4>Company</h4>
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

def page(title, desc, body, og_image="/img/flatlay.jpg", noindex=False, extra_head="", nav=True):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="icon" href="/img/mark.jpg">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://themorningupgrades.com{og_image}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js"></script>
{extra_head}
</head>
<body>
<div class="bar"><span class="isr-logo"></span>Rector &amp; Stull LLC &middot; Independent MarketPlace Global ISR &middot; <a href="https://marketplaceglobal.com/rectorandstull" rel="noopener">MarketPlace Global corporate site &rarr;</a></div>
{NAV if nav else ''}
{body}
{FOOTER}
<div class="sticky"><div><b>CoreJava &middot; 30 servings</b><span>from $69.95/mo &middot; <span data-ship="short">$8.95 US shipping</span></span></div><a class="btn" data-buy="subscribe" href="#">Get it</a></div>
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
    <div><span>Afternoon</span><span>The slide</span><span>The slide, then jitters</span><span class="hl">That's the point</span></div>
    <div><span>What's in it</span><span>Caffeine, sugar, milk</span><span>Caffeine</span><span class="hl">Caffeine + L-theanine + 5 more</span></div>
  </div>
  <p class="fine" style="text-align:center;margin-top:14px">Caf&eacute; and drip costs are typical US prices; yours will vary. CoreJava prices are ours.</p>
</div></section>
"""
FOUNDER = """
<section class="alt"><div class="wrap split">
  <div class="frame p45"><img src="/img/desk.jpg" alt="Laptop, mug and a bag of CoreJava on a desk" loading="lazy"></div>
  <div>
    <p class="eyebrow">A note from the two of us</p>
    <h2>We're new. Here's who you're buying from.</h2>
    <p>We're Rector &amp; Stull, two partners, one in Idaho and one in Texas, both of whom run on coffee and spend afternoons on calls. We drank CoreJava for a while before we decided to sell it. The reason we did is simple: the first cup stopped being the cup that needed a second one.</p>
    <p>We don't have ten thousand reviews yet. We have a bag we drink every morning, a label we quote instead of embellish, and an email a real person answers. If it's not for you, say so and we'll make it right.</p>
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

def trust_row(dark=False):
    return f"""<div class="trusticons{' on-dark' if dark else ''}">
  <span>{ICON_TRUCK}<b data-ship="trust">$8.95 flat US shipping</b></span>
  <span>{ICON_SHIELD}<b data-ship="damage">Made right if it arrives damaged</b></span>
  <span>{ICON_LOOP}<b>Cancel anytime</b></span>
</div>"""

def picker(cta="Add to cart", note=True):
    return f"""<div class="picker" data-picker>
  <label class="opt on"><input type="radio" name="plan" value="subscribe" checked><span class="radio"></span>
    <span class="ptxt"><b>Subscribe &amp; Save</b><em>Most popular</em><span class="pp">$69.95<small>/mo &middot; $2.33 a morning</small></span><span class="pfine">A bag a month. Pause, skip or cancel from your receipt.</span></span></label>
  <label class="opt"><input type="radio" name="plan" value="onetime"><span class="radio"></span>
    <span class="ptxt"><b>One bag</b><span class="pp">$79.95<small> &middot; $2.67 a morning</small></span><span class="pfine">30 servings. No commitment.</span></span></label>
  <a class="btn big" data-buy="subscribe" data-picker-btn href="#">{cta} &rarr;</a>
  {'<p class="fine" style="text-align:center;margin:12px 0 0"><span data-ship="short">$8.95 US shipping</span> &middot; 90-day guarantee on unopened bags &middot; pause or cancel anytime</p>' if note else ''}
</div>"""

INGCARDS = f"""<div class="ingcards">
  <div>{ICON_COCO}<div><h3>MCT powder</h3><p>The creamy part. From coconut, and the first thing on the label.</p></div></div>
  <div>{ICON_LEAF}<div><h3>Natural caffeine + L-theanine</h3><p>Coffee-bean caffeine with the amino acid in green tea. Focus without the edge.</p></div></div>
  <div>{ICON_SCOOP}<div><h3>30 servings. One scoop.</h3><p>Hot water, 30 seconds, no machine. A month of mornings in one bag.</p></div></div>
</div>"""

CALLOUTS = """<div class="callouts-wrap">
  <div class="bagstage">
    <img src="/img/bag.png" alt="CoreJava bag, front label" loading="lazy">
    <span class="chip c1"><b>MCT powder</b>the creamy part</span>
    <span class="chip c2"><b>L-theanine</b>focus without the edge</span>
    <span class="chip c3"><b>Natural caffeine</b>about one cup's worth</span>
    <span class="chip c4"><b>30 servings</b>one scoop a morning</span>
  </div>
</div>"""

HOSTSTRIP = """<section><div class="wrap">
  <h2 style="text-align:center">Real routine, honest hosts.</h2>
  <p style="text-align:center;color:var(--muted);max-width:60ch;margin:0 auto 26px">The people in our videos are AI presenters, and we say so on every one. They show the coffee, the scoop and the label; they don't claim results.</p>
  <div class="hoststrip">
    <div class="frame phone vid"><video muted loop playsinline autoplay poster="/media/host_kitchen.jpg"><source src="/media/host_kitchen.mp4" type="video/mp4"></video><button class="unmute" type="button" data-unmute aria-label="Turn sound on">&#9654; Sound on</button><span class="ailabel">AI host</span></div>
    <div class="frame phone vid"><video muted loop playsinline autoplay poster="/media/host_desk.jpg"><source src="/media/host_desk.mp4" type="video/mp4"></video><button class="unmute" type="button" data-unmute aria-label="Turn sound on">&#9654; Sound on</button><span class="ailabel">AI host</span></div>
    <div class="frame phone vid"><video muted loop playsinline autoplay poster="/media/host_gymbag.jpg"><source src="/media/host_gymbag.mp4" type="video/mp4"></video><button class="unmute" type="button" data-unmute aria-label="Turn sound on">&#9654; Sound on</button><span class="ailabel">AI host</span></div>
  </div>
</div></section>"""

def hero_c(h1="One scoop. No 2 PM crash.", strip=("Smooth energy","Sharp focus","30 mornings a bag"), video=True):
    striphtml = " <i>/</i> ".join(f"<span>{t}</span>" for t in strip)
    media = ('<div class="frame phone vid device light"><video autoplay muted loop playsinline poster="/media/host_kitchen.jpg"><source src="/media/host_kitchen.mp4" type="video/mp4"></video><button class="unmute" type="button" data-unmute aria-label="Turn sound on">&#9654; Sound on</button><span class="ailabel">AI host</span></div>') if video else ''
    return f"""
<div class="heroC"><div class="wrap">
  <h1 class="h1c">{h1}</h1>
  <p class="stripc">{striphtml}</p>
  <div class="heroC-grid">
    <div class="heroC-left">{CALLOUTS}</div>
    <div class="heroC-right">
      <p class="eyebrow" style="margin-bottom:6px">CoreJava &middot; instant performance coffee</p>
      <p class="lead" style="font-size:17px;margin:0 0 6px">Natural caffeine + L-theanine + MCT powder. One scoop, hot water, 30 seconds. Supports healthy appetite control, focus and energy.</p>
      {picker()}
    </div>
  </div>
  {trust_row(dark=False)}
</div></div>
"""

HOSTS = """
<section><div class="wrap">
  <p class="eyebrow" style="text-align:center">Meet the hosts</p>
  <h2 style="text-align:center">The people in our videos are AI presenters.</h2>
  <p style="text-align:center;color:var(--muted);max-width:62ch;margin:0 auto 26px">We say so up front. They show you the coffee, the scoop and what's on the label; they don't claim results, because they haven't had any. Real answers come from a real inbox: hello@themorningupgrades.com.</p>
  <div class="hosts">
    <div class="frame p45"><img src="/img/host_p3_marble.jpg" alt="AI host holding a bag of CoreJava at a marble kitchen counter" loading="lazy"><span class="ailabel">AI host</span></div>
    <div class="frame p45"><img src="/img/host_p1_raglan.jpg" alt="AI host holding a bag of CoreJava in a living room" loading="lazy"><span class="ailabel">AI host</span></div>
    <div class="frame p45"><img src="/img/host_p2_sofa.jpg" alt="AI host on a yellow sofa with a bag of CoreJava and a mug" loading="lazy"><span class="ailabel">AI host</span></div>
    <div class="frame p45"><img src="/img/host_p4_gaze.jpg" alt="AI host on a bed with a laptop and a bag of CoreJava" loading="lazy"><span class="ailabel">AI host</span></div>
  </div>
</div></section>
"""
# ---------- HOME ----------
HOME = """
""" + hero_c(h1="One scoop. No 2 PM crash.") + """
"""+"""

<section class="alt"><div class="wrap">
  <h2>Three mornings, three problems</h2>
  <div class="grid3">
    <div class="card"><h3>The 2pm slide</h3><p>A big cup hits fast and leaves fast. By the afternoon meeting your focus has gone home without you.</p></div>
    <div class="card"><h3>The second-cup jitters</h3><p>So you pour another, and now your hands are busy and your sleep is worse. Tomorrow starts tired.</p></div>
    <div class="card"><h3>The $6 habit</h3><p>A latte on the way in, a cold brew after lunch. Two stops, two lines, and the same slump either way.</p></div>
  </div>
</div></section>

<section><div class="wrap split">
  <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ritual.jpg"><source src="/media/ritual.mp4" type="video/mp4"></video></div>
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
    <p>MCT powder, for a creamy cup. Natural caffeine from coffee beans. L-theanine, the amino acid in green tea. ChromeMate, a patented chromium. Paradoxine, grains of paradise extract. Garcinia Cambogia fruit extract. Saffr'Activ saffron extract. The label says what it does: supports healthy appetite control, focus and energy.</p>
    <p><a class="btn" href="/ingredients.html">See every ingredient</a></p>
  </div>
  <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ingredients.jpg"><source src="/media/ingredients.mp4" type="video/mp4"></video></div>
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
        <label>First name</label><input type="text" name="first_name" autocomplete="given-name">
        <label>Email</label><input type="email" name="email" required autocomplete="email">
        <input type="hidden" name="quiz_result"><input type="hidden" name="cups"><input type="hidden" name="want">
        <p style="margin:16px 0 8px"><button class="btn" type="submit">Send me the guide</button></p>
        <p class="fine">You'll get the guide right away and a short series of notes after it. Unsubscribe in one click.</p>
        <p id="tmu-msg" class="fine" role="status" style="color:var(--copper2)"></p>
      </form>
    </div>
  </div>
</div></section>

""" + HOSTSTRIP + """
<section><div class="wrap split">
  <div>
    <h2>Questions, answered plainly</h2>
    <details><summary>Does it taste like coffee?</summary><p>Yes. Medium roast, a little smoother than drip. Black is fine; creamer is fine.</p></details>
    <details><summary>Is it one cup or two?</summary><p>One scoop is the serving. Most people find one is the right amount.</p></details>
    <details><summary>What if I drink coffee all day?</summary><p>Swap the first cup only for a week. That's the cup that sets the curve for the rest of the day.</p></details>
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
  <p>One scoop, hot water, and an afternoon that doesn't need rescuing.</p>
""" + CTA_BLOCK + """
</div></section>

<script>
(function(){
  var ans={}, f=document.getElementById('tmu-form'), msg=document.getElementById('tmu-msg');
  var results={
    crash:['The 2pm crash','Your first cup sets a curve that peaks early and slides into the afternoon. The guide starts with the one change that flattens it.'],
    jitters:['Sharp, not shaky','You don\\u2019t need more caffeine; you need a steadier kind. Day 1 of the guide is about the pairing that makes the difference.'],
    parent:['The 3pm pickup','Your day has a second shift. The guide is built around one cup that\\u2019s still working when it starts.'],
    desk:['Mid-morning fade','The slump arrives before lunch, which usually means the cup is doing too much too fast. The guide fixes the timing first.']
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
    <div class="frame p45"><img src="/img/hero_breakfast.jpg" alt="CoreJava coffee bag on a breakfast table in morning light"></div>
    <div class="gallery">
      <div class="frame" style="aspect-ratio:9/16"><video muted loop playsinline autoplay poster="/media/product_callouts_v2.jpg"><source src="/media/product_callouts_v2.mp4" type="video/mp4"></video></div>
      <div class="frame" style="aspect-ratio:9/16"><img src="/img/kitchen_pour.jpg" alt="Pouring hot water next to a CoreJava bag" loading="lazy"></div>
      <div class="frame" style="aspect-ratio:9/16"><video muted loop playsinline autoplay poster="/media/iced.jpg"><source src="/media/iced.mp4" type="video/mp4"></video></div>
    </div>
  </div>
  <div>
    <p class="eyebrow">CoreJava &middot; performance coffee</p>
    <h1 style="font-size:clamp(34px,4.4vw,52px)">CoreJava Coffee, 30 servings.</h1>
    <p class="lead">Medium-roast instant coffee built around natural caffeine and L-theanine, with ChromeMate, Paradoxine, Garcinia Cambogia and Saffr'Activ. Supports healthy appetite control, focus and energy. One level scoop in 8 oz of hot water.</p>
    """ + picker(note=False) + """
    <p class="fine"><span data-ship="long">Ships to all 50 states.</span> Cancel anytime &middot; <span data-ship="checkout">secure checkout</span> &middot; <span data-ship="damage">made right if it arrives damaged</span>. Questions before you buy: hello@themorningupgrades.com.</p>
    <h3 style="margin-top:30px">Details</h3>
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
    <div><h3>Days 3&ndash;5</h3><p>Most people stop reaching for the second cup here. If you still want one, make it this one.</p></div>
    <div><h3>Days 6&ndash;7</h3><p>Decide. If the afternoon is different, Subscribe &amp; Save keeps it that way for $2.33 a cup.</p></div>
  </div>
</div></section>
""" + HOSTS + COMPARE + FOUNDER + """
<section class="dark" style="text-align:center"><div class="wrap"><h2>Start tomorrow.</h2>""" + CTA_BLOCK + """</div></section>
"""

# ---------- INGREDIENTS ----------
ING = """
<section class="tight"><div class="wrap split" style="align-items:center">
  """ + CALLOUTS + """
  <div>
    <p class="eyebrow">What's in it</p>
    <h1 style="font-size:clamp(34px,4.4vw,56px)">Seven ingredients. Nothing hidden behind a blend.</h1>
    <p class="lead">We'll tell you where each one comes from. For what the blend does, the label is the authority: <em>supports healthy appetite control, focus and energy.</em> We don't go past that.</p>
  </div>
</div></section>
<section class="dark" style="padding-top:0"><div class="wrap">
  <div class="split" style="margin-bottom:40px">
    <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ingredients.jpg"><source src="/media/ingredients.mp4" type="video/mp4"></video></div>
    <div class="ing" style="grid-template-columns:1fr 1fr">
      <div class="card"><b>MCT powder</b><h3>First on the label</h3><p>Medium-chain triglycerides, usually from coconut oil, in powder form. It&rsquo;s what gives the cup body and a creamy texture without adding cream.</p></div>
      <div class="card"><b>Natural caffeine</b><h3>From coffee beans</h3><p>The same caffeine you already drink, from coffee, not synthesized. About the amount in a strong cup.</p></div>
      <div class="card"><b>L-theanine</b><h3>The amino acid in green tea</h3><p>Found naturally in tea leaves. Commonly paired with caffeine; many people describe the pairing as smoother than coffee alone.</p></div>
      <div class="card"><b>ChromeMate&reg;</b><h3>A patented chromium</h3><p>A branded form of the mineral chromium, bound to niacin. Chromium is an essential trace mineral.</p></div>
      <div class="card"><b>Paradoxine&reg;</b><h3>Grains of paradise extract</h3><p>A standardized extract of <em>Aframomum melegueta</em>, a West African seed in the ginger family.</p></div>
      <div class="card"><b>Garcinia Cambogia</b><h3>Fruit extract</h3><p>Extract of the rind of a small tropical fruit, standardized for hydroxycitric acid.</p></div>
      <div class="card"><b>Saffr'Activ&reg;</b><h3>Saffron extract</h3><p>A standardized extract of saffron stigmas, the same spice used in cooking.</p></div>
    </div>
  </div>
  <p class="fine">Full Supplement Facts, including amounts per serving and other ingredients, are printed on the bag. Trademarks belong to their respective ingredient suppliers.</p>
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
  <details><summary>Is it one cup or two?</summary><p>One scoop is the serving. Most people find one is the right amount.</p></details>
  <details><summary>What does it do?</summary><p>The label says: supports healthy appetite control, focus and energy. We stick to that. It's a dietary supplement, not a medicine, and it hasn't been evaluated by the FDA.</p></details>
  <details><summary>Who shouldn't take it?</summary><p>Children, and anyone pregnant or nursing. If you take medication or have a medical condition, ask your physician first.</p></details>
  <h2>Ordering</h2>
  <details><summary>How does Subscribe &amp; Save work?</summary><p>A bag ships every 30 days at $69.95. Pause a month, cancel, or update your card any time from the link in your receipt or at <a href="https://billing.stripe.com/p/login/3cIbJ3fEv6XIbtk8iw4wM00">the subscription portal</a>. No calls.</p></details>
  <details><summary>Where does it ship from, how fast, and what does shipping cost?</summary><p><span data-ship="policy">Right now orders are fulfilled by the maker, MarketPlace Global, and shipping is calculated at their checkout before you pay.</span> US addresses only for now. Tracking arrives by email.</p></details>
  <details><summary>Returns?</summary><p>If a bag arrives damaged or wrong, email hello@themorningupgrades.com within 14 days and we'll replace it or refund it. Full policy on the <a href="/shipping-returns.html">Shipping &amp; returns</a> page.</p></details>
  <details><summary>Who am I buying from?</summary><p>Rector &amp; Stull LLC, Independent ISR of MarketPlace Global products and services. MarketPlace Global makes CoreJava; we sell it.</p></details>
  <h2>The business</h2>
  <details><summary>Is this an MLM?</summary><p>MarketPlace Global is a direct sales company that sells through Independent Sales Representatives (ISRs), and ISRs can sponsor other ISRs. We earn on the coffee we sell and on sales made by partners we introduce. If that interests you, the <a href="/partner.html">Partner page</a> explains it without the hype.</p></details>
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
  <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ambient.jpg"><source src="/media/ambient.mp4" type="video/mp4"></video></div>
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
      <label>First name</label><input type="text" name="first_name" autocomplete="given-name">
      <label>Email</label><input type="email" name="email" required autocomplete="email">
      <label>Phone (optional)</label><input type="tel" name="phone" autocomplete="tel">
      <label>Where are you starting from?</label>
      <select name="experience">
        <option value="new">New to selling online</option>
        <option value="social">I post on social already</option>
        <option value="sales">I've done sales or direct sales before</option>
        <option value="mpg">I'm already a MarketPlace Global ISR</option>
      </select>
      <p class="fine" style="margin:6px 0 0">If you already have a MarketPlace Global ISR agreement, we can&rsquo;t enroll you under a different sponsor (MPG policy 3.6) &mdash; but we&rsquo;re happy to compare notes.</p>
      <label>Anything you want us to know?</label><textarea name="note"></textarea>
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
  <div class="frame phone"><img src="/img/gym.jpg" alt="Woman on a yoga mat holding a CoreJava bag and a mug"></div>
</div></section>

<section class="alt" id="levels"><div class="wrap">
  <h2 style="text-align:center">Three levels. No pressure to climb.</h2>
  <div class="levels">
    <div class="lvl">
      <span class="num">1</span>
      <h3>Sip</h3>
      <p class="tag2">Just drink it</p>
      <p>One bag, or Subscribe &amp; Save. Enjoy your mornings. That&rsquo;s it; most people stay right here and that&rsquo;s the point.</p>
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
      <li><strong>To stay eligible for team commissions you keep 50 QV a month,</strong> which is roughly one bag of your own or one customer order. Most people in the Share level do this by drinking the coffee they were already buying.</li>
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
    <p>Everything on this site that earns us money says so. Every video that uses an AI-generated scene is labeled. If something's unclear, email us and a human will answer: hello@themorningupgrades.com.</p>
    <p><a class="btn" href="/shop.html">Buy CoreJava</a> &nbsp; <a class="btn ghost" href="/partner.html">Partner with us</a></p>
  </div>
  <div class="frame p45"><img src="/img/bag_shadows.jpg" alt="CoreJava bag with leaf shadows"></div>
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
  <p>MarketPlace Global, the maker, backs every customer order with a 90-day money-back guarantee on unopened product in resalable condition, and replaces anything that arrives damaged or defective if you tell us within ten business days. Email hello@themorningupgrades.com with your order number (and a photo if it&rsquo;s damaged) and we handle the return authorization for you. Return shipping on change-of-mind returns is paid by the customer; original shipping isn&rsquo;t refunded. Opened bags can&rsquo;t be returned for a change of mind, for food-safety reasons.</p>
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
  <ul><li><strong>If you take the quiz:</strong> your answers, first name and email, so we can send you the guide and the follow-up emails.</li><li><strong>If you buy:</strong> your name, shipping address, email and phone. Payment details go to Stripe; we never see your card number. To fulfil your order we create a customer account for you with MarketPlace Global, the maker, and pass them your name, address, email and phone so they can ship to you and honor their guarantee. Their <a href="https://marketplaceglobal.com/rectorandstull/privacy-policy">privacy policy</a> covers what they do with it.</li><li><strong>If you ask about partnering:</strong> what you type into the form.</li><li><strong>Automatically:</strong> Google Analytics records pages viewed, where visitors came from, and button clicks, with IP addresses anonymized. A TikTok pixel, and if we run ads there a Meta pixel, record page views and purchases so we can measure which ads work.</li></ul>
  <h2>What we do with it</h2>
  <p>Fulfil orders, send the emails you signed up for, answer your questions, and measure which of our posts bring people here. We don't sell your data. We don't share it except with the services that make the site work: Stripe (payments), MarketPlace Global (the maker, who fulfils and ships orders), Klaviyo (email), GitHub (hosting), and analytics providers.</p>
  <h2>Your choices</h2>
  <p>Every email has an unsubscribe link. To see, correct or delete what we hold about you, email hello@themorningupgrades.com and we'll do it within 30 days.</p>
  <h2>Cookies</h2>
  <p>Google Analytics and the TikTok pixel set measurement cookies; you can block them with the <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">Google Analytics opt-out add-on</a> or your browser settings. Stripe and Klaviyo set the ones they need to work. TikTok&rsquo;s ad choices are at tiktok.com/legal/ads-and-your-data. If a Meta pixel is active, it sets its own; you can opt out at facebook.com/ads/preferences.</p>
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
      <li>Give it a week before you decide. Day 3 is usually where people notice.</li>
    </ul>
    <p><a class="btn ghost" href="/">Back to the site</a></p>
  </div>
</div></section>
<script>track('Purchase');</script>
"""

THANKS = """
<section style="padding-top:36px"><div class="wrap" style="max-width:720px">
  <div class="card" style="padding:34px 30px">
    <div class="frame" style="aspect-ratio:16/10;margin-bottom:22px;box-shadow:none"><img src="/img/desk.jpg" alt="A mug and a bag of coffee on a desk"></div>
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

START = """
""" + hero_c() + """
<section class="alt"><div class="wrap">""" + INGCARDS.replace("ingcards","ingcards light") + """</div></section>

<section><div class="wrap split" style="align-items:center">
  <div class="frame phone vid"><video autoplay muted loop playsinline poster="/media/host_kitchen.jpg"><source src="/media/host_kitchen.mp4" type="video/mp4"></video><button class="unmute" type="button" data-unmute aria-label="Turn sound on">&#9654; Sound on</button><span class="ailabel">AI host</span></div>
  <div>
    <p class="eyebrow">One scoop. Seven things on the label.</p>
    <h2>Nothing hidden behind a blend.</h2>
    <p>MCT powder, natural caffeine, L-theanine, ChromeMate&reg; chromium, Paradoxine&reg; grains of paradise, Garcinia Cambogia and Saffr'Activ&reg; saffron extract. The label says what it does: supports healthy appetite control, focus and energy. We quote it; we don't embellish it.</p>
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
    <div><h3>Days 6&ndash;7</h3><p>Decide. If the afternoon is different, Subscribe &amp; Save keeps it that way for $2.33 a cup.</p></div>
  </div>
</div></section>
""" + HOSTSTRIP + """
<section class="alt"><div class="wrap">
  <div class="guar">
    <div><b>Shipping</b><span data-ship="policy">Orders ship from Minnesota within about two business days, then 3&ndash;6 days in transit. US shipping is a flat $8.95 a bag.</span></div>
    <div><b>Guarantee</b><span>MarketPlace Global, the maker, backs every customer order with a 90-day money-back guarantee on unopened product, and replaces anything that arrives damaged if you tell us within ten business days. <a href="/shipping-returns.html">The full policy</a>.</span></div>
    <div><b>Who you're buying from</b><span>Rector &amp; Stull LLC, Independent Sales Representative of MarketPlace Global. A real inbox answers: hello@themorningupgrades.com.</span></div>
  </div>
</div></section>

<section><div class="wrap split">
  <div>
    <h2>Questions, answered plainly</h2>
    <details><summary>Does it taste like coffee?</summary><p>Yes. Medium roast, a little smoother than drip. Black is fine; creamer is fine.</p></details>
    <details><summary>How much caffeine is in a scoop?</summary><p>About the same as a regular cup of coffee. One scoop is the serving; most people find one is the right amount.</p></details>
    <details><summary>What does L-theanine do?</summary><p>It's the amino acid in green tea that people pair with caffeine for a steadier feel. We quote the label on what the product supports and leave the rest to you.</p></details>
    <details><summary>Can I cancel the subscription?</summary><p>Any time, from the link in your receipt. Pause a month, skip, or cancel. No calls, no forms.</p></details>
    <details><summary>Is this an MLM product?</summary><p>CoreJava is made by MarketPlace Global, a direct-sales company, and we sell it as their Independent Sales Representatives. Buying a bag makes you a customer and nothing else. <a href="/share.html">Share &amp; earn</a> exists if you want it; nobody will call you.</p></details>
  </div>
  <div>""" + picker(cta="Get CoreJava") + """</div>
</div></section>

<section class="dark" style="text-align:center"><div class="wrap">
  <h2>Tomorrow's first cup.</h2>
  <p>One scoop, hot water, and an afternoon that doesn't need rescuing.</p>
""" + CTA_BLOCK + """
</div></section>
"""

PAGES = {
  "index.html": ("The Morning Upgrade — Coffee that keeps up past lunch", "CoreJava performance coffee: natural caffeine + L-theanine, one scoop, hot water. $79.95 a bag or $69.95 a month. Take the 60-second quiz.", HOME, "/img/flatlay.jpg", False),
  "shop.html": ("Buy CoreJava Coffee — The Morning Upgrade", "CoreJava coffee, 30 servings. $79.95 one bag or $69.95 a month on Subscribe & Save. Natural caffeine, L-theanine and four more actives.", SHOP, "/img/hero_breakfast.jpg", False),
  "ingredients.html": ("What's in CoreJava — The Morning Upgrade", "Seven ingredients and what each one is: MCT powder, natural caffeine, L-theanine, ChromeMate, Paradoxine, Garcinia Cambogia, Saffr'Activ.", ING, "/media/ingredients.jpg", False),
  "faq.html": ("FAQ — The Morning Upgrade", "Taste, caffeine, shipping, subscriptions, returns, and who you're buying from.", FAQ, "/img/pour.jpg", False),
  "partner.html": ("Build with us — The Morning Upgrade", "Join our MarketPlace Global team and sell CoreJava with the same videos, site and email system we use. Honest numbers first.", PARTNER, "/media/ambient.jpg", False),
  "share.html": ("Share & earn — The Morning Upgrade", "Get your coffee covered by the friends who steal a cup. MarketPlace Global's referral program, explained in plain language.", SHARE, "/media/ritual.jpg", False),
  "about.html": ("About — The Morning Upgrade", "Rector & Stull LLC, Independent Sales Representatives for MarketPlace Global, and why we sell one bag of coffee.", ABOUT, "/img/flatlay.jpg", False),
  "shipping-returns.html": ("Shipping & returns — The Morning Upgrade", "$8.95 flat US shipping, Subscribe & Save terms, damaged-item replacement and the 90-day money-back guarantee on unopened bags.", SHIPPING, "/img/flatlay.jpg", False),
  "privacy.html": ("Privacy — The Morning Upgrade", "What we collect, what we do with it, and how to opt out.", PRIVACY, "/img/flatlay.jpg", False),
  "terms.html": ("Terms of sale — The Morning Upgrade", "Terms for buying CoreJava from Rector & Stull LLC.", TERMS, "/img/flatlay.jpg", False),
  "order-complete.html": ("Order received — The Morning Upgrade", "Thanks for your order.", ORDER_COMPLETE, "/img/flatlay.jpg", True),
  "start.html": ("CoreJava — The 2 PM cup, solved at 7 AM | The Morning Upgrade", "Instant performance coffee: natural caffeine + L-theanine + MCT powder. $69.95 a month or $79.95 a bag, $8.95 flat US shipping, 90-day guarantee on unopened bags.", START, "/media/host_kitchen.jpg", True),
  "thanks.html": ("Your guide is on its way — The Morning Upgrade", "Check your inbox for the 7 Mornings guide.", THANKS, "/img/desk.jpg", True),
}

for fn,(title,desc,body,og,noindex) in PAGES.items():
    with open(os.path.join(HERE,fn),"w") as f: f.write(page(title,desc,body,og,noindex,nav=(fn!="start.html")))
    print("wrote",fn)
