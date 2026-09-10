from app.utils.supabase_client import supabase

# Paliers de crédits
ONBOARDING_SEARCH_LIMIT = 10   # onboarding terminé, aucun achat
ONBOARDING_UPLOAD_LIMIT = 10
REPORT_SEARCH_LIMIT     = 30   # au moins un rapport simple
REPORT_UPLOAD_LIMIT     = 30
FULL_SEARCH_LIMIT       = 100  # rapport complet
FULL_UPLOAD_LIMIT       = 100

# Compatibilité ascendante
FREE_SEARCH_LIMIT = ONBOARDING_SEARCH_LIMIT
FREE_UPLOAD_LIMIT = ONBOARDING_UPLOAD_LIMIT


def has_completed_onboarding(user_id: str) -> bool:
    response = supabase.query(
        "user_profiles", select_fields="onboarding_completed",
        filters={"user_id": user_id},
    )
    return bool(response.data) and bool(response.data[0].get("onboarding_completed"))


def _limits_for(user_id: str):
    """Retourne (search_limit, upload_limit) ou (0, 0) si aucun accès."""
    if has_full_access(user_id):
        return FULL_SEARCH_LIMIT, FULL_UPLOAD_LIMIT
    if has_any_report(user_id):
        return REPORT_SEARCH_LIMIT, REPORT_UPLOAD_LIMIT
    if has_completed_onboarding(user_id):
        return ONBOARDING_SEARCH_LIMIT, ONBOARDING_UPLOAD_LIMIT
    return 0, 0

def has_full_access(user_id: str) -> bool:
    response = supabase.query(
        "reports", select_fields="id",
        filters={"user_id": user_id, "report_type": "complet", "status": "completed"},
    )
    return bool(response.data)

def has_any_report(user_id: str) -> bool:
    response = supabase.query(
        "reports", select_fields="id",
        filters={"user_id": user_id, "status": "completed"},
    )
    return bool(response.data)

def _get_or_create_quota(user_id: str) -> dict:
    response = supabase.query("user_quota", filters={"user_id": user_id})
    if response.data:
        return response.data[0]
    supabase.insert_table("user_quota", {"user_id": user_id})
    return {"user_id": user_id, "free_searches_used": 0, "free_uploads_used": 0}

def check_search_access(user_id: str):
    """Retourne (allowed: bool, reason: str | None)."""
    search_limit, _ = _limits_for(user_id)
    if search_limit == 0:
        return False, "report_required"
    if _get_or_create_quota(user_id)["free_searches_used"] < search_limit:
        return True, None
    return False, "quota_exceeded"

def consume_search(user_id: str):
    quota = _get_or_create_quota(user_id)
    supabase.update_table("user_quota", {"free_searches_used": quota["free_searches_used"] + 1}, {"user_id": user_id})

def check_upload_access(user_id: str):
    """Retourne (allowed: bool, reason: str | None)."""
    _, upload_limit = _limits_for(user_id)
    if upload_limit == 0:
        return False, "report_required"
    if _get_or_create_quota(user_id)["free_uploads_used"] < upload_limit:
        return True, None
    return False, "quota_exceeded"

def consume_upload(user_id: str):
    quota = _get_or_create_quota(user_id)

    supabase.update_table("user_quota", {"free_uploads_used": quota["free_uploads_used"] + 1}, {"user_id": user_id})