/* The Morning Upgrade — site config + shared behaviour.
   Fill the CONFIG values as accounts come online. Empty Stripe links = "handoff" mode (Buy sends to the MPG product page). */
window.TMU = {
  // Stripe Payment Links (create in Stripe Dashboard → Payment Links). Leave "" until they exist.
  STRIPE_ONETIME: "",          // one bag, $79.95, ships from us
  STRIPE_SUBSCRIBE: "",        // one bag a month, $69.95, ships from us
  // MarketPlace Global replicated product page (handoff fallback while Stripe is empty)
  MPG_PRODUCT: "https://marketplaceglobal.com/rectorandstull/product/coffee/mpgxtreme-1-bag-corejava-coffee-skucl805-us-id194",
  // Partner side
  ENROLL_URL: "https://marketplaceglobal.com/rectorandstull/isr-instructions-coffee",
  INCOME_DISCLOSURE_URL: "https://marketplaceglobal.com/rectorandstull/income-disclaimer",
  // Lists
  KLAVIYO_COMPANY: "Ucdz59",
  KLAVIYO_LIST_QUIZ: "WgctGT",
  KLAVIYO_LIST_PARTNERS: "WeMj34",   // separate list; never the customer list
  // Tracking
  RETAIL_BONUS_PCT: 0,         // ISR Retail Customer Bonus % on referred customer orders (0 = hide the math)
  GA4_ID: "G-G79BLY9MDG",       // Google Analytics 4
  TIKTOK_PIXEL: "DBDQJRRC77U24SKT5GP0", // TikTok pixel
  PIXEL_ID: "",                // Meta pixel
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
  var TT_MAP={InitiateCheckout:'InitiateCheckout',Lead:'CompleteRegistration',QuizComplete:'ViewContent',PartnerLead:'SubmitForm',PartnerClick:'ClickButton',Purchase:'CompletePayment'};
  window.track = function(name, props){ try{ if(window.gtag&&C.GA4_ID) gtag('event', name, props||{}); if(window.ttq&&C.TIKTOK_PIXEL&&TT_MAP[name]) ttq.track(TT_MAP[name], name==='Purchase'?{value:79.95,currency:'USD',content_type:'product',content_id:'CL805'}:(props||{})); if(window.fbq&&C.PIXEL_ID) fbq('track',name,props||{}); if(window.plausible) plausible(name,{props:props||{}}); }catch(e){} };

  document.addEventListener('DOMContentLoaded', function(){
    // nav
    var b=document.querySelector('.burger'), m=document.querySelector('.menu');
    if(b&&m) b.onclick=function(){ m.classList.toggle('open'); };
    var here=location.pathname.replace(/\/index\.html$/,'/');
    document.querySelectorAll('.menu a').forEach(function(a){ var h=a.getAttribute('href'); if(h && (h===here || (h!=='/' && here.indexOf(h)===0))) a.classList.add('on'); });
    // analytics notice (dismissable, remembered per browser)
    try{ if(C.GA4_ID && !localStorage.getItem('tmu_notice')){ var n=document.createElement('div'); n.className='notice'; n.innerHTML='We use Google Analytics and a TikTok pixel to see which pages and videos bring people here. <a href="/privacy.html">Privacy</a> <button type="button">OK</button>'; document.body.appendChild(n); n.querySelector('button').onclick=function(){ try{localStorage.setItem('tmu_notice','1')}catch(e){} n.remove(); }; } }catch(e){}
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
        a.href = link + (link.indexOf('?')>-1?'&':'?') + 'utm_source=site' + (utm?'&'+utm:'');
        a.removeAttribute('rel'); a.removeAttribute('target');
      } else {
        a.href = C.MPG_PRODUCT + '?utm_source=site&utm_medium=shop&utm_campaign=' + kind + (utm?'&'+utm:'');
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
