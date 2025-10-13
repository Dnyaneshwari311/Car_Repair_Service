import frappe

def get_permission_query_conditions(user):
    # Administrator sees all
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    if "Employee" in roles:
        # Get the Employee linked to this user
        employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if not employee_id:
            return "1=0"  # no matching employee → show nothing

        # Filter parent Car Repair where any child damage is assigned to this employee
        return (
            "`tabCar repair`.`name` IN ("
            "SELECT `parent` FROM `tabCar Repair Damage` "
            "WHERE `assigned_to` = '{0}')"
        ).format(employee_id)

    # Other users: no restriction
    return ""
