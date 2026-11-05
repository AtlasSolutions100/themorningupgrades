# The Morning Upgrade

Pre-sell page for themorningupgrades.com (GitHub Pages). Static HTML; the quiz posts to Klaviyo client API.

## Creator links

Creator offer (current): **15% of the coffee subtotal (before tax and shipping) on orders from
customers the creator's link brings in, for that customer's first 12 months**, paid monthly. There
are no discount codes: attribution is the creator's link only, `https://themorningupgrades.com/c/<code>`
(kasey, macy, kristen, emma, laura today). Add a creator by adding a line to `CREATORS` in
`build_site.py` and running `python3 build_site.py`.

- The link sends people to `/start` and the site remembers the creator for 60 days (the last
  creator link someone used wins). GA4 records a `CreatorVisit` event and a `creator` user property.
- The Buy button adds `client_reference_id=cr_<code>`. The first checkout with a creator code ties
  that customer to the creator, so renewals and repeat orders count too.
- Monthly payout: `STRIPE_SECRET_KEY=rk_live_... python3 tools/creator_commissions.py 2026-11`
  lists each creator's orders at 15% of the coffee subtotal. **Note:** the script still counts a
  customer's orders with no end date (it predates the 12-month term and wasn't changed); drop orders
  more than 12 months after a customer's first creator checkout by hand until it is updated, and
  check whether any creator was promised "for life" in writing before the term changed.

## Email pop-up

The offer: **the Recipe Pack PDF free for signing up** (`/assets/recipe-pack.pdf`), and the two prices
stated plainly: **Subscribe & Save is $69.95 a month; 1 bag is $79.95**. There is no promo code and no
"off", "save" or "discount" wording anywhere on the site (owner, Nov 2026); the pop-up says Subscribe &
Save is 1 bag every 30 days and can be paused, skipped or cancelled anytime.

- Code and copy: `openPopup()` in `assets/site.js`; styles at the end of `assets/site.css`. Settings in
  `window.TMU`: `KLAVIYO_LIST_NEWSLETTER` (today the quiz list id `WgctGT`; put a dedicated list id
  there to split pop-up sign-ups out), `RECIPE_PACK`, `POPUP_DELAY_MS` (10000; `0` turns the pop-up off),
  `POPUP_SNOOZE_DAYS` (14).
- When: after 10 s, at 50% scroll, or on desktop exit intent, whichever is first. Once per visitor:
  closing it (or just seeing it) snoozes it 14 days; never again after sign-up or after an order from
  that browser. Never on pages built with `<body data-popup="off">` (`NO_POPUP` in `build_site.py`:
  order page, thank-you, partner, share, 404, quiz, /start), never on a paid visit (`utm_medium` paid/cpc/
  paid_social on the page, or the 30-day `tmu_ut` flag from one), and never while the quiz is on screen or
  under way.
- Sign-up: Klaviyo `custom_source` `popup`, profile properties `offer: recipe_pack_plus_autoship10`,
  `lead_magnet: Recipe Pack`, `source: popup`, `signup_page`, UTMs. Fires `Lead` (source `popup`); GA4
  also gets `PopupView`, `PopupClose` and `RecipePackDownload`.
- Success: "Download the Recipe Pack" and "Start Subscribe & Save, $69.95 a month" (the normal
  Subscribe & Save checkout). After sign-up the browser shows "Subscribe & Save is $69.95 a month; 1 bag is
  $79.95 · Cancel anytime" next to Subscribe & Save buttons (`promoNotes()` in `assets/site.js`). State
  lives in `localStorage.tmu_pop`. (The Klaviyo property `offer: recipe_pack_plus_autoship10` keeps its
  old value so flows that branch on it keep working.)
- Tests: `popup_tests` in `tools/test_pages.py`. The other tests mark the pop-up as seen so it stays out
  of their way.

## Klaviyo: Started Checkout and Placed Order

`assets/site.js` sends 2 events with the client API (public site key `Ucdz59`, revision `2025-01-15`),
only for a visitor this browser already knows: they signed up here (a customer-list sign-up Klaviyo
accepted stores the email in `localStorage.tmu_kl`, on the device only; the partner list never does), they
arrived from a Klaviyo email link (`_kx`, kept in `tmu_kx`), or Klaviyo's own `__kla_id` cookie names them.

