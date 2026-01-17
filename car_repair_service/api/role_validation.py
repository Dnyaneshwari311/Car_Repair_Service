import frappe
from frappe import _

# -------------------------------------------------------
# ROLE → ALLOWED DOCTYPES MAPPING
# -------------------------------------------------------
ROLE_DOCTYPE_MAP = {
    "Employee": [
        "Book Appointment",
        "Car repair",
        "Car Repair Request"
    ],
    "Assign Advisor": [
        "Car Repair Request",
        "Car Diagnosis",
        "Car repair"
    ],
    "Receptionist": [
        "Book Appointment",
        "Car Repair Request",
        "Car Diagnosis",
        "Car repair"
    ]
}

# -------------------------------------------------------
# COMMON API PERMISSION VALIDATION
# -------------------------------------------------------
def validate_api_access(doctype):
    """
    Validate API access based on logged-in user's roles
    """

    user = frappe.session.user

    # Guest users not allowed
    if user == "Guest":
        frappe.throw(
            _("Login required"),
            frappe.PermissionError
        )

    user_roles = frappe.get_roles(user)

    allowed_doctypes = set()
    for role in user_roles:
        allowed_doctypes.update(ROLE_DOCTYPE_MAP.get(role, []))

    if doctype not in allowed_doctypes:
        frappe.throw(
            _(f"You do not have permission to access {doctype}"),
            frappe.PermissionError
        )

# -------------------------------------------------------
# OPTIONAL: GENERIC CRUD VALIDATION
# -------------------------------------------------------
def validate_crud_access(doctype, action="read"):
    """
    action: read | create | update | delete
    (currently same permission, extend if needed)
    """
    validate_api_access(doctype)



