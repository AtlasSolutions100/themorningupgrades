#!/usr/bin/env python3
"""Builds the themorningupgrades.com pages from shared chrome. Run: python3 build_site.py"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))

NAV = """
<nav class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/mark.jpg" alt=""><b>The Morning Upgrade</b></a>
  <button class="burger sans" aria-label="Menu">Menu</button>
  <div class="menu">
    <a href="/shop.html">Shop</a>
    <a href="/ingredients.html">Ingredients</a>
    <a href="/faq.html">FAQ</a>
    <a href="/about.html">About</a>
    <a href="/partner.html">Partner with us</a>
    <a class="btn sm" href="/shop.html">Buy CoreJava</a>
  </div>
</div></nav>
"""

FOOTER = """
<footer><div class="wrap">
  <div class="cols">
    <div>
      <h4>The Morning Upgrade</h4>
      <p>Coffee that keeps up past lunch. One scoop, hot water, smooth energy and sharp focus. Sold by Rector &amp; Stull LLC, an independent distributor of MarketPlace Global products.</p>
      <p>hello@themorningupgrades.com</p>
    </div>
    <div>
      <h4>Shop</h4>
      <a href="/shop.html">CoreJava coffee</a>
      <a href="/ingredients.html">What's in it</a>
      <a href="/faq.html">Questions</a>
      <a href="/shipping-returns.html">Shipping &amp; returns</a>
    </div>
    <div>
      <h4>Company</h4>
      <a href="/about.html">About us</a>
      <a href="/partner.html">Partner with us</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/terms.html">Terms</a>
    </div>
  </div>
  <p>These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease. Consult a physician before use if you are pregnant, nursing, taking medication, or have a medical condition. Contains caffeine.</p>
  <p>CoreJava is a product of MarketPlace Global. Rector &amp; Stull LLC is an independent distributor and is not the manufacturer. We earn income on the products we sell and on sales made by partners we introduce.</p>
  <p>&copy; <span class="yr"></span> Rector &amp; Stull LLC</p>
</div></footer>
"""

def page(title, desc, body, og_image="/img/flatlay.jpg", noindex=False, extra_head=""):
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
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js"></script>
{extra_head}
</head>
<body>
<div class="bar">Free US shipping on every order &middot; Subscribe &amp; Save: $69.95 a month, cancel anytime</div>
{NAV}
{body}
{FOOTER}
<div class="sticky"><div><b>CoreJava &middot; 30 servings</b><span>from $69.95 &middot; free shipping</span></div><a class="btn" data-buy="subscribe" href="#">Buy now</a></div>
</body>
</html>
"""

TRUST = """
<div class="trust wrap">
  <span>&#10003; Free US shipping</span><span>&#10003; Cancel anytime</span><span>&#10003; Secure checkout by Stripe</span><span>&#10003; Replaced or refunded if it arrives damaged</span>
</div>
"""
BENEFITS = """
<div class="marq"><div>
  <span>Smooth energy</span><span>Sharp focus</span><span>No 2pm slide</span><span>Tastes like coffee</span><span>Ready in 30 seconds</span><span>30 mornings a bag</span>
  <span>Smooth energy</span><span>Sharp focus</span><span>No 2pm slide</span><span>Tastes like coffee</span><span>Ready in 30 seconds</span><span>30 mornings a bag</span>
</div></div>
"""
CTA_BLOCK = """
<div class="ctab"><a class="btn" data-buy="subscribe" href="#">Subscribe &amp; Save &mdash; $69.95/mo</a><a class="btn ghost" data-buy="onetime" href="#">One bag &mdash; $79.95</a><p class="fine">Free US shipping &middot; cancel anytime &middot; secure checkout</p></div>
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
    <div><span>What's in it</span><span>Caffeine, sugar, milk</span><span>Caffeine</span><span class="hl">Caffeine + L-theanine + 4 more</span></div>
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

# ---------- HOME ----------
HOME = """
<div class="wrap hero">
  <div>
    <p class="eyebrow">Performance coffee &middot; one scoop &middot; 30 mornings</p>
    <h1>Coffee that keeps up past lunch.</h1>
    <p class="lead">Natural caffeine paired with L-theanine, the amino acid green-tea drinkers know. Smooth energy, sharp focus, and no second cup at 2pm. Tastes like coffee because it is coffee.</p>
    <p><a class="btn" href="/shop.html">Buy CoreJava</a> &nbsp; <a class="btn ghost" href="#quiz">Take the 60-second quiz</a></p>
    <p class="sub">$79.95 one bag &middot; $69.95 a month on Subscribe &amp; Save &middot; free US shipping</p>
    <div class="trust hero-trust"><span>&#10003; Free US shipping</span><span>&#10003; Cancel anytime</span><span>&#10003; Secure checkout by Stripe</span><span>&#10003; Replaced or refunded if damaged</span></div>
  </div>
  <div class="frame phone"><video autoplay muted loop playsinline poster="/media/hero_macro.jpg"><source src="/media/hero_macro.mp4" type="video/mp4"></video></div>
