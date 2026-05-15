import streamlit as st
from groq import Groq


def _call_groq(prompt: str) -> str:
    """
    Sends a prompt to Groq API and returns the response text.
    """
    try:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1000
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"❌ Groq API error: {str(e)}")


def _build_went_well_prompt(responses: list) -> str:
    formatted = "\n".join([f"- {r}" for r in responses if r.strip()])
    return f"""You are summarizing Sprint Retrospective feedback.

STRICT RULES:
- Only use information from the responses below
- Do NOT add, invent or assume anything not mentioned
- Do NOT add examples or explanations
- If there is only one response, summarize only that
- Maximum 6 bullet points
- Each bullet starts with •
- Only output bullet points, nothing else

Team responses for "What Went Well":
{formatted}

Output:"""


def _build_improve_prompt(responses: list) -> str:
    formatted = "\n".join([f"- {r}" for r in responses if r.strip()])
    return f"""You are summarizing Sprint Retrospective feedback.

STRICT RULES:
- Only use information from the responses below
- Do NOT add, invent or assume anything not mentioned
- Do NOT add examples or explanations
- If there is only one response, summarize only that
- Maximum 6 bullet points
- Each bullet starts with •
- Only output bullet points, nothing else

Team responses for "What Can Be Improved":
{formatted}

Output:"""


def _build_recognition_prompt(responses: list) -> str:
    formatted = "\n".join([f"- {r}" for r in responses if r.strip()])
    return f"""You are summarizing Sprint Retrospective recognition shoutouts.

STRICT RULES:
- Only use information from the responses below
- Do NOT add, invent or assume anything not mentioned
- Preserve names exactly as mentioned
- If there is only one response, summarize only that
- Maximum 8 bullet points
- Each bullet starts with •
- Only output bullet points, nothing else

Team responses for "Recognitions":
{formatted}

Output:"""


def _build_action_items_prompt(improve_responses: list, improve_summary: str) -> str:
    formatted = "\n".join([f"- {r}" for r in improve_responses if r.strip()])
    return f"""You are a Scrum Master creating action items from Sprint Retrospective feedback.

STRICT RULES:
- Only create action items directly based on the feedback below
- Do NOT invent problems or actions not mentioned in the feedback
- Each action item must be traceable to something in the feedback
- Maximum 5 action items
- Format: • Owner: Action
- Only output action items, nothing else

Improvement feedback from team:
{formatted}

Output:"""


def generate_summary(session_id: int) -> dict:
    """
    Main function to generate AI summary for a retro session.
    """
    from services.retro_service import get_all_submissions

    submissions = get_all_submissions(session_id)

    if not submissions:
        raise Exception("No submissions found for this session.")

    went_well_responses = [s['went_well'] for s in submissions if s.get('went_well')]
    improve_responses = [s['improve'] for s in submissions if s.get('improve')]
    recognition_responses = [s['recognition'] for s in submissions if s.get('recognition')]

    went_well_summary = ""
    improve_summary = ""
    recognition_summary = ""
    action_items_summary = ""

    if went_well_responses:
        went_well_summary = _call_groq(_build_went_well_prompt(went_well_responses))

    if improve_responses:
        improve_summary = _call_groq(_build_improve_prompt(improve_responses))

    if recognition_responses:
        recognition_summary = _call_groq(_build_recognition_prompt(recognition_responses))

    if improve_responses and improve_summary:
        action_items_summary = _call_groq(
            _build_action_items_prompt(improve_responses, improve_summary)
        )

    # Save to Supabase
    from database.db import get_client
    supabase = get_client()

    existing = supabase.table("ai_summaries").select("id").eq(
        "session_id", session_id
    ).execute()

    if existing.data:
        supabase.table("ai_summaries").update({
            "went_well_summary": went_well_summary,
            "improve_summary": improve_summary,
            "recognition_summary": recognition_summary,
            "action_items_summary": action_items_summary,
            "is_edited": 0
        }).eq("session_id", session_id).execute()
    else:
        supabase.table("ai_summaries").insert({
            "session_id": session_id,
            "went_well_summary": went_well_summary,
            "improve_summary": improve_summary,
            "recognition_summary": recognition_summary,
            "action_items_summary": action_items_summary
        }).execute()

    return {
        "went_well_summary": went_well_summary,
        "improve_summary": improve_summary,
        "recognition_summary": recognition_summary,
        "action_items_summary": action_items_summary
    }