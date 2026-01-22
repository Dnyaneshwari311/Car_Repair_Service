import frappe
from frappe import _
from car_repair_service.api.role_validation import validate_api_access

@frappe.whitelist(methods=["POST"])
def create_sales_invoice_from_car_repair(car_repair_name):
    try:
        
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "Administrator" not in roles and "Receptionist" not in roles:
           
            return {
            "status": "error",
           "message": "You are not allowed to Create Sales Invoice"
        } 

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
                "item_name": d.part_required,
                "qty": d.quantity,
                "rate": d.estimated_cost
            })

        if not si.items:
            frappe.throw(_("No valid items found"))

        si.insert(ignore_permissions=True)

        return {
            "status": "success",
            "status_code": 200,
            "message": "Sales Invoice created",
            "sales_invoice": si.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Sales Invoice Error")
        return {
            "status": "error",
            "message": str(e)
        }










@frappe.whitelist(methods=["GET"], allow_guest=False)
def list_sales_invoices(
    page=1,
    limit=20,
    search=None,
    customer=None
):
    try:
        # --------------------------------------------------
        # ROLE CHECK
        # --------------------------------------------------
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "Administrator" not in roles and "Receptionist" not in roles:
           
            return {
            "status": "error",
           "message": "You are not allowed to View Sales Invoice"
        } 

        # --------------------------------------------------
        # PAGINATION
        # --------------------------------------------------
        page = int(page)
        limit = int(limit)
        start = (page - 1) * limit

        # --------------------------------------------------
        # FILTERS
        # --------------------------------------------------
        filters = {}
        if customer:
            filters["customer"] = customer

        or_filters = []
        if search:
            or_filters = [
                ["Sales Invoice", "name", "like", f"%{search}%"],
                ["Sales Invoice", "customer_name", "like", f"%{search}%"]
            ]

        # --------------------------------------------------
        # TOTAL COUNT
        # --------------------------------------------------
        total = frappe.db.count(
            "Sales Invoice",
            filters=filters
        )

        # --------------------------------------------------
        # FETCH SALES INVOICES
        # --------------------------------------------------
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            or_filters=or_filters if or_filters else None,
            fields=[
                "name",
                "customer",
                "customer_name",
                "posting_date",
                "posting_time",
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

        # --------------------------------------------------
        # FETCH ITEMS FOR EACH INVOICE
        # --------------------------------------------------
        for inv in invoices:
            inv["items"] = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": inv["name"]},
                fields=[
                    "item_code",
                    "item_name",
                    "qty",
                    "rate",
                    "amount"
                ]
            )

        return {
            "status": "success",
            "status_code": 200,
            "page": page,
            "limit": limit,
            "total": total,
            "data": invoices
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "List Sales Invoices Error")
        return {
            "status": "error",
            "message": str(e)
        }






@frappe.whitelist(methods=["PUT", "POST"])
def update_sales_invoice(name, data=None):
    try:
        
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "Administrator" not in roles and "Receptionist" not in roles:
           
            return {
            "status": "error",
           "message": "You are not allowed to update Sales Invoice"
    }
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
        
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "Administrator" not in roles and "Receptionist" not in roles:
           
            return {
            "status": "error",
           "message": "You are not allowed to delete Sales Invoice"
    }
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










@frappe.whitelist(methods=["GET"], allow_guest=False)
def get_sales_invoice(name):
    try:
        # --------------------------------------------------
        # ROLE CHECK
        # --------------------------------------------------
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "Administrator" not in roles and "Receptionist" not in roles:
           
            return {
            "status": "error",
           "message": "You are not allowed to View Sales Invoice"
        } 

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------
        if not name:
            frappe.throw(_("Sales Invoice name is required"))

        if not frappe.db.exists("Sales Invoice", name):
            frappe.throw(_("Sales Invoice not found"))

        # --------------------------------------------------
        # FETCH INVOICE
        # --------------------------------------------------
        si = frappe.get_doc("Sales Invoice", name)

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------
        return {
            "status": "success",
            "status_code": 200,
            "data": {
                "name": si.name,
                "customer": si.customer,
                "customer_name": si.customer_name,
                "company": si.company,
                "posting_time": si.posting_time,
                "posting_date": si.posting_date,
                "due_date": si.due_date,
                "status": si.status,
                "remarks": si.remarks,
                "docstatus": si.docstatus,
                "currency": si.currency,
                "grand_total": si.grand_total,
                "outstanding_amount": si.outstanding_amount,
                "items": [
                    {
                        "item_code": d.item_code,
                        "item_name": d.item_name,
                        "qty": d.qty,
                        "rate": d.rate,
                        "amount": d.amount,
                    }
                    for d in si.items
                ],
                "taxes": [
                    {
                        "charge_type": t.charge_type,
                        "account_head": t.account_head,
                        "rate": t.rate,
                        "tax_amount": t.tax_amount,
                    }
                    for t in si.taxes
                ],
            },
        }

    except frappe.PermissionError:
        raise

    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": "Sales Invoice not found",
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Sales Invoice Error")
        return {
            "status": "error",
            "message": str(e),
        }








@frappe.whitelist(methods=["GET", "POST"])
def download_sales_invoice_pdf(name):
    try:
        
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "Administrator" not in roles and "Receptionist" not in roles:
           
            return {
            "status": "error",
           "message": "You are not allowed to download Sales Invoice"
    }
        if not name:
            frappe.throw(_("Sales Invoice name is required"))

        # Permission check (important)
        frappe.has_permission("Sales Invoice", "read", throw=True)

        pdf_data = frappe.get_print(
            doctype="Sales Invoice",
            name=name,
            print_format="Standard",
            as_pdf=True
        )

        frappe.response.filename = f"Sales-Invoice-{name}.pdf"
        frappe.response.filecontent = pdf_data
        frappe.response.type = "download"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Download Sales Invoice PDF Error")
        frappe.throw(str(e))