</div>
""" + BENEFITS + """

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
    <h2>Six things, one scoop.</h2>
    <p>Natural caffeine from coffee beans. L-theanine, the amino acid in green tea. ChromeMate, a patented chromium. Paradoxine, grains of paradise extract. Garcinia Cambogia fruit extract. Saffr'Activ saffron extract. The label says what it does: supports healthy appetite control, focus and energy.</p>
    <p><a class="btn" href="/ingredients.html">See every ingredient</a></p>
  </div>
  <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ingredients.jpg"><source src="/media/ingredients.mp4" type="video/mp4"></video></div>
</div></section>

<section><div class="wrap">
  <h2 style="text-align:center">Pick your bag</h2>
  <p style="text-align:center;color:var(--muted);margin:0 0 30px">Same coffee either way. Subscribe &amp; Save just means a bag shows up before you run out.</p>
  <div class="price">
    <div class="plan">
      <h3>One bag</h3>
      <div class="amt">$79.95</div>
      <p class="fine">30 servings &middot; $2.67 a cup</p>
      <ul><li>Try it for a month</li><li>No commitment</li><li><span class="ships-from">Ships from the maker directly.</span></li></ul>
      <a class="btn ghost" data-buy="onetime" href="#">Buy one bag</a>
    </div>
    <div class="plan best">
      <span class="tag">Most people pick this</span>
      <h3>Subscribe &amp; Save</h3>
      <div class="amt">$69.95<small> / month</small></div>
      <p class="fine">30 servings &middot; $2.33 a cup &middot; save $10 every bag</p>
      <ul><li>A bag a month, automatically</li><li>Pause or cancel any time</li><li><span class="ships-from">Ships from the maker directly.</span></li></ul>
      <a class="btn" data-buy="subscribe" href="#">Subscribe &amp; Save</a>
    </div>
  </div>
</div></section>
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

