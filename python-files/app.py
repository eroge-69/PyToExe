import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import random
from pathlib import Path

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Sign In'
if 'new_place' not in st.session_state:
    st.session_state.new_place = {'name': '', 'lat': '', 'lng': '', 'description': ''}

# File-based persistence
USER_FILE = 'users.json'
LOCATION_FILE = 'locations.json'

def load_data(file_path, default=[]):
    if Path(file_path).exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return default

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Load initial data
users = load_data(USER_FILE)
locations = load_data(LOCATION_FILE)

# Custom CSS for uiverse.io-inspired styling
st.markdown("""
    <style>
    .stApp { background: #f0f0f0; }
    .geocache-green { background: #3B7A57; }
    .geocache-green:hover { background: #2E5E44; }
    .uiverse-button {
        position: relative; background: #3B7A57; color: white; padding: 0.8em 1.8em; border: none; border-radius: 25px;
        font-weight: 600; font-size: 1em; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(59, 122, 87, 0.3);
        width: 100%; text-align: center; display: inline-block;
    }
    .uiverse-button:hover { background: #2E5E44; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(46, 94, 68, 0.4); }
    .uiverse-input {
        width: 100%; padding: 12px; border: 2px solid #3B7A57; border-radius: 8px; font-size: 1em; transition: all 0.3s ease; background: white;
    }
    .uiverse-input:focus { border-color: #2E5E44; box-shadow: 0 0 8px rgba(46, 94, 68, 0.3); outline: none; }
    .uiverse-textarea {
        width: 100%; padding: 12px; border: 2px solid #3B7A57; border-radius: 8px; font-size: 1em; min-height: 100px; resize: vertical;
    }
    .uiverse-textarea:focus { border-color: #2E5E44; box-shadow: 0 0 8px rgba(46, 94, 68, 0.3); outline: none; }
    .uiverse-link { color: #3B7A57; text-decoration: none; }
    .uiverse-link:hover { text-decoration: underline; }
    .card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
    .nav-container { background: #3B7A57; color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
    .map-container { height: 400px; margin-bottom: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# Sign In
def sign_in():
    st.markdown('<h1 class="card text-2xl font-bold text-center text-gray-800 mb-6">Sign In</h1>', unsafe_allow_html=True)
    email = st.text_input('Email', key='signin_email', help='Enter your email', placeholder='Email', value='', 
                          extra_attrs={'class': 'uiverse-input'})
    password = st.text_input('Password', type='password', key='signin_password', help='Enter your password', 
                             placeholder='Password', value='', extra_attrs={'class': 'uiverse-input'})
    
    if st.button('Sign In', key='signin_button', help='Click to sign in', extra_attrs={'class': 'uiverse-button'}):
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)
        if user:
            st.session_state.user = user
            st.session_state.active_tab = 'Map'
            st.experimental_rerun()
        else:
            st.error('Invalid credentials')
    
    st.markdown('<p class="text-center mt-4">Don\'t have an account? <a href="#" class="uiverse-link" onclick="st.session_state.active_tab=\'Sign Up\';st.experimental_rerun()">Sign Up</a></p>', 
                unsafe_allow_html=True)

# Sign Up
def sign_up():
    st.markdown('<h1 class="card text-2xl font-bold text-center text-gray-800 mb-6">Sign Up</h1>', unsafe_allow_html=True)
    username = st.text_input('Username', key='signup_username', help='Choose a username', placeholder='Username', 
                             value='', extra_attrs={'class': 'uiverse-input'})
    email = st.text_input('Email', key='signup_email', help='Enter your email', placeholder='Email', 
                          value='', extra_attrs={'class': 'uiverse-input'})
    password = st.text_input('Password', type='password', key='signup_password', help='Choose a password', 
                             placeholder='Password', value='', extra_attrs={'class': 'uiverse-input'})
    
    if st.button('Sign Up', key='signup_button', help='Click to sign up', extra_attrs={'class': 'uiverse-button'}):
        if not (email and password and username):
            st.error('Please fill in all fields')
        elif any(u['email'] == email for u in users):
            st.error('Email already exists')
        else:
            new_user = {'email': email, 'username': username, 'password': password, 'points': 0}
            users.append(new_user)
            save_data(USER_FILE, users)
            st.session_state.user = new_user
            st.session_state.active_tab = 'Map'
            st.experimental_rerun()
    
    st.markdown('<p class="text-center mt-4">Already have an account? <a href="#" class="uiverse-link" onclick="st.session_state.active_tab=\'Sign In\';st.experimental_rerun()">Sign In</a></p>', 
                unsafe_allow_html=True)

# Main Page
def main_page():
    st.markdown(f'<div class="nav-container"><h1 class="text-xl font-bold">Abandoned Explorer</h1><div><span class="mr-4">Welcome, {st.session_state.user["username"]} ({st.session_state.user["points"]} Points)</span><button class="uiverse-button" onclick="st.session_state.user=null;st.session_state.active_tab=\'Sign In\';st.experimental_rerun()">Sign Out</button></div></div>', 
                unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(['Map', 'Shop'])
    
    with tabs[0]:  # Map Tab
        # Initialize map
        m = folium.Map(location=[51.505, -0.09], zoom_start=13)
        folium.TileLayer('openstreetmap').add_to(m)
        
        # Try to get user location
        try:
            # Simulate geolocation (Streamlit runs server-side, so we can't use navigator.geolocation)
            user_location = [51.505, -0.09]  # Default to London
            folium.Marker(user_location, popup='You are here!', icon=folium.Icon(color='blue')).add_to(m)
            m.location = user_location
        except:
            st.warning('Unable to get location')

        # Add existing locations
        for loc in locations:
            popup_content = f"""
                <div>
                    <b>{loc['name']}</b><br>
                    {loc['description']}<br>
                    Status: {loc['status']}<br>
                    Discovered by: {loc['discoverer']}<br>
                    {('<b>2x Points!</b><br>' if loc['multiplier'] else '')}
                    <button id="exists-{loc['id']}" class="bg-green-500 text-white px-2 py-1 rounded mr-2">Still There</button>
                    <button id="gone-{loc['id']}" class="bg-red-500 text-white px-2 py-1 rounded">Not There</button>
                </div>
            """
            folium.Marker([loc['lat'], loc['lng']], popup=popup_content).add_to(m)

        # Map rendering and click handling
        map_data = st_folium(m, width='100%', height=400, key='map')
        
        if map_data.get('last_clicked'):
            st.session_state.new_place['lat'] = str(map_data['last_clicked']['lat'])
            st.session_state.new_place['lng'] = str(map_data['last_clicked']['lng'])

        # Add New Place
        st.markdown('<div class="card"><h2 class="text-xl font-semibold mb-4 text-gray-800">Add New Abandoned Place</h2></div>', 
                    unsafe_allow_html=True)
        st.session_state.new_place['name'] = st.text_input('Place Name', value=st.session_state.new_place['name'], 
                                                          key='place_name', extra_attrs={'class': 'uiverse-input'})
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.new_place['lat'] = st.text_input('Latitude (click map to set)', 
                                                             value=st.session_state.new_place['lat'], 
                                                             key='place_lat', extra_attrs={'class': 'uiverse-input'})
        with col2:
            st.session_state.new_place['lng'] = st.text_input('Longitude (click map to set)', 
                                                             value=st.session_state.new_place['lng'], 
                                                             key='place_lng', extra_attrs={'class': 'uiverse-input'})
        st.session_state.new_place['description'] = st.text_area('Description', 
                                                                value=st.session_state.new_place['description'], 
                                                                key='place_description', extra_attrs={'class': 'uiverse-textarea'})
        
        if st.button('Add Location', key='add_location', extra_attrs={'class': 'uiverse-button'}):
            if not (st.session_state.new_place['name'] and st.session_state.new_place['lat'] and st.session_state.new_place['lng']):
                st.error('Please fill in all fields')
            else:
                new_id = max([loc['id'] for loc in locations], default=0) + 1
                multiplier = random.random() < 0.3
                new_location = {
                    'id': new_id,
                    'name': st.session_state.new_place['name'],
                    'lat': float(st.session_state.new_place['lat']),
                    'lng': float(st.session_state.new_place['lng']),
                    'description': st.session_state.new_place['description'],
                    'status': 'exists',
                    'discoverer': st.session_state.user['username'],
                    'multiplier': multiplier
                }
                locations.append(new_location)
                points_earned = 2 if multiplier else 1
                st.session_state.user['points'] += points_earned
                save_data(LOCATION_FILE, locations)
                save_data(USER_FILE, [u if u['email'] != st.session_state.user['email'] else st.session_state.user for u in users])
                st.session_state.new_place = {'name': '', 'lat': '', 'lng': '', 'description': ''}
                st.success(f'Location added! +{points_earned} Abandoned Point{"s" if points_earned > 1 else ""}{" (2x Multiplier)" if multiplier else ""}')
                st.experimental_rerun()

        # Discovered Locations
        st.markdown('<div class="card"><h2 class="text-xl font-semibold mb-4 text-gray-800">Discovered Locations</h2></div>', 
                    unsafe_allow_html=True)
        for loc in locations:
            st.markdown(f"""
                <div class="card">
                    <span class="font-medium text-green-700">{loc['name']}</span>
                    <p class="text-gray-600">{loc['description']}</p>
                    <p class="text-sm text-gray-500">Status: {loc['status']} | By: {loc['discoverer']} {('| 2x Points' if loc['multiplier'] else '')}</p>
                </div>
            """, unsafe_allow_html=True)

    with tabs[1]:  # Shop Tab
        st.markdown('<div class="card"><h2 class="text-xl font-semibold mb-4 text-gray-800">Shop</h2></div>', unsafe_allow_html=True)
        st.markdown('<p class="text-gray-600 mb-4">Spend 5 points to unlock a random abandoned place to explore!</p>', 
                    unsafe_allow_html=True)
        if st.button('Unlock Random Place (5 Points)', key='unlock_place', extra_attrs={'class': 'uiverse-button'}):
            if st.session_state.user['points'] < 5:
                st.error('Need at least 5 points to unlock a place!')
            else:
                new_id = max([loc['id'] for loc in locations], default=0) + 1
                multiplier = random.random() < 0.3
                random_lat = 51.505 + (random.random() - 0.5) * 0.1  # Default location
                random_lng = -0.09 + (random.random() - 0.5) * 0.1
                new_location = {
                    'id': new_id,
                    'name': f'Mystery Place {new_id}',
                    'lat': random_lat,
                    'lng': random_lng,
                    'description': 'A mysterious abandoned place unlocked in the shop!',
                    'status': 'exists',
                    'discoverer': st.session_state.user['username'],
                    'multiplier': multiplier
                }
                locations.append(new_location)
                points_earned = 2 if multiplier else 1
                st.session_state.user['points'] += points_earned - 5
                save_data(LOCATION_FILE, locations)
                save_data(USER_FILE, [u if u['email'] != st.session_state.user['email'] else st.session_state.user for u in users])
                st.success(f'Unlocked a new place! +{points_earned} Abandoned Point{"s" if points_earned > 1 else ""}{" (2x Multiplier)" if multiplier else ""}')
                st.experimental_rerun()

# Main app logic
if st.session_state.user:
    main_page()
else:
    if st.session_state.active_tab == 'Sign In':
        sign_in()
    else:
        sign_up()