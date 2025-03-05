#!/usr/bin/env python3

import requests
import json
import sys
import os
from typing import Any
from itertools import zip_longest


def read_collection(filepath: str) -> Any:
    """Read a user's card collection from a given filepath.
    Should be in the ptcgp.app JSON format with dash delimiters.
    Returns a dictionary with the JSON contents."""
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError("Could not open " + filepath +
                                ", file does not exist")


def get_all_card_data() -> Any:
    """If data.json doesn't exist already, download the latest PTCGP card data
    from Pokemon Zone and save it to the file.
    If data.json does exist, load the JSON data from the file.
    Either way, returns a dictionary with the contents of the JSON file."""
    if os.path.exists("data.json") and os.path.isfile("data.json"):
        print("Card data already downloaded, using saved data...")
        with open("data.json", "r") as f:
            return json.load(f)
    else:
        print("Card data does not exist, downloading...")
        r = requests.get("https://www.pokemon-zone.com/api/game/game-data/")
        r.raise_for_status()
        with open("data.json", "w") as f:
            f.write(r.text)
        print("Downloaded and saved card data!")
        return r.json()


def get_card_metadata(all_card_data, ptcgp_app_card_id: str, card_data):
    """Given Pokemon Zone card data (all_card_data), find the card given by
    ptcgp_app_card_id (which should be in the form A#(α)-### or P-A-###) and
    add the card's name and rarity to card_data."""
    cards = all_card_data['data']['cards']
    # Handle alpha characters and promo expansion id in the form P-A-###,
    # as well as normal expansions in the form A#(a)-###
    expansion: str = "-".join(ptcgp_app_card_id.split("-")[:-1]) \
        .replace("α", "a")
    # The Pokemon Zone expansion id for Promo-A is "PROMO-A", but ptcgp.app's
    # is "P-A" - do the conversion if necessary
    if expansion == "P-A":
        expansion = "PROMO-A"
    # This also works with promo cards (since it takes the last index of the
    # split string)
    collection_number: int = int(ptcgp_app_card_id.split("-")[-1])
    for card in cards:
        if card["collectionNumber"] == collection_number and \
                card["expansion"]["expansionId"] == expansion:
            # Once the card is found, attach rarity and name data
            card_data["rarity"] = card["rarityName"]
            card_data["name"] = card["name"]
            break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: main.py <collection1>.json <collection2>.json")
        sys.exit(1)

    card_data = get_all_card_data()
    print()

    collection_1_path: str = sys.argv[1]
    collection_2_path: str = sys.argv[2]
    # Read both collections from file paths
    collection_1 = read_collection(collection_1_path)
    collection_2 = read_collection(collection_2_path)
    # Find unique cards against each other collection
    col1_only = {card: count for card, count in collection_1.items()
                 if card not in collection_2.keys()}
    col2_only = {card: count for card, count in collection_2.items()
                 if card not in collection_1.keys()}
    # Filter out un-tradable expansions
    banned_expansions = ["A2α", "P-A"]
    col1_only = {card: count for card, count in col1_only.items()
                 if "-".join(card.split("-")[:-1]) not in banned_expansions}
    col2_only = {card: count for card, count in col2_only.items()
                 if "-".join(card.split("-")[:-1]) not in banned_expansions}
    # Filter out cards with counts less than threshold
    count_threshold = 1
    col1_only_multiple = {card: {"count": count} for card, count in
                          col1_only.items() if count > count_threshold}
    col2_only_multiple = {card: {"count": count} for card, count in
                          col2_only.items() if count > count_threshold}
    # Find metadata for cards
    for card, data in col1_only_multiple.items():
        get_card_metadata(card_data, card, data)
    for card, data in col2_only_multiple.items():
        get_card_metadata(card_data, card, data)

    # Rarities (from Pokemon Zone data):
    # Common = 1 Diamond
    # Uncommon = 2 Diamonds
    # Rare = 3 Diamonds
    # Double Rare = 4 Diamonds
    # Art Rare = 1 Star
    # Super Rare = 2 Star
    # Immersive Rare = 3 Star
    # Crown Rare = Crown
    rarities: list[str] = ["Common", "Uncommon", "Rare", "Double Rare",
                           "Art Rare", "Super Rare", "Immersive Rare",
                           "Crown Rare"]
    banned_rarities: list[str] = ["Super Rare", "Immersive Rare", "Crown Rare"]
    # Filter out banned rarities
    rarities = [rarity for rarity in rarities if rarity not in banned_rarities]
    for rarity in rarities:
        col1_rarity = {card: data for card, data in col1_only_multiple.items()
                       if data["rarity"] == rarity}
        col2_rarity = {card: data for card, data in col2_only_multiple.items()
                       if data["rarity"] == rarity}
        # Skip the current rarity if neither collection has cards of the rarity
        # to trade
        if len(col1_rarity) == 0 and len(col2_rarity) == 0:
            continue
        # Print rarity header
        print(rarity)
        print("{: <40}| {: <40}".format("Collection 1", "Collection 2"))
        print("-" * 40 + "+" + "-" * 40)
        # Sort data into columns
        zipped = list(zip_longest(col1_rarity, col2_rarity))
        for pair in zipped:
            # ID = ptcgp.app-style id (A#(α)-### or P-A-###)
            # Name = Card's pokemon name
            # Count = collection count
            id1 = pair[0] if pair[0] else ""
            id2 = pair[1] if pair[1] else ""
            name1 = col1_rarity[id1]["name"] if pair[0] else ""
            name2 = col2_rarity[id2]["name"] if pair[1] else ""
            count1 = col1_rarity[id1]["count"] if pair[0] else ""
            count2 = col2_rarity[id2]["count"] if pair[1] else ""
            print("{: <40}| {: <40}".format(name1 + " (" + id1 + " x" +
                                            str(count1) + ")"
                                            if pair[0] else "",
                                            name2 + " (" + id2 + " x" +
                                            str(count2) + ")"
                                            if pair[1] else ""))
        print()