<section><div class="wrap split">
  <div>
    <h2>Questions, answered plainly</h2>
    <details><summary>Does it taste like coffee?</summary><p>Yes. Medium roast, a little smoother than drip. Black is fine; creamer is fine.</p></details>
    <details><summary>Is it one cup or two?</summary><p>One scoop is the serving. Most people find one is the right amount.</p></details>
    <details><summary>What if I drink coffee all day?</summary><p>Swap the first cup only for a week. That's the cup that sets the curve for the rest of the day.</p></details>
    <details><summary>Can I cancel the subscription?</summary><p>Any time, from the link in your receipt. No calls, no forms.</p></details>
    <p><a class="btn ghost" href="/faq.html">All questions</a></p>
  </div>
  <div class="frame p45"><img src="/img/pour.jpg" alt="Hot water poured into a glass mug" loading="lazy"></div>
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
    <div class="frame sq" style="background:#0B0F17"><img src="/img/bag.png" alt="CoreJava coffee bag, 30 servings" style="object-fit:contain;padding:8%"></div>
    <div class="gallery">
      <div class="frame" style="aspect-ratio:9/16"><video muted loop playsinline autoplay poster="/media/ambient.jpg"><source src="/media/ambient.mp4" type="video/mp4"></video></div>
      <div class="frame" style="aspect-ratio:9/16"><img src="/img/scoop.jpg" alt="Scoop of coffee" loading="lazy"></div>
      <div class="frame" style="aspect-ratio:9/16"><video muted loop playsinline autoplay poster="/media/iced.jpg"><source src="/media/iced.mp4" type="video/mp4"></video></div>
    </div>
  </div>
  <div>
    <p class="eyebrow">CoreJava &middot; performance coffee</p>
    <h1 style="font-size:clamp(30px,4vw,44px)">CoreJava Coffee, 30 servings</h1>
    <p class="lead">Medium-roast instant coffee built around natural caffeine and L-theanine, with ChromeMate, Paradoxine, Garcinia Cambogia and Saffr'Activ. Supports healthy appetite control, focus and energy. One level scoop in 8 oz of hot water.</p>
    <div class="price" style="grid-template-columns:1fr;max-width:none;gap:14px;margin:22px 0">
      <div class="plan best">
        <span class="tag">Most people pick this</span>
        <h3>Subscribe &amp; Save &mdash; <span style="white-space:nowrap">$69.95 / month</span></h3>
        <p class="fine">A bag a month, $2.33 a cup. Pause, skip or cancel from your receipt any time.</p>
        <a class="btn" data-buy="subscribe" href="#" style="margin-top:12px">Subscribe &amp; Save</a>
      </div>
      <div class="plan">
        <h3>One bag &mdash; $79.95</h3>
        <p class="fine">30 servings, $2.67 a cup. No commitment.</p>
        <a class="btn ghost" data-buy="onetime" href="#" style="margin-top:12px">Buy one bag</a>
      </div>
    </div>
    <p class="fine">Free US shipping &middot; cancel anytime &middot; secure checkout by Stripe &middot; replaced or refunded if it arrives damaged. Questions before you buy: hello@themorningupgrades.com.</p>
    <h3 style="margin-top:30px">Details</h3>
    <ul class="clean">
      <li><strong>Serving:</strong> 1 level scoop (about 6.8 g) in 8 fl oz hot water. 30 servings per 7.2 oz (204 g) bag.</li>
      <li><strong>Actives:</strong> natural caffeine, L-theanine, ChromeMate&reg; chromium, Paradoxine&reg; grains of paradise extract, Garcinia Cambogia extract, Saffr'Activ&reg; saffron extract. <a href="/ingredients.html">Full breakdown</a>.</li>
      <li><strong>Taste:</strong> medium roast, smooth. Works black, with creamer, or over ice.</li>
      <li><strong>Who it's for:</strong> adults who drink coffee daily and want a steadier morning. Not for children, or if you're pregnant or nursing. Contains caffeine.</li>
      <li><strong>Made by:</strong> MarketPlace Global. Sold by Rector &amp; Stull LLC, independent distributor.</li>
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
""" + COMPARE + FOUNDER + """
<section class="dark" style="text-align:center"><div class="wrap"><h2>Start tomorrow.</h2>""" + CTA_BLOCK + """</div></section>
"""

# ---------- INGREDIENTS ----------
ING = """
<section style="padding-top:36px"><div class="wrap">
  <p class="eyebrow">What's in it</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Six ingredients, and what each one is.</h1>
  <p class="lead">We'll tell you where each ingredient comes from. For what the blend does, the label is the authority: <em>supports healthy appetite control, focus and energy.</em> We don't go past that.</p>
</div></section>
<section class="dark" style="padding-top:0"><div class="wrap">
  <div class="split" style="margin-bottom:40px">
    <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ingredients.jpg"><source src="/media/ingredients.mp4" type="video/mp4"></video></div>
    <div class="ing" style="grid-template-columns:1fr 1fr">
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
  <h2>One scoop has all six.</h2>
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
  <details><summary>How does Subscribe &amp; Save work?</summary><p>A bag ships every 30 days at $69.95. Pause, skip or cancel from the link in your receipt, any time, no calls.</p></details>
  <details><summary>Where does it ship from, and how fast?</summary><p><span class="ships-from">Ships from the maker directly.</span> US addresses only for now. Tracking arrives by email.</p></details>
  <details><summary>Returns?</summary><p>If a bag arrives damaged or wrong, email hello@themorningupgrades.com within 14 days and we'll replace it or refund it. Full policy on the <a href="/shipping-returns.html">Shipping &amp; returns</a> page.</p></details>
  <details><summary>Who am I buying from?</summary><p>Rector &amp; Stull LLC, an independent distributor of MarketPlace Global products. MarketPlace Global makes CoreJava; we sell it.</p></details>
  <h2>The business</h2>
  <details><summary>Is this an MLM?</summary><p>MarketPlace Global sells through independent distributors, and distributors can introduce other distributors. We earn on the coffee we sell and on sales made by partners we introduce. If that interests you, the <a href="/partner.html">Partner page</a> explains it without the hype.</p></details>
