

# @frappe.whitelist(allow_guest=True)
# def login_and_get_token():
#     """
#     POST JSON or form-data:
#     {
#         "usr": "email / username / phone",
#         "pwd": "password"
#     }

#     Returns:
#     {
#         "status": "success",
#         "user": {...},
#         "token": {
#             "api_key": "xxxx",
#             "api_secret": "xxxx"
#         }
#     }
#     """
#     data = frappe.local.form_dict or frappe.request.get_json(force=True, silent=True) or {}
#     login_input = data.get("usr") or data.get("username") or data.get("email")
#     pwd = data.get("pwd") or data.get("password")

#     if not login_input or not pwd:
#         return api_error("Username/Email/Phone and password are required")

#     usr = get_user_id_from_input(login_input)

#     try:
#         # Authenticate user
#         lm = LoginManager()
#         lm.authenticate(user=usr, pwd=pwd)
#         lm.post_login()

#         user_doc = frappe.get_doc("User", frappe.session.user)

#         # Generate or fetch existing API token
#         api_key, api_secret = _generate_api_token(user_doc)
#         print("api_secret ...",api_secret)

#         # Get employee details if user linked
#         employee_id, company = get_employee_details(user_doc.name)

#         return {
#             "status": "success",
#             "user": {
#                 "name": user_doc.name,
#                 "email": user_doc.email,
#                 "full_name": user_doc.full_name,
#                 "roles": [r.role for r in user_doc.roles],
#                 "company": company,
#                 "employee_id": employee_id
#             },
#             "token": {
#                 "api_key": api_key,
#                 "api_secret": api_secret
#             }
#         }

#     except frappe.AuthenticationError:
#         frappe.local.response.http_status_code = 401
#         return api_error("Invalid login credentials")

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Login and Token API Error")
#         frappe.local.response.http_status_code = 500
#         return api_error(str(e))


# def get_user_id_from_input(login_input):
#     """Detect phone number and fetch user if login via mobile number."""
#     if login_input.isdigit():
#         user = frappe.db.get_value("User", {"phone": login_input}, "name")
#         if user:
#             return user
#     return login_input


# def _generate_api_token(user_doc):
#     """Generate API key & secret only if missing."""
#     import secrets

#     api_key = user_doc.api_key or secrets.token_urlsafe(15)
#     api_secret = user_doc.api_secret or secrets.token_urlsafe(15)
#     print("api_secret ....",api_secret,'api_key')
#     if not (user_doc.api_key and user_doc.api_secret):
#         user_doc.api_key = api_key
#         user_doc.api_secret = api_secret
#         user_doc.save(ignore_permissions=True)

#     return api_key, api_secret


# def get_employee_details(user_id):
#     emp = frappe.db.get_value("Employee", {"user_id": user_id}, ["name", "company"], as_dict=True)
#     if emp:
#         return emp.name, emp.company
#     return None, ""






# # For Reset password 

# @frappe.whitelist(allow_guest=False)
# def reset_password():
#     """
#     Reset password for logged-in user.

#     POST JSON:
#     {
#         "previous_password": "oldPass",
#         "new_password": "NewPass",
#         "confirm_password": "NewPass"
#     }
#     """
#     if frappe.session.user == "Guest":
#         return api_error("You must be logged in to change your password")

#     data = frappe.local.form_dict or frappe.request.get_json(force=True, silent=True) or {}
#     prev_pwd = data.get("previous_password")
#     new_pwd = data.get("new_password")
#     confirm_pwd = data.get("confirm_password")

#     if not prev_pwd or not new_pwd or not confirm_pwd:
#         return api_error("All fields are required")

#     if new_pwd != confirm_pwd:
#         return api_error("New password and confirm password do not match")

#     try:
#         check_password(frappe.session.user, prev_pwd)
#         update_password(frappe.session.user, new_pwd)

#         return {
#             "status": "success",
#             "message": "Password updated successfully"
#         }

#     except frappe.AuthenticationError:
#         return api_error("Previous password is incorrect")

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Reset Password API Error")
#         return api_error(str(e))




import frappe
from frappe import _
from frappe.auth import LoginManager
from car_repair_service.api.utils import api_error

