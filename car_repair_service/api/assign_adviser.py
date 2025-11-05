import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    # Full access for Admin & System Manager
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""

    # Restrict Assign Adviser role
    if "Assign Adviser" in frappe.get_roles(user):
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee:
            return f"`tabCar Repair Request`.`assign_adviser` = '{employee}'"

    # Block everything for others
    return "1 = 0"
