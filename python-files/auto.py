import requests
from bs4 import BeautifulSoup
import re
import csv
import random
from datetime import datetime
import os

# global variables
base_url = "https://hookcoupons.com"

# --- NEW: Login function ---
def login_alldaycoupons(username, password):
    """
    Logs into alldaycoupons.com and returns an authenticated session, or None on failure.
    """
    login_url = f"{base_url}/login"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    try:
        login_page_res = session.get(login_url)
        login_page_res.raise_for_status()
        login_soup = BeautifulSoup(login_page_res.text, 'html.parser')
        login_token = login_soup.find('input', {'name': '_token'})['value']
        login_payload = {
            'username': username,
            'password': password,
            '_token': login_token,
        }
        login_res = session.post(login_url, data=login_payload, headers={'Referer': login_url})
        login_res.raise_for_status()
        if "/login" in login_res.url:
            print("Login failed. Please check your credentials.")
            return None
        print("Login successful!")
        return session
    except Exception as e:
        print(f"Login error: {e}")
        return None

# --- NEW: Create store with existing session ---
def create_store_with_session(session, store_data):
    """
    Uses an authenticated session to create a store.
    """
    create_url = f"{base_url}/backend/store/create"
    save_url = f"{base_url}/backend/store/save"
    try:
        get_response = session.get(create_url)
        get_response.raise_for_status()
        if "/login" in get_response.url:
            raise PermissionError("Access denied to create page. Login may have failed or user lacks permissions.")
        create_soup = BeautifulSoup(get_response.text, 'html.parser')
        create_token_element = create_soup.find('input', {'name': '_token'})
        if not create_token_element:
            raise ValueError("Failed to find CSRF token on the store creation page.")
        create_token = create_token_element['value']
        form_data = store_data.copy()
        form_data['_token'] = create_token
        post_headers = {
            'Referer': create_url,
            'Origin': base_url
        }
        post_response = session.post(save_url, data=form_data, headers=post_headers)
        post_response.raise_for_status()
        return post_response
    except Exception as e:
        print(f"Create store error: {e}")
        return None

