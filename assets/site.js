/* The Morning Upgrade — site config + shared behaviour.
   Fill the CONFIG values as accounts come online. Empty Stripe links = "handoff" mode (Buy sends to the MPG product page). */
window.TMU = {
  // Stripe Payment Links (create in Stripe Dashboard → Payment Links). Leave "" until they exist.
  STRIPE_ONETIME: "https://buy.stripe.com/3cIbJ3fEv6XIbtk8iw4wM00",          // one bag, $79.95, ships from us
  STRIPE_SUBSCRIBE: "https://buy.stripe.com/8x228t3VN2Hsapg56k4wM01",        // one bag a month, $69.95, ships from us
  // House coffees (Nov 2026), roasted to order and shipped by our roasting partner. One-time only; $5.95 flat US
  // shipping and the roast picker (Cup of Joe) live on the Payment Link. Redirect: /order-complete.html?plan=<key>
  STRIPE_CUPOFJOE: "https://buy.stripe.com/4gMeVffEv5TEfJA42g4wM02",         // Cup of Joe Everyday Coffee, 12 oz, $27.95
  STRIPE_MUSHROOM: "https://buy.stripe.com/00w5kF77Z1Do9lccyM4wM03",         // The Morning Upgrade Mushroom Coffee Blend, 12 oz, $33.95
  // MarketPlace Global replicated product page (handoff fallback while Stripe is empty)
  MPG_PRODUCT: "https://marketplaceglobal.com/rectorandstull/product/coffee/mpgxtreme-1-bag-corejava-coffee-skucl805-us-id194",
  // Partner side
  ENROLL_URL: "https://marketplaceglobal.com/rectorandstull/join-the-place",
  INCOME_DISCLOSURE_URL: "https://marketplaceglobal.com/rectorandstull/income-disclaimer",
  // Lists
  KLAVIYO_COMPANY: "Ucdz59",
  KLAVIYO_LIST_QUIZ: "WgctGT",
  KLAVIYO_LIST_PARTNERS: "WeMj34",   // separate list; never the customer list
  KLAVIYO_LIST_NEWSLETTER: "WgctGT", // email pop-up sign-ups. Same id as the quiz list for now; put a dedicated list id here to split them
  // Email pop-up: the free Recipe Pack for signing up, and the two prices stated plainly (Subscribe & Save is
  // $69.95 a month; 1 bag is $79.95; no promo code, no "off"). POPUP_DELAY_MS 0 turns the pop-up off.
  RECIPE_PACK: "/assets/recipe-pack.pdf",
  POPUP_DELAY_MS: 10000,             // pop-up opens after this long, at 50% scroll, or on desktop exit intent
  POPUP_SNOOZE_DAYS: 14,             // after it's closed (or seen), wait this long before showing it again
  // Tracking
  RETAIL_BONUS_PCT: 0,         // ISR Retail Customer Bonus % on referred customer orders (0 = hide the math)
  GA4_ID: "G-G79BLY9MDG",       // Google Analytics 4
  TIKTOK_PIXEL: "DBDQJRRC77U24SKT5GP0", // TikTok pixel
  PIXEL_ID: "28758618673764449", // Meta pixel (dataset "TMU Website", Rector & Stull LLC portfolio)
  SNAP_PIXEL: "ed6288c4-136e-418b-9d3d-5f3cb47998d4", // Snap pixel ("Rector & Stull Pixel")
  GOOGLE_ADS_ID: "AW-18543041154",               // Google Ads account "Rector & Stull" (shared with Crowdcut)
  GOOGLE_PURCHASE: "AW-18543041154/9DvuCJSurq0dEIK1gYpF", // conversion action "TMU Purchase"
  ANALYTICS_DOMAIN: "themorningupgrades.com",
  // First-party funnel events (visits, quiz starts, email sign-ups, Buy clicks) for the R&S HQ dashboard. "" turns them off.
  COLLECT_URL: "https://dashboard.rectorandstull.com/collect/tmu"
};

