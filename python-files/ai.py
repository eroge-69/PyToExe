import requests
import json

# Function to print the logo
def print_logo():
    logo_text = "HUNTER AI SIGNAL"
    print("\n" + "=" * len(logo_text))  # Print a line based on the logo text length
    print(logo_text)
    print("=" * len(logo_text))  # Print a line based on the logo text length
    print()  # Blank line for separation

# Function to display the available assets
def display_assets():
    print("+-------------------+")
    print("| Available Assets: |")
    print("+-------------------+")
    print("|@monsters_king_1st |")
    print("|    ALLPAIR AI     |")
    print("+-------------------+")

# Function to clean and format the ALLPAIR AI response
def clean_response_text(text):
    text = text.replace("🇧🇷PA～", "").replace("～", "<>")  # Remove 🇧🇷PA and replace '～' with '<>'
    parts = text.split("<>")
    if len(parts) == 4:
        time, pair, action = parts[1], parts[2], parts[3].upper()  # Extract relevant parts
        return f"{time}<> {pair}<> {action}"
    else:
        return text.strip()

# Function to interact with the ALLPAIR AI (Signal Generator)
def allpair_signal_generator():
    # Collecting start and end times from the user
    start_time = input("Enter start time (e.g., 18:46): ").strip()
    end_time = input("Enter end time (e.g., 19:59): ").strip()

    # Comma-separated string of specific pairs
    pairs = ",".join([
        "BRLUSD_otc", "USDPKR_otc", "USDINR_otc", "USDTRY_otc",
        "USDEGP_otc", "USDMXN_otc", "USDBDT_otc", "USDIDR_otc",
        "USDMXN_otc", "USDPHP_otc", "USDCOP_otc", "USDARS_otc"
    ])

    # Fixed parameters for the API request
    days = "7"
    mode = "normal"
    min_percentage = "100"
    filter_value = "1"
    separate = "1"

    # Constructing the API URL
    url = (
        f"https://alltradingapi.com/signal_list_gen/qx_signal.js?"
        f"start_time={start_time}&end_time={end_time}&days={days}"
        f"&pairs={pairs}&mode={mode}&min_percentage={min_percentage}"
        f"&filter={filter_value}&separate={separate}"
    )

    # Making the API request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            print("Request successful.\n")
            try:
                # Attempt to parse the response as JSON
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        print(clean_response_text(str(item)))
                else:
                    print(clean_response_text(str(data)))
            except ValueError:
                # Handle non-JSON response
                print("Response content is not in JSON format.")
                print(clean_response_text(response.text))
        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

# Main function
def main():
    print_logo()  # Print the logo text
    display_assets()  # Display the asset options

    # Get user choice
    choice = input("\nEnter your choice (ALLPAIR AI): ").strip().upper()

    if choice == "ALLPAIR AI":
        allpair_signal_generator()
    else:
        print("Invalid choice. Please enter 'ALLPAIR AI'.")

# Run the main function
if __name__ == "__main__":
    main()