import bcrypt
from supabase import create_client

# Fill these in directly for the seed script
SUPABASE_URL = "https://bpuoiufzdcxrkjetfldj.supabase.co"
SUPABASE_KEY = "sb_publishable_vpuMCadbrfCHjXoI5j8ndw_dSLM2jdb"
SM_EMAIL = "koanand@deloitte.com"
SM_PASSWORD = "123456"


def seed():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Check if SM already exists
    result = supabase.table("scrum_master").select("id").eq(
        "email", SM_EMAIL
    ).execute()

    if result.data:
        print(f"SM account already exists for {SM_EMAIL}")
        return

    # Hash password
    password_hash = bcrypt.hashpw(
        SM_PASSWORD.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Insert into Supabase
    supabase.table("scrum_master").insert({
        "email": SM_EMAIL,
        "password_hash": password_hash,
        "failed_attempts": 0
    }).execute()

    print(f"✅ SM account created for {SM_EMAIL}")


if __name__ == "__main__":
    seed()