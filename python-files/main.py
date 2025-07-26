# Instagram Following Scraper - The Brand Erector Edition
# NOTE: This is a simplified placeholder. Real scraping requires Instagram API or automation (e.g., Selenium).

def scrape_followings(username):
    print(f"Scraping followings for: {username}")
    # Simulated output
    return [
        {"username": "user1", "name": "User One", "email": "user1@example.com", "phone": "+1234567890"},
        {"username": "user2", "name": "User Two", "email": "user2@example.com", "phone": "+0987654321"}
    ]

if __name__ == "__main__":
    user = input("Enter Instagram username: ")
    data = scrape_followings(user)
    for entry in data:
        print(entry)
