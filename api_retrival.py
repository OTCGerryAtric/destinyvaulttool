import requests
import streamlit as st
import pandas as pd

# Set Page Config
st.set_page_config(page_title="Destiny 2 Vault Tool", page_icon=None, layout="wide", initial_sidebar_state="expanded", menu_items=None)

# Constants for Bungie's Links and Redirect
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'
REDIRECT_URI = 'https://destinyvaulttool.streamlit.app'

# List Client ID and API Key
CLIENT_ID = '46615'
API_KEY = 'a287ebb36bcb4f6db80c8b7e2afa12df'

# Generate the authorization URL
def generate_auth_url():
    return f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

if st.button('Login with Bungie.net'):
    auth_url = generate_auth_url()
    st.markdown(f"Please [click here to authenticate]({auth_url}) with Bungie.net.")

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

def get_membership_info(headers):
    url = "https://www.bungie.net/Platform/User/GetMembershipsForCurrentUser/"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        unique_name = data['Response']['destinyMemberships'][0]['displayName']
        membership_type = data['Response']['destinyMemberships'][0]['membershipType']
        membership_id = data['Response']['destinyMemberships'][0]['membershipId']
        return membership_type, membership_id, unique_name
    else:
        return None, None, None

def get_all_inventories(membership_type, membership_id, character_ids, headers):
    component = '201'  # CharacterInventories component
    all_items = []

    for character_id in character_ids:
        inventory_url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/Character/{character_id}/?components={component}"
        response = requests.get(inventory_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            items = data['Response']['inventory']['data']['items']
            for item in items:
                if item['itemHash'] == 2119346509:  # Ammit AR2 item hash
                    all_items.append(item)

    return pd.DataFrame(all_items)

code = st.text_input("Enter the code from URL here:")
if st.button("Get Token"):
    token_response = exchange_code_for_token(code)
    if isinstance(token_response, dict) and 'access_token' in token_response:
        access_token = token_response['access_token']
        st.success("Token successfully obtained!")

        # Setup headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-API-Key': API_KEY
        }

        # Fetch membership info
        membership_type, membership_id, unique_name = get_membership_info(headers)
        if membership_type and membership_id:
            st.write(f"Display Name: {unique_name}")
            st.write(f"Membership Type: {membership_type}")
            st.write(f"Membership ID: {membership_id}")

            # Fetch inventory
            inventory_df = get_inventory(membership_type, membership_id, headers)
            if not inventory_df.empty:
                st.dataframe(inventory_df)
            else:
                st.error("Failed to retrieve inventory.")
        else:
            st.error("Failed to retrieve membership information.")
    else:
        st.error("Failed to get token. Please check the code and try again.")
        st.write(token_response)  # To display more detailed error info
