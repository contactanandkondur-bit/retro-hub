import streamlit as st
from supabase import create_client, Client


def get_client() -> Client:
    """
    Returns a Supabase client using credentials from secrets.toml
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def init_db():
    """
    Seeds the Scrum Master account if it doesn't exist.
    Tables are already created in Supabase directly.
    """
    _seed_scrum_master()


def _seed_scrum_master():
    """
    Creates the SM account from secrets.toml if it doesn't already exist.
    """
    import bcrypt

    supabase = get_client()

    sm_email = st.secrets["SM_EMAIL"]
    sm_password = st.secrets["SM_PASSWORD"]

    # Check if SM already exists
    result = supabase.table("scrum_master").select("id").eq(
        "email", sm_email
    ).execute()

    if not result.data:
        password_hash = bcrypt.hashpw(
            sm_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        supabase.table("scrum_master").insert({
            "email": sm_email,
            "password_hash": password_hash,
            "failed_attempts": 0
        }).execute()
        print(f"✅ Scrum Master account created for {sm_email}")
    else:
        print(f"ℹ️ Scrum Master account already exists for {sm_email}")