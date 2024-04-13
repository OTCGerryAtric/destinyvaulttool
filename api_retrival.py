import requests
import streamlit as st

st.title('Hello Streamlit!')
st.write("This is a simple test to check if Streamlit is working.")

# Constants for Bungie's OAuth
CLIENT_ID = '46615'  # Update with your actual client ID
REDIRECT_URI = 'https://destinyvaulttool.streamlit.app/callback'  # Update with your actual redirect URI
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'

# Generate the authorization URL
def generate_auth_url():
    return f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

if st.button('Login with Bungie.net'):
    auth_url = generate_auth_url()
    st.markdown(f"[Authenticate here]({auth_url})")

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
        # Log the entire response to help debugging
        return response.text  # This will show the error message from the API

code = st.text_input("Enter the code from URL here:")
if st.button("Get Token"):
    token_response = exchange_code_for_token(code)
    if isinstance(token_response, dict) and 'access_token' in token_response:
        st.success("Token successfully obtained!")
        st.write("Access Token:", token_response['access_token'])
    else:
        st.error("Failed to get token.")
        st.write(token_response)  # Display the error message or response text