</div></section>
"""

# ---------- PARTNER ----------
PARTNER = """
<section style="padding-top:36px"><div class="wrap split">
  <div>
    <p class="eyebrow">Partner with us</p>
    <h1 style="font-size:clamp(30px,4vw,46px)">Sell the coffee you already drink. We'll show you exactly how we do it.</h1>
    <p class="lead">Rector &amp; Stull is a small team of independent distributors for MarketPlace Global. We sell CoreJava online with short videos, a simple website and an email list. If you join our team, you get the same playbook, the same creative, and a weekly call with people doing it.</p>
    <p><a class="btn" data-enroll data-fallback="Ask about joining" href="#apply">Join our team</a> &nbsp; <a class="btn ghost" href="#how">How it works</a></p>
    <p class="fine" style="margin-top:14px">Independent distributor opportunity with MarketPlace Global. Earnings depend on your own sales and effort; most participants earn little or nothing. Read the <a data-disclosure href="#">income disclosure statement</a> before you decide.</p>
  </div>
  <div class="frame phone"><video autoplay muted loop playsinline poster="/media/ambient.jpg"><source src="/media/ambient.mp4" type="video/mp4"></video></div>
</div></section>

<section class="alt" id="how"><div class="wrap">
  <h2>How it works</h2>
  <div class="steps">
    <div><h3>Enroll with MarketPlace Global</h3><p>You sign up as an independent distributor under our team. MarketPlace Global handles product, shipping, payments and commissions.</p></div>
    <div><h3>Get the playbook</h3><p>Our content system: the product films, the captions, the pre-sell page, the email flows, and the disclosure rules that keep it clean. Yours to use on day one.</p></div>
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
      <li>You want a side income you can build in evenings, not a second job.</li>
      <li>You're fine with honest numbers. We'll show you ours.</li>
    </ul>
    <h2 style="margin-top:28px">Who it isn't for</h2>
    <p style="color:var(--muted)">Anyone who needs income this month. Anyone who wants to recruit before they've sold a bag. Anyone who'd rather not disclose that they earn a commission.</p>
  </div>
</div></section>

<section class="dark"><div class="wrap">
  <h2>The honest part</h2>
  <div class="grid3">
    <div class="card"><h3>It costs money to start</h3><p>MarketPlace Global charges an enrollment fee and you'll want product to try. We'll tell you the current numbers before you sign anything.</p></div>
    <div class="card"><h3>Most people earn little</h3><p>That's true of every direct-sales company, and the income disclosure statement shows it. We'd rather you read it first than hear it later.</p></div>
    <div class="card"><h3>Results take work</h3><p>Our system shortens the learning curve. It does not remove the work: posting, replying, following up, every week.</p></div>
  </div>
  <p class="fine" style="margin-top:22px">Rector &amp; Stull LLC does not guarantee any level of income. Any earnings figures we share are our own, are not typical, and are not a promise of what you will earn. See the <a data-disclosure href="#" style="color:#C9C2B6">MarketPlace Global income disclosure statement</a>.</p>
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
        <option value="mpg">I'm already with MarketPlace Global</option>
      </select>
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

# ---------- ABOUT ----------
ABOUT = """
<section style="padding-top:36px"><div class="wrap split">
  <div>
    <p class="eyebrow">About</p>
    <h1 style="font-size:clamp(30px,4vw,46px)">Two people, one bag of coffee, and a website that says what it is.</h1>
    <p class="lead">Rector &amp; Stull LLC is a small company run by two partners, one in Idaho and one in Texas. We're independent distributors for MarketPlace Global, and CoreJava is the product we drink ourselves, which is why it's the one we sell.</p>
    <p>We started The Morning Upgrade because most coffee marketing is either a lifestyle fantasy or a wall of supplement jargon. We wanted a page that tells you what's in the bag, what it costs per cup, and how to find out in a week whether it's for you.</p>
    <p>Everything on this site that earns us money says so. Every video that uses an AI-generated scene is labeled. If something's unclear, email us and a human will answer: hello@themorningupgrades.com.</p>
    <p><a class="btn" href="/shop.html">Buy CoreJava</a> &nbsp; <a class="btn ghost" href="/partner.html">Partner with us</a></p>
  </div>
  <div class="frame p45"><img src="/img/flatlay.jpg" alt="Morning counter with a scoop, a mug and a bag of coffee"></div>
</div></section>
"""

