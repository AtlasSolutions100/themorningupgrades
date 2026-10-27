# The Morning Upgrade

Pre-sell page for themorningupgrades.com (GitHub Pages). Static HTML; the quiz posts to Klaviyo client API.

## Creator links (15% lifetime commission)

Each creator on the $100 + 15% deal gets a link: `https://themorningupgrades.com/c/<code>`
(kasey, macy, kristen, emma, laura today). Add a creator by adding a line to `CREATORS` in
`build_site.py` and running `python3 build_site.py`.

- The link sends people to `/start` and the site remembers the creator for 60 days (the last
  creator link someone used wins). GA4 records a `CreatorVisit` event and a `creator` user property.
- With Stripe Payment Links filled in (`assets/site.js`), the Buy button adds
  `client_reference_id=cr_<code>`. The first checkout with a creator code ties that customer to the
  creator for life, so renewals and repeat orders count too.
- While checkout is still the MarketPlace Global handoff, the link only carries `utm_content=cr_<code>`;
  MPG doesn't report orders back to us, so commission can't be counted until Stripe checkout is live.
- Monthly payout: `STRIPE_SECRET_KEY=rk_live_... python3 tools/creator_commissions.py 2026-11`
  lists each creator's orders and what they're owed (15% of the coffee subtotal, before tax and shipping).
