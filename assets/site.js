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
  PIXEL_ID: "1881913686131010", // Meta pixel (dataset "TMU Website", Rector & Stull LLC portfolio)
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

  var TT_MAP={InitiateCheckout:'InitiateCheckout',Lead:'CompleteRegistration',QuizComplete:'ViewContent',PartnerLead:'SubmitForm',PartnerClick:'ClickButton',Purchase:'CompletePayment'};
  var FB_STD={InitiateCheckout:1,Lead:1,Purchase:1};
  window.track = function(name, props){ try{ if(window.gtag&&C.GA4_ID) gtag('event', name, props||{}); if(window.ttq&&C.TIKTOK_PIXEL&&TT_MAP[name]) ttq.track(TT_MAP[name], name==='Purchase'?{value:79.95,currency:'USD',content_type:'product',content_id:'CL805'}:(props||{})); if(window.fbq&&C.PIXEL_ID){ if(FB_STD[name]) fbq('track',name,name==='Purchase'?Object.assign({value:79.95,currency:'USD',content_ids:['CL805'],content_type:'product'},props||{}):(props||{})); else fbq('trackCustom',name,props||{}); } if(window.plausible) plausible(name,{props:props||{}}); }catch(e){} };

  if (qref) track('CreatorVisit',{creator:qref});

  document.addEventListener('DOMContentLoaded', function(){
    // nav
    var b=document.querySelector('.burger'), m=document.querySelector('.menu');
    if(b&&m) b.onclick=function(){ var open=m.classList.toggle('open'); b.setAttribute('aria-expanded', open?'true':'false'); b.setAttribute('aria-label', open?'Close menu':'Open menu'); };
    var here=location.pathname.replace(/\/index\.html$/,'/');
    document.querySelectorAll('.menu a').forEach(function(a){ var h=a.getAttribute('href'); if(h && (h===here || (h!=='/' && here.indexOf(h)===0))) a.classList.add('on'); });
    // analytics notice (dismissable, remembered per browser)
    try{ if(C.GA4_ID && !localStorage.getItem('tmu_notice')){ var n=document.createElement('div'); n.className='notice'; n.setAttribute('role','region'); n.setAttribute('aria-label','Analytics notice'); n.innerHTML='We use Google Analytics and a TikTok pixel to see which pages and videos bring people here. <a href="/privacy.html">Privacy</a> <button type="button">OK</button>'; document.body.appendChild(n); var done=function(){ try{localStorage.setItem('tmu_notice','1')}catch(e){} n.remove(); window.removeEventListener('scroll',onScroll); }; var onScroll=function(){ if(window.scrollY>window.innerHeight*0.6) done(); }; n.querySelector('button').onclick=done; window.addEventListener('scroll',onScroll,{passive:true}); } }catch(e){}
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
      p.querySelectorAll('input[name=plan]').forEach(function(r){ r.addEventListener('change', function(){
        p.querySelectorAll('.opt').forEach(function(o){ o.classList.toggle('on', o.contains(r)); });
        btn.setAttribute('data-buy', r.value); wire(btn);
      }); });
    });
    // Buy buttons: data-buy="onetime|subscribe"
    var utm = location.search ? location.search.replace(/^\?/,'') : '';
    function wire(a){
      var kind=a.getAttribute('data-buy');
      var link = kind==='subscribe' ? C.STRIPE_SUBSCRIBE : C.STRIPE_ONETIME;
      if (link) {
        a.href = link + (link.indexOf('?')>-1?'&':'?') + 'utm_source=site' + (utm?'&'+utm:'')
          + (C.REF ? '&client_reference_id=cr_' + C.REF : '');
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
      a.addEventListener('click', function(){ track('InitiateCheckout',{plan:a.getAttribute('data-buy'), mode:a.dataset.mode}); });
    });
    // Shipping / checkout copy depends on which checkout is live. Never promise free shipping in handoff mode.
    var SELF = !!(C.STRIPE_ONETIME||C.STRIPE_SUBSCRIBE);
    var SHIP = SELF ? {
      bar:'$8.95 flat US shipping', short:'$8.95 US shipping', trust:'$8.95 flat US shipping', long:'$8.95 flat US shipping, added at checkout.',
      checkout:'Secure checkout by Stripe', damage:'90-day money-back guarantee on unopened bags',
      policy:'Orders are fulfilled by the maker, MarketPlace Global, from Maple Grove, Minnesota, usually within two business days, then 3\u20136 days in transit. US shipping is a flat $8.95 a bag.'
    } : {
      bar:'$8.95 flat US shipping', short:'$8.95 US shipping', trust:'$8.95 flat US shipping', long:'$8.95 flat US shipping, shown at checkout.',
      checkout:'Secure checkout', damage:'Made right if it arrives damaged',
      policy:'Orders are fulfilled by the maker, MarketPlace Global, from Maple Grove, Minnesota, usually within two business days, then 3\u20136 days in transit. US shipping is a flat $8.95 a bag, shown at their checkout before you pay.'
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
