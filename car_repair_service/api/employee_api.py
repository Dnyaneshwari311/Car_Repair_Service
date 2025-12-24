import frappe
@frappe.whitelist(methods=["GET"])
def list_employees(page=1, page_size=20, search=None):
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    filters = {}
    if search:
        filters = {
            "employee_name": ["like", f"%{search}%"]
        }

    employees = frappe.get_all(
        "Employee",
        filters=filters,
        fields=[
            "name",
            "employee_name",
            "company",
            "department",
            "designation",
            "status"
        ],
        start=start,
        page_length=page_size,
        order_by="modified desc"
    )

    total = frappe.db.count("Employee", filters)

    return {
        "status": "success",
        "data": employees,
        "total": total,
        "page": page
    }












@frappe.whitelist(methods=["POST"])
def create_employee(data=None):
    """
    Create Employee (ERPNext default flow)
    """
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        employee = frappe.get_doc({
            "doctype": "Employee",
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "employee_name": data.get("employee_name"),
            "company": data.get("company"),
            "department": data.get("department"),
            "designation": data.get("designation"),
            "gender": data.get("gender"),
            "date_of_joining": data.get("date_of_joining"),
            "status": data.get("status", "Active"),
            "personal_email": data.get("personal_email"),
            "cell_number": data.get("cell_number")
        })

        employee.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "employee": employee.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Employee API Error")
        return {"status": "error", "message": str(e)}









@frappe.whitelist(methods=["DELETE"])
def delete_employee(name):
    try:
        employee = frappe.get_doc("Employee", name)

        if employee.docstatus != 0:
            return {
                "status": "error",
                "message": "Cannot delete submitted employee"
            }

        employee.delete(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Employee {name} deleted"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