@frappe.whitelist(allow_guest=True)
def login_and_get_token():
    """
    POST JSON or form-data:
      { "usr": "email@example.com" or phone number, "pwd": "password" }

    Returns JSON with API key, API secret, and user info.
    """
    data = frappe.local.form_dict or frappe.request.get_json(force=True, silent=True) or {}
    login_input = data.get("usr") or data.get("username") or data.get("email")
    pwd = data.get("pwd") or data.get("password")

    if not login_input or not pwd:
        frappe.throw(_("Username/Email/Phone and password are required"), frappe.AuthenticationError)

    # Detect phone number and fetch actual username/email from DB
    usr = get_user_id_from_input(login_input)

    try:
        # 1️⃣ Authenticate
        lm = LoginManager()
        lm.authenticate(user=usr, pwd=pwd)
        lm.post_login()

        # 2️⃣ Create new API key + secret for this login
        user_doc = frappe.get_doc("User", frappe.session.user)
        api_key, api_secret = _generate_new_api_token(user_doc)
        # try:
        #     emp_details =  frappe.get_doc("Employee",{"user_id":user_doc.name})
        #     company = emp_details.company
        # except:
        #     company = ""
        #     emp_details = {}
        employee_id, company = get_employee_details(user_doc.name)

        # 3️⃣ Return success with tokens + user info
        return {
            "status": "success",
            "user": {
                "name": user_doc.name,
                "email": user_doc.email,
                "full_name": user_doc.full_name,
                "roles": [r.role for r in user_doc.roles],
                "company":company,
                # "emp_details":emp_details,
                "employee_id":employee_id
            },
            "token": {
                "api_key": api_key,
                "api_secret": api_secret
            }
        }

    except frappe.AuthenticationError:
        print("i ex....")
        frappe.local.response["http_status_code"] = 401
        frappe.local.response["message"] = "Invalid login credentials"
        return
        # return {"status": "error", "message": _("Invalid login credentials")}
        # return api_error("Invalid login credentials")
    except Exception as e:
        print("in")
        frappe.log_error(frappe.get_traceback(), "Login and Token API Error")
        frappe.local.response.http_status_code = 500
        # return {"status": "error", "message": str(e)}
        return api_error(e)


def get_user_id_from_input(login_input):
    """Detect phone number and fetch corresponding user id."""
    if login_input.isdigit():  # If numeric, treat as phone number
        user = frappe.db.get_value("User", {"phone": login_input}, "name")
        if user:
            return user
    return login_input


def _generate_new_api_token(user_doc):
    """Generates a fresh API key & secret for the given user."""
    import secrets

    # Generate API key & secret (shortened to 15 chars)
    api_key = secrets.token_urlsafe(15)
    api_secret = secrets.token_urlsafe(15)

    # Store in the User record (overwrite old ones)
    user_doc.api_key = api_key
    user_doc.api_secret = api_secret
    user_doc.save(ignore_permissions=True)

    return api_key, api_secret

def get_employee_details(user_id):
    emp = frappe.db.get_value("Employee", {"user_id": user_id}, ["name", "company"], as_dict=True)
    if emp:
        return emp.name, emp.company
    return None, ""



# apps/education_api/education_api/api/login.py

import frappe
from frappe import _
from frappe.utils.password import check_password, update_password

@frappe.whitelist(allow_guest=False)
def reset_password():
    """
    Reset password for the currently logged-in user.

    POST JSON or form-data:
    {
        "previous_password": "oldPass123",
        "new_password": "NewPass456",
        "confirm_password": "NewPass456"
    }

    Requires authentication.
    """
    if frappe.session.user == "Guest":
        return api_error("You must be logged in to change your password")

    data = frappe.local.form_dict or frappe.request.get_json(force=True, silent=True) or {}
    previous_password = data.get("previous_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    # Validate inputs
    if not previous_password or not new_password or not confirm_password:
        return api_error("All fields (previous_password, new_password, confirm_password) are required")

    if new_password != confirm_password:
        return api_error("New password and confirm password do not match")

    try:

        # Check old password
        check_password(frappe.session.user, previous_password)

        # Update password
        update_password(frappe.session.user, new_password)

        return {
            "status": "success",
            "status_code": 201,
            "msg": ("Password updated successfully")
        }

    except frappe.AuthenticationError:
        return api_error("Previous password is incorrect")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reset Password API Error")
        return api_error(e)