# ---------- LEGAL ----------
SHIPPING = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">Policies</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Shipping &amp; returns</h1>
  <h2>Shipping</h2>
  <p>We ship to addresses in the United States. <span class="ships-from">Ships from the maker directly.</span> Orders placed by 2 PM Central on a business day ship that day or the next. Standard shipping is included in the price. You'll get a tracking email when it leaves.</p>
  <h2>Subscribe &amp; Save</h2>
  <p>A new bag ships every 30 days and your card is charged $69.95 each time. You can pause, skip a month, or cancel from the link in any receipt, up to the day before your next shipment. There are no cancellation fees.</p>
  <h2>Returns and refunds</h2>
  <p>If your order arrives damaged, opened, or wrong, email hello@themorningupgrades.com within 14 days of delivery with your order number and a photo, and we'll replace it or refund it in full. For unopened bags you simply don't want, email us within 30 days of delivery and we'll refund the price once the bag is back with us; return shipping is on you. Opened bags can't be returned for a change of mind, for food-safety reasons.</p>
  <h2>Questions</h2>
  <p>hello@themorningupgrades.com. A real person answers, usually the same business day.</p>
  <p class="fine">Rector &amp; Stull LLC, independent distributor of MarketPlace Global products. Last updated October 2026.</p>
</div></section>
"""

PRIVACY = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">Policies</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Privacy</h1>
  <p>This is the privacy policy for themorningupgrades.com, operated by Rector &amp; Stull LLC ("we"). It's written to be read.</p>
  <h2>What we collect</h2>
  <ul><li><strong>If you take the quiz:</strong> your answers, first name and email, so we can send you the guide and the follow-up emails.</li><li><strong>If you buy:</strong> your name, shipping address, email and phone (for the carrier). Payment details go to Stripe; we never see your card number.</li><li><strong>If you ask about partnering:</strong> what you type into the form.</li><li><strong>Automatically:</strong> basic, aggregated analytics (pages viewed, where visitors came from). If we run ads, a Meta pixel may record page views and purchases so we can measure them.</li></ul>
  <h2>What we do with it</h2>
  <p>Fulfil orders, send the emails you signed up for, answer your questions, and measure which of our posts bring people here. We don't sell your data. We don't share it except with the services that make the site work: Stripe (payments), Klaviyo (email), our shipping carrier, GitHub (hosting), and analytics providers.</p>
  <h2>Your choices</h2>
  <p>Every email has an unsubscribe link. To see, correct or delete what we hold about you, email hello@themorningupgrades.com and we'll do it within 30 days.</p>
  <h2>Cookies</h2>
  <p>The site itself sets none. Stripe and Klaviyo set the ones they need to work. If a Meta pixel is active, it sets its own; you can opt out at facebook.com/ads/preferences.</p>
  <p class="fine">Rector &amp; Stull LLC. Last updated October 2026.</p>
</div></section>
"""

