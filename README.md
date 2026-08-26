# UPI vs Card — Payment Rails Infra Demo

A live, hands-on demo comparing how money actually moves through **UPI** vs
**Card (debit/credit)** infrastructure — built for a fintech infra event.
Instead of a lecture, this simulates a transaction hop-by-hop on both rails
so people can *see* why UPI settles instantly and cards don't.

Pure Python, runs straight in the terminal. No browser, no server, no
extra packages to install.

## Files

| File | What it is |
|---|---|
| `upi_vs_card.py` | The demo script. Standard library only. |

## What it shows

- **UPI rail**: Customer → NPCI switch → Remitter bank → Merchant (3 hops, near-instant settlement)
- **Card rail**: Customer → POS/gateway → Acquiring bank → Card network → Issuing bank → Merchant (6 hops, authorization is instant but merchant settlement is T+1/T+2)
- A comparison table printed at the end: merchant fees (MDR), settlement time, hardware needed, credit availability, and dispute process

Running it prints each hop live as it "happens" (small delay between lines
for effect), then a comparison table with real MDR fees computed on the
amount you pass in.

## Running it

Requires Python 3.7+, nothing else.

\`\`\`bash
python upi_vs_card.py
\`\`\`

Options:

\`\`\`bash
python upi_vs_card.py --amount 1200      # custom transaction amount (default 500)
python upi_vs_card.py --fast             # skip the delays, print instantly
python upi_vs_card.py --amount 1200 --fast
\`\`\`

## Customizing for your session

- **Change the fee assumption**: edit `CARD_MDR_RATE` / `UPI_MDR_RATE` near
  the top of the script.
- **Add/remove hops**: edit the `UPI_HOPS` / `CARD_HOPS` lists — each entry
  is `(label, description)`.
- **Change the pacing**: edit the `delay` value (seconds between printed
  hops) or just use `--fast` on stage if you're narrating over it manually.

## Suggested flow for the event

1. Explain what a debit/credit card is, and what UPI is, at a high level.
2. Run this script live in a terminal — let the audience watch UPI finish
   printing while the card transaction is still hopping through banks.
3. Walk through the comparison table row by row (fees, settlement, hardware).
4. Segue into the credit card interest/minimum-due demo (separate module,
   not included here) using the "credit available" row as the bridge.
