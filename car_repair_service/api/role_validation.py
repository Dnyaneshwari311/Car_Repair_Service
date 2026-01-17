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



# import frappe
# from frappe import _

# ROLE_DOCTYPE_MAP = {
#     "Employee": [
#         "Book Appointment",
#         "Car Repair",
#         "Car Repair Request"
#     ],
#     "Assign Advisor": [
#         "Car Repair Request",
#         "Car Diagnosis",
#         "Car Repair"
#     ],
#     "Receptionist": [
#         "Book Appointment",
#         "Car Repair Request",
#         "Car Diagnosis",
#         "Car Repair"
#     ]
# }

# ROLE_CREATE_BLOCK = {
#     "Employee": ["Book Appointment"]
# }


# def validate_api_access(doctype, action="read", doc_name=None):
#     user = frappe.session.user

#     if user == "Guest":
#         frappe.throw(_("Login required"), frappe.PermissionError)

#     user_roles = frappe.get_roles(user)

#     # -------------------------
#     # DOCTYPE ACCESS CHECK
#     # -------------------------
#     allowed_doctypes = set()
#     for role in user_roles:
#         allowed_doctypes.update(ROLE_DOCTYPE_MAP.get(role, []))

#     if doctype not in allowed_doctypes:
#         frappe.throw(
#             _(f"You do not have permission to access {doctype}"),
#             frappe.PermissionError
#         )

#     # -------------------------
#     # CREATE BLOCK
#     # -------------------------
#     if action == "create":
#         if "Employee" in user_roles and doctype == "Book Appointment":
#             frappe.throw(
#                 _("Employee cannot create Book Appointment"),
#                 frappe.PermissionError
#             )

#     # -------------------------
#     # UPDATE / DELETE RULES
#     # -------------------------
#     if action in ["update", "delete"]:

#         # Employee → Book Appointment (only assigned)
#         if "Employee" in user_roles and doctype == "Book Appointment":
#             if not doc_name:
#                 frappe.throw(_("Document name required"), frappe.ValidationError)

#             assigned_to = frappe.get_value(doctype, doc_name, "assigned_to")
#             if assigned_to != user:
#                 frappe.throw(
#                     _(f"You can only {action} assigned Book Appointments"),
#                     frappe.PermissionError
#                 )

#         # Employee → Car Repair Request (NO UPDATE AT ALL)
#         if "Employee" in user_roles and doctype == "Car Repair Request":
#             frappe.throw(
#                 _("Employee cannot update or delete Car Repair Request"),
#                 frappe.PermissionError
#             )
