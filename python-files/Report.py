import httpx

# URL for fetching incident categories
url_categories = "https://www.clubhouseapi.com/api/get_incident_categories"
# Manual token for getting categories
manual_token = "b69c02565ed92add34e4205fd33fd1e410071205"


# Read tokens from the file 'tokens.txt' for creating incidents
def read_tokens_from_file(filename="tokens.txt"):
    tokens = []
    try:
        with open(filename, "r") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
            if not tokens:
                print(f"No tokens found in {filename}.")
            return tokens
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []


data = {
    "target": "channel_topic"  # Ensure this is the correct format
}


def fetch_categories():
    with httpx.Client() as client:
        try:
            headers = {"Authorization": f"Token {manual_token}"}
            response = client.post(url_categories, headers=headers, json=data)
            if response.status_code == 200:
                categories = response.json().get("categories", [])
                if categories:
                    print("Available categories:")
                    for i, category in enumerate(categories):
                        label = category.get("label", "N/A")
                        slug = category.get("slug", "N/A")
                        print(f"Category {i + 1}: {label}")
                    return categories
                else:
                    print("No categories found.")
            else:
                print(f"Request failed with status code: {response.status_code}")
                print(response.text)
        except httpx.RequestError as e:
            print(f"An error occurred while making the request: {e}")
    return []



def read_description_from_file(filename="Description.txt"):
    try:
        with open(filename, "r") as file:
            description = file.read().strip()
            if description:
                return description
            else:
                return "No description provided."
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return "No description provided."


def create_incident(selected_slug, reported_channel, description, tokens):
    url_create_incident = "https://www.clubhouseapi.com/api/create_incident"
    headers_create_incident_base = {
        "Sentry-Trace": "b1ca423221ad4b0fafeb481a1302e1aa-d425585715e24d5f",
        "Baggage": "sentry-environment=production,sentry-public_key=18e5c150252f4e3c877f62705ac96471,sentry-release=com.clubhouse.app%4024.11.07%2B1033404,sentry-trace_id=b1ca423221ad4b0fafeb481a1302e1aa"
    }

    data_create_incident = {
        "time_to_complete_form_ms": 8990,
        "category": selected_slug,  # Using the slug of the selected category
        "description": description,  # Provided description
        "reported_channel": reported_channel,  # Manually entered reported channel
        "target": "channel_topic"
    }

    # Loop through each token and make a request for each
    for token in tokens:
        if not token.strip():
            print("Skipping empty token.")
            continue

        # Make sure to include the 'Token ' prefix if required by the API
        if not token.startswith("Token "):
            token = f"Token {token}"

        headers_create_incident = headers_create_incident_base.copy()
        headers_create_incident["Authorization"] = token

        # Debugging: Print the headers to verify they are being sent correctly
        print(f"Sending request with token: {token}")

        try:
            response = httpx.post(url_create_incident, headers=headers_create_incident, json=data_create_incident)
            if response.status_code == 200:
                print(f"Incident created successfully with token {token}!")
                print(response.json())  # Print response to verify successful creation
            else:
                print(f"Request failed with status code: {response.status_code} using token {token}")
                print(response.text)
        except httpx.RequestError as e:
            print(f"An error occurred while making the request with token {token}: {e}")


categories = fetch_categories()

if categories:
    try:
        selection = int(input(f"Select a category (1-{len(categories)}): ")) - 1
        if 0 <= selection < len(categories):
            selected_category = categories[selection]
            selected_slug = selected_category.get("slug", "N/A")
            print(f"Selected Category Slug: {selected_slug}")

            room_url = input('Enter room link: ')
            start = room_url.find('room/') + len('room/')
            end = room_url.find('?utm') if '?utm' in room_url else len(room_url)
            channel_id = room_url[start:end]
            while True:
                reported_channel = channel_id
                if reported_channel:
                    break
                else:
                    print("Invalid reported_channel ID. Please try again.")

            description = read_description_from_file()
            print(f"Using description: {description}")
            tokens = read_tokens_from_file()
            if tokens:
                create_incident(selected_slug, reported_channel, description, tokens)
            else:
                print("No tokens available. Incident not created.")
        else:
            print(f"Invalid selection. Please choose a number between 1 and {len(categories)}")
    except ValueError:
        print("Invalid input. Please enter a valid number.")
