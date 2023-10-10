from boatapp.utils import get_public_url
from mollie.api.client import Client
from mollie.api.error import Error
from flask import current_app


def get_client():
    # Get api key from app config
    api_key = current_app.config['MOLLIE_API_KEY']
    public_url = get_public_url()
    mollie_client = Client()
    mollie_client.set_api_key(api_key)
    
    return mollie_client