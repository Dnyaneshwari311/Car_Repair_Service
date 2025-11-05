
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



import frappe

def get_permission_query_conditions(user, doctype):
    if not user:
        user = frappe.session.user

    # Full access for Administrator & System Manager
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""

    # Restrict Assign Advisor role
    if "Assign Advisor" in frappe.get_roles(user):
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if not employee:
            return "1=0"

        # Apply only on specific doctypes
        if doctype in ["Car Repair Request", "Car Diagnosis", "Car Repair"]:
            return f"`tab{doctype}`.`assign_adviser` = '{employee}'"

        # Any other DocType -> block
        return "1=0"

    # No other users allowed
    return "1=0"