# --- NEW: Create offer with existing session ---
def create_offer_with_session(session, offer_data):
    """
    Uses an authenticated session to create an offer.
    
    Args:
        session: An authenticated requests session
        offer_data (dict): Dictionary containing offer form data with keys:
            - name: Offer name
            - offer: Offer description/details  
            - code: Coupon code
            - url: Offer URL
            - store_id: Store ID (numeric)
            - store_name: Store name
            - verified: Whether verified (1 or 0)
            - state: State (1 for active)
    
    Returns:
        requests.Response: The response object from the POST request, or None on failure
    """

    offer_data['description'] = get_random_description_for_deal(offer_data['store_name'])

    create_url = f"{base_url}/backend/offer/create"
    save_url = f"{base_url}/backend/offer/save"
    
    try:
        # Get the create page to extract CSRF token
        print(f"Fetching CSRF token from offer create page: {create_url}")
        get_response = session.get(create_url)
        get_response.raise_for_status()
        
        if "/login" in get_response.url:
            raise PermissionError("Access denied to create page. Login may have failed or user lacks permissions.")
        
        # Extract CSRF token from the form
        create_soup = BeautifulSoup(get_response.text, 'html.parser')
        create_token_element = create_soup.find('input', {'name': '_token'})
        
        if not create_token_element:
            raise ValueError("Failed to find CSRF token on the offer creation page.")
        
        create_token = create_token_element['value']
        print(f"Successfully extracted offer create CSRF Token: {create_token}")
        
        # Prepare form data with CSRF token
        form_data = offer_data.copy()
        form_data['_token'] = create_token
        
        # Set headers for the POST request
        post_headers = {
            'Referer': create_url,
            'Origin': base_url,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Linux"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"Submitting offer creation form to: {save_url}")
        # Note: Using files parameter to send as multipart/form-data like the curl command
        files = {}
        for key, value in form_data.items():
            files[key] = (None, str(value))
        
        post_response = session.post(save_url, files=files, headers=post_headers)
        post_response.raise_for_status()
        
        return post_response
        
    except Exception as e:
        print(f"Create offer error: {e}")
        return None

def create_alldaycoupons_store(username, password, store_data):
    """
    Handles login, CSRF token, and creates a store on alldaycoupons.com.

    This function automates the process of:
    1.  Starting a session and logging into the website.
    2.  Fetching the store creation page to get a valid CSRF token (while authenticated).
    3.  Extracting the CSRF token from the HTML form.
    4.  Submitting the store data along with the valid token to the save endpoint.

    Args:
        username (str): The username or email for logging in.
        password (str): The password for the account.
        store_data (dict): A dictionary containing all the form data for the new store.
                           This dictionary should NOT include the '_token' key.

    Returns:
        requests.Response: The response object from the final POST request, or None on failure.
    """
    # Base URLs for the target site
    login_url = f"{base_url}/login"
    create_url = f"{base_url}/backend/store/create"
    save_url = f"{base_url}/backend/store/save"

    with requests.Session() as session:
        # Set headers that mimic a real browser for the entire session.
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        try:
            # --- STEP 1: LOGIN ---
            print(f"Fetching login page to get CSRF token: {login_url}")
            login_page_res = session.get(login_url)
            login_page_res.raise_for_status()

            # Extract CSRF token from the login form
            login_soup = BeautifulSoup(login_page_res.text, 'html.parser')
            login_token = login_soup.find('input', {'name': '_token'})['value']
            print(f"Extracted login CSRF Token: {login_token}")
            
            # Prepare login payload
            login_payload = {
                'username': username, # Assuming the login field is 'email'
                'password': password,
                '_token': login_token,
            }

            # Send the login request
            print("Submitting login credentials...")
            login_res = session.post(login_url, data=login_payload, headers={'Referer': login_url})
            login_res.raise_for_status()

            # Check if login was successful by looking for a redirect away from /login
            if "/login" in login_res.url:
                raise ValueError("Login failed. Please check your credentials. Redirected back to login page.")
            print("Login successful!")

            # --- STEP 2: CREATE STORE (now authenticated) ---
            print(f"Fetching CSRF token from create page: {create_url}")
            get_response = session.get(create_url)
            get_response.raise_for_status()
            
            if "/login" in get_response.url:
                 raise PermissionError("Access denied to create page. Login may have failed or user lacks permissions.")

            # Extract the '_token' value from the create store form
            create_soup = BeautifulSoup(get_response.text, 'html.parser')
            create_token_element = create_soup.find('input', {'name': '_token'})
            
            if not create_token_element:
                 raise ValueError("Failed to find CSRF token on the store creation page.")
            
            create_token = create_token_element['value']
            print(f"Successfully extracted create store CSRF Token: {create_token}")

            # Prepare the final form data with the new token
            form_data = store_data.copy()
            form_data['_token'] = create_token

            post_headers = {
                'Referer': create_url,
                'Origin': base_url
            }

            print(f"Submitting store creation form to: {save_url}")
            post_response = session.post(save_url, data=form_data, headers=post_headers)
            post_response.raise_for_status()

            return post_response

        except requests.exceptions.RequestException as e:
            print(f"An HTTP request error occurred: {e}")
            return None
        except (ValueError, PermissionError, KeyError) as e:
            print(f"An error occurred: {e}")
            return None

# --- NEW: Function to extract all store IDs and save to CSV ---
def extract_stores_to_csv(session, csv_filename="stores.csv"):
    """
    Extracts all store IDs and names from the offer create page and saves them to a CSV file.
    
    Args:
        session: An authenticated session object
        csv_filename (str): The filename for the CSV file (default: "stores.csv")
    
    Returns:
        bool: True if successful, False otherwise
    """
    offer_create_url = f"{base_url}/backend/offer/create"
    
    try:
        print(f"Fetching offer create page: {offer_create_url}")
        response = session.get(offer_create_url)
        response.raise_for_status()
        
        # Check if we're redirected to login (session expired)
        if "/login" in response.url:
            print("Error: Redirected to login page. Session may have expired.")
            return False
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the store_id select element
        store_select = soup.find('select', {'name': 'store_id', 'id': 'store_id'})
        
        if not store_select:
            print("Error: Could not find store_id select element on the page")
            return False
        
        # Extract all option values and text
        stores = []
        options = store_select.find_all('option')
        
        for option in options:
            store_id = option.get('value')
            store_name = option.get_text(strip=True)
            
            # Skip empty values or placeholder options
            if store_id and store_name and store_id.isdigit():
                stores.append({
                    'store_id': store_id,
                    'store_name': store_name
                })
        
        if not stores:
            print("Warning: No stores found in the select element")
            return False
        
        # Write to CSV file (overwrite if exists)
        print(f"Writing {len(stores)} stores to {csv_filename}")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['store_id', 'store_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write store data
            for store in stores:
                writer.writerow(store)
        
        print(f"Successfully extracted and saved {len(stores)} stores to {csv_filename}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return False
    except Exception as e:
        print(f"Error extracting stores: {e}")
        return False

# --- NEW: Function to extract all store IDs and return as dictionary ---
def extract_stores_to_dict_with_session(session):
    """
    Extracts all store IDs and names from the offer create page and returns them as a dictionary.
    
    Args:
        session: An authenticated session object
    
    Returns:
        dict: Dictionary mapping store names to store IDs, or None on failure
    """
    offer_create_url = f"{base_url}/backend/offer/create"
    
    try:
        print(f"Fetching offer create page: {offer_create_url}")
        response = session.get(offer_create_url)
        response.raise_for_status()
        
        # Check if we're redirected to login (session expired)
        if "/login" in response.url:
            print("Error: Redirected to login page. Session may have expired.")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the store_id select element
        store_select = soup.find('select', {'name': 'store_id', 'id': 'store_id'})
        
        if not store_select:
            print("Error: Could not find store_id select element on the page")
            return None
        
        # Extract all option values and text into dictionary
        stores_dict = {}
        options = store_select.find_all('option')
        
        for option in options:
            store_id = option.get('value')
            store_name = option.get_text(strip=True)
            
            # Skip empty values or placeholder options
            if store_id and store_name and store_id.isdigit():
                stores_dict[store_name] = store_id
        
        if not stores_dict:
            print("Warning: No stores found in the select element")
            return None
        
        print(f"Successfully extracted {len(stores_dict)} stores")
        
        return stores_dict
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None
    except Exception as e:
        print(f"Error extracting stores: {e}")
        return None

# --- NEW: Convenience function to login and extract stores ---
def extract_all_stores_to_csv(username, password, csv_filename="stores.csv"):
    """
    Complete function to login and extract all stores to CSV file.
    
    Args:
        username (str): Login username
        password (str): Login password
        csv_filename (str): Output CSV filename (default: "stores.csv")
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Logging in to extract stores...")
    session = login_alldaycoupons(username, password)
    
    if not session:
        print("Failed to login. Cannot extract stores.")
        return False
    
    return extract_stores_to_csv(session, csv_filename)

# --- NEW: Convenience function to login and extract stores as dictionary ---
def extract_all_stores_to_dict(username, password):
    """
    Complete function to login and extract all stores as a dictionary.
    
    Args:
        username (str): Login username
        password (str): Login password
    
    Returns:
        dict: Dictionary mapping store names to store IDs, or None on failure
    """
    print("Logging in to extract stores...")
    session = login_alldaycoupons(username, password)
    
    if not session:
        print("Failed to login. Cannot extract stores.")
        return None
    
    return extract_stores_to_dict_with_session(session)

def extract_categories_to_dict_with_session(session):
    """
    Extracts all category IDs and names from the store create page and returns them as a dictionary.
    
    Args:
        session: An authenticated session object
    
    Returns:
        dict: Dictionary mapping category names to category IDs, or None on failure
    """
    store_create_url = f"{base_url}/backend/store/create"
    
    try:
        print(f"Fetching store create page: {store_create_url}")
        response = session.get(store_create_url)
        response.raise_for_status()
        
        # Check if we're redirected to login (session expired)
        if "/login" in response.url:
            print("Error: Redirected to login page. Session may have expired.")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the cat_id select element
        cat_select = soup.find('select', {'id': 'cat_id'})
        
        if not cat_select:
            print("Error: Could not find cat_id select element on the page")
            return None
        
        # Extract all option values and text into dictionary
        categories_dict = {}
        options = cat_select.find_all('option')
        
        for option in options:
            cat_id = option.get('value')
            cat_name = option.get_text(strip=True)
            
            # Skip empty values or placeholder options
            if cat_id and cat_name and cat_id.isdigit():
                categories_dict[cat_name] = cat_id
        
        if not categories_dict:
            print("Warning: No categories found in the select element")
            return None
        
        print(f"Successfully extracted {len(categories_dict)} categories")
        
        return categories_dict
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None
    except Exception as e:
        print(f"Error extracting categories: {e}")
        return None

# --- NEW: Convenience function to login and extract categories as dictionary ---
def extract_all_categories_to_dict(username, password):
    """
    Complete function to login and extract all categories as a dictionary.
    
    Args:
        username (str): Login username
        password (str): Login password
    
    Returns:
        dict: Dictionary mapping category names to category IDs, or None on failure
    """
    print("Logging in to extract categories...")
    session = login_alldaycoupons(username, password)
    
    if not session:
        print("Failed to login. Cannot extract categories.")
        return None
    
    return extract_categories_to_dict_with_session(session)

# --- NEW: Convenience function to create offer with login ---
def create_alldaycoupons_offer(username, password, offer_data):
    """
    Complete function to login and create an offer.
    
    Args:
        username (str): Login username
        password (str): Login password
        offer_data (dict): Dictionary containing offer form data
    
    Returns:
        requests.Response: The response object from the POST request, or None on failure
    """
    session = login_alldaycoupons(username, password)
    
    if not session:
        print("Failed to login. Cannot create offer.")
        return None
    
    return create_offer_with_session(session, offer_data)

# return random description from the list and replace %Store Name% with store name
def get_random_description_for_deal(store_name):
    descriptions = [
        "Don't miss out! For today time only, you can enjoy huge price discounts with this %Store Name% coupon.",
        "Discover difference discounts now! This %Store Name% coupon are yours only if you want it.",
        "These must-have items won't last long. Don't eye this %Store Name% coupon any longer.",
        "It's the best way to buy anything at the discounted price! Don't miss this opportunity to get this top %Store Name% coupon.",
        "Nothing feel as good as when you check out! Use this %Store Name% coupon when you shop at this store this spring and get deep discount.",
        "What are you waiting for? Don't miss this %Store Name% coupon or you will regret.",
        "Experience major savings with this great deal at %Store Name%! Snatch up your savings before they are gone.",
        "Get yours now! You will only find the best %Store Name% coupon here!",
        "Let's use this %Store Name% coupon at checkout to save off. Don't hesitate any more!",
        "Excellent savings at %Store Name%. Look no further than here for the most amazing deals.",
        "Spend much less on your dream items when you shop at %Store Name%. Grab the garbain before it's gone.",
        "Such quality and price are hard to come by! Great chance to save money with this %Store Name% coupon.",
        "More of what you want, less of what you don't. Your bargain is waiting at %Store Name%.",
        "We know you don't want to miss any discounts from %Store Name%! Make your purchase now with this %Store Name% coupon.",
        "Apply %Store Name% hot coupon to your order and save. Great bargains begin here.",
        "Get it immediately, instead of regret later! Take this %Store Name% coupon before the amazing deals end!",
        "%Store Name% is offering goods at a much cheaper price than its competitors. Your gateway to a great shopping experience.",
        "Don't miss this chance to save money with %Store Name% coupon code.",
        "Enjoy incredible discounts from %Store Name% on all your favorite items. Savings you can see.",
        "Enter %Store Name% coupon to your order and save. Must have it? We've got it.",
        "Great chance to save money at %Store Name% because sale season is here. Time to go shopping!",
        "You have a chance to be the first who save money with this %Store Name% coupon! Go ahead and shop!",
        "Your place to shop and discover amazing deals! You will only find the best %Store Name% coupon here!",
        "Excellent savings at %Store Name% A great place to be if you want a bargain.",
        "Beat the crowd and start saving. Make your purchase today using this %Store Name% coupon.",
        "Choose your favorite products at %Store Name% and save money. Check-out to close your deal at this shop.",
        "%Store Name% is now offering great discounts! Come and check it out. We only help you find the best bargains.",
        "Enjoy incredible discounts from %Store Name% on all your favorite items. For a limited time only.",
        "Don't miss out! For today time only, you can enjoy huge price discounts with this %Store Name% coupon.",
        "Discover difference discounts now! This %Store Name% coupon are yours only if you want it.",
        "These must-have items won't last long. Don't eye this %Store Name% coupon any longer.",
        "It's the best way to buy anything at the discounted price! Don't miss this opportunity to get this top %Store Name% coupon.",
        "Nothing feel as good as when you check out! Use this %Store Name% coupon when you shop at this store this spring and get deep discount."
    ]
    return random.choice(descriptions).replace("%Store Name%", store_name)

# get random 3 faqs from the list -> replace %Store Name% with store name and concatenate them
def random_faqs(store_name):
    faqs = [
        """
        <tr>
            <td>Q: What if the %Store Name% promo code or deal is unvalid?
            A: It may be that the applicable time of %Store Name% for that promo code goes to the end. Please select another option to save and be quick next time.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Why can’t I use a promo code for my purchase at %Store Name%?
            A: The %Store Name% promo code will have a date and be used for eligible items. Make sure your code is valid and hasn’t expired yet.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How many items can I include with a %Store Name% discount code?
            A: Usually, %Store Name% doesn’t limit the number of items customers have to buy to enjoy discounts. However, they will lay down conditions on the value of your order to be eligible for applying discount codes of %Store Name%.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can a %Store Name% coupon code be added later if I forget to apply it at checkout?
            A: No, it can’t. If you forget to apply a %Store Name% coupon code at checkout, you cannot do it later. The only way not to miss it is to redeem it to another order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: What conditions are required to get free shipping for %Store Name% order?
            A: The condition for getting %Store Name% free shipping is described on the offer description. If the value of your order is at least equal to the required value, you can enjoy free shipping.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can I give my %Store Name% exclusive code to someone else?
            A: If %Store Name% requires you to provide email at checkout to use the exclusive code, you cannot give it to another. Check how many orders the coupon code can be applied and plan to save.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to know if the %Store Name% coupon discount was deducted from my purchase?
            A: When you apply the coupon or promo code into the discount field at %Store Name%, the discount will be promptly deducted from your purchase. You will see both the amount of discount and the price after being discounted before clicking to finish the order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to know if an item of %Store Name% is eligible for a coupon?
            A: Each option of %Store Name% coupons or deals comes with a detailed description for eligible items and the discount rate. Pick the right choice for your order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Does %Store Name% have coupons available every day?
            A: No. %Store Name% can offer many coupons but not every day. But, if you are a loyal customer, you can have your own award for each time of shopping.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Why don’t I see %Store Name%’s discount code field at Checkout?
            A: There are two main cases making it happen, which are unapplicable payment method and the discount code field containing in your cart at %Store Name%.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to get %Store Name% free shipping offer?
            A: Check %Store Name% coupons at Greatsreview86 to find a deal of free shipping. Learn the condition for using the offer to make sure your order can meet it.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: What types of %Store Name% discount codes are there?
            A: %Store Name% discount codes fall into 4 main types including percentage offer, delivery offer, free item and more if updated. Customers will choose the option that enables them to save at best.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can you give me a guide for using %Store Name% coupon codes?
            A: Follow the guide below to score %Store Name% coupon: - Copy the coupon code that fits your order. - Navigate to %Store Name% and add your favorite items into the cart. - Apply code at checkout and enjoy saving.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Why can’t I use a promo code for my purchase at %Store Name%?
            A: The %Store Name% promo code will have a date and be used for eligible items. Make sure your code is valid and hasn’t expired yet.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can a %Store Name% coupon code be added later if I forget to apply it at checkout?
            A: No, it can’t. If you forget to apply a %Store Name% coupon code at checkout, you cannot do it later. The only way not to miss it is to redeem it to another order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Does %Store Name% provide free delivery?
            A: The offer of free delivery for %Store Name% order is not available all the time or only available for selected products. Once a deal exists, you can find it on Greatsreview86.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can I submit to Greatsreview86 a %Store Name% coupon code?
            A: We appreciate all contributions from both users and partners. Reach out to us at 'Contact Us' for %Store Name% coupon submission.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to know if an item of %Store Name% is eligible for a coupon?
            A: Each option of %Store Name% coupons or deals comes with a detailed description for eligible items and the discount rate. Pick the right choice for your order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: What is currently the best coupon of %Store Name%?
            A: As of the latest update, the best coupon of %Store Name% can give customers a discount corresponding to half of their purchase.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How many items can I include with a %Store Name% discount code?
            A: Usually, %Store Name% doesn’t limit the number of items customers have to buy to enjoy discounts. However, they will lay down conditions on the value of your order to be eligible for applying discount codes of %Store Name%.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Why should I visit Greatsreview86 for %Store Name% coupons?
            A: Greatsreview86 collects the top discounts from %Store Name%, even at the last minute while updating continually to ensure consumer savings. Coupons, promo codes, gift cards and many more can also be found on the website.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Where to find %Store Name% promo codes?
            A: Right on the website of %Store Name% or join Greatsreview86 for more options of %Store Name% promo codes.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Will all %Store Name% discounts automatically be applied at checkout?
            A: No. It depends on each %Store Name% deal. Some require you to apply a code at discount field while some are applied automatically.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can you give me a guide for using %Store Name% coupon codes?
            A: Follow the guide below to score %Store Name% coupon: - Copy the coupon code that fits your order. - Navigate to %Store Name% and add your favorite items into the cart. - Apply code at checkout and enjoy saving.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Are there any %Store Name% Gift Cards available?
            A: If a %Store Name% Gift Card is available, it will be aggregated above. Let’s check!</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to use %Store Name% coupon code?
            A: Visit %Store Name% on Greatsreview86 and pick the coupon making your order the biggest saving. Click GET CODE or GET DEAL for code displaying and enjoy the discount.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How often does %Store Name% release a new coupon?
            A: For normal days, there is no specific frequency for %Store Name% coupon releasing, but it tends to give out once per month. On the peak times of shopping, deals and discounts will be constantly launched and much bigger.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to know if an item of %Store Name% is eligible for a coupon?
            A: Each option of %Store Name% coupons or deals comes with a detailed description for eligible items and the discount rate. Pick the right choice for your order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How long are %Store Name% deals valid?
            A: %Store Name% will announce how long their promotional program will last. %Store Name% deals will also be valid within that period of time.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How are errors about %Store Name% coupons reported?
            A: Let us know at 'Contact Us'. Describe your problems and the errors about %Store Name% coupons in detail, we will solve it as soon as possible.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: When to use %Store Name% coupons to save at best?
            A: Go to %Store Name% and find the time that coupon is applicable. Huge discounts and deals tend to be available in a short period of time, requiring buyers to hurry. Be ready at that time to save at best.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to get %Store Name% free shipping offer?
            A: Check %Store Name% coupons at Greatsreview86 to find a deal of free shipping. Learn the condition for using the offer to make sure your order can meet it.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Who to contact if I am having trouble using a %Store Name% coupon?
            A: That %Store Name% coupon may expire at that moment. Shopping at %Store Name% and then contact its owner to let them know your issue.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Can you give me a guide for using %Store Name% coupon codes?
            A: Follow the guide below to score %Store Name% coupon: - Copy the coupon code that fits your order. - Navigate to %Store Name% and add your favorite items into the cart. - Apply code at checkout and enjoy saving.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: What is currently the best coupon of %Store Name%?
            A: As of the latest update, the best coupon of %Store Name% can give customers a discount corresponding to half of their purchase.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How do I find %Store Name% coupons?
            A: Visiting the website of %Store Name% regularly or checking %Store Name% coupons on Greatsreview86 is the best and easiest way to score a discount.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How to know if the %Store Name% coupon discount was deducted from my purchase?
            A: When you apply the coupon or promo code into the discount field at %Store Name%, the discount will be promptly deducted from your purchase. You will see both the amount of discount and the price after being discounted before clicking to finish the order.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Does %Store Name% have a loyalty program?
            A: The loyalty program of %Store Name% will be applicable for regular customers. Thereby, they can redeem %Store Name% awards for promotions, coupons and special sales.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: Does a sitewide coupon of %Store Name% exist?
            A: If %Store Name% makes available a sitewide coupon, it will be gathered above. Let's have a look!</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How many items can I include with a %Store Name% discount code
            A: Usually, %Store Name% doesn’t limit the number of items customers have to buy to enjoy discounts. However, they will lay down conditions on the value of your order to be eligible for applying discount codes of %Store Name%.</td>
        </tr>
        """,
        """
        <tr>
            <td>Q: How many items can I include with a %Store Name% discount code
            A: Usually, %Store Name% doesn’t limit the number of items customers have to buy to enjoy discounts. However, they will lay down conditions on the value of your order to be eligible for applying discount codes of %Store Name%.</td>
        </tr>
        """,
        ]

    # get random 3 unique faqs
    faqs = random.sample(faqs, 7)
    rs = """
            <table border="1" cellpadding="0" cellspacing="0" dir="ltr">
            <tbody>
        """
    for faq in faqs:
        rs += faq.replace("%Store Name%", store_name)
    rs += """
	</tbody>
	</table>
	"""
    return rs

def get_random_description_for_store(store_name):
    descriptions = [
        "Don't miss out! For today time only, you can enjoy huge price discounts with this %Store Name% coupon.",
        "Discover difference discounts now! This %Store Name% coupon are yours only if you want it.",
        "These must-have items won't last long. Don't eye this %Store Name% coupon any longer.",
        "It's the best way to buy anything at the discounted price! Don't miss this opportunity to get this top %Store Name% coupon.",
        "Nothing feel as good as when you check out! Use this %Store Name% coupon when you shop at this store this spring and get deep discount.",
        "What are you waiting for? Don't miss this %Store Name% coupon or you will regret.",
        "Experience major savings with this great deal at %Store Name%! Snatch up your savings before they are gone.",
        "Get yours now! You will only find the best %Store Name% coupon here!",
        "Let's use this %Store Name% coupon at checkout to save off. Don't hesitate any more!",
        "Excellent savings at %Store Name%. Look no further than here for the most amazing deals.",
        "Spend much less on your dream items when you shop at %Store Name%. Grab the garbain before it's gone."
    ]
    return random.choice(descriptions).replace("%Store Name%", store_name)

def generate_how_to_apply(store_name):
    how_to_apply_pattern = """
        <p>How to apply %Store Name% coupon codes?<br />
        Step1: Find your %Store Name% Coupons, discount codes on this page or Greatsreview86 and click &quot;GET CODE&quot; button to view the code, then click &quot;Copy&quot; and the coupons, discount codes will be copied to your phone&#39;s or computer&#39;s clipboard.<br />
        Step2: Go to %Store Name% then select all items you want to buy and add to shopping cart. When finished shopping, go to the %Store Name% checkout page.<br />
        Step3: During checkout, find the text &quot;Promo Code&quot; or &quot;Discount Code&quot; and paste your %Store Name% coupons, discount codes in step 1 to this box. Click &quot;Apply&quot; and your savings for %Store Name% will be applied.</p>
    """
    return how_to_apply_pattern.replace("%Store Name%", store_name)

if __name__ == '__main__':
    # LOGIN_USERNAME = "admin"
    # LOGIN_PASSWORD = "Lan789!@#"
    # csv_store_filename = "store.csv"
    # csv_offer_filename = "offer.csv"

    # update global variable base_url
    # "https://hookcoupons.com/"

      # Get login credentials and CSV filename from user input
    print("=== Auto Post Setup ===")
    LOGIN_USERNAME = input("Enter your username: ").strip()
    LOGIN_PASSWORD = input("Enter your password: ").strip()
    csv_offer_filename = input("Enter CSV file path (e.g., offer.csv): ").strip()
    csv_store_filename = input("Enter CSV filen path(e.g., store.csv): ").strip()
    base_url = input("Enter your base url: ").strip()

    # Validate inputs
    if not LOGIN_USERNAME or not LOGIN_PASSWORD or not csv_offer_filename or not csv_store_filename:
        print("Error: All fields are required!")
        exit(1)

    print(f"\nUsing credentials for user: {LOGIN_USERNAME}")
    print(f"Using CSV file: {csv_offer_filename}")
    print(f"Using CSV file: {csv_store_filename}")
    print("=" * 50)


    # Login once
    session = login_alldaycoupons(LOGIN_USERNAME, LOGIN_PASSWORD)
    categories_dict = extract_all_categories_to_dict(LOGIN_USERNAME, LOGIN_PASSWORD)

    # Read stores from CSV file
    stores_to_create = []
    try:
        print(f"Reading stores from {csv_store_filename}...")
        with open(csv_store_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                store_name = row["Store Name"].strip()
                store_url = row["URL"].strip()
                about_store = row["About Store"].strip()
                category = row["Category"].strip()

                # get category id from categories_dict
                category_id = categories_dict.get(category)
                if not category_id:
                    print(f"Warning: Category '{category}' not found in categories dictionary")
                    category_id="18"
                
                # Create slug: Store Name to lower case and replace space with "_"
                slug = store_name.lower().replace(" ", "_")
                
                store = {
                    "name": store_name,                                        # name: Store Name
                    "store_url": store_url,                                    # store_url: URL
                    "slug": slug,                                              # slug: Store Name to lower case and replace space with "_"
                    "event_id": "0",                                           # event_id: always 0
                    "cat_id": category_id,                                           # cat_id: Category ID
                    "image": "",                                               # image: empty
                    "logo_url": f"/uploads/images/{store_name}.jpg",           # logo_url: /uploads/images/%store name%.jpg
                    "state": "1",                                              # state: always 1 (required for store creation)
                    "description": get_random_description_for_store(store_name), # description: using function get_random_description_for_store
                    "about_store": about_store,                                # about_store: About Store
                    "how_to_apply": generate_how_to_apply(store_name),         # how_to_apply: using generate_how_to_apply function
                    "faqs": random_faqs(store_name),                            # faqs: using randomfaqs function
                    "meta_title": "",                                          # meta_title: empty
                    "meta_keys": "",                                           # meta_keys: empty
                    "meta_des": ""                                             # meta_des: empty
                }
                stores_to_create.append(store)
        
        print(f"Successfully loaded {len(stores_to_create)} stores from CSV")
        
    except FileNotFoundError:
        print(f"Error: {csv_store_filename} file not found!")
        stores_to_create = []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        stores_to_create = []


    # help me to create a new csv file with name "store_link_DDMMYYYY.csv"
    # the file will have 2 columns: "Store Name" and "URL"
    # the "Store Name" will be the name of the store
    # the "URL" will be the url of the store: base domain + /store/ + slug
    # the file will be created in the same directory as the running exe file
    # create a new csv file with name "store_link_timestamp.csv"
    # get current timestamp
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    store_link_filename = f"store_link_{current_timestamp}.csv"

    # write the data to the csv file
    with open(store_link_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Store Name", "URL"])
        writer.writeheader()
        for store in stores_to_create:
            store_url = f"{base_url}/store/{store['slug']}"
            writer.writerow({"Store Name": store["name"], "URL": store_url})


    # Create stores using the session
    if session and stores_to_create:
        print(f"\n=== CREATING {len(stores_to_create)} STORES ===")
        for idx, store_payload in enumerate(stores_to_create, 1):
            print(f"\n--- Creating store {idx}: {store_payload['name']} ---")
            response = create_store_with_session(session, store_payload)
            if response:
                print(f"Status Code: {response.status_code}")
                print("Final Response URL:", response.url)
                if "/login" in response.url:
                    print("Result: Failed. Redirected to login page unexpectedly.")
                elif "backend/store" in response.url:
                    print("Result: Success! Store likely created.")
                else:
                    print("Result: Request processed. Check response.")
            else:
                print("Failed to create store.")
    elif not session:
        print("No active session available for creating stores.")
    elif not stores_to_create:
        print("No stores available to create.")


    stores_dict = extract_stores_to_dict_with_session(session)

    # --- Creating offers ---
    offers_to_create = []    
    try:
        print(f"Reading offers from {csv_offer_filename}...")
        with open(csv_offer_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                offer = {
                    "name": row["Offer"],           # name: Offer
                    "offer": row["Offer"],          # offer: Offer  
                    "code": row["Code"],            # code: Code
                    "url": row["Link"],             # url: Link
                    "store_name": row["Store Name"], # store_name: Store Name (will be converted to store_id)
                    "verified": "1",                # verified: always 1
                    "state": "1"                    # state: always 1
                    # description will be added by create_offer_with_session function
                }
                offers_to_create.append(offer)
        
        print(f"Successfully loaded {len(offers_to_create)} offers from CSV")
        
    except FileNotFoundError:
        print(f"Error: {csv_offer_filename} file not found!")
        offers_to_create = []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        offers_to_create = []

    # Convert store_name to store_id using the stores dictionary
    for offer in offers_to_create:
        if offer['store_name'] in stores_dict:
            offer['store_id'] = stores_dict[offer['store_name']]
        else:
            print(f"Warning: Store '{offer['store_name']}' not found in stores dictionary")
            offer['store_id'] = None  # This will likely cause the offer creation to fail

    # Filter out offers with invalid store_ids
    valid_offers = [offer for offer in offers_to_create if offer['store_id'] is not None]
    invalid_count = len(offers_to_create) - len(valid_offers)
    
    if invalid_count > 0:
        print(f"Skipping {invalid_count} offers with invalid store names")
    
    offers_to_create = valid_offers
    
    if not offers_to_create:
        print("No valid offers to create!")
    else:
        print(f"Ready to create {len(offers_to_create)} offers")
    
    # Create offers using the same session or login again
    if session and offers_to_create:
        for idx, offer_payload in enumerate(offers_to_create, 1):
            print(f"\n--- Creating offer {idx}: {offer_payload['name']} ---")
            response = create_offer_with_session(session, offer_payload)
            if response:
                print(f"Status Code: {response.status_code}")
                print("Final Response URL:", response.url)
                if "/login" in response.url:
                    print("Result: Failed. Redirected to login page unexpectedly.")
                elif "backend/offer" in response.url:
                    print("Result: Success! Offer likely created.")
                else:
                    print("Result: Request processed. Check response.")
            else:
                print("Failed to create offer.")
    elif not session:
        print("No active session available for creating offers.")
    elif not offers_to_create:
        print("No offers available to create.")

    # print location of csv file 
    print(f"Store link file created in {os.path.abspath(store_link_filename)}")

    #  wait for user press enter to exit
    input("Press Enter to exit...")