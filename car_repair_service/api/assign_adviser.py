
# import frappe

# def get_permission_query_conditions(user):
#     if not user:
#         user = frappe.session.user

#     # Full access for Administrator & System Manager
#     if user == "Administrator" or "System Manager" in frappe.get_roles(user):
#         return ""

#     # ✅ Fix: use correct role name "Assign Advisor"
#     if "Assign Advisor" in frappe.get_roles(user):
#         employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
#         if employee:
#             return f"`tabCar Repair Request`.`assign_adviser` = '{employee}'"
#         else:
#             return "1=0"

#     return "1=0"



# import frappe

# def get_permission_query_conditions(user, doctype):
#     if not user:
#         user = frappe.session.user

#     # Full access for Administrator & System Manager
#     if user == "Administrator" or "System Manager" in frappe.get_roles(user):
#         return ""

#     # Restrict Assign Advisor role
#     if "Assign Advisor" in frappe.get_roles(user):
#         employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
#         if not employee:
#             return "1=0"

#         # Apply only on specific doctypes
#         if doctype in ["Car Repair Request", "Car Diagnosis", "Car Repair"]:
#             return f"`tab{doctype}`.`assign_adviser` = '{employee}'"

#         # Any other DocType -> block
#         return "1=0"

#     # No other users allowed
#     return "1=0"




# import frappe

# def get_permission_query_conditions(user, doctype):
#     if not user:
#         user = frappe.session.user

#     roles = frappe.get_roles(user)

#     # Admin & System Manager → full access
#     if user == "Administrator" or "System Manager" in roles:
#         return ""

#     # Assign Advisor role
#     if "Assign Advisor" in roles:
#         employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
#         if not employee:
#             return "1=0"

#         # Show only docs assigned to him
#         return f"`tab{doctype}`.`assign_adviser` = '{employee}'"

#     # Others → no access
#     return "1=0"


# def has_permission(doc, user):
#     roles = frappe.get_roles(user)

#     # Admin & System Manager → full access
#     if user == "Administrator" or "System Manager" in roles:
#         return True

#     # Assign Advisor role
#     if "Assign Advisor" in roles:
#         employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
#         if not employee:
#             return False

#         # Allow the user only if assigned adviser matches
#         return doc.assign_adviser == employee

#     # Others → no access
#     return False





import frappe

def get_permission_query_conditions(user, doctype):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    # Full access for Administrator & System Manager
    if user == "Administrator" or "System Manager" in roles:
        return ""

    # Restrict Assign Advisor role
    if "Assign Advisor" in roles:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if not employee:
            return "1=0"

        # Only apply restriction on certain doctypes
        if doctype in ["Car Repair Request", "Car Diagnosis", "Car repair"]:
            return f"`tab{doctype}`.`assign_adviser` = '{employee}'"

        # Any other DocType -> block
        return "1=0"

    # No access for other users
    return "1=0"



def has_permission(doc, user):
    roles = frappe.get_roles(user)

    # Full access for Admin & System Manager
    if user == "Administrator" or "System Manager" in roles:
        return True

    # Assign Advisor: check assign_adviser field
    if "Assign Advisor" in roles:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if not employee:
            return False

        # Only allow access if assigned adviser matches
        if doc.doctype in ["Car Repair Request", "Car Diagnosis", "Car repair"]:
            return doc.assign_adviser == employee

    # All others: no access
    return False




# def has_permission(doc, user):
#     roles = frappe.get_roles(user)

#     if user == "Administrator" or "System Manager" in roles:
#         return True

#     if "Assign Advisor" in roles:
#         employee = frappe.db.get_value(
#             "Employee",
#             {"user_id": user},
#             "name",
#             ignore_permissions=True
#         )
#         if not employee:
#             return False

#         return frappe.db.get_value(
#             doc.doctype,
#             doc.name,
#             "assign_adviser"
#         ) == employee

#     return False
