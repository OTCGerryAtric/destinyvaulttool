import requests
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Constants for Bungie's Links and Redirect
REDIRECT_URI = 'https://destinyvaulttool.streamlit.app'  # Update with your actual redirect URI
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'

# List Client ID and API Key
CLIENT_ID = '46615'
API_KEY = 'a287ebb36bcb4f6db80c8b7e2afa12df'

# Generate the authorization URL
def generate_auth_url():
    return f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

if st.button('Login with Bungie.net'):
    auth_url = generate_auth_url()
    # Redirect in the same window
    js_redirect = f"window.location.href = '{auth_url}';"
    st.components.v1.html(f"<script>{js_redirect}</script>", height=0)

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
        return None, None

def get_inventory(membership_type, membership_id, headers):
    url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/?components=201"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data['Response']
        filtered_items = [
            {
                'itemHash': item.get('itemHash'),
                'itemInstanceId': item.get('itemInstanceId', None),  # Some items might not have an instance ID
                'quantity': item.get('quantity', 1)  # Default quantity to 1 if not provided
            }
            for item in items
        ]
        return pd.DataFrame(filtered_items)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if the API call was unsuccessful

code = st.text_input("Enter the code from URL here:")
if st.button("Get Token"):
    token_response = exchange_code_for_token(code)
    if isinstance(token_response, dict) and 'access_token' in token_response:
        access_token = token_response['access_token']
        st.success("Token successfully obtained!")
        st.write("Access Token:", access_token)

        # Setup headers
        headers = {'Authorization': f'Bearer {access_token}', 'X-API-Key': API_KEY}

        # Fetch membership info
        membership_type, membership_id, unique_name = get_membership_info(headers)
        if membership_type and membership_id and unique_name:
            st.write("Display Name:", unique_name)
            st.write("Membership Type:", membership_type)
            st.write("Membership ID:", membership_id)
            inventory = get_inventory(membership_type, membership_id, headers)
            st.write(inventory)

        else:
            st.error("Failed to retrieve membership information.")
    else:
        st.error("Failed to get token.")
        st.write(token_response)  # Display the error message or response text