import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def create_sales_invoice_from_car_repair(car_repair_name):
    try:
        # ⚠️ Use exact DocType name
        car_repair = frappe.get_doc("Car repair", car_repair_name)

        # -----------------------------
        # RESOLVE CUSTOMER (MANDATORY)
        # -----------------------------
        customer = frappe.db.get_value(
            "Customer",
            {"customer_name": car_repair.customer_name},
            "name"
        )

        if not customer:
            frappe.throw(_("Customer not found in ERPNext"))

        # -----------------------------
        # CREATE SALES INVOICE
        # -----------------------------
        si = frappe.new_doc("Sales Invoice")
        si.customer = customer                          # ✅ REQUIRED
        si.company = frappe.defaults.get_user_default("Company")
        si.posting_date = frappe.utils.today()
        si.due_date = frappe.utils.today()
        si.set_posting_time = 1
        si.remarks = f"Car Repair: {car_repair.name} | Vehicle: {car_repair.license_plate}"

        # -----------------------------
        # ITEMS
        # -----------------------------
        for d in car_repair.list_of_damage:
            if not d.part_required or d.quantity <= 0:
                continue

            si.append("items", {
                "item_code": d.part_required,
                "qty": d.quantity,
                "rate": d.estimated_cost
            })

        if not si.items:
            frappe.throw(_("No valid items found"))

        si.insert(ignore_permissions=True)

        return {
            "status": "success",
            "message": "Sales Invoice created",
            "sales_invoice": si.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Sales Invoice Error")
        return {
            "status": "error",
            "message": str(e)
        }










@frappe.whitelist(methods=["GET"])
def list_sales_invoices(
    page=1,
    limit=20,
    search=None,
    customer=None
):
    page = int(page)
    limit = int(limit)
    start = (page - 1) * limit

    filters = {}
    if customer:
        filters["customer"] = customer

    or_filters = []
    if search:
        or_filters = [
            ["Sales Invoice", "name", "like", f"%{search}%"],
            ["Sales Invoice", "customer_name", "like", f"%{search}%"]
        ]

    # -----------------------------
    # TOTAL COUNT (NO or_filters)
    # -----------------------------
    total_records = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        pluck="name"
    )

    total = len(total_records)

    # -----------------------------
    # PAGINATED DATA
    # -----------------------------
    data = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=[
            "name",
            "customer",
            "customer_name",
            "posting_date",
            "due_date",
            "status",
            "grand_total",
            "outstanding_amount",
            "docstatus"
        ],
        start=start,
        page_length=limit,
        order_by="modified desc"
    )

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": data
    }









@frappe.whitelist(methods=["PUT", "POST"])
def update_sales_invoice(name, data=None):
    try:
        # -----------------------------
        # READ INPUT DATA
        # -----------------------------
        if not data:
            data = frappe.form_dict

        if isinstance(data, str):
            data = frappe.parse_json(data)

        # -----------------------------
        # LOAD SALES INVOICE
        # -----------------------------
        si = frappe.get_doc("Sales Invoice", name)

        # -----------------------------
        # VALIDATION
        # -----------------------------
        if si.docstatus == 1:
            frappe.throw(_("Submitted Sales Invoice cannot be updated"))

        # -----------------------------
        # UPDATE HEADER FIELDS
        # -----------------------------
        header_fields = [
            "due_date",
            "posting_date",
            "remarks"
        ]

        for field in header_fields:
            if field in data:
                setattr(si, field, data[field])

        # -----------------------------
        # UPDATE ITEMS (FULL REPLACE)
        # -----------------------------
        if "items" in data:
            if not data["items"]:
                frappe.throw(_("Items cannot be empty"))

            si.set("items", [])

            for item in data["items"]:
                if not item.get("item_code"):
                    frappe.throw(_("Item Code is required"))

                si.append("items", {
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty", 1),
                    "rate": item.get("rate", 0)
                })

        # -----------------------------
        # SAVE
        # -----------------------------
        si.save(ignore_permissions=True)

        return {
            "status": "success",
            "message": "Sales Invoice updated successfully",
            "sales_invoice": si.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Sales Invoice Error")
        return {
            "status": "error",
            "message": str(e)
        }








@frappe.whitelist(methods=["DELETE"])
def delete_sales_invoice(name):
    try:
        if not name:
            frappe.throw(_("Sales Invoice name is required"))

        si = frappe.get_doc("Sales Invoice", name)

        # -----------------------------
        # VALIDATIONS
        # -----------------------------
        if si.outstanding_amount < si.grand_total and si.docstatus == 1:
            frappe.throw(_("Cannot delete a paid or partially paid Sales Invoice"))

        # -----------------------------
        # CANCEL IF SUBMITTED
        # -----------------------------
        if si.docstatus == 1:
            si.cancel()

        # -----------------------------
        # DELETE
        # -----------------------------
        si.delete(ignore_permissions=True)

        return {
            "status": "success",
            "message": f"Sales Invoice {name} deleted successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Sales Invoice Error")
        return {
            "status": "error",
            "message": str(e)
        }
