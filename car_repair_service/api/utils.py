import frappe
from urllib.parse import urlencode

def api_error(message, status_code=400):
    frappe.local.response['http_status_code'] = status_code
    return {
        "status": "error",
        "message": str(message)
    }



def get_paginated_data(
    doctype,
    fields,
    filters=None,
    search=None,
    search_fields=None,
    sort_by="name",
    sort_order="asc",
    page=1,
    page_size=10,
    is_pagination=False,
    base_url="",
    extra_params=None
):
    filters = filters or {}
    search_fields = search_fields or []
    extra_params = extra_params or {}

    # Search filter
    if search and search_fields:
        search_conditions = []
        for field in search_fields:
            search_conditions.append([doctype, field, "like", f"%{search}%"])
        filters.setdefault("_or", search_conditions)

    total_records = frappe.db.count(doctype, filters=filters)

    data = frappe.get_all(
        doctype,
        fields=fields,
        filters=filters,
        order_by=f"{sort_by} {sort_order}",
        start=(page - 1) * page_size,
        page_length=page_size
    )

    # If pagination is not requested, return raw data
    if not is_pagination:
        return data

    total_pages = (total_records + page_size - 1) // page_size

    pagination = {
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next_page": None,
        "prev_page": None
    }

    if base_url:
        params = {"page_size": page_size, **extra_params}

        if page < total_pages:
            params["page"] = page + 1
            pagination["next_page"] = f"{base_url}?{urlencode(params)}"

        if page > 1:
            params["page"] = page - 1
            pagination["prev_page"] = f"{base_url}?{urlencode(params)}"

    return {
        "pagination": pagination,
        "data": data
    }
    
    
    
    
    
    


# def ensure_authenticated():
#     """
#     Validate that a request includes a valid API token.
#     Works on all Frappe versions (v13–v15).
#     """
#     auth_header = frappe.get_request_header("Authorization")
#     print("AUTH HEADER:", auth_header)
#     print("ARGS:", frappe.form_dict)
#     print("CURRENT USER:", frappe.session.user)
#     if not auth_header or not auth_header.lower().startswith("token "):
#         frappe.throw("Unauthorized: Missing API token", frappe.PermissionError)

#     try:
#         # Header format: token <api_key>:<api_secret>
#         token_str = auth_header.split("token ")[1].strip()
#         api_key, api_secret = token_str.split(":")

#         user = frappe.db.get_value("User", {"api_key": api_key}, "name")
#         if not user:
#             frappe.throw("Invalid API token", frappe.PermissionError)

#         stored_secret = frappe.utils.password.get_decrypted_password("User", user, "api_secret")
#         if stored_secret != api_secret:
#             frappe.throw("Invalid API token", frappe.PermissionError)

#         # Set current user context
#         frappe.set_user(user)
#         print("TOKEN AFTER PARSE:", auth_header)

#     except Exception:
#         frappe.throw("Unauthorized: Missing or invalid API token", frappe.PermissionError)



# def ensure_authenticated():
#     """Validate API token for all frappe versions."""
#     auth_header = frappe.get_request_header("Authorization")

#     if not auth_header or not auth_header.lower().startswith("token "):
#         frappe.throw("Unauthorized: Missing API token", frappe.PermissionError)

#     try:
#         # Extract token
#         token_str = auth_header.split("token ")[1].strip()
#         api_key, api_secret = token_str.split(":")

#         # Find user
#         user = frappe.db.get_value("User", {"api_key": api_key}, "name")
#         if not user:
#             frappe.throw("Invalid API Key", frappe.PermissionError)

#         # Get stored api_secret
#         stored_secret = frappe.utils.password.get_decrypted_password(
#             "User", user, "api_secret"
#         )

#         if stored_secret != api_secret:
#             frappe.throw("Invalid API Secret", frappe.PermissionError)

#         # 🔥 FIX: Set user before frappe loads session
#         frappe.local.login_manager = None    # Clear old session
#         frappe.set_user(user)                # Set new user
#         frappe.local.session = frappe._dict(user=user)  # Fix session for v15

#     except Exception as e:
#         print("AUTH ERROR:", e)
#         frappe.throw("Unauthorized: Missing or invalid API token", frappe.PermissionError)







# def check_authorization():
#     # Allow login, assets, etc. without token
#     if frappe.request.path.startswith("/api/method/car_repair_service"):
#         auth = frappe.get_request_header("Authorization")

#         if not auth:
#             frappe.throw(
#                 "Authorization header missing.",
#                 frappe.AuthenticationError
#             )
