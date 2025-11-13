import frappe
from car_repair_service.api.utils import get_paginated_data


#................Create Customer...............
@frappe.whitelist()
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

@frappe.whitelist()
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
@frappe.whitelist()
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

@frappe.whitelist()
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
@frappe.whitelist()
def list_customers(
    page=1,
    page_size=10,
    search=None,
    sort_by="customer_name",
    sort_order="asc",
    is_pagination=False,
    **kwargs
):
    """
    Fetch paginated Customer list with filters, search, sorting, and optional pagination.
    """

    is_pagination = frappe.utils.sbool(is_pagination)  # convert "true"/"false" to bool
    extra_params = {"search": search} if search else {}

    # Remove frappe default param
    kwargs.pop("cmd", None)

    # 🔹 Collect filters from query params
    filters = {}
    for key, val in kwargs.items():
        if val not in [None, ""]:
            filters[key] = val

    print("Customer Filters =>", filters)

    # ✅ Safe base_url handling
    try:
        base_url = frappe.request.host_url.rstrip("/") + frappe.request.path
    except Exception:
        base_url = ""   # fallback when frappe.request doesn't exist

    return get_paginated_data(
        doctype="Customer",
        fields=["name", "customer_name", "mobile_no", "email_id", "disabled"],
        filters=filters,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=int(page),
        page_size=int(page_size),
        search_fields=["customer_name", "mobile_no", "email_id"],
        is_pagination=is_pagination,
        base_url=base_url,
        extra_params=extra_params
    )
