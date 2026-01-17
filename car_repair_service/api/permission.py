# import frappe

# def book_appointment_permission(user):
#     if "System Manager" in frappe.get_roles(user):
#         return ""

#     employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
#     if not employee:
#         return "1=0"

#     return f"`tabBook Appointment`.assigned_to = '{employee}'"




import frappe

def book_appointment_permission(user):
    roles = frappe.get_roles(user)


    # System Manager → see all
    if "System Manager" in roles:
        return ""

    # Receptionist → see all
    if "Receptionist" in roles:
        return ""

    # Employee → only assigned records
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if employee:
        return f"`tabBook Appointment`.assigned_to = '{employee}'"

    # Others → no access
    return "1=0"
