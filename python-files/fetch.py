# A program that fetches past winning numbers and draw results from www.calottery.com

# # Setup
# python3 -m venv .venv
# source .venv/bin/activate
# (venv) $ python -m pip install requests requests_cache dotted-notation
#
# # Run
# python fetch.py
#

import requests
import requests_cache
import json
import csv
import dotted

URL = "https://www.calottery.com/api/DrawGameApi/DrawGamePastDrawResults/{game}/{page}/{size}"
GAMES = {
    'POWERBALL': 12,
    'MEGA Millions': 15,
    'SuperLotto Plus': 8
}


OUTPUT = "output.csv"


requests_cache.install_cache('cache')

def download_result(game, page):
    """Returns a object representing a page of data for this game"""

    url = URL.format(
        game = game,
        page = page,
        size = 20,
    )

    results = requests.get(url)

    return json.loads(results.text)


def download_results():
    game = GAMES['POWERBALL']
    fieldnames = {
        'DrawNumber': 'DrawNumber',
        'DrawDate': 'DrawDate',

        # Winning Numbers
        '0': 'WinningNumbers."0".Number',
        '1': 'WinningNumbers."1".Number',
        '2': 'WinningNumbers."2".Number',
        '3': 'WinningNumbers."3".Number',
        '4': 'WinningNumbers."4".Number',
        'Powerball': 'WinningNumbers."5".Number',

        # Prize amounts
        # TODO Populate the titles from the json instead of hard coding.
        '5 + Powerball Count': 'Prizes."1".Count',
        '5 + Powerball Amount': 'Prizes."1".Amount',

        '5 Count': 'Prizes."2".Count',
        '5 Amount': 'Prizes."2".Amount',

        '4 + Powerball Count': 'Prizes."3".Count',
        '4 + Powerball Amount': 'Prizes."3".Amount',

        '4 Count': 'Prizes."4".Count',
        '4 Amount': 'Prizes."4".Amount',

        '3 + Powerball Count': 'Prizes."5".Count',
        '3 + Powerball Amount': 'Prizes."5".Amount',

        '3 Count': 'Prizes."6".Count',
        '3 Amount': 'Prizes."6".Amount',

        '2 + Powerball Count': 'Prizes."7".Count',
        '2 + Powerball Amount': 'Prizes."7".Amount',

        '1 + Powerball Count': 'Prizes."8".Count',
        '1 + Powerball Amount': 'Prizes."8".Amount',

        'Powerball Count': 'Prizes."9".Count',
        'Powerball Amount': 'Prizes."9".Amount',
    }

    with open(OUTPUT, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames.keys(), extrasaction='ignore')
        writer.writeheader()

        for page in range(1, 7):
            results = download_result(game, page)

            for draw in results['PreviousDraws']:
                row = {}
                for key, value in fieldnames.items():
                    row[key] = dotted.get(draw, value)

                writer.writerow(row)

    #with open(OUTPUT, 'w', newline='') as csvfile:
    #    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='raise')
    #
    #    writer.writeheader()
    #
    #    for material in materials:
    #        # Ensure all values are strings
    #        material = {k: sanitise(v) for k, v in material.items()}
    #
    #        writer.writerow(material)

if __name__ == "__main__":
    download_results()