- **Started Checkout**: a Buy button that goes to Stripe. Properties `plan` (`subscribe`/`onetime`),
  `plan_name`, `value` (69.95/79.95, also the event value), `currency`, `shipping` (8.95), `CheckoutURL`
  (the Payment Link with `utm_source=klaviyo&utm_medium=email&utm_campaign=started_checkout` and the same
  `client_reference_id` the click carried), `clicked_url`, `ItemNames`, `page`, `source` (`site`/`popup`).
  A plain same-tab click waits for the send, at most 500 ms.
- **Placed Order**: the order page, once per Stripe session (`unique_id` = the session id), so the
  abandoned-checkout flow can stop for people who bought.
- Never sent when the browser has Global Privacy Control or Do Not Track on. The email or `_kx` rides in
  the POST body only, never in a URL, and `_kx` is never forwarded to Stripe.
- Tests: `klaviyo_checkout_tests` in `tools/test_pages.py`.

## Editing pages

Every page, `sitemap.xml`, `robots.txt` and `llms.txt` is generated by `build_site.py`.
Change the text there and run `python3 build_site.py`; edits made only in the `.html`
files are overwritten on the next build. No claims past the label anywhere (`tools/check_copy.py`
blocks weight, appetite and metabolism wording in copy, alt text, schema and file names). The
CoreJava name is fine in titles, headings and Product schema; bidding on branded keywords in ads is
a separate rule handled in the ad accounts. Photos show the bag as it is; alt text says "CoreJava
bag" and never transcribes the label's claims.

Images: add or change a photo in `img/`, list it in `tools/images.py`, then run
`python3 tools/images.py && python3 build_site.py` (WebP plus JPEG/PNG at 480/800/1200 px).
The home hero (`img/hero_scene.jpg`) is the same real bag photo composited by `tools/hero_scene.py` (scaled
and globally graded only) onto an AI-generated still-life plate (`img/hero_scene_plate.jpg`: stone counter,
cup, window light; no bag or text in it). The main product image (`img/packshot.jpg`: the first /shop slide, /corejava-coffee) is a real
bag: `img/bag_photo.png`, cut out of the owner's own phone photo (Nov 2026, background removed with rembg,
nothing else changed), only scaled, on a backdrop and contact shadow drawn by `tools/packshot.py`
(`python3 tools/packshot.py` rebuilds it). The shop gallery's "Front" (`img/lux_pattern.jpg`) is `img/bag.png`
composited in by hand (Nov 2026). Never an AI-drawn or altered bag. The one
FAQ about the label's printed name ("Weight Control Coffee") is answered from the label only and is the
only place that word may appear (`ALLOW` in `tools/check_copy.py`; kept out of FAQ rich results).

`/partner` and `/share` (the ISR pages) stay reachable by URL with their disclosures, but are noindex,
out of the sitemap and not linked from the customer nav or footer (owner, Nov 2026).

## Tracking (what fires where)

- **ViewContent** fires on `/`, `/shop.html` and `/start.html` for the TikTok, Meta and Snap pixels
  (GA4 already has `page_view`).
- **InitiateCheckout** fires on every Buy click with the plan and its price, and the click stores the
  plan in `localStorage.tmu_plan`.
- **Purchase** fires on `/order-complete.html` only when the URL carries a Stripe `session_id`
  (`cs_...`), and only once per session id in a browser (refresh-safe). The session id is the
  `transaction_id` / event id everywhere (GA4 standard `purchase`, Google Ads, Meta `eventID`,
  TikTok `event_id`, Snap `transaction_id`), so a server-side event can dedupe against it later.
  Value = the coffee subtotal of the plan: `?plan=` first, then `tmu_plan`, then $69.95.
- **Stripe Payment Link redirects** (set in Stripe; both links pass `plan=`):
  - Subscribe & Save (`plink_1UVMJNRskSkrZOvOPlxbduJo`):
    `https://themorningupgrades.com/order-complete.html?session_id={CHECKOUT_SESSION_ID}&plan=subscribe`
  - One bag (`plink_1UVMJMRskSkrZOvORjXEhOe2`):
    `https://themorningupgrades.com/order-complete.html?session_id={CHECKOUT_SESSION_ID}&plan=onetime`
- **Ad attribution (`tmu_ut`)** stores the first paid visit's UTMs when `utm_medium` is one of
  `paid`, `cpc`, `ppc`, `paid_social`, `paid-social`, `paidsocial`, `social_paid`. Ad URLs:
  `?utm_source={tiktok|snap|meta|google}&utm_medium=paid&utm_campaign=<campaign>&utm_content=<creative>`.
  Link-in-bio and pinned-comment links use `utm_medium=organic` so GA4 separates them from paid.
- Tests: `python3 tools/test_tracking.py` (Playwright, local, third-party requests blocked).
