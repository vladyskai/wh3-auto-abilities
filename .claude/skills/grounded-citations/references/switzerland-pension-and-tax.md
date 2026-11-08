# Swiss pension, tax and employment-benefit research

Notes for cited research on Swiss personal-finance questions (3a, 2nd pillar,
employee share plans, mortgage and tax mechanics). The procedure and the
citation machinery are in SKILL.md; this file is the source map and the checks
that decide the answer.

## Source map

| Layer | Sources | What it settles |
|---|---|---|
| Law and annual limits | admin.ch press releases, ESTV, BSV, fedlex (BVV3, BVG, DBG/StHG) | Current-year deduction ceilings, buy-back rules, who may contribute, how a payout is taxed |
| Cantonal practice | cantonal TaxInfo pages (e.g. Bern, St. Gallen), cantonal Steuerbuch PDFs | Deduction mechanics, separate annual tax on capital benefits, which canton taxes a payout |
| Provider register | ESTV list of recognised 3a providers | Legal name and seat of each pension foundation, which is what determines the withholding tax if the holder lives abroad |
| Independent comparisons | moneyland.ch (including its cost simulations), VZ VermögensZentrum, Evaluno, SRF Kassensturz, Beobachter | Fee levels, interest-rate tables, performance, and the consumer-protection verdict |
| Affiliate-driven comparisons | schwiizerfranke, mustachianpost, provider knowledge bases (finpension, frankly, VIAC) | Useful for feature tables (equity ranges, number of pots, withdrawal fees) and for provider self-reports; treat their rankings as marketing and corroborate with the independent layer |

Provider knowledge bases are a legitimate primary source for that provider's own
published rate and for cross-provider tables they maintain (foundation seat,
withholding tax by canton), but never for their own ranking.

Once the user has picked a provider and wants its terms read, switch method:
the regulation stack and the clause families that decide a
provider-versus-provider comparison are in the `contract-compliance-review`
skill, `references/provider-terms-review.md`.

## Checks that decide any Swiss retirement-product question

Work through these in order; each one can invalidate the product comparison
below it.

1. **Which ceiling applies.** Covered by a pension fund (the normal employee
   case) versus no 2nd-pillar cover (self-employed or uncovered) are two
   different limits, re-decided every year. Read the current figures from the
   official layer, not from a comparison site's article, and say which tax year
   the numbers belong to. A year-end contribution or a retroactive buy-back only
   helps if it is paid before the deadline.
2. **Product wrapper first:** savings account versus securities solution versus
   insurance policy. Consumer-protection reporting and the independent advisory
   houses both advise against combining saving with risk cover inside the
   wrapper; the standard recommendation is to separate the two. A surrender
   value on early exit, an entry commission taken from early premiums, and a
   fixed payout date are the mechanisms to look for.
3. **For securities products, compare total cost, not the headline fee:**
   provider fee plus product cost, whether the product cost is bundled, whether
   the uninvested cash part is charged, the maximum equity share, the number of
   separate contracts (pots), the minimum amount, and the fees for transfers and
   for a house-purchase withdrawal. Equity share drives portfolio return far
   more than fund choice.
4. **Payout mechanics decide the real tax bill.** The lump-sum tax is
   progressive, so one payout in one year versus five pots over five years is
   the largest avoidable cost in the whole structure. Check how many contracts a
   provider allows instead of only its fee.
5. **Canton logic, in the right case:** while resident in Switzerland the canton
   of residence at the due date taxes the payout (not the canton at year end,
   and not the foundation's seat). Only for someone resident abroad when the
   money is due does the foundation's seat matter, because a withholding tax is
   then levied there, with treaty refundability as a separate question. Say
   plainly which of the two cases applies to the reader.
6. **Annually changing values always carry a re-verification note.** Limits,
   interest tables and fee schedules move; state the date of the figure and tell
   the reader to confirm the current published tariff before signing.

## Reusable phrasing for the honesty that carries the answer

- Separate the sourced figures from your own model: label a projection as yours
  with its assumptions (contribution, years, gross return), and never cite it.
- Scope every number to the product it belongs to. A minimum, ceiling or fee that
  belongs to one product is not a threshold for another; unscoped, a minimum for
  uninvested free assets reads as a condition on the pension contribution the
  user is actually making. Name the product, and say explicitly whether the
  figure applies to the account being asked about.
- State what you could not verify: a provider fee page that would not load, a
  rule whose edge case (for example starting from zero accounts) the sources do
  not cover. Recommend confirming those with the provider and the cantonal tax
  office rather than smoothing them over.
- Quantify the second-order effects so the reader can stop optimizing the wrong
  thing: a fee difference of a few basis points is tens of francs a year on a
  typical balance, while the wrapper choice and the payout staggering are worth
  five or six figures over a working life.
