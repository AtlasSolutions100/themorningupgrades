/* The Morning Upgrade — site config + shared behaviour.
   Fill the CONFIG values as accounts come online. Empty Stripe links = "handoff" mode (Buy sends to the MPG product page). */
window.TMU = {
  // Stripe Payment Links (create in Stripe Dashboard → Payment Links). Leave "" until they exist.
  STRIPE_ONETIME: "https://buy.stripe.com/3cIbJ3fEv6XIbtk8iw4wM00",          // one bag, $79.95, ships from us
  STRIPE_SUBSCRIBE: "https://buy.stripe.com/8x228t3VN2Hsapg56k4wM01",        // one bag a month, $69.95, ships from us
  // MarketPlace Global replicated product page (handoff fallback while Stripe is empty)
  MPG_PRODUCT: "https://marketplaceglobal.com/rectorandstull/product/coffee/mpgxtreme-1-bag-corejava-coffee-skucl805-us-id194",
  // Partner side
  ENROLL_URL: "https://marketplaceglobal.com/rectorandstull/join-the-place",
  INCOME_DISCLOSURE_URL: "https://marketplaceglobal.com/rectorandstull/income-disclaimer",
  // Lists
  KLAVIYO_COMPANY: "Ucdz59",
  KLAVIYO_LIST_QUIZ: "WgctGT",
  KLAVIYO_LIST_PARTNERS: "WeMj34",   // separate list; never the customer list
  // Tracking
  RETAIL_BONUS_PCT: 0,         // ISR Retail Customer Bonus % on referred customer orders (0 = hide the math)
  GA4_ID: "G-G79BLY9MDG",       // Google Analytics 4
  TIKTOK_PIXEL: "DBDQJRRC77U24SKT5GP0", // TikTok pixel
  PIXEL_ID: "28758618673764449", // Meta pixel (dataset "TMU Website", Rector & Stull LLC portfolio)
  SNAP_PIXEL: "ed6288c4-136e-418b-9d3d-5f3cb47998d4", // Snap pixel ("Rector & Stull Pixel")
  GOOGLE_ADS_ID: "AW-18543041154",               // Google Ads account "Rector & Stull" (shared with Crowdcut)
  GOOGLE_PURCHASE: "AW-18543041154/9DvuCJSurq0dEIK1gYpF", // conversion action "TMU Purchase"
  ANALYTICS_DOMAIN: "themorningupgrades.com"
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

  var TT_MAP={InitiateCheckout:'InitiateCheckout',ViewContent:'ViewContent',Lead:'CompleteRegistration',QuizComplete:'ViewContent',PartnerLead:'SubmitForm',PartnerClick:'ClickButton',Purchase:'CompletePayment'};
  var FB_STD={InitiateCheckout:1,ViewContent:1,Lead:1,Purchase:1};
  var SNAP_MAP={InitiateCheckout:'START_CHECKOUT',ViewContent:'VIEW_CONTENT',Lead:'SIGN_UP',QuizComplete:'VIEW_CONTENT',PartnerLead:'SIGN_UP',Purchase:'PURCHASE'};
  var GA_SKIP={ViewContent:1};   // GA4 already has page_view; ViewContent is for the ad pixels
  // Plan prices (coffee subtotal, before shipping and tax). Purchase/InitiateCheckout values use these.
  var PRICE={subscribe:69.95,onetime:79.95}, SKU='CL805';
  C.PRICE=PRICE;
  window.track = function(name, props){ try{
    props=props||{};
    var isP=name==='Purchase', val=(typeof props.value==='number')?props.value:PRICE.subscribe, eid=props.transaction_id||'';
    if(window.gtag&&C.GA4_ID&&!GA_SKIP[name]) gtag('event', name, props);
    if(window.ttq&&C.TIKTOK_PIXEL&&TT_MAP[name]) ttq.track(TT_MAP[name], (isP||name==='ViewContent'||name==='InitiateCheckout')?{value:val,currency:'USD',content_type:'product',content_id:SKU}:props, eid?{event_id:eid}:undefined);
    if(window.fbq&&C.PIXEL_ID){ if(FB_STD[name]) fbq('track',name,(isP||name==='ViewContent'||name==='InitiateCheckout')?Object.assign({},props,{value:val,currency:'USD',content_ids:[SKU],content_type:'product'}):props, eid?{eventID:eid}:undefined); else fbq('trackCustom',name,props); }
    if(window.gtag&&C.GOOGLE_PURCHASE&&isP) gtag('event','conversion',{send_to:C.GOOGLE_PURCHASE,value:val,currency:'USD',transaction_id:eid});
    if(window.snaptr&&C.SNAP_PIXEL&&SNAP_MAP[name]) snaptr('track',SNAP_MAP[name],(isP||name==='ViewContent'||name==='InitiateCheckout')?Object.assign({price:val,currency:'USD',item_ids:[SKU],number_items:1},eid?{transaction_id:eid}:{}):{});
    if(window.plausible) plausible(name,{props:props});
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
    if(window.gtag&&C.GA4_ID) gtag('event','purchase',{transaction_id:sid,value:value,currency:'USD',
      items:[{item_id:SKU,item_name:'MCT Instant Coffee with L-Theanine, 30 Servings',item_variant:plan,price:value,quantity:1}]});
    return true;
  }catch(e){ return false; } };

  // ViewContent on the product pages, for TikTok / Meta / Snap optimisation.
  // GitHub Pages also serves /shop and /start without .html: count those too (ad URLs often drop it).
  if (/^\/((index|shop|start)(\.html)?)?$/.test(location.pathname)) track('ViewContent',{value:PRICE.subscribe,currency:'USD'});

  if (qref) track('CreatorVisit',{creator:qref});

  document.addEventListener('DOMContentLoaded', function(){
    // nav
    var b=document.querySelector('.burger'), m=document.querySelector('.menu');
    if(b&&m) b.onclick=function(){ var open=m.classList.toggle('open'); b.setAttribute('aria-expanded', open?'true':'false'); b.setAttribute('aria-label', open?'Close menu':'Open menu'); };
    var here=location.pathname.replace(/\/index\.html$/,'/');
    document.querySelectorAll('.menu a').forEach(function(a){ var h=a.getAttribute('href'); if(h && (h===here || (h!=='/' && here.indexOf(h)===0))) a.classList.add('on'); });
    // analytics notice (dismissable, remembered per browser)
    try{ if(C.GA4_ID && !localStorage.getItem('tmu_notice')){ var n=document.createElement('div'); n.className='notice'; n.setAttribute('role','region'); n.setAttribute('aria-label','Analytics notice'); n.innerHTML='We use analytics and ad-measurement pixels (Google, TikTok, Meta, Snap) to see which pages and ads bring people here. <a href="/privacy.html">Privacy</a> <button type="button">OK</button>'; var nv=document.querySelector('.nav'); if(nv&&nv.parentNode) nv.parentNode.insertBefore(n, nv.nextSibling); else document.body.insertBefore(n, document.body.firstChild); var done=function(){ try{localStorage.setItem('tmu_notice','1')}catch(e){} n.remove(); window.removeEventListener('scroll',onScroll); }; var onScroll=function(){ if(window.scrollY>window.innerHeight*0.6) done(); }; n.querySelector('button').onclick=done; window.addEventListener('scroll',onScroll,{passive:true}); } }catch(e){}
    // autoplay only while in view (saves bandwidth, keeps LCP clean)
    var vids=document.querySelectorAll('video[data-autoplay]');
    if('IntersectionObserver' in window){ var io=new IntersectionObserver(function(es){ es.forEach(function(e){ var v=e.target; if(e.isIntersecting){ v.play().catch(function(){}); } else { v.pause(); } }); },{threshold:.25}); vids.forEach(function(v){ io.observe(v); }); }
    else { vids.forEach(function(v){ v.setAttribute('autoplay',''); v.play().catch(function(){}); }); }
    // sound toggle on muted autoplay host videos
    document.querySelectorAll('[data-unmute]').forEach(function(b){ var v=b.parentNode.querySelector('video'); if(!v) return; b.onclick=function(){ v.muted=!v.muted; if(!v.muted){ v.currentTime=0; v.play(); } b.innerHTML = v.muted ? '&#9654; Sound on' : '&#10073;&#10073; Mute'; track('VideoSound',{on:!v.muted}); }; });
    // year
    document.querySelectorAll('.yr').forEach(function(e){ e.textContent=new Date().getFullYear(); });

    // Plan picker: radio choice drives the single buy button
    document.querySelectorAll('[data-picker]').forEach(function(p){
      var btn=p.querySelector('[data-picker-btn]');
      p.querySelectorAll('input[type=radio]').forEach(function(r){ r.addEventListener('change', function(){
        p.querySelectorAll('.opt').forEach(function(o){ o.classList.toggle('on', o.contains(r)); });
        btn.setAttribute('data-buy', r.value); wire(btn);
        var t=btn.querySelector('[data-cta]'); if(t&&r.getAttribute('data-cta')) t.textContent=r.getAttribute('data-cta');
        // the sticky bar follows the plan the visitor picked
        var sb=document.querySelector('.sticky a[data-buy]'); if(sb){ sb.setAttribute('data-buy', r.value); wire(sb); }
        var sp=document.querySelector('.sticky [data-sticky-price]'); if(sp&&r.getAttribute('data-sticky')) sp.textContent=r.getAttribute('data-sticky');
      }); });
    });
    // Buy buttons: data-buy="onetime|subscribe"
    var utm = location.search ? location.search.replace(/^\?/,'') : '';
    // Only the page's utm_* tags ride to Stripe (utm_source defaults to "site"). Anything else in the
    // landing URL (client_reference_id, prefilled_email, promo codes, click ids) is never forwarded, so
    // a crafted link can't override creator/ad credit and Stripe sees one value per tag.
    var stripeQs = (function(){ var o=[], has={}; try{ new URLSearchParams(location.search).forEach(function(v,k){
        if(/^utm_(source|medium|campaign|content|term)$/.test(k) && !has[k] && v){ has[k]=1; o.push(k+'='+encodeURIComponent(v.slice(0,100))); } }); }catch(e){}
      if(!has.utm_source) o.unshift('utm_source=site'); return o.join('&'); })();
    function wire(a){
      var kind=a.getAttribute('data-buy');
      var link = kind==='subscribe' ? C.STRIPE_SUBSCRIBE : C.STRIPE_ONETIME;
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
      a.addEventListener('click', function(){ var k=a.getAttribute('data-buy'); try{ localStorage.setItem('tmu_plan', k); }catch(e){} track('InitiateCheckout',{plan:k, mode:a.dataset.mode, value:PRICE[k]||PRICE.subscribe, currency:'USD'}); });
    });
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
      return fetch('https://a.klaviyo.com/client/subscriptions/?company_id='+C.KLAVIYO_COMPANY,{method:'POST',headers:{'Content-Type':'application/json','revision':'2025-01-15'},body:JSON.stringify(body)});
    };
  });
})();