(function(){
  var C = window.TMU;
  // Google Analytics 4
  if (C.GA4_ID) {
    var g=document.createElement('script'); g.async=true; g.src='https://www.googletagmanager.com/gtag/js?id='+C.GA4_ID; document.head.appendChild(g);
    window.dataLayer = window.dataLayer || []; window.gtag = function(){ dataLayer.push(arguments); };
    gtag('js', new Date()); gtag('config', C.GA4_ID, { anonymize_ip: true });
  }
  // Google Ads (same gtag.js; loads it if GA4 is off)
  if (C.GOOGLE_ADS_ID) {
    if (!window.gtag) { var ga=document.createElement('script'); ga.async=true; ga.src='https://www.googletagmanager.com/gtag/js?id='+C.GOOGLE_ADS_ID; document.head.appendChild(ga);
      window.dataLayer = window.dataLayer || []; window.gtag = function(){ dataLayer.push(arguments); }; gtag('js', new Date()); }
    gtag('config', C.GOOGLE_ADS_ID);
  }
  // TikTok pixel
  if (C.TIKTOK_PIXEL) {
    !function (w, d, t) { w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie","holdConsent","revokeConsent","grantConsent"],ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e},ttq.load=function(e,n){var r="https://analytics.tiktok.com/i18n/pixel/events.js",o=n&&n.partner;ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=r,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};var s=document.createElement("script");s.type="text/javascript",s.async=!0,s.src=r+"?sdkid="+e+"&lib="+t;var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(s,a)};
      ttq.load(C.TIKTOK_PIXEL); ttq.page(); }(window, document, 'ttq');
  }
  // Meta pixel
  if (C.PIXEL_ID) {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', C.PIXEL_ID); fbq('track','PageView');
  }
  // Snap pixel
  if (C.SNAP_PIXEL) {
    (function(e,t,n){if(e.snaptr)return;var a=e.snaptr=function(){a.handleRequest?a.handleRequest.apply(a,arguments):a.queue.push(arguments)};a.queue=[];var s='script',r=t.createElement(s);r.async=!0;r.src=n;var u=t.getElementsByTagName(s)[0];u.parentNode.insertBefore(r,u);})(window,document,'https://sc-static.net/scevent.min.js');
    snaptr('init', C.SNAP_PIXEL, {}); snaptr('track','PAGE_VIEW');
  }
  // Plausible (privacy-safe, no cookie banner). Loads only once the domain is registered at plausible.io.
  if (C.ANALYTICS_DOMAIN && window.TMU_ANALYTICS_ON) {
    var s=document.createElement('script'); s.defer=true; s.setAttribute('data-domain',C.ANALYTICS_DOMAIN); s.src='https://plausible.io/js/script.outbound-links.js'; document.head.appendChild(s);
  }
  // Creator attribution. A creator link (/c/<code>, or any page with ?ref=<code>) is remembered for
  // REF_DAYS; the last creator link someone used wins. The code rides to Stripe as client_reference_id
  // (cr_<code>) so tools/creator_commissions.py can pay the creator on that customer's orders for life.
  var REF_DAYS = 60, REF_RE = /^[a-z0-9_-]{2,32}$/;
  function readRef(){
    try{ var r=JSON.parse(localStorage.getItem('tmu_ref')||'null'); if(r&&REF_RE.test(r.c)&&Date.now()-r.t<REF_DAYS*864e5) return r.c; }catch(e){}
    var m=document.cookie.match(/(?:^|; )tmu_ref=([a-z0-9_-]{2,32})/); return m?m[1]:'';
  }
  function saveRef(c){
    try{ localStorage.setItem('tmu_ref', JSON.stringify({c:c,t:Date.now()})); }catch(e){}
    try{ document.cookie='tmu_ref='+c+'; max-age='+(REF_DAYS*86400)+'; path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':''); }catch(e){}
  }
  var qref=''; try{ qref=(new URLSearchParams(location.search).get('ref')||'').toLowerCase(); }catch(e){}
  if (REF_RE.test(qref)) saveRef(qref); else qref='';
  C.REF = readRef();
  if (C.REF && window.gtag && C.GA4_ID) gtag('set','user_properties',{creator:C.REF});
  // Ad attribution for orders without a creator: the first paid-ad visit's utm tags are remembered for
  // 30 days and ride to Stripe as client_reference_id ut__<source>__<campaign>__<content> (R&S HQ reads it).
  function clean(v){ return String(v||'').toLowerCase().replace(/[^a-z0-9_-]/g,'-').replace(/_+/g,'_').slice(0,40); }
  try{
    var q=new URLSearchParams(location.search), us=q.get('utm_source');
    if (us && /^(paid|cpc|ppc|paid_social|paid-social|paidsocial|social_paid)$/i.test(q.get('utm_medium')||'') && !localStorage.getItem('tmu_ut')) localStorage.setItem('tmu_ut', JSON.stringify({s:clean(us),c:clean(q.get('utm_campaign')),n:clean(q.get('utm_content')),t:Date.now()}));
    var ut=JSON.parse(localStorage.getItem('tmu_ut')||'null');
    if (ut && Date.now()-ut.t<30*864e5) C.UT='ut__'+ut.s+'__'+ut.c+'__'+ut.n;
  }catch(e){}
  // A paid visit: this page's utm_medium is a paid one, or the 30-day tmu_ut flag is set. The pop-up stays
  // closed and pickers marked data-paid-default preselect that plan (1 bag first for ad traffic).
  C.PAID=false; try{ C.PAID=!!C.UT || /^(paid|cpc|ppc|paid_social|paid-social|paidsocial|social_paid)$/i.test(new URLSearchParams(location.search).get('utm_medium')||''); }catch(e){}

  // First-party funnel events for R&S HQ (COLLECT_URL): an anonymous visitor id (tmu_vid cookie, 1 year) and this
  // browser's first touch (tmu_ft: the first visit's utm tags of any medium, ad click id, referring site; 90 days,
  // never overwritten) ride with each step. Never an email, a name or anything typed into a form. Loads like the
  // pixels above (the analytics notice covers both). tmu_ut above still sets the 30-day Stripe tag on its own.
  var FT_DAYS=90, VID='', FT={};
  try{
    var vm=document.cookie.match(/(?:^|; )tmu_vid=([a-z0-9]{8,40})/); VID=vm?vm[1]:'';
    if(!VID){ var rb=''; try{ var a8=new Uint8Array(10); crypto.getRandomValues(a8); for(var i=0;i<a8.length;i++) rb+=(a8[i]%36).toString(36); }catch(e){ rb=Math.random().toString(36).slice(2,12); }
      VID=(rb+Date.now().toString(36)).replace(/[^a-z0-9]/g,'').slice(0,40);
      document.cookie='tmu_vid='+VID+'; max-age=31536000; path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':''); }
  }catch(e){}
  try{
    var ft=null; try{ ft=JSON.parse(localStorage.getItem('tmu_ft')||'null'); }catch(e){ ft=null; }
    if(!ft || !(Date.now()-(+ft.t||0) < FT_DAYS*864e5)){
      var fq=new URLSearchParams(location.search); ft={t:Date.now()};
      ['utm_source','utm_medium','utm_campaign','utm_content','utm_term'].forEach(function(k){ var v=fq.get(k); if(v) ft[k]=v.slice(0,100); });
      ['gclid','ttclid','fbclid'].some(function(k){ var v=fq.get(k); if(v){ ft.click_id=v.slice(0,200); ft.click_type=k; return true; } return false; });
      try{ var rh=document.referrer?new URL(document.referrer).hostname:''; if(rh && rh!==location.hostname) ft.referrer_host=rh.slice(0,100); }catch(e){}
      try{ localStorage.setItem('tmu_ft', JSON.stringify(ft)); }catch(e){}
    }
    ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','click_id','click_type','referrer_host'].forEach(function(k){ if(ft[k]) FT[k]=String(ft[k]); });
  }catch(e){}
  // name: lp_view | quiz_start | lead (detail quiz|popup|newsletter) | buy_click (detail stripe|mpg:onetime|subscribe)
  window.tmuEvent = function(name, detail){ try{
    if(!C.COLLECT_URL || !VID) return;
    var b=JSON.stringify({name:name,vid:VID,path:location.pathname,detail:detail||null,ft:FT});
    if(navigator.sendBeacon && navigator.sendBeacon(C.COLLECT_URL, b)) return;   // a string goes as text/plain: no preflight
    fetch(C.COLLECT_URL,{method:'POST',body:b,keepalive:true,mode:'cors',credentials:'omit',headers:{'Content-Type':'text/plain'}}).catch(function(){});
  }catch(e){} };
  tmuEvent('lp_view');

  var TT_MAP={InitiateCheckout:'InitiateCheckout',ViewContent:'ViewContent',Lead:'CompleteRegistration',QuizComplete:'ViewContent',PartnerLead:'SubmitForm',PartnerClick:'ClickButton',Purchase:'CompletePayment'};
  var FB_STD={InitiateCheckout:1,ViewContent:1,Lead:1,Purchase:1};
  var SNAP_MAP={InitiateCheckout:'START_CHECKOUT',ViewContent:'VIEW_CONTENT',Lead:'SIGN_UP',QuizComplete:'VIEW_CONTENT',PartnerLead:'SIGN_UP',Purchase:'PURCHASE'};
  var GA_SKIP={ViewContent:1};   // GA4 already has page_view; ViewContent is for the ad pixels
  // Plan prices (coffee subtotal, before shipping and tax). Purchase/InitiateCheckout values use these.
  // cupofjoe / mushroom: the house coffees (1 bag each, one-time). ITEM: what each plan key is, for pixels and Klaviyo.
  var PRICE={subscribe:69.95,onetime:79.95,cupofjoe:27.95,mushroom:33.95}, SKU='CL805';
  var ITEM={
    subscribe:{sku:SKU, name:'CoreJava Instant Coffee, 30 servings', ga:'MCT Instant Coffee with L-Theanine, 30 Servings', plan:'Subscribe & Save, 1 bag every 30 days', ship:8.95, link:'STRIPE_SUBSCRIBE'},
    onetime:{sku:SKU, name:'CoreJava Instant Coffee, 30 servings', ga:'MCT Instant Coffee with L-Theanine, 30 Servings', plan:'1 bag', ship:8.95, link:'STRIPE_ONETIME'},
    cupofjoe:{sku:'TMU-CUPOFJOE-12', name:'Cup of Joe Everyday Coffee, 12 oz', ga:'Cup of Joe Everyday Coffee, 12 oz', plan:'Cup of Joe, 1 bag', ship:5.95, link:'STRIPE_CUPOFJOE', house:1},
    mushroom:{sku:'TMU-MUSHROOM-12', name:'The Morning Upgrade Mushroom Coffee Blend, 12 oz', ga:'The Morning Upgrade Mushroom Coffee Blend, 12 oz', plan:'Mushroom Coffee Blend, 1 bag', ship:5.95, link:'STRIPE_MUSHROOM', house:1}
  };
  C.PRICE=PRICE; C.ITEM=ITEM;
  function skuOf(props){ return (props && ITEM[props.plan]) ? ITEM[props.plan].sku : SKU; }
  function linkOf(plan){ return ITEM[plan] ? (C[ITEM[plan].link]||'') : C.STRIPE_ONETIME; }
  window.track = function(name, props){ try{
    props=props||{};
    var isP=name==='Purchase', val=(typeof props.value==='number')?props.value:PRICE.subscribe, eid=props.transaction_id||'', sku=skuOf(props);
    if(window.gtag&&C.GA4_ID&&!GA_SKIP[name]) gtag('event', name, props);
    if(window.ttq&&C.TIKTOK_PIXEL&&TT_MAP[name]) ttq.track(TT_MAP[name], (isP||name==='ViewContent'||name==='InitiateCheckout')?{value:val,currency:'USD',content_type:'product',content_id:sku}:props, eid?{event_id:eid}:undefined);
    if(window.fbq&&C.PIXEL_ID){ if(FB_STD[name]) fbq('track',name,(isP||name==='ViewContent'||name==='InitiateCheckout')?Object.assign({},props,{value:val,currency:'USD',content_ids:[sku],content_type:'product'}):props, eid?{eventID:eid}:undefined); else fbq('trackCustom',name,props); }
    if(window.gtag&&C.GOOGLE_PURCHASE&&isP) gtag('event','conversion',{send_to:C.GOOGLE_PURCHASE,value:val,currency:'USD',transaction_id:eid});
    if(window.snaptr&&C.SNAP_PIXEL&&SNAP_MAP[name]) snaptr('track',SNAP_MAP[name],(isP||name==='ViewContent'||name==='InitiateCheckout')?Object.assign({price:val,currency:'USD',item_ids:[sku],number_items:1},eid?{transaction_id:eid}:{}):{});
    if(window.plausible) plausible(name,{props:props});
  }catch(e){} };

  // ---------- Klaviyo events (client API, public site key only): Started Checkout and Placed Order ----------
  // Sent only when this browser already knows who the visitor is: they signed up here (quiz, guide capture or
  // pop-up; tmu_kl keeps that email on this device only), they arrived from a Klaviyo email link (_kx), or
  // Klaviyo's own __kla_id cookie names them. The email or id rides in the POST body, never in a URL. Loads
  // like the pixels above (the analytics notice covers it), and is skipped entirely when the browser sends
  // Global Privacy Control or Do Not Track, since it ties the click to a person.
  var KL_DAYS=365, EMAIL_RE=/^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  function privacySignal(){ try{ return navigator.globalPrivacyControl===true || navigator.doNotTrack==='1' || window.doNotTrack==='1'; }catch(e){ return false; } }
  try{ var kxq=new URLSearchParams(location.search).get('_kx'); if(kxq && kxq.length<=400) localStorage.setItem('tmu_kx', JSON.stringify({k:kxq,t:Date.now()})); }catch(e){}
  C.klRemember = function(email){ try{ email=String(email||'').trim(); if(EMAIL_RE.test(email)) localStorage.setItem('tmu_kl', JSON.stringify({e:email.slice(0,200),t:Date.now()})); }catch(e){} };
  C.klWho = function(){
    var who={}, fresh=function(o){ return o && Date.now()-(+o.t||0) < KL_DAYS*864e5; };
    try{ var k=JSON.parse(localStorage.getItem('tmu_kl')||'null'); if(fresh(k) && EMAIL_RE.test(k.e||'')) who.email=k.e; }catch(e){}
    try{ var x=JSON.parse(localStorage.getItem('tmu_kx')||'null'); if(fresh(x) && x.k) who._kx=String(x.k); }catch(e){}
    if(!who._kx){ try{ var m=document.cookie.match(/(?:^|; )__kla_id=([^;]+)/); if(m){ var j=JSON.parse(atob(decodeURIComponent(m[1]))); if(j && j.$exchange_id) who._kx=String(j.$exchange_id); } }catch(e){} }
    return (who.email || who._kx) ? who : null;
  };
  // Returns the fetch promise, or null when nothing was sent (no known visitor, a privacy signal, no site key).
  C.klEvent = function(metric, props, value, uid){ try{
    var who=C.klWho(); if(!who || privacySignal() || !C.KLAVIYO_COMPANY) return null;
    var at={properties:props||{}, metric:{data:{type:'metric',attributes:{name:metric}}}, profile:{data:{type:'profile',attributes:who}}};
    if(typeof value==='number') at.value=value;
    if(uid) at.unique_id=String(uid);
    return fetch('https://a.klaviyo.com/client/events/?company_id='+C.KLAVIYO_COMPANY,{method:'POST',keepalive:true,
      headers:{'Content-Type':'application/json','revision':'2025-01-15'},body:JSON.stringify({data:{type:'event',attributes:at}})}).catch(function(){});
  }catch(e){ return null; } };
  // Started Checkout, from a Buy button that goes to our Stripe checkout. CheckoutURL is the plain Payment Link
  // with email utm tags (and the same creator/ad credit the click carried), for the abandoned-checkout emails.
  // A plain left click on a same-tab link waits for the send (at most 500 ms) so leaving the page can't drop it.
  C.startedCheckout = function(a, plan, source, ev){ try{
    if(!a || a.dataset.mode!=='stripe' || !PRICE[plan]) return;
    var link = linkOf(plan); if(!link) return;
    var cr=((a.href||'').match(/[?&]client_reference_id=([A-Za-z0-9_-]{1,200})/)||[])[1];
    var url=link+(link.indexOf('?')>-1?'&':'?')+'utm_source=klaviyo&utm_medium=email&utm_campaign=started_checkout'+(cr?'&client_reference_id='+cr:'');
    var props={plan:plan, plan_name:ITEM[plan].plan,
      value:PRICE[plan], currency:'USD', shipping:ITEM[plan].ship, CheckoutURL:url, checkout_url:url, clicked_url:a.href,
      ItemNames:[ITEM[plan].name], page:location.pathname, source:source||'site'};
    var p=C.klEvent('Started Checkout', props, PRICE[plan], 'sc_'+plan+'_'+Math.floor(Date.now()/6e4));
    if(!p || !ev || ev.defaultPrevented || ev.button || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || a.target==='_blank') return;
    ev.preventDefault();
    var href=a.href, gone=false, go=function(){ if(!gone){ gone=true; location.href=href; } };
    p.then(go, go); setTimeout(go, 500);
  }catch(e){} };

  // Which plan was bought. Order of trust: ?plan= on the Stripe redirect, then the last Buy button
  // this browser clicked (tmu_plan), then Subscribe & Save.
  C.plan = function(){
    var p=''; try{ p=(new URLSearchParams(location.search).get('plan')||'').toLowerCase(); }catch(e){}
    if(!PRICE[p]){ try{ p=localStorage.getItem('tmu_plan')||''; }catch(e){ p=''; } }
    return PRICE[p]?p:'subscribe';
  };
  // Purchase: once per Stripe Checkout Session. transaction_id/event id = session_id, so a refresh,
  // a bookmark or a second tab never counts twice, and a server-side event can dedupe against it later.
  window.tmuPurchase = function(){ try{
    var sid=new URLSearchParams(location.search).get('session_id')||'';
    if(!/^cs_[A-Za-z0-9_]{6,200}$/.test(sid)) return false;      // not a Stripe redirect: no purchase
    var key='tmu_purchased', done=[]; try{ done=JSON.parse(localStorage.getItem(key)||'[]'); }catch(e){ done=[]; }
    if(done.indexOf(sid)>-1) return false;
    var plan=C.plan(), value=PRICE[plan];
    try{ done.push(sid); localStorage.setItem(key, JSON.stringify(done.slice(-20))); }catch(e){}
    track('Purchase',{value:value,currency:'USD',transaction_id:sid,plan:plan});
    C.klEvent('Placed Order',{plan:plan,value:value,currency:'USD',order_id:sid,ItemNames:[ITEM[plan].name]},value,sid);
    if(window.gtag&&C.GA4_ID) gtag('event','purchase',{transaction_id:sid,value:value,currency:'USD',
      items:[{item_id:ITEM[plan].sku,item_name:ITEM[plan].ga,item_variant:plan,price:value,quantity:1}]});
    return true;
  }catch(e){ return false; } };

  // Pop-up state, kept in this browser only: tmu_pop = {s:'seen'|'closed'|'signed', t:time}.
  function lsGet(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }
  function lsSet(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
  function lsJSON(k){ try{ return JSON.parse(lsGet(k)||'null'); }catch(e){ return null; } }
  C.ordered = function(){ var d=lsJSON('tmu_purchased'); return !!(d && d.length); };
  C.signedUp = function(){ var p=lsJSON('tmu_pop'); return !!(p && p.s==='signed'); };

  // ViewContent on the product pages, for TikTok / Meta / Snap optimisation.
  // GitHub Pages also serves /shop and /start without .html: count those too (ad URLs often drop it).
  // Each product page reports its own product (value and SKU); home, /shop and /start report CoreJava as before.
  var VC_PAGE={'corejava':'subscribe','cup-of-joe':'cupofjoe','mushroom-coffee-blend':'mushroom'};
  var vcm=location.pathname.match(/^\/([a-z-]+?)(\.html)?$/), vcp=vcm&&VC_PAGE[vcm[1]];
  if (vcp) track('ViewContent',{value:PRICE[vcp],currency:'USD',plan:vcp});
  else if (/^\/((index|shop|start)(\.html)?)?$/.test(location.pathname)) track('ViewContent',{value:PRICE.subscribe,currency:'USD'});

  if (qref) track('CreatorVisit',{creator:qref});

  document.addEventListener('DOMContentLoaded', function(){
    // nav
    var b=document.querySelector('.burger'), m=document.querySelector('.menu');
    var setMenu=function(open){ m.classList.toggle('open',open); b.setAttribute('aria-expanded', open?'true':'false'); b.setAttribute('aria-label', open?'Close menu':'Open menu'); };
    if(b&&m){ b.onclick=function(){ setMenu(!m.classList.contains('open')); };
      document.addEventListener('keydown',function(e){ if((e.key==='Escape'||e.key==='Esc') && m.classList.contains('open') && !document.querySelector('.dd.open')){ setMenu(false); b.focus(); } }); }
    // Shop / Learn disclosure buttons (desktop): click or Enter toggles; Esc, a click outside or tabbing away closes.
    var dds=[].slice.call(document.querySelectorAll('.menu .dd'));
    var ddSet=function(dd,open){ dd.classList.toggle('open',open); var bt=dd.querySelector('.ddb'); if(bt) bt.setAttribute('aria-expanded',open?'true':'false'); };
    dds.forEach(function(dd){ var bt=dd.querySelector('.ddb'); if(!bt) return;
      bt.addEventListener('click',function(){ var open=!dd.classList.contains('open'); dds.forEach(function(o){ if(o!==dd) ddSet(o,false); }); ddSet(dd,open); });
      dd.addEventListener('keydown',function(e){ if((e.key==='Escape'||e.key==='Esc') && dd.classList.contains('open')){ e.stopPropagation(); ddSet(dd,false); bt.focus(); } });
      dd.addEventListener('focusout',function(e){ if(e.relatedTarget && !dd.contains(e.relatedTarget)) ddSet(dd,false); });
    });
    document.addEventListener('click',function(e){ dds.forEach(function(dd){ if(dd.classList.contains('open') && !dd.contains(e.target)) ddSet(dd,false); }); });
    var here=location.pathname.replace(/\/index\.html$/,'/');
    document.querySelectorAll('.menu a').forEach(function(a){ var h=a.getAttribute('href'); if(h && (h===here || (h!=='/' && here.indexOf(h)===0))){ a.classList.add('on'); var dd=a.closest('.dd'); if(dd) dd.classList.add('on'); } });
    // analytics notice: a 1-line toast at the bottom, gone on the first scroll or tap (remembered per browser)
    try{ if(C.GA4_ID && !localStorage.getItem('tmu_notice')){ var n=document.createElement('div'); n.className='notice'; n.setAttribute('role','region'); n.setAttribute('aria-label','Analytics notice'); n.innerHTML='We use analytics and ad-measurement pixels (Google, TikTok, Meta, Snap) to see which pages and ads bring people here. <a href="/privacy.html">Privacy</a> <button type="button">OK</button>'; document.body.appendChild(n);
      var done=function(){ try{localStorage.setItem('tmu_notice','1')}catch(e){} n.remove(); window.removeEventListener('scroll',onScroll); document.removeEventListener('pointerdown',onTap,true); };
      var onScroll=function(){ if(window.scrollY>24) done(); }, onTap=function(e){ if(!n.contains(e.target)) done(); };
      n.querySelector('button').onclick=done; window.addEventListener('scroll',onScroll,{passive:true}); document.addEventListener('pointerdown',onTap,true); } }catch(e){}
    // autoplay only while in view (saves bandwidth, keeps LCP clean)
    var vids=document.querySelectorAll('video[data-autoplay]');
    if('IntersectionObserver' in window){ var io=new IntersectionObserver(function(es){ es.forEach(function(e){ var v=e.target; if(e.isIntersecting){ v.play().catch(function(){}); } else { v.pause(); } }); },{threshold:.25}); vids.forEach(function(v){ io.observe(v); }); }
    else { vids.forEach(function(v){ v.setAttribute('autoplay',''); v.play().catch(function(){}); }); }
    // sound toggle on muted autoplay host videos
    document.querySelectorAll('[data-unmute]').forEach(function(b){ var v=b.parentNode.querySelector('video'); if(!v) return; b.onclick=function(){ v.muted=!v.muted; if(!v.muted){ v.currentTime=0; v.play(); } b.innerHTML = v.muted ? '&#9654; Sound on' : '&#10073;&#10073; Mute'; track('VideoSound',{on:!v.muted}); }; });
    // /shop product gallery: thumbs (buttons) swap the stage; arrow keys move between thumbs; swipe on the stage.
    // The video slide has no src until its thumb is chosen, then plays from that click; it pauses when you leave it.
    document.querySelectorAll('[data-gallery-stage]').forEach(function(stage){
      var thumbs=[].slice.call(document.querySelectorAll('[data-gallery-thumbs] .pthumb')), slides=[].slice.call(stage.querySelectorAll('.pslide')), cur=0;
      if(!thumbs.length||thumbs.length!==slides.length) return;
      var show=function(i, play){
        i=(i+slides.length)%slides.length;
        slides.forEach(function(s,k){ s.hidden=(k!==i); var v=s.querySelector('video'); if(v&&k!==i&&!v.paused) v.pause(); });
        thumbs.forEach(function(t,k){ t.setAttribute('aria-pressed', k===i?'true':'false'); t.tabIndex=(k===i?0:-1); });
        cur=i; stage.setAttribute('data-current', String(i)); [].forEach.call(stage.querySelectorAll('.pdots i'),function(d,k){ d.classList.toggle('on',k===i); });
        var v=slides[i].querySelector('video');
        if(v){ if(!v.getAttribute('data-loaded')){ [].forEach.call(v.querySelectorAll('source[data-src]'),function(s){ s.src=s.getAttribute('data-src'); }); v.setAttribute('data-loaded','1'); v.load(); }
          if(play){ v.muted=true; var p=v.play(); if(p&&p.catch) p.catch(function(){}); } }
        var t=thumbs[i], pr=t.parentNode; if(pr.scrollWidth>pr.clientWidth) pr.scrollLeft=t.offsetLeft-pr.clientWidth/2+t.offsetWidth/2;
        var rk=slides[i].getAttribute('data-roast'); if(rk) roastPick(rk, false);
      };
      stage.tmuShow=show;
      thumbs.forEach(function(t,k){ t.tabIndex=(k===0?0:-1);
        t.addEventListener('click',function(){ show(k, true); });
        t.addEventListener('keydown',function(e){ var d={ArrowRight:1,ArrowDown:1,ArrowLeft:-1,ArrowUp:-1}[e.key], j=null;
          if(d) j=(k+d+thumbs.length)%thumbs.length; else if(e.key==='Home') j=0; else if(e.key==='End') j=thumbs.length-1;
          if(j===null) return; e.preventDefault(); thumbs[j].focus(); show(j, false); });
      });
      // swipe: a mostly horizontal drag of 40px or more on the stage (not on the video's own controls)
      var x0=null, y0=0;
      stage.addEventListener('pointerdown',function(e){ if(e.pointerType==='mouse'||e.target.tagName==='VIDEO'){ x0=null; return; } x0=e.clientX; y0=e.clientY; });
      stage.addEventListener('pointerup',function(e){ if(x0===null) return; var dx=e.clientX-x0, dy=e.clientY-y0; x0=null;
        if(Math.abs(dx)>=40&&Math.abs(dx)>Math.abs(dy)*1.3) show(cur+(dx<0?1:-1), false); });
      stage.addEventListener('pointercancel',function(){ x0=null; });
    });
    // Cup of Joe roast picker: shows that roast's tasting notes and its bag in the gallery. The roast itself is
    // chosen on the Stripe checkout page (a Payment Link can't be prefilled with a custom field).
    function roastPick(k, moveGallery){
      var box=document.querySelector('[data-roast-pick]'); if(!box) return;
      var r=box.querySelector('input[value="'+k+'"]'); if(!r) return;
      r.checked=true;
      box.querySelectorAll('.ropt').forEach(function(o){ o.classList.toggle('on', o.contains(r)); });
      var nm=box.querySelector('[data-roast-name]'), nt=box.querySelector('[data-roast-notes]');
      if(nm) nm.textContent=r.parentNode.textContent.trim(); if(nt) nt.textContent=r.getAttribute('data-notes')||'';
      if(moveGallery){ var st=document.querySelector('[data-gallery-stage]'), sl=st&&st.querySelector('.pslide[data-roast="'+k+'"]');
        if(st&&st.tmuShow&&sl){ st.tmuShow([].indexOf.call(st.querySelectorAll('.pslide'), sl), false); } }
    }
    document.querySelectorAll('[data-roast-pick] input[type=radio]').forEach(function(r){ r.addEventListener('change',function(){ roastPick(r.value, true); }); });
    // year
    document.querySelectorAll('.yr').forEach(function(e){ e.textContent=new Date().getFullYear(); });

    // Plan picker: radio choice drives the single buy button
    document.querySelectorAll('[data-picker]').forEach(function(p){
      var btn=p.querySelector('[data-picker-btn]');
      // paid visits start on the plan the page asks for (data-paid-default, "onetime" on /start)
      var pd=p.getAttribute('data-paid-default'); if(pd && C.PAID){ var pr=p.querySelector('input[value="'+pd+'"]'); if(pr && !pr.checked){ pr.checked=true; setTimeout(function(){ pr.dispatchEvent(new Event('change',{bubbles:true})); },0); } }
      p.querySelectorAll('input[type=radio]').forEach(function(r){ r.addEventListener('change', function(){
        p.querySelectorAll('.opt').forEach(function(o){ o.classList.toggle('on', o.contains(r)); });
        btn.setAttribute('data-buy', r.value); wire(btn);
        var t=btn.querySelector('[data-cta]'); if(t&&r.getAttribute('data-cta')) t.textContent=r.getAttribute('data-cta');
        // the sticky bar follows the plan the visitor picked
        var sb=document.querySelector('.sticky a[data-buy]'); if(sb){ sb.setAttribute('data-buy', r.value); wire(sb); }
        var sp=document.querySelector('.sticky [data-sticky-price]'); if(sp&&r.getAttribute('data-sticky')) sp.textContent=r.getAttribute('data-sticky');
        promoNotes();
      }); });
    });
    // Buy buttons: data-buy="onetime|subscribe", or a house coffee: data-buy="cupofjoe|mushroom" (Stripe only)
    var utm = location.search ? location.search.replace(/^\?/,'') : '';
    // Only the page's utm_* tags ride to Stripe (utm_source defaults to "site"). Anything else in the
    // landing URL (client_reference_id, prefilled_email, promo codes, click ids) is never forwarded, so
    // a crafted link can't override creator/ad credit and Stripe sees one value per tag.
    var stripeQs = (function(){ var o=[], has={}; try{ new URLSearchParams(location.search).forEach(function(v,k){
        if(/^utm_(source|medium|campaign|content|term)$/.test(k) && !has[k] && v){ has[k]=1; o.push(k+'='+encodeURIComponent(v.slice(0,100))); } }); }catch(e){}
      if(!has.utm_source) o.unshift('utm_source=site'); return o.join('&'); })();
    function wire(a){
      var kind=a.getAttribute('data-buy');
      var link = linkOf(kind);
      if (ITEM[kind] && ITEM[kind].house && !link) { a.dataset.mode='none'; return; }   // no MarketPlace Global fallback for house coffee
      if (link) {
        a.href = link + (link.indexOf('?')>-1?'&':'?') + stripeQs
          + (C.REF ? '&client_reference_id=cr_' + C.REF : (C.UT ? '&client_reference_id=' + C.UT : ''));
        a.removeAttribute('rel'); a.removeAttribute('target');
      } else {
        a.href = C.MPG_PRODUCT + '?utm_source=site&utm_medium=shop&utm_campaign=' + kind + (utm?'&'+utm:'')
          + (C.REF && !/(^|&)utm_content=/.test(utm) ? '&utm_content=cr_' + C.REF : '');
        a.setAttribute('rel','sponsored'); a.setAttribute('target','_blank');
      }
      a.dataset.mode = link?'stripe':'mpg';
    }
    document.querySelectorAll('[data-buy]').forEach(function(a){
      wire(a);
      a.addEventListener('click', function(ev){ var k=a.getAttribute('data-buy'); try{ localStorage.setItem('tmu_plan', k); }catch(e){} track('InitiateCheckout',{plan:k, mode:a.dataset.mode, value:PRICE[k]||PRICE.subscribe, currency:'USD'}); tmuEvent('buy_click', a.dataset.mode+':'+(ITEM[k]&&ITEM[k].house?k:(k==='onetime'?'onetime':'subscribe'))); C.startedCheckout(a, k, 'site', ev); });
    });
    promoNotes();
    // The sticky bar steps aside while any picker's buy button is on screen (it would duplicate it).
    var stickyEl=document.querySelector('.sticky'), pbs=document.querySelectorAll('[data-picker-btn],[data-buy-main]');
    if(stickyEl && pbs.length && 'IntersectionObserver' in window){ var seen=new Map();
      var sio=new IntersectionObserver(function(es){ es.forEach(function(e){ seen.set(e.target, e.isIntersecting); }); var any=false; seen.forEach(function(v){ if(v) any=true; }); stickyEl.classList.toggle('hide', any); },{threshold:0});
      pbs.forEach(function(b){ sio.observe(b); }); }
    // Shipping / checkout copy depends on which checkout is live. Never promise free shipping in handoff mode.
    var SELF = !!(C.STRIPE_ONETIME||C.STRIPE_SUBSCRIBE);
    var SHIP = SELF ? {
      bar:'$8.95 flat US shipping', short:'$8.95 US shipping', trust:'$8.95 flat US shipping', long:'$8.95 flat US shipping, added at checkout.',
      checkout:'Secure checkout by Stripe', damage:'90-day money-back guarantee on unopened bags',
      policy:'The maker, MarketPlace Global, ships from Maple Grove, Minnesota within about 2 business days, then 3\u20136 days in transit. US shipping is a flat $8.95 a bag.'
    } : {
      bar:'$8.95 flat US shipping', short:'$8.95 US shipping', trust:'$8.95 flat US shipping', long:'$8.95 flat US shipping, shown at checkout.',
      checkout:'Secure checkout', damage:'Made right if it arrives damaged',
      policy:'The maker, MarketPlace Global, ships from Maple Grove, Minnesota within about 2 business days, then 3\u20136 days in transit. US shipping is a flat $8.95 a bag, shown at their checkout.'
    };
    document.querySelectorAll('[data-ship]').forEach(function(e){ var k=e.getAttribute('data-ship'); if(SHIP[k]) e.textContent = SHIP[k]; });
    // First-order bonus is only promised when checkout is ours (the order page delivers it).
    document.querySelectorAll('[data-bonus]').forEach(function(e){ e.hidden = !SELF; });

    // Partner buttons
    document.querySelectorAll('[data-enroll]').forEach(function(a){
      if (C.ENROLL_URL) { a.href=C.ENROLL_URL; a.setAttribute('target','_blank'); }
      else { a.href='#apply'; a.textContent = a.getAttribute('data-fallback') || 'Ask about joining'; }
      a.addEventListener('click', function(){ track('PartnerClick'); });
    });
    document.querySelectorAll('[data-disclosure]').forEach(function(a){
      if (C.INCOME_DISCLOSURE_URL) { a.href=C.INCOME_DISCLOSURE_URL; a.setAttribute('target','_blank'); }
      else { a.textContent='Income disclosure statement (available on request: hello@themorningupgrades.com)'; a.removeAttribute('href'); }
    });

    // Klaviyo subscribe helper
    window.klaviyoSubscribe = function(listId, email, firstName, props, source){
      var body={data:{type:'subscription',attributes:{custom_source:source||'themorningupgrades.com',
        profile:{data:{type:'profile',attributes:{email:email,first_name:firstName||'',properties:props||{}}}}},
        relationships:{list:{data:{type:'list',id:listId}}}}};
      // a customer-list sign-up that Klaviyo accepted: remember the email on this device for Started Checkout
      return fetch('https://a.klaviyo.com/client/subscriptions/?company_id='+C.KLAVIYO_COMPANY,{method:'POST',headers:{'Content-Type':'application/json','revision':'2025-01-15'},body:JSON.stringify(body)})
        .then(function(r){ if(r && r.status===202 && listId!==C.KLAVIYO_LIST_PARTNERS) C.klRemember(email); return r; });
    };

    // ---------- After a pop-up sign-up: a short note next to Subscribe & Save buttons ----------
    // (function declarations only: promoNotes() first runs above, before any var here is assigned)
    function noteEl(){ var n=document.createElement('p'); n.className='promo-note'; n.textContent='Subscribe & Save is $69.95 a month; 1 bag is $79.95 \u00b7 Cancel anytime'; return n; }
    function promoNotes(){
      var on=C.signedUp() && !!C.STRIPE_SUBSCRIBE;
      // plan pickers: under the buy button, only while Subscribe & Save is picked
      document.querySelectorAll('[data-picker]').forEach(function(p){
        var btn=p.querySelector('[data-picker-btn]'); if(!btn) return;
        var n=p.querySelector('.promo-note'); if(!n && on){ n=noteEl(); btn.parentNode.insertBefore(n, btn.nextSibling); }
        if(n) n.hidden=!(on && btn.getAttribute('data-buy')==='subscribe');
      });
      // other Subscribe & Save buttons (CTA rows, the order page's next-bag card)
      document.querySelectorAll('a[data-buy="subscribe"]').forEach(function(a){
        if(a.closest('[data-picker],.sticky,.tmu-pop')) return;
        if(!a._pn && on){
          var n=noteEl(), row=a.closest('.ctab'), par=a.parentNode;
          if(row) row.insertBefore(n, row.querySelector('.fine'));
          else if(par.tagName==='P' && par.children.length===1) par.parentNode.insertBefore(n, par.nextSibling);
          else par.insertBefore(n, a.nextSibling);
          a._pn=n;
        }
        if(a._pn) a._pn.hidden=!on;
      });
      // the phone sticky bar: a short line under the price while it checks out Subscribe & Save
      var sb=document.querySelector('.sticky a[data-buy]'), sd=sb&&sb.parentNode.querySelector('div');
      if(sd){ var sn=sd.querySelector('.promo-sticky');
        if(!sn && on){ sn=document.createElement('span'); sn.className='promo-sticky'; sn.textContent='$69.95 a month; 1 bag is $79.95'; sd.appendChild(sn); }
        if(sn) sn.hidden=!(on && sb.getAttribute('data-buy')==='subscribe'); }
    }

    // ---------- Pop-up: the Recipe Pack free for signing up, and the two prices stated plainly ----------
    // Opens once per visitor after POPUP_DELAY_MS, at 50% scroll, or on desktop exit intent, whichever is
    // first. Never on pages built with <body data-popup="off"> (order page, thank-you, partner/ISR, 404,
    // the quiz page, /start), never on a paid visit (C.PAID), never while the quiz is on screen or in
    // progress, never after an order from this browser, never again after sign-up; closing it (or just
    // seeing it) snoozes it POPUP_SNOOZE_DAYS.
    function ga(n,p){ try{ if(window.gtag&&C.GA4_ID) gtag('event',n,p||{}); }catch(e){} }
    function popEligible(){
      if(!C.STRIPE_SUBSCRIBE || !C.POPUP_DELAY_MS) return false;
      if(document.body.getAttribute('data-popup')==='off' || C.PAID || C.ordered()) return false;
      var s=lsJSON('tmu_pop'); if(s && (s.s==='signed' || Date.now()-(+s.t||0) < (C.POPUP_SNOOZE_DAYS||14)*864e5)) return false;
      return !document.querySelector('.tmu-pop');
    }
    function popBusy(){
      var qz=document.querySelector('.quiz[data-source]');
      if(qz){ var cur=qz.querySelector('.q.on'); if(cur && cur.getAttribute('data-q')!=='1') return true;   // quiz under way or done
        var r=(document.getElementById('quiz')||qz).getBoundingClientRect(); if(r.top<innerHeight && r.bottom>0) return true; }
      var ae=document.activeElement; if(ae && /^(INPUT|TEXTAREA|SELECT)$/.test(ae.tagName)) return true;   // typing somewhere
      return !!document.querySelector('.menu.open') || document.visibilityState==='hidden';
    }
    if (popEligible()) (function(){
      var armed=true, retry=0, t0=Date.now();
      function off(){ armed=false; clearTimeout(timer); clearTimeout(retry); window.removeEventListener('scroll',onScroll); document.removeEventListener('mouseout',onOut); }
      function attempt(why, again){
        if(!armed) return;
        if(!popEligible()){ off(); return; }
        if(popBusy()){ if(again && !retry) retry=setTimeout(function(){ retry=0; attempt(why, true); }, 3000); return; }
        off(); openPopup(why);
      }
      var timer=setTimeout(function(){ attempt('timer', true); }, C.POPUP_DELAY_MS);
      function onScroll(){ var max=document.documentElement.scrollHeight-innerHeight;
        if(max>innerHeight*0.5 && scrollY/max>=0.5) attempt('scroll', true); }
      function onOut(e){ if(!e.relatedTarget && e.clientY<=0 && Date.now()-t0>2500) attempt('exit', false); }
      window.addEventListener('scroll',onScroll,{passive:true});
      if(window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches && innerWidth>860) document.addEventListener('mouseout',onOut);
    })();

    function openPopup(why){
      var pack=C.RECIPE_PACK||'/assets/recipe-pack.pdf', img='/img/opt/lux-iced-';
      var srcs=function(ext){ return img+'480.'+ext+' 480w, '+img+'800.'+ext+' 800w'; };
      var wrap=document.createElement('div'); wrap.className='tmu-pop';
      wrap.innerHTML=
        '<div class="tp-bg" data-close></div>'+
        '<div class="tp-panel" role="dialog" aria-modal="true" aria-labelledby="tp-h" aria-describedby="tp-d" tabindex="-1">'+
          '<button class="tp-x" type="button" aria-label="Close" data-close><span aria-hidden="true"></span></button>'+
          '<div class="tp-media" aria-hidden="true"><picture><source type="image/avif" srcset="'+srcs('avif')+'" sizes="340px"><source type="image/webp" srcset="'+srcs('webp')+'" sizes="340px"><img src="'+img+'800.jpg" alt="" width="1600" height="2000" loading="lazy" decoding="async"></picture></div>'+
          '<div class="tp-body">'+
            '<div class="tp-step" data-step="form">'+
              '<p class="eyebrow">The Morning Upgrade list</p>'+
              '<h2 id="tp-h">Get the Recipe Pack free.<br> Subscribe&nbsp;&amp;&nbsp;Save is $69.95 a month.</h2>'+
              '<ol class="tp-gets" id="tp-d">'+
                '<li><span>01</span><div><b>The Recipe Pack, free</b><i>12 drinks, hot, iced and blended, plus a 30-morning tracker. PDF.</i></div></li>'+
                '<li><span>02</span><div><b>Subscribe &amp; Save, $69.95 a month</b><i>1 bag every 30 days. 1 bag on its own is $79.95. Pause, skip or cancel anytime.</i></div></li>'+
              '</ol>'+
              '<form class="tp-form" novalidate>'+
                '<div class="tp-fields">'+
                  '<div><label for="tp-first">First name <span>(optional)</span></label><input id="tp-first" type="text" name="first_name" autocomplete="given-name"></div>'+
                  '<div><label for="tp-email">Email</label><input id="tp-email" type="email" name="email" required autocomplete="email" inputmode="email" aria-describedby="tp-msg"></div>'+
                '</div>'+
                '<button class="btn big" type="submit">Send my Recipe Pack</button>'+
                '<p class="tp-msg" id="tp-msg" role="status" aria-live="polite"></p>'+
                '<p class="tp-fine">Subscribe &amp; Save is $69.95 a month (1 bag every 30 days); 1 bag on its own is $79.95. Pause, skip or cancel anytime.</p>'+
                '<p class="tp-fine">By signing up you agree to emails from The Morning Upgrade. Unsubscribe anytime. <a href="/privacy.html">Privacy</a></p>'+
              '</form>'+
              '<button class="tp-no" type="button" data-close>No thanks</button>'+
            '</div>'+
            '<div class="tp-step" data-step="done" hidden>'+
              '<p class="eyebrow">You&rsquo;re on the list</p>'+
              '<h2 id="tp-h2" tabindex="-1">Your Recipe Pack is ready.</h2>'+
              '<p class="tp-lede">12 drinks and a 30-morning tracker for the fridge. When you&rsquo;re ready for coffee, Subscribe &amp; Save is $69.95 a month; 1 bag is $79.95.</p>'+
              '<a class="btn ghost big tp-dl" href="'+pack+'" download>Download the Recipe Pack</a>'+
              '<a class="btn big tp-use" data-buy="subscribe" href="/corejava.html">Start Subscribe &amp; Save, $69.95 a month</a>'+
              '<p class="tp-fine">$69.95 every 30 days plus $8.95 shipping, until you cancel. Pause, skip or cancel anytime.</p>'+
            '</div>'+
          '</div>'+
        '</div>';
      var panel=wrap.querySelector('.tp-panel'), f=wrap.querySelector('form'), msg=wrap.querySelector('#tp-msg');
      var prev=document.activeElement, root=document.documentElement, oldOverflow=root.style.overflow, signed=false;
      document.body.appendChild(wrap);
      root.style.overflow='hidden';
      lsSet('tmu_pop', JSON.stringify({s:'seen',t:Date.now()}));
      requestAnimationFrame(function(){ wrap.classList.add('on'); });
      var fine=window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
      (fine ? wrap.querySelector('#tp-email') : panel).focus({preventScroll:true});
      ga('PopupView',{trigger:why});

      function close(){
        if(!wrap.parentNode) return;
        if(!signed) lsSet('tmu_pop', JSON.stringify({s:'closed',t:Date.now()}));
        document.removeEventListener('keydown',onKey,true); document.removeEventListener('focusin',onFocus,true);
        root.style.overflow=oldOverflow; wrap.remove();
        try{ if(prev && prev.focus && document.contains(prev)) prev.focus({preventScroll:true}); }catch(e){}
        ga('PopupClose',{signed:signed});
      }
      function focusables(){ return [].slice.call(panel.querySelectorAll('a[href],button:not([disabled]),input:not([disabled])')).filter(function(e){ return e.getClientRects().length>0; }); }
      function onKey(e){
        if(e.key==='Escape'||e.key==='Esc'){ e.preventDefault(); close(); return; }
        if(e.key!=='Tab') return;
        var fs=focusables(); if(!fs.length){ e.preventDefault(); return; }
        var a=document.activeElement, first=fs[0], last=fs[fs.length-1];
        if(e.shiftKey && (a===first || !panel.contains(a) || a===panel)){ e.preventDefault(); last.focus(); }
        else if(!e.shiftKey && (a===last || !panel.contains(a))){ e.preventDefault(); first.focus(); }
      }
      function onFocus(e){ if(!panel.contains(e.target)){ var fs=focusables(); (fs[0]||panel).focus(); } }
      document.addEventListener('keydown',onKey,true); document.addEventListener('focusin',onFocus,true);
      wrap.querySelectorAll('[data-close]').forEach(function(b){ b.addEventListener('click', close); });

      f.addEventListener('submit', function(e){
        e.preventDefault();
        var em=f.email, email=em.value.trim(), first=f.first_name.value.trim().slice(0,60);
        if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){ em.setAttribute('aria-invalid','true'); msg.textContent='Check the email address.'; em.focus(); return; }
        em.removeAttribute('aria-invalid');
        var btn=f.querySelector('button[type=submit]'), label=btn.textContent; btn.disabled=true; btn.textContent='Sending…'; msg.textContent='';
        var q; try{ q=new URLSearchParams(location.search); }catch(x){ q={get:function(){ return ''; }}; }
        var props={offer:'recipe_pack_plus_autoship10',lead_magnet:'Recipe Pack',source:'popup',signup_page:location.pathname,
          utm_source:q.get('utm_source')||'',utm_medium:q.get('utm_medium')||'',utm_campaign:q.get('utm_campaign')||'',utm_content:q.get('utm_content')||''};
        var p; try{ p=window.klaviyoSubscribe(C.KLAVIYO_LIST_NEWSLETTER||C.KLAVIYO_LIST_QUIZ, email, first, props, 'popup'); }catch(x){ p=Promise.reject(x); }
        p.then(function(r){ if(r && r.status===202) done(); else throw new Error(r && r.status); })
         .catch(function(){ msg.textContent='That didn’t go through. Check your connection and try again.'; btn.disabled=false; btn.textContent=label; });
      });
      function done(){
        signed=true;
        lsSet('tmu_pop', JSON.stringify({s:'signed',t:Date.now()}));
        track('Lead',{source:'popup'});
        tmuEvent('lead','popup');
        wrap.querySelector('[data-step="form"]').hidden=true;
        wrap.querySelector('[data-step="done"]').hidden=false;
        panel.setAttribute('aria-labelledby','tp-h2'); panel.removeAttribute('aria-describedby');
        promoNotes();
        wrap.querySelector('#tp-h2').focus({preventScroll:true});
      }
      var use=wrap.querySelector('.tp-use');
      wire(use);   // the normal Subscribe & Save checkout (utm tags and creator/ad credit ride along as usual)
      use.addEventListener('click', function(ev){ lsSet('tmu_plan','subscribe'); track('InitiateCheckout',{plan:'subscribe',mode:use.dataset.mode,value:PRICE.subscribe,currency:'USD',source:'popup'}); tmuEvent('buy_click', use.dataset.mode+':subscribe'); C.startedCheckout(use, 'subscribe', 'popup', ev); });
      wrap.querySelector('.tp-dl').addEventListener('click', function(){ ga('RecipePackDownload',{source:'popup'}); });
    }
  });
})();
