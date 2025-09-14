import sys

def remove_duplicate_urls(urls):
    seen = set()
    unique_urls = []
    for url in urls:
        url = url.strip()
        if url and url not in seen:
            unique_urls.append(url)
            seen.add(url)
    return unique_urls

if __name__ == "__main__":
    print("Enter URLs (one per line). Press Ctrl+Z then Enter when done:")
    urls = [line.strip() for line in sys.stdin if line.strip()]

    cleaned = remove_duplicate_urls(urls)

    print("\nURLs without duplicates:")
    for url in cleaned:
        print(url)
