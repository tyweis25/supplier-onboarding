This is a simulated Blitzy-style PR and Blitzy did not produce it.

# Adding an upgrade bidding capability

Passengers bid for premium cabin upgrades. This report describes how supplier onboarding should accept that capability for airline suppliers and reject it for every other onboarded supplier.

## Current behavior

Onboarding is an in-memory check. A request is approved only when the supplier is onboarded and the requested capability is in that supplier's supported set.

The onboarded suppliers are fictional:

- AIR1, an airline, supports SEARCH, BOOK, and CANCEL
- HOTEL1, a hotel chain, supports SEARCH, BOOK, and CANCEL
- CAR1, a car rental, supports SEARCH and BOOK

UPGRADE_BIDDING is already a capability name. No supplier supports it, so every check for it is rejected.

## Target behavior

UPGRADE_BIDDING becomes a supported capability for airline suppliers only.

- AIR1 is approved for UPGRADE_BIDDING
- HOTEL1 is not approved for UPGRADE_BIDDING
- CAR1 is not approved for UPGRADE_BIDDING

The reason text keeps the existing shape. An approval reads: Capability UPGRADE_BIDDING is supported for supplier AIR1. A rejection reads: Capability UPGRADE_BIDDING is not supported for supplier HOTEL1, with the supplier code of the supplier that was checked.

Unknown suppliers stay rejected. Missing, empty, and wrong-type fields stay invalid. SEARCH, BOOK, and CANCEL do not change. Health checks do not change.

## Verification

Cover the approved case for AIR1 and the rejected cases for HOTEL1 and CAR1. The rest of the onboarding matrix stays as it is on the baseline.

## Out of scope

This change does not add suppliers, rename capabilities, or alter flags, scripts, or manifests.
