import requests
from bs4 import BeautifulSoup

def scrape_rss_links(url, output_file="rss_links.txt"):
    """
    Scrapes RSS links from a given URL and appends them to a text file without duplicates.

    The script looks for links inside an <a> tag that are next to a <strong> tag
    with the text 'RSS Feed'.

    Args:
        url (str): The URL of the website to scrape.
        output_file (str): The name of the file to save the RSS links to.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <strong> tags with the text 'RSS Feed'
        strong_tags = soup.find_all('strong', string=lambda t: t and 'RSS Feed' in t)

        if not strong_tags:
            print("No 'RSS Feed' strong tags found on the page.")
            return

        # Read existing links from the output file to avoid duplicates
        try:
            with open(output_file, 'r') as f:
                existing_links = set(line.strip() for line in f)
        except FileNotFoundError:
            existing_links = set()

        new_links_found = 0
        with open(output_file, 'a') as f:
            for tag in strong_tags:
                # Find the next sibling 'a' tag
                next_a_tag = tag.find_next_sibling('a')
                if next_a_tag and next_a_tag.has_attr('href'):
                    rss_link = next_a_tag['href']
                    # If the link is not already in the file, write it
                    if rss_link not in existing_links:
                        f.write(rss_link + '\n')
                        existing_links.add(rss_link)
                        print(f"Found and saved new RSS link: {rss_link}")
                        new_links_found += 1

        if new_links_found == 0:
            print("No new RSS links were found.")
        else:
            print(f"\nSuccessfully saved {new_links_found} new RSS link(s) to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while fetching the URL - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Prompt the user for the URL
    website_url = input("Please enter the URL of the website to scrape for RSS links: ")
    scrape_rss_links(website_url)