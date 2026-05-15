import random
import string
import uuid
from datetime import date


def generate_passcode(length: int = 6) -> str:
    """
    Generates a random alphanumeric passcode.
    Example: A3X9KL
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


def generate_summary_token() -> str:
    """
    Generates a unique UUID token for the public shareable summary link.
    Example: 3f7a2b1c-4d5e-6f7a-8b9c-0d1e2f3a4b5c
    """
    return str(uuid.uuid4())


def format_date(d) -> str:
    """
    Formats a date object to a readable string.
    Example: 2024-01-15 -> 15 Jan 2024
    """
    if not d:
        return "N/A"
    if isinstance(d, str):
        return d
    return d.strftime("%d %b %Y")


def validate_emails(email_string: str) -> tuple[bool, list]:
    """
    Validates a comma-separated string of emails.
    Returns (is_valid, list_of_emails)
    """
    if not email_string:
        return False, []

    emails = [e.strip() for e in email_string.split(',') if e.strip()]

    if not emails:
        return False, []

    # Basic email validation
    for email in emails:
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, []

    return True, emails