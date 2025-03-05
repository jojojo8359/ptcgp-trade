# ptcgp-trade

![GitHub License](https://img.shields.io/github/license/jojojo8359/ptcgp-trade)

A small utility for coordinating trades with another user for the Pokémon Trading Card Game: Pocket mobile game.

This utility assumes that both users have their collections tracked with [ptcgp.app](https://ptcgp.app/), and have exported their collections as JSON files.

# Setup

A stable version of Python 3 should be used (3.9+).

To install required dependencies (just [requests](https://docs.python-requests.org/en/latest/index.html)), run `pip3 install -r requirements.txt`. Use of a virtual environment is left up to the user, but recommended.

# How to Use

Both users should use ptcgp.app to export their collections as JSON files with dash delimiters (in the export dialog, choose "JSON" and "Dash (A1-094)").

Once exported, run the utility with paths to the two files:

`python3 ptcgp-trade.py <collection_1_path>.json <collection_2_path>.json`

When run, the utility will attempt to download current PTCGP card data from [Pokémon Zone](https://www.pokemon-zone.com/cards/) to the working directory as `data.json`. On subsequent runs, if this file is present, the data will not be re-downloaded - deleting the file will allow it to update.

After all card data has been acquired, the utility will output potential trades by rarity between the two collections, making trade coordination trivial on both ends!

# Restrictions

There are certain expansions/rarities that cannot be traded. Some of these restrictions can be accounted for with this utility.

> [!IMPORTANT]
> Please note that the following information can change at any time. The most up-to-date trading rules for the game can always be found in the Trade Rules help screen in-game.

Restrictions that are not accounted for with this utility include:
- flair status (since ptcgp.app is not able to track flair)


## Expansion Restrictions

Currently, the following expansions are restricted from trading:
- Triumphant Light (ptcgp.app ID `P2α`, Pokémon Zone ID `P2a`)
- Promo-A (ptcgp.app ID `P-A`, Pokémon Zone ID `PROMO-A`)

The utility uses the `banned_expansions` list to filter out restricted expansions from its comparison.

## Rarity Restrictions

Currently, the following card rarities are restricted from trading:
- Super Rare (2 gold stars)
- Immersive Rare (3 gold stars)
- Crown Rare (1 crown)

This rule currently applies to all tradable expansions, but is subject to change per expansion in the future.

The utility uses the `banned_rarities` list to filter out restricted rarities from its comparisons.
