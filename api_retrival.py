import requests
import streamlit as st

st.title('Hello Streamlit!')
st.write("This is a simple test to check if Streamlit is working.")

# Constants for Bungie's OAuth
CLIENT_ID = '46615'  # Your Bungie application client ID
REDIRECT_URI = 'https://destinyvaulttool.streamlit.app/callback'  # Your callback URL registered in the Bungie application
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'

# Redirect user for authentication
def generate_auth_url():
    return f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

st.title('Destiny Vault Tool')
if st.button('Login with Bungie.net'):
    st.write('Please authenticate:', generate_auth_url())

def exchange_code_for_token(code):
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()

code = st.text_input("Enter the code from URL here:")
if st.button("Get Token"):
    token_response = exchange_code_for_token(code)
    st.text("Access Token:")
    st.write(token_response.get('access_token'))
