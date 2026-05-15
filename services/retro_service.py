from database.db import get_client
from utils.helpers import generate_passcode, generate_summary_token


def create_retro_session(
    sprint_name: str,
    sprint_goal: str,
    team_size: int,
    start_date: str,
    end_date: str,
    email_recipients: str
) -> dict:
    supabase = get_client()

    # Check if active session exists
    existing = supabase.table("retro_sessions").select("id").eq(
        "status", "active"
    ).execute()

    if existing.data:
        raise Exception(
            "There is already an active retro session. "
            "Please close it before creating a new one."
        )

    passcode = generate_passcode()
    summary_token = generate_summary_token()

    result = supabase.table("retro_sessions").insert({
        "sprint_name": sprint_name,
        "sprint_goal": sprint_goal,
        "team_size": team_size,
        "start_date": start_date,
        "end_date": end_date,
        "passcode": passcode,
        "summary_token": summary_token,
        "email_recipients": email_recipients,
        "status": "active"
    }).execute()

    return result.data[0]


def get_active_retro() -> dict | None:
    supabase = get_client()
    result = supabase.table("retro_sessions").select("*").eq(
        "status", "active"
    ).order("created_at", desc=True).limit(1).execute()

    return result.data[0] if result.data else None


def get_retro_by_token(token: str) -> dict | None:
    supabase = get_client()
    result = supabase.table("retro_sessions").select("*").eq(
        "summary_token", token
    ).execute()

    return result.data[0] if result.data else None


def get_retro_by_id(session_id: int) -> dict | None:
    supabase = get_client()
    result = supabase.table("retro_sessions").select("*").eq(
        "id", session_id
    ).execute()

    return result.data[0] if result.data else None


def get_all_past_retros() -> list:
    supabase = get_client()

    # Get all closed/approved sessions
    sessions = supabase.table("retro_sessions").select("*").in_(
        "status", ["closed", "approved"]
    ).order("created_at", desc=True).execute()

    if not sessions.data:
        return []

    # Add submission count to each session
    result = []
    for session in sessions.data:
        count_result = supabase.table("submissions").select(
            "id", count="exact"
        ).eq("session_id", session['id']).execute()

        session['submission_count'] = count_result.count or 0
        result.append(session)

    return result


def get_submission_count(session_id: int) -> int:
    supabase = get_client()
    result = supabase.table("submissions").select(
        "id", count="exact"
    ).eq("session_id", session_id).execute()

    return result.count or 0


def save_submission(
    session_id: int,
    went_well: str,
    improve: str,
    recognition: str
) -> bool:
    supabase = get_client()
    supabase.table("submissions").insert({
        "session_id": session_id,
        "went_well": went_well,
        "improve": improve,
        "recognition": recognition
    }).execute()
    return True


def get_all_submissions(session_id: int) -> list:
    supabase = get_client()
    result = supabase.table("submissions").select("*").eq(
        "session_id", session_id
    ).execute()
    return result.data or []


def close_retro_session(session_id: int) -> bool:
    supabase = get_client()
    supabase.table("retro_sessions").update({
        "status": "closed"
    }).eq("id", session_id).execute()
    return True


def approve_retro_session(session_id: int) -> bool:
    supabase = get_client()
    supabase.table("retro_sessions").update({
        "status": "approved"
    }).eq("id", session_id).execute()
    return True


def get_summary(session_id: int) -> dict | None:
    supabase = get_client()
    result = supabase.table("ai_summaries").select("*").eq(
        "session_id", session_id
    ).execute()
    return result.data[0] if result.data else None


def update_summary(
    session_id: int,
    went_well_summary: str,
    improve_summary: str,
    recognition_summary: str,
    action_items_summary: str
) -> bool:
    supabase = get_client()
    supabase.table("ai_summaries").update({
        "went_well_summary": went_well_summary,
        "improve_summary": improve_summary,
        "recognition_summary": recognition_summary,
        "action_items_summary": action_items_summary,
        "is_edited": 1
    }).eq("session_id", session_id).execute()
    return True


def save_action_items(
    session_id: int,
    sprint_name: str,
    action_items_text: str
) -> bool:
    supabase = get_client()

    # Clear existing action items for this session
    supabase.table("action_items").delete().eq(
        "session_id", session_id
    ).execute()

    # Parse bullet points
    lines = action_items_text.split('\n')
    items = [
        line.replace('•', '').strip()
        for line in lines
        if line.strip()
    ]

    for item in items:
        if item:
            supabase.table("action_items").insert({
                "session_id": session_id,
                "sprint_name": sprint_name,
                "item_text": item,
                "status": "open"
            }).execute()

    return True


def get_all_action_items() -> list:
    supabase = get_client()

    # Get all action items with sprint name from retro_sessions
    result = supabase.table("action_items").select(
        "*, retro_sessions(sprint_name)"
    ).order("created_at", desc=True).execute()

    # Flatten sprint_name from nested object
    items = []
    for item in result.data or []:
        item['sprint_name'] = item.get(
            'retro_sessions', {}
        ).get('sprint_name', 'Unknown Sprint')
        items.append(item)

    return items


def get_action_items_by_session(session_id: int) -> list:
    supabase = get_client()

    result = supabase.table("action_items").select(
        "*, retro_sessions(sprint_name)"
    ).eq("session_id", session_id).order("created_at").execute()

    items = []
    for item in result.data or []:
        item['sprint_name'] = item.get(
            'retro_sessions', {}
        ).get('sprint_name', 'Unknown Sprint')
        items.append(item)

    return items


def update_action_item_status(item_id: int, status: str) -> bool:
    supabase = get_client()
    supabase.table("action_items").update({
        "status": status
    }).eq("id", item_id).execute()
    return True