# Beguile — Independent Audit and Q4 Scale Decision

Prepared 9 October 2026 for Beguile management. Period under review: 1 January – 30 September 2026. Every comparison is against April–June 2026 (momentum) and January–September 2025 (year). All money is in naira (₦) unless marked. Every number in this document was pulled from a connected tool in this session and aggregated by a script kept in `audit/scripts/`; the pulls are in `audit/data/`. Platform-reported figures are labelled as such and set against Shopify, which is the source of truth.

**What was reachable.** Meta Ads (account 480225648142941), Shopify (beguilebyomaa), Google Analytics 4 (518041609), Google Ads (173-070-6186), Search Console (sc-domain:beguile.com), Snapchat (OMAA Enterprises), Klaviyo (account Sd8R9N) and both Google Sheets.

**What was not.** The storefront (beguile.com, shopbeguile.com and the myshopify address) is blocked by this environment's network policy, so the Store section rests on Shopify data, not a page fetch. Search Console returns nothing older than June 2025, so it has no January–September 2025 window. GA4 begins in late December 2025, so it has no year comparison. Google Ads has no rows before March 2026. The unit economics sheet has no cost inputs, so no profit verdict is given anywhere in this document.

---

## 1. The year in four facts

1. **Sales are up 67% on last year.** Net sales for January–September 2026 were ₦1,031.0m on 9,040 orders, against ₦617.4m on 6,912 orders in the same months of 2025. Average order value rose 28%, from ₦89,456 to ₦114,369. (Shopify)
2. **The growth was bought, and each naira now buys less.** Meta spend was ₦161.2m, up 189% from ₦55.7m. Shopify net sales per ₦1 of Meta spend fell from ₦11.09 to ₦6.40 for the nine months, and to ₦5.03 in July–September. (Shopify net ÷ Meta spend)
3. **The third quarter fell by a third.** July–September net sales were ₦268.9m, down 34% from ₦405.0m in April–June; orders fell 39%, from 3,570 to 2,185. Every market fell: Nigeria −33%, UK −39%, Canada −15%, US −55%. Meta spend fell only 14% in the same period, and September's ₦25.4m was the highest monthly spend on record. Three things moved with the fall and are in the data: site visits fell 23% (161,418 to 123,822 sessions), the share of visits that bought fell from 1.96% to 1.61%, and the share of Meta spend sitting in campaigns too small to learn rose from 27% to 36%. The data does not prove which caused which. (Shopify, Meta, GA4)
4. **Export markets take 47% of ad spend and produce 25% of sales.** In July–September a new customer cost ₦95,222 in the UK (71% of that market's average order), ₦80,371 in Canada (63%) and ₦68,133 in the US (42%), against ₦31,047 in Nigeria (26%). (Meta spend by delivery country ÷ Shopify first-order customers by shipping country)

---

## 2. Audit

### 2.1 Shopify — source of truth

Definitions: orders exclude test (none found) and cancelled orders (41); net sales = gross − discounts − returns, dated as Shopify dates them; country = shipping country; "new" = first order from that customer; average order value = net at order placement ÷ orders.

**Orders, net sales and order value by window and country**

| Market | Window | Orders | Net sales | Average order value | New customers (% of orders) | Orders with a discount code |
|---|---|---:|---:|---:|---:|---:|
| All | Jan–Sep 2026 | 9,040 | ₦1,031.0m | ₦114,369 | 58.4% | 3.8% |
| All | Jan–Sep 2025 | 6,912 | ₦617.4m | ₦89,456 | 54.6% | 0.0% |
| All | Apr–Jun 2026 | 3,570 | ₦405.0m | ₦113,753 | 62.0% | 5.0% |
| All | Jul–Sep 2026 | 2,185 | ₦268.9m | ₦123,239 | 55.9% | 7.6% |
| Nigeria | Jan–Sep 2026 | 7,022 | ₦775.9m | ₦110,614 | 57.9% | 2.5% |
| Nigeria | Jan–Sep 2025 | 5,230 | ₦458.6m | ₦87,685 | 55.5% | 0.0% |
| Nigeria | Apr–Jun 2026 | 2,780 | ₦301.1m | ₦108,468 | 61.2% | 4.6% |
| Nigeria | Jul–Sep 2026 | 1,695 | ₦202.2m | ₦119,376 | 54.5% | 2.6% |
| UK | Jan–Sep 2026 | 1,011 | ₦122.1m | ₦122,387 | 56.6% | 5.0% |
| UK | Jan–Sep 2025 | 958 | ₦95.4m | ₦100,204 | 46.0% | 0.0% |
| UK | Apr–Jun 2026 | 346 | ₦43.3m | ₦127,260 | 60.7% | 5.5% |
| UK | Jul–Sep 2026 | 199 | ₦26.6m | ₦134,436 | 54.3% | 16.1% |
| Canada | Jan–Sep 2026 | 715 | ₦90.0m | ₦126,209 | 58.3% | 14.3% |
| Canada | Jan–Sep 2025 | 724 | ₦63.4m | ₦88,024 | 59.8% | 0.0% |
| Canada | Apr–Jun 2026 | 244 | ₦31.7m | ₦130,098 | 57.4% | 9.0% |
| Canada | Jul–Sep 2026 | 211 | ₦27.1m | ₦128,444 | 63.0% | 37.9% |
| US | Jan–Sep 2026 | 291 | ₦43.1m | ₦148,414 | 77.7% | 6.5% |
| US | Jan–Sep 2025 | 0 | – | – | – | – |
| US | Apr–Jun 2026 | 200 | ₦28.8m | ₦143,910 | 82.5% | 4.0% |
| US | Jul–Sep 2026 | 80 | ₦13.0m | ₦163,524 | 70.0% | 13.8% |

**Third quarter against second quarter**

| Market | Net sales | Orders |
|---|---:|---:|
| All | −34% | −39% |
| Nigeria | −33% | −39% |
| UK | −39% | −42% |
| Canada | −15% | −14% |
| US | −55% | −60% |

Nigeria is 75% of net sales, the UK 12%, Canada 9%, the US 4%. The US market opened in March 2026. Canada's order count is flat on 2025 (715 vs 724); its 42% sales growth is all order value. Discount codes were not used in 2025; by July–September 2026 they were on 38% of Canadian orders and 16% of UK orders, which is why the discount rate as a share of gross rose to 3.6% in Canada. Total discounting is still small (0.8% of gross in Q3).

**Month by month, 2026 (orders / net sales)**

| Month | All | Nigeria | UK | Canada | US |
|---|---:|---:|---:|---:|---:|
| Jan | 918 / ₦97.9m | 667 / ₦70.0m | 150 / ₦16.7m | 101 / ₦11.2m | 0 |
| Feb | 1,255 / ₦135.0m | 985 / ₦106.3m | 195 / ₦19.9m | 74 / ₦8.8m | 0 |
| Mar | 1,112 / ₦124.3m | 895 / ₦96.3m | 121 / ₦15.6m | 85 / ₦11.1m | 11 / ₦1.3m |
| Apr | 1,376 / ₦150.1m | 1,121 / ₦117.4m | 132 / ₦17.0m | 93 / ₦12.1m | 30 / ₦3.6m |
| May | 1,232 / ₦141.6m | 990 / ₦109.4m | 100 / ₦13.0m | 74 / ₦9.7m | 68 / ₦9.5m |
| Jun | 962 / ₦113.3m | 669 / ₦74.3m | 114 / ₦13.3m | 77 / ₦9.9m | 102 / ₦15.7m |
| Jul | 549 / ₦63.3m | 347 / ₦37.9m | 118 / ₦15.1m | 65 / ₦8.0m | 19 / ₦2.4m |
| Aug | 836 / ₦105.3m | 699 / ₦86.9m | 48 / ₦6.9m | 66 / ₦8.2m | 23 / ₦3.4m |
| Sep | 800 / ₦100.2m | 649 / ₦77.5m | 33 / ₦4.6m | 80 / ₦11.0m | 38 / ₦7.1m |

The best month on record is October 2025: 1,711 orders and ₦167.4m (55 orders a day). The best 2026 month is April: 1,376 orders and ₦150.1m. July 2026 (549 orders) is the lowest month since January 2025. The UK fell from 118 orders in July to 33 in September.

**Products** (line items, titles merged across two spellings: MYSTIQUE/Mystique, GOLDEN KISS/Golden Kiss, SWEET OUD/Sweet Oud, BLUSH BLOOM/Blush Bloom, and the same for Oil Trio, Clean Musk, White Florals, Vanilla Sugar and Golden Kiss 10ml)

| Product | Jan–Sep 2026 units / net / share | Jan–Sep 2025 | Apr–Jun 2026 | Jul–Sep 2026 |
|---|---:|---:|---:|---:|
| Mystique | 5,044 / ₦410.1m / 38% | 3,324 / ₦224.2m / 36% | 1,972 / ₦159.2m / 38% | 1,045 / ₦99.3m / 34% |
| Golden Kiss (launched 2026) | 2,188 / ₦189.9m / 18% | – | 998 / ₦87.2m / 21% | 492 / ₦43.7m / 15% |
| Goddess | 2,049 / ₦166.3m / 15% | 2,008 / ₦103.6m / 16% | 680 / ₦54.0m / 13% | 708 / ₦63.2m / 22% |
| Sweet Oud | 1,267 / ₦99.8m / 9% | 1,562 / ₦110.9m / 18% | 509 / ₦39.2m / 9% | 298 / ₦26.9m / 9% |
| Mini Set | 1,164 / ₦96.0m / 9% | 553 / ₦39.7m / 6% | 490 / ₦39.9m / 10% | 320 / ₦30.4m / 11% |
| Blush Bloom | 377 / ₦28.7m / 3% | 1,579 / ₦111.2m / 18% | 136 / ₦10.3m / 2% | 20 / ₦2.4m / 1% |
| Oil Trio (launched 2026) | 213 / ₦22.7m / 2% | – | 64 / ₦6.7m / 2% | 36 / ₦3.9m / 1% |
| Seduction | 324 / ₦19.0m / 2% | 564 / ₦20.8m / 3% | 116 / ₦7.1m / 2% | 58 / ₦3.8m / 1% |
| Passion | 217 / ₦13.5m / 1% | 385 / ₦18.1m / 3% | 6 / ₦0.6m / 0% | 94 / ₦6.6m / 2% |
| Golden Kiss 10ml | 557 / ₦10.3m / 1% | – | 354 / ₦6.1m / 1% | 145 / ₦3.4m / 1% |
| Three oils (20ml) | 419 / ₦17.8m / 2% | – | 128 / ₦5.7m / 1% | 136 / ₦5.5m / 2% |

Three products carry 71% of sales. Blush Bloom went from 18% of 2025 sales to 1% in Q3 2026 because it has no stock in Lagos (see inventory) and is tagged sold out for Nigeria. Golden Kiss, the 2026 launch, fell from 21% of Q2 sales to 15% in Q3. Goddess rose to 22% of Q3 sales from 13% in Q2. The three 3ml samples sold 53 units in nine months, all to the US.

**Where the last visit came from** (Shopify's last-visit source on the order; 2025 recorded storefront URLs rather than a channel for 75% of orders, so the year comparison is not usable)

| Source, Jan–Sep 2026 | All | Nigeria | UK | Canada | US |
|---|---:|---:|---:|---:|---:|
| Instagram | 59% | 62% | 52% | 41% | 43% |
| Direct | 17% | 16% | 18% | 21% | 19% |
| Google | 9% | 8% | 13% | 13% | 13% |
| Source not identified by Shopify | 7% | 7% | 6% | 11% | 10% |
| Facebook | 2% | 2% | 3% | 3% | 3% |
| Email | 2% | 1% | 3% | 3% | 2% |

Of the 9,041 orders, 2,541 carried a paid Facebook tag and 2,977 an Instagram social tag; 3,224 carried no tag. Shopify cannot separate paid from organic Instagram, so "Instagram 59%" is paid and organic together.

**Stock on hand, 8 October 2026** (sellable units; inventory tracking is on for every product except the test gift card; the unit-cost field is 0 for every variant, so stock value cannot be costed)

| Product | Lagos | UK | Canada | "Warehance – 5 Logistics" | Q3 units sold | Days of cover at the Q3 rate |
|---|---:|---:|---:|---:|---:|---:|
| Mystique | 1,721 | 115 | 254 | 122 | 1,045 | 195 |
| Golden Kiss | 296 | 401 | 334 | 120 | 492 | 215 |
| Goddess | 532 | 408 | 455 | 43 | 708 | 187 |
| Sweet Oud | 513 | 2 | 2 | 0 | 298 | 160 |
| Mini Set | 464 | 148 | 125 | 121 | 320 | 247 |
| Blush Bloom | 0 | 244 | 50 | 0 | 20 | 1,352 |
| Passion | 387 | 262 | 0 | 0 | 94 | 635 |
| Seduction | 0 | 255 | 146 | 0 | 58 | 636 |
| Golden Kiss 10ml | 7 | 177 | 94 | 0 | 145 | 176 |
| Oil Trio | 83 | 120 | 60 | 0 | 36 | 672 |
| 3ml samples (three) | 0 | 0 | 5 | 347 | 19 | – |

Days of cover are for all warehouses together; by market the gaps are: Sweet Oud has 2 units in the UK and 2 in Canada; Blush Bloom and Seduction have 0 in Lagos; Passion has 0 in Canada; Golden Kiss 10ml has 7 in Lagos; the UK holds 115 Mystique against 106 sold there in Q3. The Shopify product tags confirm it: Blush Bloom and Seduction are tagged sold out for Nigeria, Passion for Canada, and every sample is sold out in at least two markets. Which market the "Warehance – 5 Logistics" location serves is not stated in Shopify; POK to confirm.

### 2.2 Meta

Meta figures are what the platform reports: pixel website purchases and purchase value, 7-day click / 1-day view attribution (the account default, as returned by the connector; no change of window is visible in the data). Country = Meta's delivery country. The reconciliation column divides Meta's purchase count by Shopify's order count for the same country and window.

| Market | Window | Spend | Impressions | People who clicked | Cost per click | Meta purchases | Meta purchase value | Meta cost per purchase | Meta sales per ₦1 | Shopify orders | Meta purchases as % of Shopify orders | Shopify net per ₦1 of Meta |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All | Jan–Sep 2026 | ₦161.2m | 22.4m | 342,941 | ₦470 | 7,094 | ₦919.2m | ₦22,720 | 5.70 | 9,040 | 78% | 6.40 |
| All | Jan–Sep 2025 | ₦55.7m | 19.0m | 129,718 | ₦429 | 5,462 | ₦529.6m | ₦10,193 | 9.51 | 6,912 | 79% | 11.09 |
| All | Apr–Jun 2026 | ₦62.1m | 8.5m | 161,655 | ₦384 | 2,665 | ₦339.6m | ₦23,312 | 5.47 | 3,570 | 75% | 6.52 |
| All | Jul–Sep 2026 | ₦53.5m | 6.5m | 91,464 | ₦585 | 1,858 | ₦260.2m | ₦28,782 | 4.86 | 2,185 | 85% | 5.03 |
| Nigeria | Jan–Sep 2026 | ₦85.2m | 17.7m | 270,255 | ₦315 | 5,494 | ₦683.3m | ₦15,513 | 8.02 | 7,022 | 78% | 9.10 |
| Nigeria | Jan–Sep 2025 | ₦32.0m | 17.1m | 96,243 | ₦333 | 4,224 | ₦388.2m | ₦7,586 | 12.12 | 5,230 | 81% | 14.31 |
| Nigeria | Apr–Jun 2026 | ₦32.4m | 6.8m | 129,710 | ₦250 | 2,029 | ₦243.6m | ₦15,953 | 7.53 | 2,780 | 73% | 9.30 |
| Nigeria | Jul–Sep 2026 | ₦28.7m | 5.1m | 71,661 | ₦400 | 1,476 | ₦200.1m | ₦19,436 | 6.98 | 1,695 | 87% | 7.05 |
| UK | Jan–Sep 2026 | ₦34.0m | 2.3m | 38,232 | ₦889 | 778 | ₦114.8m | ₦43,682 | 3.38 | 1,011 | 77% | 3.59 |
| UK | Jan–Sep 2025 | ₦12.2m | 0.8m | 19,073 | ₦640 | 584 | ₦69.9m | ₦20,906 | 5.72 | 958 | 61% | 7.82 |
| UK | Apr–Jun 2026 | ₦13.1m | 0.8m | 16,824 | ₦776 | 260 | ₦39.1m | ₦50,236 | 3.00 | 346 | 75% | 3.32 |
| UK | Jul–Sep 2026 | ₦10.3m | 0.8m | 9,053 | ₦1,136 | 156 | ₦25.3m | ₦65,923 | 2.46 | 199 | 78% | 2.58 |
| Canada | Jan–Sep 2026 | ₦31.3m | 2.0m | 25,539 | ₦1,226 | 593 | ₦85.0m | ₦52,816 | 2.71 | 715 | 83% | 2.87 |
| Canada | Jan–Sep 2025 | ₦11.4m | 1.1m | 14,401 | ₦793 | 650 | ₦71.2m | ₦17,575 | 6.23 | 724 | 90% | 5.55 |
| Canada | Apr–Jun 2026 | ₦10.2m | 0.7m | 8,745 | ₦1,168 | 202 | ₦30.7m | ₦50,547 | 3.01 | 244 | 83% | 3.11 |
| Canada | Jul–Sep 2026 | ₦10.7m | 0.6m | 8,420 | ₦1,270 | 174 | ₦25.2m | ₦61,433 | 2.36 | 211 | 82% | 2.54 |
| US | Jan–Sep 2026 | ₦10.6m | 0.3m | 8,915 | ₦1,194 | 226 | ₦35.8m | ₦47,088 | 3.36 | 291 | 78% | 4.05 |
| US | Apr–Jun 2026 | ₦6.5m | 0.2m | 6,376 | ₦1,017 | 172 | ₦25.9m | ₦37,707 | 3.99 | 200 | 86% | 4.44 |
| US | Jul–Sep 2026 | ₦3.8m | 0.1m | 2,330 | ₦1,638 | 51 | ₦9.5m | ₦74,813 | 2.49 | 80 | 64% | 3.40 |

Nigeria took 53% of the nine months' Meta spend; the UK, Canada and the US together took 47% (₦75.9m) and produced 25% of net sales. Nigeria returns ₦9.10 of Shopify sales per ₦1 of Meta over nine months, the UK ₦3.59, Canada ₦2.87, the US ₦4.05. Every market's return has fallen each window since 2025, and the cost per click abroad has risen by a third to a half in a year. The UK's 2026 spend is 2.8 times its 2025 spend for 5% more orders.

**Meta claims more than the store took.** In September 2026 Meta reported 861 purchases against 800 Shopify orders from every source (108%); in Nigeria 696 against 649, in the UK 49 against 33. For July–September Meta claims 85% of all orders, while Shopify's own last-visit field credits Facebook and Instagram with 61% of orders and Google with 9%. Meta's purchase counts therefore overstate what it drives, by an amount that cannot be fixed without order-level tagging; the ratio of Shopify net to Meta spend is used for decisions instead.

**Cost of a new customer** (Meta spend in the country ÷ Shopify first-order customers shipped to the country; Meta is 100% of paid social spend, so this is the ceiling, not a measure of attribution)

| Market | Jan–Sep 2026 | Jan–Sep 2025 | Jul–Sep 2026 | Q3 cost as % of Q3 average order value |
|---|---:|---:|---:|---:|
| Nigeria | ₦20,956 (4,067 new) | ₦11,041 (2,902 new) | ₦31,047 (924 new) | 26% |
| UK | ₦59,413 (572) | ₦27,685 (441) | ₦95,222 (108) | 71% |
| Canada | ₦75,108 (417) | ₦26,383 (433) | ₦80,371 (133) | 63% |
| US | ₦47,088 (226) | – | ₦68,133 (56) | 42% |

**Campaign structure** (campaigns with spend in the month, all countries)

| Month | Campaigns with spend | Average daily spend per campaign | Spend | Share of spend in campaigns with fewer than 7 Meta purchases that month |
|---|---:|---:|---:|---:|
| Jan 2026 | 52 | ₦7,567 | ₦12.2m | 28% |
| Feb | 79 | ₦7,240 | ₦16.0m | 24% |
| Mar | 93 | ₦6,021 | ₦17.4m | 28% |
| Apr | 78 | ₦8,433 | ₦19.7m | 19% |
| May | 76 | ₦8,205 | ₦19.3m | 20% |
| Jun | 111 | ₦6,925 | ₦23.1m | 39% |
| Jul | 85 | ₦4,726 | ₦12.5m | 46% |
| Aug | 87 | ₦5,777 | ₦15.6m | 42% |
| Sep | 78 | ₦10,872 | ₦25.4m | 28% |

In 2026 the account ran 82 campaigns a month on average, against 25 in January–September 2025. 30% of 2026 spend (₦48.2m) sat in campaigns that produced fewer than 7 purchases in the month; in 2025 it was 13%, and in July–September 2026 it was 36%. On 8 October 2026, 91 campaigns had spent in the month and 49 were active: 14 Nigeria, 11 UK, 15 Canada, 9 US, with campaign-level daily budgets of ₦685,000 (Nigeria ₦260,000, UK ₦155,000, Canada ₦170,000, US ₦100,000). 41 of the 49 have a daily budget of ₦15,000 or less.

**Reach and frequency, 2026** (monthly reach, de-duplicated within the month only)

| Market | Monthly frequency Jan→Sep | Months at 5+ | Reach Jan→Sep |
|---|---|---:|---|
| Nigeria | 6.6, 2.8, 7.9, 10.8, 9.0, 3.7, 4.5, 8.1, 9.3 | 6 of 9 | 133k, 1,071k, 263k, 211k, 229k, 661k, 323k, 180k, 230k |
| UK | 7.2, 5.0, 5.7, 3.6, 4.7, 5.1, 5.5, 10.7, 2.3 | 6 of 9 | 27k, 64k, 31k, 83k, 46k, 65k, 34k, 20k, 176k |
| Canada | 3.7, 5.7, 6.3, 3.3, 4.3, 4.7, 6.0, 8.3, 7.2 | 5 of 9 | 118k, 22k, 30k, 77k, 43k, 61k, 24k, 20k, 35k |
| US | 2.0, 3.0, 4.1, 3.4, 4.7, 5.0, 5.2 (Mar→Sep) | 1 of 7 | 4k, 9k, 15k, 25k, 2k, 5k, 10k |

The same people see the ads five to ten times a month in Nigeria, the UK and Canada in most months. In August the UK reached 20,000 people 10.7 times each.

**Creative type, judged only within its own country** (classified from campaign names; ads are mostly named "New Sales Ad"; "ISWIS" is the podcast partnership, not a format; a type needs 20+ purchases in the country to be read, otherwise "insufficient data")

Nigeria, Jan–Sep 2026 (₦85.2m):

| Type | Spend (share) | Meta purchases | Meta cost per purchase |
|---|---:|---:|---:|
| Not stated in the name | ₦47.2m (55%) | 2,970 | ₦15,898 |
| Video, type not stated | ₦8.4m (10%) | 496 | ₦16,935 |
| DT / Dynamic | ₦7.6m (9%) | 458 | ₦16,678 |
| Image | ₦6.3m (7%) | 409 | ₦15,349 |
| CEO | ₦4.8m (6%) | 343 | ₦13,935 |
| Named creators | ₦3.2m (4%) | 301 | ₦10,551 |
| Catalogue | ₦2.3m (3%) | 225 | ₦9,996 |
| Podcast (ISWIS) | ₦2.2m (3%) | 131 | ₦16,938 |
| UGC | ₦2.0m (2%) | 89 | ₦22,173 |
| Street interview | ₦1.3m (2%) | 72 | ₦18,033 |

UK (₦34.0m): not stated ₦22.1m, 500 purchases, ₦44,119; video ₦3.4m, 82, ₦41,881; named creators ₦1.8m, 44, ₦39,712; CEO ₦1.6m, 34, ₦47,028; image ₦1.4m, 40, ₦35,976; podcast ₦1.1m, 38, ₦29,623. Dynamic (4), UGC (8), carousel (14), street interview (6), catalogue (8): insufficient data.

Canada (₦31.3m): not stated ₦22.8m, 432, ₦52,750; named creators ₦2.7m, 50, ₦53,205; dynamic ₦2.0m, 40, ₦49,126. All other types under 20 purchases: insufficient data.

US (₦10.6m): not stated ₦8.1m, 172, ₦47,225. Every named type under 20 purchases: insufficient data.

Reading: in Nigeria, catalogue (₦9,996) and named creators (₦10,551) buy a purchase for about two-thirds of the account's Nigerian average (₦15,513); UGC (₦22,173) and street interviews (₦18,033) cost more than average. In the UK the podcast partnership is the cheapest readable type (₦29,623 vs ₦43,682 average). Abroad, 65–76% of spend sits in campaigns whose names do not say what the creative is, so most export creative cannot be judged at all.

**Product in the campaign name, within country** (20+ purchases). Nigeria: Passion ₦9,821 per purchase (188), oils ₦13,183 (326), Blush Bloom ₦15,387 (178), Goddess ₦16,601 (627), Mystique ₦16,329 (376), Sweet Oud ₦17,027 (311), Mini Set ₦17,846 (337), Golden Kiss ₦18,293 (1,269; 27% of Nigerian spend). UK: oils ₦32,259 (71), Goddess ₦43,394 (73), Golden Kiss ₦46,042 (139), Mystique ₦46,414 (134), Sweet Oud ₦52,207 (47), Mini Set ₦51,884 (46). Canada: oils ₦44,416 (39), Sweet Oud ₦45,419 (44), Goddess ₦49,002 (92), Golden Kiss ₦52,849 (70), Mystique ₦56,010 (168). US: Mystique ₦38,460 (86), Goddess ₦43,120 (48), Mini Set ₦53,499 (23), Golden Kiss ₦62,636 (48). Golden Kiss, the most-funded product abroad, is the most expensive purchase in the US and among the most expensive in the UK.

**Heritage audiences.** Campaigns whose names state a Nigerian or African audience took 6.7% of UK spend, 3.4% of Canadian and 2.0% of US spend in January–September 2026 (8.0%, 6.4% and 5.5% in Q3). That is inside the 25% cap. Audience settings inside the other campaigns are not in the data, so the true diaspora share could be higher; the October campaigns carry a "NID" label whose meaning CodeSM must state.

**Snapchat** spent 276.66 (account currency not stated) in April 2025 and nothing in any other month; it reported 10 purchases that month. It is not a channel.

### 2.3 Email (Klaviyo)

Flow figures are Klaviyo's, with its Placed Order attribution. Totals are rebuilt from nine monthly pulls because a single nine-month pull returned fewer recipients than January–April alone (the monthly pulls reconcile exactly to a four-month pull). 2025 flows exist only from July 2025; the old flows were replaced in May 2026.

**All flows**

| Window | Emails delivered to (recipients) | Unique opens | Unique clicks | Orders (Klaviyo) | Revenue (Klaviyo) | Revenue per recipient |
|---|---:|---:|---:|---:|---:|---:|
| Jan–Sep 2026 | 47,243 | 22,046 | 1,112 | 207 | ₦27.8m | ₦588 |
| Jan–Sep 2025 (Jul–Sep only) | 996 | 436 | 38 | 16 | ₦1.8m | ₦1,840 |
| Apr–Jun 2026 | 18,694 | 9,303 | 486 | 100 | ₦13.4m | ₦714 |
| Jul–Sep 2026 | 22,292 | 9,304 | 351 | 41 | ₦5.9m | ₦265 |

**Old flows (Jan–Apr 2026) against rebuilt flows (May–Sep 2026)**

| Flow | Recipients | Opens | Clicks | Orders | Revenue | Revenue per recipient |
|---|---:|---:|---:|---:|---:|---:|
| Abandoned Checkout (old) | 4,127 | 2,202 | 196 | 60 | ₦7.5m | ₦1,825 |
| 2026 Abandoned Checkout (new) | 7,257 | 3,134 | 167 | 55 | ₦8.2m | ₦1,124 |
| Email Welcome Series (old) | 6,905 | 3,728 | 205 | 42 | ₦5.2m | ₦749 |
| Beguile Welcome Series (new) | 12,061 | 4,776 | 237 | 25 | ₦2.9m | ₦242 |
| Browse Abandonment – Standard (old) | 131 | 73 | 13 | 2 | ₦0.3m | ₦2,220 |
| 2026 Browse Abandonment (new) | 1,380 | 586 | 86 | 8 | ₦1.0m | ₦717 |
| Beguile Post Purchase (new) | 3,727 | 2,548 | 87 | 4 | ₦0.9m | ₦254 |
| 2026 Customer Winback (new, from Jul) | 2,988 | 1,227 | 15 | 2 | ₦0.5m | ₦170 |
| Beguile MiniSet Cross-Sell (new) | 3,016 | 1,369 | 35 | 2 | ₦0.3m | ₦90 |
| 2026 Review request (new) | 4,587 | 1,835 | 40 | 2 | ₦0.3m | ₦56 |
| Old flows, Jan–Apr total | 11,163 | 6,003 | 414 | 104 | ₦13.0m | ₦1,164 |
| New flows, May–Sep total | 36,080 | 16,043 | 698 | 103 | ₦14.8m | ₦409 |

The rebuild tripled the volume of email and kept the order count flat: 103 orders from 36,080 emails against 104 from 11,163. Revenue per recipient fell 65%. The abandoned-checkout flow is the only one that pays: it is 30% of recipients and 55% of flow revenue. The welcome series went from ₦749 to ₦242 per recipient; the new post-purchase, cross-sell, winback and review flows produced 10 orders from 14,318 emails between them.

**Abandoned-checkout coverage** (abandoned-checkout emails sent ÷ GA4 checkouts started)

| Month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Emails sent | 1,068 | 1,083 | 851 | 1,125 | 1,879 | 1,732 | 1,118 | 1,332 | 1,446 |
| Checkouts started (GA4) | 3,897 | 5,215 | 4,606 | 6,542 | 5,949 | 4,748 | 2,651 | 3,862 | 3,403 |
| Coverage | 27% | 21% | 18% | 17% | 32% | 36% | 42% | 34% | 42% |

Coverage doubled after May but 58% of checkouts started in September got no email. GA4 counts every checkout and the flow can only reach checkouts with a known email, so 100% is not reachable; the gap is still the largest untouched pool in the business (about 4,000 checkouts a month in Q2).

**Campaigns**

| Window | Sends | Recipients | Orders (Klaviyo) | Revenue | Revenue per recipient |
|---|---:|---:|---:|---:|---:|
| Jan–Sep 2026 | 57 | 410,289 | 78 | ₦11.2m | ₦27 |
| Jan–Sep 2025 | 51 | 175,118 | 68 | ₦6.8m | ₦39 |
| Apr–Jun 2026 | 8 | 29,745 | 7 | ₦1.1m | ₦37 |
| Jul–Sep 2026 | 40 | 319,519 | 51 | ₦7.1m | ₦22 |

Forty of the year's 57 campaigns were sent in July–September, to 319,519 recipients, for 51 orders. Shopify's own last-visit field credits email with 139 orders (1.5%) in January–September and 52 (2.4%) in Q3, against Klaviyo's 285 for flows and campaigns together.

**Reviews.** The review-request flow went live on 8 May 2026 and has sent 4,587 emails. Klaviyo holds 600 reviews; 393 were published in January–September 2026 with an average rating of 4.4. 393 of them came in January–April (98 a month, before the flow) and 55 in May–September (11 a month, with the flow). Klaviyo's "Submitted review" event counts 6, 8, 14, 11 and 8 submissions in May to September. Reviews are shown on the storefront: the reviews widget recorded 5,664 to 7,605 impressions a month from May onwards and none before May. So the widget went live with the flow, and the flow collects one review for every 80 emails.

### 2.4 Google Ads

The account reports in US dollars; no conversion to naira is applied. Rows exist from March 2026 only. Conversions are what Google reports.

| Campaign | Window | Cost | Clicks | Conversions | Conversion value | Cost per conversion |
|---|---|---:|---:|---:|---:|---:|
| NGN PMAX | Mar–Sep 2026 | $2,149 | 19,243 | 579 | $49,388 | $3.7 |
| CA PMAX | Mar–Sep 2026 | $2,298 | 2,844 | 102 | $9,694 | $22.5 |
| Website traffic | Mar 2026 | $405 | 517 | 14 | $1,028 | $29.0 |
| All | Mar–Sep 2026 | $4,852 | 22,604 | 695 | $60,110 | $7.0 |
| NGN PMAX | Apr–Jun 2026 | $909 | – | 261 | $20,707 | $3.5 |
| NGN PMAX | Jul–Sep 2026 | $913 | – | 273 | $25,344 | $3.3 |
| CA PMAX | Apr–Jun 2026 | $900 | – | 31 | $2,854 | $29.0 |
| CA PMAX | Jul–Sep 2026 | $906 | – | 66 | $6,230 | $13.7 |

Both campaigns run at about $300 a month. Nigeria's Performance Max reports a conversion for $3.7 and its September was the best month on record (141 conversions, $13,996 value on $304). Canada's cost per conversion halved from Q2 to Q3. Brand terms are not excluded: the search-terms report shows "beguile by oma" as the largest term ($18.3), but it covers only $254 of the $4,852 spent, because Performance Max does not expose its search terms. Google's 695 conversions cannot be reconciled to Shopify: Shopify's last-visit field credits "Google" with 803 orders in January–September 2026, paid and organic together.

### 2.5 Search (Search Console)

Query data runs from June 2025, so there is no January–September 2025 window. Branded = query contains beguile, beguile by oma/omaa, shopbeguile or a product name (Mystique, Golden Kiss, Goddess, Sweet Oud, Blush Bloom).

| Month | Branded clicks / impressions | Non-branded clicks / impressions | Non-branded share of clicks | Average position |
|---|---:|---:|---:|---:|
| Jul–Sep 2025 | 13 / 85 | 0 / 455 | 0% | 20.4 |
| Jan 2026 | 791 / 4,541 | 1 / 367 | 0.1% | 7.1 |
| Apr 2026 | 2,049 / 32,332 | 4 / 2,178 | 0.2% | 7.2 |
| Jun 2026 | 890 / 20,076 | 5 / 2,460 | 0.6% | 8.2 |
| Jul 2026 | 771 / 9,438 | 18 / 2,535 | 2.3% | 8.9 |
| Aug 2026 | 799 / 9,799 | 18 / 5,233 | 2.2% | 9.1 |
| Sep 2026 | 557 / 6,291 | 57 / 6,438 | 9.3% | 10.2 |
| Jan–Sep 2026 | 8,737 | 125 | 1.4% | – |
| Apr–Jun 2026 | 3,862 | 27 | 0.7% | – |
| Jul–Sep 2026 | 2,127 | 93 | 4.2% | – |

Search is a brand channel: 98.6% of the year's 8,862 clicks were people typing the brand or a product name. An observation, not yet a finding, because it is three months old: non-branded impressions grew from 2,178 in April to 6,438 in September and non-branded clicks from 4 to 57; the queries are "best perfume for summer female 2026", "best sweet perfume for women", "nigerian perfume brand". By country, January–September clicks were Nigeria 5,073, UK 2,962, US 1,638, Canada 1,365; the US had 86,586 impressions for those clicks, the most of any market, which means the site appears in US results but low on the page.

### 2.6 GA4 funnel, January–September 2026

| Market | Sessions | Product views | Add to cart | Checkout started | Purchases (GA4) | Add to cart ÷ sessions | Checkout ÷ add to cart | Purchase ÷ checkout | Purchase ÷ sessions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All | 398,159 | 275,247 | 44,735 | 40,873 | 8,030 | 11.2% | 91.4% | 19.6% | 2.02% |
| Nigeria | 270,990 | 182,338 | 28,346 | 27,634 | 5,703 | 10.5% | 97.5% | 20.6% | 2.10% |
| UK | 54,940 | 38,764 | 7,643 | 5,907 | 1,080 | 13.9% | 77.3% | 18.3% | 1.97% |
| Canada | 39,897 | 31,643 | 5,236 | 4,570 | 735 | 13.1% | 87.3% | 16.1% | 1.84% |
| US | 20,726 | 15,728 | 2,571 | 1,922 | 384 | 12.4% | 74.8% | 20.0% | 1.85% |

Momentum: purchases per session fell from 1.96% in April–June to 1.61% in July–September (Nigeria 2.06% → 1.67%, UK 1.58% → 1.53%, Canada 1.76% → 1.62%, US 2.09% → 1.61%). The step that loses most is checkout to purchase: four in five people who start a checkout do not finish it, in every market and both windows. The step before it barely leaks: 91% of carts reach checkout. GA4's 8,030 purchases against Shopify's 9,040 orders means GA4 sees 89% of orders. By channel in GA4, paid social brought 61% of sessions and 29% of purchases; organic social brought 15% of sessions and 36% of purchases.

### 2.7 Store

The storefront could not be fetched (network policy), so this section uses Shopify's product, order and shipping-line data for July–September 2026.

| Check | Finding | Source |
|---|---|---|
| Product descriptions | All 12 scented products have a description of 57–125 words; 10 list top, mid and dry notes; Mini Set and Oil Trio describe contents without a notes line. The Sweet Oud description holds about 30 leftover formatting tags from a pasted editor. The three 3ml samples have no description at all. | Shopify products |
| Reviews visible | Yes since May 2026 (5,664–7,605 widget impressions a month); 393 published reviews, rating 4.4. | Klaviyo |
| Samples | Three 3ml samples (Golden Kiss, Mystique, Goddess), price shown as ₦0, 53 units sold in nine months, all to the US; tagged sold out in Nigeria, the UK and Canada; stock 347 units at the "Warehance" location and 0–5 elsewhere. No samples page can be confirmed without the storefront. | Shopify |
| Free-shipping threshold | None in any market. Nigeria: 1,179 of 1,699 Q3 orders paid ₦5,000 home delivery, the rest ₦8,000–₦10,000; no Nigerian order shipped free, including the ₦1,023,400 one. UK: £6.50 flat on 196 of 202 orders. Canada: C$11.99–12.99. US: $8.99; one order used a "Free Shipping" line. | Shopify shipping lines |
| Currency per market | Nigeria NGN; UK GBP (197 of 202 orders); Canada CAD (212 of 213); US USD (81 of 82). Implied rates on Q3 orders: ₦1,905 per £, ₦1,012 per C$, ₦1,412 per $. | Shopify presentment |
| Products available per market | Not available from the connector (market catalogues are not exposed). The sold-out tags show Passion unavailable in Canada, Blush Bloom and Seduction in Nigeria, the tote and bottle in the UK and Canada. | Shopify tags |
| Price per market | Not available (presentment prices per product were not pulled; storefront blocked). POK to supply the four price lists. | – |
| SKU completeness | 22 variants carry a SKU; the tote (5 variants), bottle and samples have none. | Shopify |

### 2.8 Unit economics

The sheet "Beguile Unit Economics" reads live Shopify and Meta data (last 90 days to 7 October: Nigeria 1,692 orders at ₦133,939 average and ₦16,940 ad cost per order; UK 164, ₦166,491, ₦58,882; Canada 204, ₦157,334, ₦52,660; US 77, ₦172,635, ₦55,698). Its cost inputs are empty, so its verdict row reads "Enter costs" for every market, and Shopify's unit-cost field is 0 for every variant.

**No profit judgement is possible until these cells are filled**, on the "Unit Economics" tab, columns B to E (Nigeria, United Kingdom, Canada, United States):

- Row 10, B10:E10 — Product cost per order, ₦
- Row 11, B11:E11 — Shipping and fulfilment per order, ₦
- Row 12, B12:E12 — Packaging and other per order, ₦
- Row 13, B13:E13 — Payment fees, % of order
- Row 14, B14:E14 — Returns and discounts, % of order
- Row 15, B15:E15 — Target profit after ads, % of order

Owner: POK. Until then, every "Scale" in this document rests on sales per naira of ads, not profit.

### 2.9 Where this audit agrees and disagrees with the prior Meta audit sheet

Read after the Meta audit above was complete. The prior sheet covers 7 October 2025 – 6 October 2026 at ad level; this audit covers January–September 2026 at campaign level, so totals differ by window.

Agree:
- Fragmentation. The prior sheet counts 476 campaigns launched in 12 months with a median life of 8 days and no ad set reaching 50 purchases in a week; this audit finds 82 campaigns a month and 30% of spend in sub-7-purchase campaigns. Same finding, different ruler.
- Export markets cost 2.9 times Nigeria per purchase (prior: ₦38,875 vs ₦13,364); this audit: ₦43,682–₦52,816 vs ₦15,513 for 2026.
- Meta over-claims. Both find September 2026 Meta purchases above Shopify orders (861 vs 804 there; 861 vs 800 here, the difference being 4 cancelled orders).
- Catalogue is the cheapest Nigerian format and the least funded (prior: ₦11,522 per purchase on 1.4% of spend; here ₦9,996 on 3%).
- Retargeting has never been tested (prior: ₦161k in 12 months). This audit cannot see audiences and takes that as read.
- The "CA Awareness" campaign targets the UK (prior sheet, from targeting metadata). Not visible here; POK and CodeSM should check it.

Disagree or add:
- The prior sheet's first recommendation is to move 20% of export budget to Nigeria at 12-month rates. This audit shows Nigeria's own return falling every quarter (₦14.31 → ₦9.30 → ₦7.05 of Shopify sales per ₦1), so the shift should be gated, not assumed; the plan below uses a monthly gate of ₦6.00.
- The prior sheet treats the account as the lever. This audit finds the bigger Q3 loss outside the ad account: checkout-to-purchase stayed at one in five while orders fell 39%, and 58% of started checkouts got no email. The plan therefore puts CRO, stock and email ahead of media moves.
- The prior sheet reads Blush Bloom and Sweet Oud as products; it does not see that both are out of stock in markets that sold them (Blush Bloom 0 in Lagos; Sweet Oud 2 in the UK and 2 in Canada). Some "international ad sets with zero purchases" were selling unavailable products.
- Named creators are not in the prior sheet's format classes (it classifies by creative object). Here they are the second-cheapest readable Nigerian type (₦10,551) and the cheapest readable UK type after the podcast.

---

## 3. Decision per country

Each decision rests on one metric and one threshold. The metric is **Shopify net sales per ₦1 of Meta spend in that country, measured monthly** ("return"), because it is the only efficiency figure that does not depend on Meta's own counting. Cost per new customer is the secondary check. Profit gates come into force the day the unit-economics cells are filled.

| Market | Decision | The number it rests on | The gate that changes it |
|---|---|---|---|
| **Nigeria** | **SCALE, in steps** | Return ₦7.05 in Q3 (₦9.10 for the year; ₦5.5 in September). Cost of a new customer ₦31,047 = 26% of order value. 75% of sales. | Raise Nigeria spend 25% every two weeks while the trailing-month return stays at or above **₦6.00** and cost per new customer at or below **₦30,000**. A month below ₦6.00 freezes spend at the prior level; a month below ₦5.00 cuts it back one step. The first step is conditional on consolidation (plan NG-4) being done. |
| **UK** | **FIX** | Return ₦2.58 in Q3, down from ₦7.82 in 2025. Cost of a new customer ₦95,222 = 71% of order value. 33 orders in September. | Hold spend at the September level (₦3.3m a month) and run it through at most three campaigns on non-heritage audiences. Reopen scaling when the trailing-month return reaches **₦4.00** and cost per new customer falls below **₦55,000** for two consecutive months with Sweet Oud, Blush Bloom and samples in stock. |
| **Canada** | **FIX** | Return ₦2.54 in Q3, down from ₦5.55 in 2025. Cost of a new customer ₦80,371 = 63% of order value. 38% of Q3 orders used a discount code. | Hold spend at the September level (₦5.6m is above the Q3 average of ₦3.6m; cap at ₦3.6m). Same reopening gate as the UK: return **₦4.00** and cost per new customer below **₦55,000** for two months, with discount-code share under 20%. |
| **US** | **HOLD** | Return ₦3.40 in Q3 (₦4.44 in Q2); cost of a new customer ₦68,133 = 42% of order value; 80 orders in Q3 from 56 new customers. Too small to read month to month. | Keep spend at the Q3 level (₦1.3m a month) in no more than two campaigns, and judge on the quarter: scale if the quarter's return is at or above **₦4.50** with at least 100 new customers; move to Fix if below **₦3.00**. |

No market is stopped: every market still returns more than ₦2.50 of sales per ₦1 of ads. Whether ₦2.50 is above or below break-even is exactly the question the empty cost cells leave open.

---

## 4. Q4 plan

Owners: POK (store, operations, finance, approvals); CodeSM (media, email, creative, reporting). "Why" cites the audit number the action rests on.

### Nigeria

| # | Lane | Action | When | Why (the number) | Owner |
|---|---|---|---|---|---|
| NG-1 | Inventory | Restock Blush Bloom and Seduction in Lagos; move Golden Kiss 10ml stock to Lagos (7 units left). | By 20 Oct | Blush Bloom was 18% of 2025 sales and is 1% now with 0 Lagos units; Seduction 0 units; Golden Kiss 10ml sold 519 units in Nigeria this year. | POK |
| NG-2 | CRO | Checkout-step fix: test one-page checkout and a visible delivery cost before checkout. Measure purchase ÷ checkout started. | Live by 31 Oct, read by 30 Nov | 20.6% of started checkouts become orders; 27,634 checkouts for 5,703 purchases in nine months. | POK (approve), CodeSM (measure) |
| NG-3 | Content (formats) | Produce formats in this priority: catalogue ads, named-creator video, CEO video, static image. Stop commissioning street interviews and generic UGC for Nigeria. | From 15 Oct, continuous | Cost per Meta purchase: catalogue ₦9,996, named creators ₦10,551, CEO ₦13,935, image ₦15,349, vs UGC ₦22,173 and street interview ₦18,033. | CodeSM |
| NG-4 | Meta Nigeria | Consolidate to at most 6 Nigeria sales campaigns, each with a budget that buys 50+ purchases a week (about ₦95,000 a day at the Q3 cost per purchase of ₦19,436). New creative goes in as ads, not campaigns. | By 24 Oct | 14 Nigeria campaigns live on 8 Oct; 36% of Q3 spend in campaigns under 7 purchases a month; frequency 8–11 in Apr, May, Aug, Sep. | CodeSM |
| NG-5 | Meta Nigeria | Scale in 25% steps against the ₦6.00 gate (section 3). Start from the September base of ₦14.0m. | First step 1 Nov if October passes | Return ₦7.05 in Q3; ₦5.5 in September alone. | CodeSM (execute), POK (approve each step) |
| NG-6 | Meta Nigeria | Add one retargeting campaign (site visitors and checkout starters, last 30 days, buyers excluded) at 10% of Nigeria spend. | By 31 Oct | 27,634 checkouts started vs 5,703 purchases; no retargeting has run (prior audit: ₦161k in 12 months). | CodeSM |
| NG-7 | Email | Raise abandoned-checkout coverage: capture email earlier in checkout and add an SMS step for Nigerian numbers. | By 31 Oct | 42% of started checkouts got an email in September; the flow returns ₦1,124 per email, four times any other flow. | CodeSM (flow), POK (checkout field) |
| NG-8 | Google Ads | Double the Nigeria Performance Max budget to about $600 a month; exclude brand terms. | 15 Oct | Google reports $3.7 per conversion and 141 conversions in September on $304; "beguile by oma" is the largest paid search term. | CodeSM |
| NG-9 | Reviews | Keep the review flow; add a review request to the post-purchase flow's second email. | 31 Oct | 11 reviews a month with the flow vs 98 a month before it; 1 review per 80 emails. | CodeSM |
| NG-10 | Measurement | Put a tracking tag on every Meta ad link so Shopify can tell paid Instagram from organic. | By 20 Oct | 3,224 of 9,041 orders carry no tag; Meta claimed 108% of September's orders. | CodeSM |

### UK

| # | Lane | Action | When | Why (the number) | Owner |
|---|---|---|---|---|---|
| UK-1 | Inventory | Ship Sweet Oud and Blush Bloom stock to the UK warehouse; confirm Mystique cover (115 units vs 106 sold in Q3). | By 25 Oct | Sweet Oud has 2 UK units; it was 16% of UK sales in 2025 and 7% now. | POK |
| UK-2 | Meta export | Cut to at most 3 sales campaigns, all on audiences with no heritage link, at the September spend (₦3.3m a month). Heritage targeting as one control campaign capped at 25%. | By 24 Oct | 11 UK campaigns live; return ₦2.58; 65% of UK spend in campaigns with no stated creative type. | CodeSM |
| UK-3 | Content (formats) | Lead with the podcast partnership and named-creator video; test static image. Do not fund dynamic or UGC until each has 20 purchases. | From 20 Oct | Podcast ₦29,623 per Meta purchase, named creators ₦39,712, image ₦35,976, vs UK average ₦43,682. | CodeSM |
| UK-4 | Podcast partnerships | Extend ISWIS to the UK as the primary format and measure it as its own campaign. | Q4 | ISWIS UK ₦29,623 per purchase on 38 purchases, the cheapest readable UK type. | POK (deal), CodeSM (run) |
| UK-5 | Creator partnerships | Tier 1: two named UK creators with no Nigerian-heritage positioning, whitelisted. Tier 2: whitelisting of existing creators (Woomi, Amy Okoli) as a control. Tier 3: micro-influencer UGC only after Tier 1 shows 20 purchases. | Tier 1 live by 15 Nov | Named creators are the cheapest readable export format in both the UK and Canada; UGC is ₦78,005 per purchase in the UK on 8 purchases (insufficient data, so not funded first). | CodeSM |
| UK-6 | CRO | Test a free-delivery threshold at £75 against the £6.50 flat fee. | Test live by 7 Nov | No free-shipping threshold exists; checkout-to-purchase is 18.3%; UK average order about £70 (₦134,436 ÷ ₦1,905). | POK |
| UK-7 | SEO/AEO | Publish one answer page per non-branded query family ("best sweet perfume for women", "perfume notes"). Low cost; rests on a three-month observation, so it is not a priority item. | Q4 | 1.4% of the year's search clicks are non-branded; the September rise to 57 clicks is an observation. | CodeSM |
| UK-8 | Measurement | Report weekly: return, cost per new customer, orders, discount-code share. Reopen scaling only at the section 3 gate. | From 20 Oct | Gate: ₦4.00 return and cost per new customer below ₦55,000 for two months. | CodeSM |

### Canada

| # | Lane | Action | When | Why (the number) | Owner |
|---|---|---|---|---|---|
| CA-1 | Inventory | Ship Sweet Oud and Passion to the Canada warehouse; confirm "Warehance – 5 Logistics" market. | By 25 Oct | Sweet Oud 2 units, Passion 0; Sweet Oud was 19% of Canadian sales in 2025. | POK |
| CA-2 | Meta export | Cap spend at the Q3 average (₦3.6m a month; September was ₦5.6m) in at most 3 campaigns on non-heritage audiences. | By 24 Oct | Return ₦2.54; 15 Canada campaigns live; 73% of spend with no stated creative type. | CodeSM |
| CA-3 | Content (formats) | Named-creator video first, dynamic second; nothing else until 20 purchases. | From 20 Oct | Named creators ₦53,205 and dynamic ₦49,126 per purchase are the only readable Canadian types. | CodeSM |
| CA-4 | Creator partnerships | Same three tiers as the UK; Tier 1 creators chosen for Toronto and Vancouver without heritage positioning. | Tier 1 by 15 Nov | Named creators are 8% of Canadian spend and the only format with 50 purchases. | CodeSM |
| CA-5 | CRO | Stop open discount codes; replace with a free-delivery threshold test at C$100. | By 31 Oct | 38% of Q3 orders used a code; checkout-to-purchase 16.1%, the lowest of any market. | POK |
| CA-6 | Google Ads | Keep CA Performance Max at $300 a month. | Continue | Cost per conversion halved to $13.7 in Q3; 29 conversions in September. | CodeSM |
| CA-7 | Measurement | Weekly report as UK-8; reopen at the section 3 gate. | From 20 Oct | Gate: ₦4.00 return, cost per new customer below ₦55,000, discount share under 20%. | CodeSM |

### US

| # | Lane | Action | When | Why (the number) | Owner |
|---|---|---|---|---|---|
| US-1 | Inventory | Confirm the US fulfilment location and its stock (if "Warehance" is the US, Goddess has 43 units and Sweet Oud 0). | By 20 Oct | US sold 24 Goddess and 25 Mystique in Q3; location not stated in Shopify. | POK |
| US-2 | Meta export | Hold at ₦1.3m a month in at most 2 campaigns (Mystique, Goddess); no Golden Kiss. | By 24 Oct | Mystique ₦38,460 and Goddess ₦43,120 per Meta purchase vs Golden Kiss ₦62,636; return ₦3.40. | CodeSM |
| US-3 | Content (formats) | CEO video, then podcast; read only at the quarter. | Q4 | Every US type is under 20 purchases: insufficient data. | CodeSM |
| US-4 | Store | Keep samples live; they sell only here (53 units); add a description to the three sample products. | By 31 Oct | Samples have 0 words of description; all sample sales are US. | POK |
| US-5 | SEO/AEO | Target US non-branded queries; the US has the most search impressions (86,586) and a low position. | Q4 | US impressions 86,586 for 1,638 clicks. | CodeSM |
| US-6 | Measurement | Judge on the quarter: scale at ₦4.50 return with 100+ new customers; Fix below ₦3.00. | 31 Dec | 56 new customers in Q3 is too few to read monthly. | CodeSM |

### Shared platform

| # | Lane | Action | When | Why (the number) | Owner |
|---|---|---|---|---|---|
| S-1 | Measurement | Fill the six cost rows of the unit-economics sheet (section 2.8). No scaling step is approved before this. | By 17 Oct | Every verdict cell reads "Enter costs". | POK |
| S-2 | Measurement | Fix the Meta over-count: confirm in Meta's Events Manager that a purchase sent from the browser and from the server is counted once, not twice; report monthly Meta purchases ÷ Shopify orders. | By 31 Oct | 108% in September 2026. | CodeSM |
| S-3 | Measurement | One weekly scorecard (section 5), by country, from Shopify first. | From 20 Oct | Platform numbers over-claim; Shopify is the source of truth. | CodeSM |
| S-4 | Email | Cut the welcome series to the first email plus one follow-up; pause cross-sell and winback until they show 10 orders a month between them. Keep sending campaigns at the Q3 cadence but to engaged segments only. | By 31 Oct | Welcome ₦242 per email; cross-sell, winback, post-purchase and review flows: 10 orders from 14,318 emails; campaigns ₦22 per recipient in Q3. | CodeSM |
| S-5 | Store | Clean the Sweet Oud description; add descriptions and SKUs to samples, tote and bottle; supply the four price lists. | By 31 Oct | 30 leftover tags; 0-word descriptions; 8 variants with no SKU. | POK |
| S-6 | Meta | Name every campaign "Market \| Product \| Format \| Audience" from 15 October, so the next audit can read export creative. | 15 Oct | 55–76% of spend per market has no format in its name. | CodeSM |
| S-7 | Inventory | Weekly stock-by-market report against the "days of cover" table; reorder at 60 days. | Weekly from 20 Oct | Sweet Oud UK and Canada at 2 units; Golden Kiss 10ml Lagos at 7. | POK |

---

## 5. Goal

### Testing ₦1bn in Q4

| Requirement for ₦1bn | Needed | Q3 2026 actual | Best on record |
|---|---:|---:|---:|
| Net sales | ₦1,000m | ₦268.9m | ₦364.6m (Q4 2025); ₦167.4m in a month (Oct 2025) |
| Multiple of the comparison | – | 3.72× Q3 | 2.74× the best quarter; 1.99× the best month ×3 |
| Orders at the Q3 order value (₦123,239) | 8,114 (88 a day) | 2,185 (24 a day) | 55 a day (Oct 2025) |
| Meta spend at the Q3 return (₦5.03 per ₦1) | ₦199m (₦2.16m a day) | ₦53.5m (₦0.58m a day) | ₦25.4m in a month (Sep 2026, at ₦3.9 return) |
| Meta spend at the nine-month return (₦6.40) | ₦156m | – | – |
| Stock, units at 3.72× Q3 | Mystique 3,887; Goddess 2,633; Golden Kiss 1,830; Mini Set 1,190; Sweet Oud 1,108 | – | On hand: 2,212; 1,438; 1,151; 858; 517 |

₦1bn in Q4 needs 3.7 times the quarter just ended, 2.7 times the best quarter the business has had, and four times the daily spend, at a return the account has not reached since June. Stock on hand covers about half of it for every top product. It is not a plan; it is the Ambition case below, stated as conditions.

### Three scenarios

**Base — the fixes alone, modest extra spend: ₦339m.** Q3 2026 net (₦268.9m) × the 2025 seasonal lift (Q4 2025 was 1.26× Q3 2025). Assumes: the stock gaps in NG-1, UK-1, CA-1 are closed by 25 October; Meta spend flat at the Q3 level (₦53.5m) but consolidated (NG-4); checkout-to-purchase and email coverage unchanged. 2,754 orders, 30 a day.

**Stretch — every October gate passed: ₦440m.** Base plus ₦14.3m of extra Nigeria spend (the first two 25% steps) at the Q3 Nigeria return of ₦7.05, adding ₦101m. Assumes: the October return in Nigeria holds at ₦6.00 or better after consolidation; checkout-to-purchase improves (not counted); UK and Canada hold at their caps. Total Meta spend ₦67.8m; about 3,570 orders, 39 a day — the Q2 2026 level.

**Ambition — ₦1bn, stated as what would have to be true.** Each line is a gate; miss one and the case fails:
1. Nigeria's return holds at ₦7.00 or better while spend triples from ₦14.0m to ₦42m a month (it fell from ₦9.30 to ₦7.05 while spend rose 11%).
2. Export markets return ₦4.00, not ₦2.54–₦2.58, on non-heritage audiences, at double their Q3 spend.
3. Checkout-to-purchase rises from 20% to 30% (that alone is +50% orders at the same traffic).
4. Abandoned-checkout coverage rises from 42% to 70%.
5. Stock: a further 1,700 Mystique, 1,200 Goddess, 700 Golden Kiss, 600 Sweet Oud and 350 Mini Set units in the right warehouses by mid-November.
6. The unit-economics cells show that an order at ₦5.03 of sales per ₦1 of ads is profitable; otherwise ₦1bn of sales is ₦199m of ads for a loss.
7. 88 orders a day for 92 days, against a record of 55.

### Scorecard

Today's value is July–September 2026 unless stated; the 31 December target is the Stretch case. Both comparisons are given where the source has them.

| Measure | Today | vs Apr–Jun 2026 | vs Jan–Sep 2025 | Target, 31 Dec 2026 |
|---|---:|---:|---:|---:|
| Monthly net sales (Shopify) | ₦100.2m (Sep) | ₦135.0m a month | ₦68.6m a month | ₦147m a month (₦440m for the quarter) |
| Orders a day (Shopify) | 24 | 39 | 25 | 39 |
| Shopify net per ₦1 of Meta, all markets | ₦5.03 | ₦6.52 | ₦11.09 | ₦6.50 |
| Nigeria cost of a new customer | ₦31,047 | ₦19,040 | ₦11,041 | ≤ ₦30,000 |
| Export (UK+CA+US) cost of a new customer | ₦83,464 | ₦57,782 | ₦27,040 (UK+CA; no US in 2025) | ≤ ₦55,000 |
| Share of Meta spend in campaigns with fewer than 7 purchases a month | 36% | 27% | 13% | ≤ 15% |
| Checkout started → purchase (GA4) | 20.1% | 18.3% | not available (GA4 starts Dec 2025) | 25% |
| Abandoned-checkout email coverage | 42% (Sep) | 17–36% | not available (no checkout data for 2025) | 70% |
| Reviews collected a month | 11 | 34 | not available (reviews start Oct 2025) | 60 |
| Meta purchases as % of Shopify orders | 85% (108% in Sep) | 75% | 79% | under 90% every month, after deduplication |

---

*Sources and windows for every figure: Shopify orders, line items, products and inventory via Windsor (pulled 8 Oct 2026); Meta campaign × country × month and reach × month via Windsor (attribution 7-day click / 1-day view); Klaviyo flow and campaign reports (Placed Order), reviews and metric aggregates via the Klaviyo MCP; Google Ads (USD) and Search Console via Windsor; GA4 property 518041609 via Windsor; Google Sheets "Beguile Unit Economics" and "Beguile Meta Ads Audit, Oct 2025 to Oct 2026". Scripts: `audit/scripts/01`–`17`; outputs: `audit/out/`.*
