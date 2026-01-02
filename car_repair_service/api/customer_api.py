import frappe
from car_repair_service.api.utils import get_paginated_data


#................Create Customer...............
@frappe.whitelist(allow_guest=False)
def create_customer(customer_name, mobile_no=None, email_id=None):
    
    
    doc = frappe.new_doc("Customer")
    doc.customer_name = customer_name
    doc.mobile_no = mobile_no
    doc.email_id = email_id
    doc.insert(ignore_permissions=True) 
    frappe.db.commit()
    return {"status": "success", 
            "message": "Customer created", 
            "data": doc
            }



#.................Get Customer...................

@frappe.whitelist(allow_guest=False)
def get_customer(search=None):
    if not search:
        return {"status": "error", "message": "Search parameter is required"}

    customers = frappe.db.get_all(
        "Customer",
        filters={},
        or_filters=[
            ["name", "like", f"%{search}%"],
            ["customer_name", "like", f"%{search}%"],
            ["mobile_no", "like", f"%{search}%"],
            ["email_id", "like", f"%{search}%"],
        ],
        fields=["name", "customer_name", "mobile_no", "email_id"],
        limit_page_length=1
    )

    if customers:
        return {"status": "success", "data": customers[0]}

    return {"status": "error", 
            "message": f"No customer found for '{search}'"}


 
#.....................Update Customer...............................
@frappe.whitelist(allow_guest=False)
def update_customer(customer_id, customer_name=None, mobile_no=None, email_id=None):
    try:
        # Fetch customer document
        doc = frappe.get_doc("Customer", customer_id)
    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": f"Customer '{customer_id}' not found"
        }

    # Update only provided fields
    if customer_name:
        doc.customer_name = customer_name
    if mobile_no:
        doc.mobile_no = mobile_no
    if email_id:
        doc.email_id = email_id

    # Save and commit changes
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "message": "Customer updated successfully",
        "data": {
            "name": doc.name,
            "customer_name": doc.customer_name,
            "mobile_no": doc.mobile_no,
            "email_id": doc.email_id
        }
    }

#......................Delete Customer...................

@frappe.whitelist(allow_guest=False)
def delete_customer(customer_id, force=False):
    """
    Delete Customer by ID
    :param customer_id: name of customer doc (e.g. CUST-0001)
    :param force: pass true to force delete even if linked (optional)
    """

    if not customer_id:
        return {"status": "error", "message": "Customer ID is required"}

    try:
        # Check if customer exists
        frappe.get_doc("Customer", customer_id)

        # Delete doc safely
        frappe.delete_doc(
            doctype="Customer",
            name=customer_id,
            force=frappe.utils.cint(force),  # force delete if needed
            ignore_permissions=True
        )

        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Customer '{customer_id}' deleted successfully",
            "customer_id": customer_id
        }

    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"Customer '{customer_id}' not found"}

    except frappe.LinkExistsError as e:
        return {
            "status": "error",
            "message": f"Cannot delete, linked with other documents",
            "linked_doctype": str(e)
        }

    except Exception as e:
        frappe.log_error(title="Delete Customer Error", message=str(e))
        return {"status": "error", "message": str(e)}



#....................List all Customers...................


from frappe.utils import cint

@frappe.whitelist()
def list_customers(
    page=1,
    page_size=20,
    search=None,
    order_by="customer_name asc",
    **filters
):
    """
    ERPNext default-style Customer list API
    """

    page = cint(page)
    page_size = cint(page_size)
    start = (page - 1) * page_size

    # Remove internal param
    filters.pop("cmd", None)

    # -----------------------------
    # ERPNext default OR search
    # -----------------------------
    or_filters = []
    if search:
        or_filters = [
            ["Customer", "customer_name", "like", f"%{search}%"],
            ["Customer", "mobile_no", "like", f"%{search}%"],
            ["Customer", "email_id", "like", f"%{search}%"],
        ]

    # -----------------------------
    # Fetch paginated data
    # -----------------------------
    customers = frappe.get_list(
        "Customer",
        fields=[
            "name",
            "customer_name",
            "mobile_no",
            "email_id",
            "disabled"
        ],
        filters=filters,
        or_filters=or_filters,
        order_by=order_by,
        limit_start=start,
        limit_page_length=page_size,
        ignore_permissions=False   # ✅ ERP behavior
    )

    # -----------------------------
    # ERPNext way to get total count
    # -----------------------------
    total_count = len(
        frappe.get_all(
            "Customer",
            filters=filters,
            or_filters=or_filters,
            limit_page_length=0,
            ignore_permissions=False
        )
    )

    return {
        "data": customers,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    }
