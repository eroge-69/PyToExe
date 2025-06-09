#!/usr/bin/env python3

# One-liner install to /usr/local/bin/remove_emojis
# sudo curl -L https://gist.githubusercontent.com/beveradb/421e1653c056ee5b6770f7d1f05aa760/raw/remove_emojis.py -o /usr/local/bin/remove_emojis && sudo chmod +x /usr/local/bin/remove_emojis

import os
import re
import sys

def remove_emojis(filename):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"  # Enclosed characters
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001F000-\U0001F02F"  # Mahjong Tiles, Domino Tiles, Playing Cards
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'_EMOJI_', filename)


def main():
    dry_run = False
    if len(sys.argv) > 1 and sys.argv[1] == '-n':
        dry_run = True

    for filename in os.listdir('.'):
        new_filename = remove_emojis(filename)
        if filename != new_filename:
            print(f'Renaming: {filename} -> {new_filename}')
            if not dry_run:
                os.rename(filename, new_filename)
        else:
            print(f'No changes: {filename}')

if __name__ == "__main__":
    main()