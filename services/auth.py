import bcrypt
import streamlit as st
from database.db import get_client
from datetime import datetime, timedelta

SESSION_TIMEOUT_MINUTES = 30
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_MINUTES = 5


def verify_scrum_master(email: str, password: str) -> tuple[bool, str]:
    supabase = get_client()

    result = supabase.table("scrum_master").select("*").eq(
        "email", email
    ).execute()

    if not result.data:
        return False, "Invalid email or password."

    row = result.data[0]

    # Check lockout
    if row.get('locked_until'):
        locked_until = datetime.fromisoformat(row['locked_until'])
        if datetime.now() < locked_until:
            remaining = int((locked_until - datetime.now()).total_seconds() / 60) + 1
            return False, f"Account locked. Try again in {remaining} minute(s)."
        else:
            _reset_failed_attempts(email)

    # Check password
    is_valid = bcrypt.checkpw(
        password.encode('utf-8'),
        row['password_hash'].encode('utf-8')
    )

    if is_valid:
        _reset_failed_attempts(email)
        return True, "Login successful."
    else:
        attempts = _increment_failed_attempts(email)
        remaining_attempts = MAX_FAILED_ATTEMPTS - attempts
        if attempts >= MAX_FAILED_ATTEMPTS:
            _lock_account(email)
            return False, f"Too many failed attempts. Account locked for {LOCKOUT_MINUTES} minutes."
        return False, f"Invalid email or password. {remaining_attempts} attempt(s) remaining."


def _increment_failed_attempts(email: str) -> int:
    supabase = get_client()
    result = supabase.table("scrum_master").select(
        "failed_attempts"
    ).eq("email", email).execute()

    current = result.data[0]['failed_attempts'] if result.data else 0
    new_attempts = current + 1

    supabase.table("scrum_master").update({
        "failed_attempts": new_attempts
    }).eq("email", email).execute()

    return new_attempts


def _reset_failed_attempts(email: str):
    supabase = get_client()
    supabase.table("scrum_master").update({
        "failed_attempts": 0,
        "locked_until": None
    }).eq("email", email).execute()


def _lock_account(email: str):
    supabase = get_client()
    locked_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
    supabase.table("scrum_master").update({
        "locked_until": locked_until.isoformat()
    }).eq("email", email).execute()


def verify_passcode(passcode: str) -> dict | None:
    supabase = get_client()
    result = supabase.table("retro_sessions").select("*").eq(
        "passcode", passcode
    ).eq("status", "active").execute()

    if result.data:
        return result.data[0]
    return None


def login_as_sm():
    st.session_state['role'] = 'sm'
    st.session_state['is_logged_in'] = True
    st.session_state['last_activity'] = datetime.now().isoformat()


def login_as_member(session: dict):
    st.session_state['role'] = 'member'
    st.session_state['is_logged_in'] = True
    st.session_state['retro_session'] = session
    st.session_state['last_activity'] = datetime.now().isoformat()


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_sm() -> bool:
    return st.session_state.get('role') == 'sm'


def is_member() -> bool:
    return st.session_state.get('role') == 'member'


def is_logged_in() -> bool:
    return st.session_state.get('is_logged_in', False)


def check_session_timeout() -> bool:
    last_activity = st.session_state.get('last_activity')

    if not last_activity:
        return True

    last_activity_dt = datetime.fromisoformat(last_activity)
    timeout_dt = last_activity_dt + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    if datetime.now() > timeout_dt:
        return True

    st.session_state['last_activity'] = datetime.now().isoformat()
    return False


def has_already_submitted(session_id: int) -> bool:
    submitted_sessions = st.session_state.get('submitted_sessions', [])
    return session_id in submitted_sessions


def mark_as_submitted(session_id: int):
    if 'submitted_sessions' not in st.session_state:
        st.session_state['submitted_sessions'] = []
    st.session_state['submitted_sessions'].append(session_id)