TERMS = """
<section style="padding-top:36px"><div class="wrap legal">
  <p class="eyebrow">Policies</p>
  <h1 style="font-size:clamp(30px,4vw,46px)">Terms of sale</h1>
  <p>By ordering from themorningupgrades.com you agree to these terms. The seller is Rector &amp; Stull LLC, an independent distributor of MarketPlace Global products. MarketPlace Global manufactures CoreJava; we are not the manufacturer.</p>
  <h2>Orders and prices</h2>
  <p>Prices are in US dollars and include standard US shipping. We may change prices at any time; the price you pay is the one shown at checkout. If we can't fill an order we'll refund it in full.</p>
  <h2>Subscriptions</h2>
  <p>Subscribe &amp; Save renews every 30 days at the price shown until you cancel. Cancel any time from the link in your receipt, effective before the next shipment.</p>
  <h2>Use of the product</h2>
  <p>CoreJava is a dietary supplement containing caffeine, for adults. It is not intended to diagnose, treat, cure or prevent any disease. Read the label. Do not use if pregnant or nursing. Ask a physician if you take medication or have a medical condition. Keep out of reach of children.</p>
  <h2>Returns</h2>
  <p>See <a href="/shipping-returns.html">Shipping &amp; returns</a>.</p>
  <h2>Liability</h2>
  <p>To the extent the law allows, our liability for any order is limited to the amount you paid for it.</p>
  <h2>Partner opportunity</h2>
  <p>Information on the Partner page describes an independent distributor opportunity with MarketPlace Global and is governed by MarketPlace Global's own agreement and policies, which you accept when you enroll with them. We make no guarantee of income.</p>
  <p class="fine">Rector &amp; Stull LLC. Governing law: Idaho. Last updated October 2026.</p>
</div></section>
"""

ORDER_COMPLETE = """
<section style="padding-top:36px"><div class="wrap" style="max-width:720px">
  <div class="card" style="padding:34px 30px">
    <p class="eyebrow">Order received</p>
    <h1 style="font-size:clamp(30px,4vw,44px)">Your coffee is on its way.</h1>
    <p>Stripe has emailed your receipt. You'll get a tracking email when the bag ships. If anything looks wrong, reply to the receipt or write hello@themorningupgrades.com.</p>
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
    <p><a class="btn" href="/shop.html">See the coffee</a> <a class="btn ghost" href="/">Back to the start</a></p>
  </div>
</div></section>
"""

PAGES = {
  "index.html": ("The Morning Upgrade — Coffee that keeps up past lunch", "CoreJava performance coffee: natural caffeine + L-theanine, one scoop, hot water. $79.95 a bag or $69.95 a month. Take the 60-second quiz.", HOME, "/img/flatlay.jpg", False),
  "shop.html": ("Buy CoreJava Coffee — The Morning Upgrade", "CoreJava coffee, 30 servings. $79.95 one bag or $69.95 a month on Subscribe & Save. Natural caffeine, L-theanine and four more actives.", SHOP, "/img/bag.png", False),
  "ingredients.html": ("What's in CoreJava — The Morning Upgrade", "Six ingredients and what each one is: natural caffeine, L-theanine, ChromeMate, Paradoxine, Garcinia Cambogia, Saffr'Activ.", ING, "/media/ingredients.jpg", False),
  "faq.html": ("FAQ — The Morning Upgrade", "Taste, caffeine, shipping, subscriptions, returns, and who you're buying from.", FAQ, "/img/pour.jpg", False),
  "partner.html": ("Partner with us — The Morning Upgrade", "Join our MarketPlace Global team and sell CoreJava with the same videos, site and email system we use. Honest numbers first.", PARTNER, "/media/ambient.jpg", False),
  "about.html": ("About — The Morning Upgrade", "Rector & Stull LLC, independent distributors of MarketPlace Global, and why we sell one bag of coffee.", ABOUT, "/img/flatlay.jpg", False),
  "shipping-returns.html": ("Shipping & returns — The Morning Upgrade", "US shipping, Subscribe & Save terms, and our 14-day replacement / 30-day unopened return policy.", SHIPPING, "/img/flatlay.jpg", False),
  "privacy.html": ("Privacy — The Morning Upgrade", "What we collect, what we do with it, and how to opt out.", PRIVACY, "/img/flatlay.jpg", False),
  "terms.html": ("Terms of sale — The Morning Upgrade", "Terms for buying CoreJava from Rector & Stull LLC.", TERMS, "/img/flatlay.jpg", False),
  "order-complete.html": ("Order received — The Morning Upgrade", "Thanks for your order.", ORDER_COMPLETE, "/img/flatlay.jpg", True),
  "thanks.html": ("Your guide is on its way — The Morning Upgrade", "Check your inbox for the 7 Mornings guide.", THANKS, "/img/desk.jpg", True),
}

for fn,(title,desc,body,og,noindex) in PAGES.items():
    with open(os.path.join(HERE,fn),"w") as f: f.write(page(title,desc,body,og,noindex))
    print("wrote",fn)
