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
  PIXEL_ID: "",                // Meta pixel
  ANALYTICS_DOMAIN: "themorningupgrades.com"
};

(function(){
  var C = window.TMU;
  // Meta pixel
  if (C.PIXEL_ID) {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', C.PIXEL_ID); fbq('track','PageView');
  }
  // Plausible (privacy-safe, no cookie banner). Loads only once the domain is registered at plausible.io.
  if (C.ANALYTICS_DOMAIN && window.TMU_ANALYTICS_ON) {
    var s=document.createElement('script'); s.defer=true; s.setAttribute('data-domain',C.ANALYTICS_DOMAIN); s.src='https://plausible.io/js/script.outbound-links.js'; document.head.appendChild(s);
  }
  window.track = function(name, props){ try{ if(window.fbq&&C.PIXEL_ID) fbq('track',name,props||{}); if(window.plausible) plausible(name,{props:props||{}}); }catch(e){} };

  document.addEventListener('DOMContentLoaded', function(){
    // nav
    var b=document.querySelector('.burger'), m=document.querySelector('.menu');
    if(b&&m) b.onclick=function(){ m.classList.toggle('open'); };
    var here=location.pathname.replace(/\/index\.html$/,'/');
    document.querySelectorAll('.menu a').forEach(function(a){ var h=a.getAttribute('href'); if(h && (h===here || (h!=='/' && here.indexOf(h)===0))) a.classList.add('on'); });
    // year
    document.querySelectorAll('.yr').forEach(function(e){ e.textContent=new Date().getFullYear(); });

    // Buy buttons: data-buy="onetime|subscribe"
    var utm = location.search ? location.search.replace(/^\?/,'') : '';
    document.querySelectorAll('[data-buy]').forEach(function(a){
      var kind=a.getAttribute('data-buy');
      var link = kind==='subscribe' ? C.STRIPE_SUBSCRIBE : C.STRIPE_ONETIME;
      if (link) {
        a.href = link + (link.indexOf('?')>-1?'&':'?') + 'utm_source=site' + (utm?'&'+utm:'');
        a.removeAttribute('rel');
      } else {
        a.href = C.MPG_PRODUCT + '?utm_source=site&utm_medium=shop&utm_campaign=' + kind + (utm?'&'+utm:'');
        a.setAttribute('rel','sponsored'); a.setAttribute('target','_blank');
      }
      a.addEventListener('click', function(){ track('InitiateCheckout',{plan:kind}); });
    });
    // Shipping / checkout copy depends on which checkout is live. Never promise free shipping in handoff mode.
    var SELF = !!(C.STRIPE_ONETIME||C.STRIPE_SUBSCRIBE);
    var SHIP = SELF ? {
      bar:'Free US shipping on every order', short:'free US shipping', trust:'Free US shipping', long:'Free US shipping. Ships within 2 business days.',
      checkout:'Secure checkout by Stripe', damage:'Replaced or refunded if it arrives damaged',
      policy:'Standard shipping is included in the price. Orders placed by 2 PM Central on a business day ship that day or the next.'
    } : {
      bar:'$8.95 flat US shipping', short:'$8.95 US shipping', trust:'$8.95 flat US shipping', long:'$8.95 flat US shipping, shown at checkout.',
      checkout:'Secure checkout', damage:'Made right if it arrives damaged',
      policy:'Orders are fulfilled by the maker, MarketPlace Global. US shipping is a flat $8.95 for a bag, shown at their checkout before you pay.'
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
