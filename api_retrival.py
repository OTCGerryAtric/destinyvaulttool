import requests
import streamlit as st
import sqlite3
import json

st.title('Hello Streamlit!')
st.write("This is a simple test to check if Streamlit is working.")

# Constants for Bungie's OAuth
CLIENT_ID = '46615'  # Update with your actual client ID
REDIRECT_URI = 'https://destinyvaulttool.streamlit.app/callback'  # Update with your actual redirect URI
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'
API_KEY = 'a287ebb36bcb4f6db80c8b7e2afa12df'  # Replace with your actual Bungie API key

# Database Initialization
def init_db():
    conn = sqlite3.connect('destiny_data.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS memberships (
            membership_id TEXT PRIMARY KEY,
            membership_type TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            character_id TEXT PRIMARY KEY,
            membership_id TEXT,
            FOREIGN KEY(membership_id) REFERENCES memberships(membership_id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT,
            character_id TEXT,
            json_detail TEXT,
            FOREIGN KEY(character_id) REFERENCES characters(character_id)
        )
    ''')
    conn.commit()
    conn.close()

# Call init_db to set up the database on script start
init_db()

# Function to generate the authorization URL
def generate_auth_url():
    return f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

if st.button('Login with Bungie.net'):
    auth_url = generate_auth_url()
    st.markdown(f"[Authenticate here]({auth_url})")

# Function to exchange code for token
def exchange_code_for_token(code):
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return response.text

# Database functions to insert data
def insert_membership(membership_type, membership_id):
    conn = sqlite3.connect('destiny_data.db')
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO memberships (membership_type, membership_id) VALUES (?, ?)',
                (membership_type, membership_id))
    conn.commit()
    conn.close()

def insert_character_ids(membership_id, character_ids):
    conn = sqlite3.connect('destiny_data.db')
    cur = conn.cursor()
    for character_id in character_ids:
        cur.execute('INSERT OR REPLACE INTO characters (character_id, membership_id) VALUES (?, ?)',
                    (character_id, membership_id))
    conn.commit()
    conn.close()

def insert_inventory(character_id, items):
    conn = sqlite3.connect('destiny_data.db')
    cur = conn.cursor()
    for item in items:
        item_id = str(item.get('itemHash'))  # Assuming itemHash is the identifier
        json_detail = json.dumps(item)  # Convert the item dictionary to a JSON string
        cur.execute('INSERT INTO inventory (item_id, character_id, json_detail) VALUES (?, ?, ?)',
                    (item_id, character_id, json_detail))
    conn.commit()
    conn.close()

# Input for the OAuth code
code = st.text_input("Enter the code from URL here:")
if st.button("Get Token"):
    token_response = exchange_code_for_token(code)
    if isinstance(token_response, dict) and 'access_token' in token_response:
        access_token = token_response['access_token']
        st.success("Token successfully obtained!")
        st.write("Access Token:", access_token)

        # Setup headers
        headers = {'Authorization': f'Bearer {access_token}', 'X-API-Key': API_KEY}

        # Fetch and process membership info
        membership_type, membership_id = get_membership_info(headers)
        if membership_type and membership_id:
            insert_membership(membership_type, membership_id)
            st.write("Membership Type:", membership_type)
            st.write("Membership ID:", membership_id)

            # Fetch and process character IDs
            character_ids = get_character_ids(membership_type, membership_id, headers)
            insert_character_ids(membership_id, character_ids)
            st.write("Character IDs:", character_ids)

            # Fetch and display inventory for each character, and save to database
            for character_id in character_ids:
                inventory = get_inventory(membership_type, membership_id, character_id, headers)
                insert_inventory(character_id, inventory)
                st.write(f"Inventory for Character {character_id}:", inventory)
        else:
            st.error("Failed to retrieve membership information.")
    else:
        st.error("Failed to get token.")
        st.write(token_response)  # Display the error message or response text