from app.utils.supabase_client import supabase

FREE_SEARCH_LIMIT = 1
FREE_UPLOAD_LIMIT = 1

def has_full_access(user_id: str) -> bool:
    response = supabase.query(
        "reports", select_fields="id",
        filters={"user_id": user_id, "report_type": "complet", "status": "completed"},
    )
    return bool(response.data)

def _get_or_create_quota(user_id: str) -> dict:
    response = supabase.query("user_quota", filters={"user_id": user_id})
    if response.data:
        return response.data[0]
    supabase.insert_table("user_quota", {"user_id": user_id})
    return {"user_id": user_id, "free_searches_used": 0, "free_uploads_used": 0}

def can_use_search(user_id: str) -> bool:
    return has_full_access(user_id) or _get_or_create_quota(user_id)["free_searches_used"] < FREE_SEARCH_LIMIT

def consume_search(user_id: str):
    if has_full_access(user_id):
        return
    quota = _get_or_create_quota(user_id)
    supabase.update_table("user_quota", {"free_searches_used": quota["free_searches_used"] + 1}, {"user_id": user_id})

def can_use_upload(user_id: str) -> bool:
    return has_full_access(user_id) or _get_or_create_quota(user_id)["free_uploads_used"] < FREE_UPLOAD_LIMIT

def consume_upload(user_id: str):
    if has_full_access(user_id):
        return
    quota = _get_or_create_quota(user_id)
    supabase.update_table("user_quota", {"free_uploads_used": quota["free_uploads_used"] + 1}, {"user_id": user_id})