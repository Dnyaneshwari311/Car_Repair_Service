import frappe
from frappe import _
from car_repair_service.api.utils import get_paginated_data

# ----------------------
# CREATE QUOTATION
# ----------------------
@frappe.whitelist(allow_guest=False)
def create_quotation(data):
    
    """
    Create a Quotation from JSON data.
    Example data:
    {
        "customer_name": "Customer 1",
        "remarks": "Some remarks",
        "items": [
            {"item_code": "Item-001", "qty": 2, "rate": 100}
        ]
    }
    """
    try:
        data = frappe._dict(data)
        if not data.customer_name:
            frappe.throw(_("Customer Name is required"))

        qtn = frappe.new_doc("Quotation")
        qtn.quotation_to = "Customer"
        qtn.party_name = data.customer_name
        qtn.remarks = data.get("remarks", "")

        # Add items
        for d in data.get("items", []):
            qty = float(d.get("qty") or 1)
            rate = float(d.get("rate") or 0)
            uom = frappe.db.get_value("Item", d.get("item_code"), "stock_uom") or "Nos"
            item = qtn.append("items", {})
            item.item_code = d.get("item_code")
            item.item_name = d.get("item_name") or d.get("item_code")
            item.qty = qty
            item.rate = rate
            item.uom = uom
            item.amount = qty * rate

        qtn.flags.ignore_permissions = True
        qtn.set_missing_values()
        qtn.calculate_taxes_and_totals()
        qtn.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success",
                "status_code":201,
                "quotation_name": qtn.name}

    except Exception as e:
        frappe.log_error(f"Error creating Quotation", frappe.get_traceback())
        return {"status": "error", "message": str(e)}




# ----------------------
# UPDATE QUOTATION
# ----------------------

@frappe.whitelist(allow_guest=False)
def update_quotation(quotation_name, data):
    
    """
    Add new items to an existing Quotation without removing existing items.
    """
    try:
        # Parse JSON string if needed
        if isinstance(data, str):
            data = json.loads(data)
        data = frappe._dict(data)

        qtn = frappe.get_doc("Quotation", quotation_name)

        # Add new items from data
        new_items = data.get("items") or []
        for d in new_items:
            qty = float(d.get("qty") or 1)
            rate = float(d.get("rate") or 0)
            uom = frappe.db.get_value("Item", d.get("item_code"), "stock_uom") or "Nos"

            item = qtn.append("items", {})
            item.item_code = d.get("item_code")
            item.item_name = d.get("item_name") or d.get("item_code")
            item.qty = qty
            item.rate = rate
            item.uom = uom
            item.amount = qty * rate

        qtn.flags.ignore_permissions = True
        qtn.calculate_taxes_and_totals()
        qtn.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_messages()
        return {"status": "success", 
                "status_code":201,
                "message": f"{len(new_items)} item(s) added to {quotation_name}", "quotation_name": qtn.name}

    except Exception as e:
        frappe.log_error(f"Error adding items to Quotation {quotation_name}", frappe.get_traceback())
        return {"status": "error", "message": str(e)}
    
    
    
    
    


# ----------------------
# GET QUOTATION BY ID
# ----------------------
@frappe.whitelist(allow_guest=False)
def get_quotation(quotation_name):
   
    """
    Get Quotation details by name
    """
    try:
        qtn = frappe.get_doc("Quotation", quotation_name)
        data = qtn.as_dict()
        data["items"] = [item.as_dict() for item in qtn.items]
        return {"status": "success", "quotation": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    




from urllib.parse import urljoin

@frappe.whitelist(allow_guest=False)
def quotation_list(page=1, page_size=10, search=None, sort_by="creation", sort_order="desc", is_pagination=False, **kwargs):
   
    """
    Fetch paginated Quotation list with items, search, and sorting.
    """
    try:
        is_pagination = frappe.utils.sbool(is_pagination)
        base_url = frappe.request.host_url.rstrip("/") + frappe.request.path
        del kwargs["cmd"]

        # Searchable fields
        search_fields = ["name", "customer_name", "custom_car_diagnosis"]

        # Fields to return
        return_fields = [
            "name",
            "quotation_to",
            "customer_name",
            "valid_till",
            "order_type",
            "custom_car_diagnosis",
            "grand_total",
            "status",
            "creation",
            "modified"
        ]

        # Build filters
        filters = {}
        if kwargs.get("order_type"):
            filters["order_type"] = kwargs.get("order_type")

        # Build search condition
        search_condition = ""
        if search:
            search_condition = " OR ".join([f"{field} LIKE %(search)s" for field in search_fields])

        # Build main query
        query = f"""
            SELECT {", ".join(return_fields)}
            FROM `tabQuotation`
            WHERE 1=1
        """

        # Apply filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    query += f" AND `{key}` IN %({key})s"
                else:
                    query += f" AND `{key}`=%({key})s"

        # Apply search
        if search_condition:
            query += f" AND ({search_condition})"

        query += f" ORDER BY `{sort_by}` {sort_order.upper()}"

        # Pagination
        if is_pagination:
            offset = (int(page) - 1) * int(page_size)
            query += f" LIMIT {offset}, {int(page_size)}"

        # Prepare query values
        values = filters.copy()
        if search:
            values["search"] = f"%{search}%"

        # Execute main query
        quotations = frappe.db.sql(query, values, as_dict=True)

        # Fetch items for each quotation
        for q in quotations:
            q["items"] = frappe.db.sql("""
                SELECT
                    item_code,
                    item_name,
                    qty,
                    rate,
                    amount
                FROM `tabQuotation Item`
                WHERE parent = %s
            """, (q["name"],), as_dict=True)

        # Count total records
        total_count = frappe.db.count("Quotation", filters=filters)

        # Pagination metadata
        meta = {}
        if is_pagination:
            meta = {
                "page": int(page),
                "page_size": int(page_size),
                "total_records": total_count,
                "total_pages": (total_count // int(page_size)) + (1 if total_count % int(page_size) else 0),
                "next_page": int(page) + 1 if total_count > int(page) * int(page_size) else None,
                "previous_page": int(page) - 1 if int(page) > 1 else None,
                "base_url": base_url
            }

        return {
            "status": "success",
            "status_code": 200,
            "data": quotations,
            "pagination": meta if is_pagination else None
        }

    except Exception as e:
        frappe.log_error("Quotation List Error", str(e))
        return {"status": "error", "message": str(e)}


# ----------------------
# DELETE QUOTATION
# ----------------------
@frappe.whitelist(allow_guest=False)
def delete_quotation(quotation_name):
    
    """
    Delete a Quotation by name
    """
    try:
        frappe.delete_doc("Quotation", quotation_name, ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", 
                "status_code":200,
                "message": f"Quotation {quotation_name} deleted"}
    except Exception as e:
        frappe.log_error(f"Error deleting Quotation {quotation_name}", frappe.get_traceback())
        return {"status": "error", "message": str(e)}
