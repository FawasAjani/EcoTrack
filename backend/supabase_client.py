
import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Load Supabase configuration from the backend .env file.
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be configured "
        "in the .env file."
    )


def get_supabase_client(access_token: str) -> Client:
    """
    Create a Supabase client using the authenticated user's
    access token.

    The token is applied to PostgREST so database requests
    are evaluated using the user's RLS permissions.
    """

    if not access_token:
        raise ValueError("An access token is required.")

    # Create a standard Supabase client.
    client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    # Apply the user's JWT to database requests.
    client.postgrest.auth(access_token)

    return client
