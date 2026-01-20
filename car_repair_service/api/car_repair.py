# import frappe

# def get_permission_query_conditions(user):
#     # Administrator sees all
#     if user == "Administrator":
#         return ""

#     roles = frappe.get_roles(user)

#     if "Employee" in roles:
#         # Get the Employee linked to this user
#         employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
#         if not employee_id:
#             return "1=0"  # no matching employee → show nothing

#         # Only show Car Repair records where this employee is assigned in child table
#         return f"""
#             `tabCar repair`.`name` IN (
#                 SELECT `parent` 
#                 FROM `tabCar Repair Damage` 
#                 WHERE `assigned_to` = '{employee_id}'
#             )
#         """

#     # Other users: no restriction
#     return ""



import frappe

def get_permission_query_conditions(user):
    # Admin sees everything
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    # Restrict for Employee role
    if "Employee" in roles:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if not employee:
            return "1=0"

        return f"""
            `tabCar repair`.`name` IN (
                SELECT `parent`
                FROM `tabCar Repair Damage`
                WHERE `assigned_to` = '{employee}'
            )
        """

    # Other roles → no restriction
    return ""
