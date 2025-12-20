import frappe

def book_appointment_permission(user):
    if "System Manager" in frappe.get_roles(user):
        return ""

    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        return "1=0"

    return f"`tabBook Appointment`.assigned_to = '{employee}'"
