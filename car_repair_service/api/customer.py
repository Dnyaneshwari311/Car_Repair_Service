import frappe
from car_repair_service.api.utils import get_paginated_data




# ---------------------------------------------------------
#................Create Customer...........................
# ---------------------------------------------------------


@frappe.whitelist()
def create_customer_and_vehicle(data=None):
    try:
        if not data:
            frappe.throw("Missing 'data' parameter")

        if isinstance(data, str):
            data = json.loads(data)

        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")
        license_plate = data.get("license_plate")
        make = data.get("make")
        model = data.get("model")

        required_fields = ["customer_name", "email", "phone", "license_plate", "make", "model"]
        for field in required_fields:
            if not data.get(field):
                frappe.throw(f"Missing required field: {field}")

        # -------------------------
        # CUSTOMER
        # -------------------------
        customer = None
        if frappe.db.exists("Customer", {"customer_name": customer_name}):
            customer = frappe.get_doc("Customer", {"customer_name": customer_name})
        if not customer and frappe.db.exists("Customer", {"email_id": email}):
            customer = frappe.get_doc("Customer", {"email_id": email})
        if not customer:
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "email_id": email,
                "mobile_no": phone,
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)

        # -------------------------
        # VEHICLE MAKE
        # -------------------------
        make_doc_name = frappe.db.get_value("Vehicle Make", {"make": make}, "name")
        if not make_doc_name:
            mk = frappe.get_doc({
                "doctype": "Vehicle Make",
                "make": make
            }).insert(ignore_permissions=True)
            make_doc_name = mk.name

        # -------------------------
        # VEHICLE MODEL
        # -------------------------
        model_doc_name = frappe.db.get_value("Vehicle Model", {"model": model}, "name")
        if not model_doc_name:
            mdl = frappe.get_doc({
                "doctype": "Vehicle Model",
                "model": model
            }).insert(ignore_permissions=True)
            model_doc_name = mdl.name

        # -------------------------
        # VEHICLE
        # -------------------------
        existing_vehicle = frappe.db.exists("Vehicle", {"license_plate": license_plate})
        if existing_vehicle:
            vehicle = frappe.get_doc("Vehicle", existing_vehicle)
        else:
            vehicle_name = f"{model}-{license_plate}"
            vehicle = frappe.get_doc({
                "doctype": "Vehicle",
                "license_plate": license_plate,
                "make": make_doc_name,
                "model": model_doc_name,
                "custom_customer_name": customer.name,
                "email": email,
                "phone": phone
            })
            vehicle.set_new_name(vehicle_name)
            vehicle.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "status_code":200,
            "message": "Customer and Vehicle created successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Customer + Vehicle API Error")
        return {
            "status": "error",
            "message": str(e)
        }



# -----------------------------------------------------------------
#.....................Update Customer..............................
# -----------------------------------------------------------------


@frappe.whitelist()
def update_customer(customer_id=None, customer_name=None, mobile_no=None, email_id=None,
                    vehicle_id=None, license_plate=None, make=None, model=None):
    from car_repair_service.api.utils import ensure_authenticated
    ensure_authenticated()

    result = {}
    message = {}

    # -------------------------
    # UPDATE CUSTOMER
    # -------------------------
    if customer_id:
        try:
            customer = frappe.get_doc("Customer", customer_id)
            updated_fields = []
            if customer_name:
                customer.customer_name = customer_name
                updated_fields.append("customer_name")
            if mobile_no:
                customer.mobile_no = mobile_no
                updated_fields.append("mobile_no")
            if email_id:
                customer.email_id = email_id
                updated_fields.append("email_id")

            customer.save(ignore_permissions=True)
            message["customer"] = {
                "name": customer.name,
                "customer_name": customer.customer_name,
                "mobile_no": customer.mobile_no,
                "email_id": customer.email_id,
                "updated_fields": updated_fields
            }
        except frappe.DoesNotExistError:
            message["customer_error"] = f"Customer '{customer_id}' not found"
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Update Customer API Error")
            message["customer_error"] = str(e)

    # -------------------------
    # UPDATE VEHICLE
    # -------------------------
    if vehicle_id:
        try:
            vehicle = frappe.get_doc("Vehicle", vehicle_id)
            updated_fields = []

            if license_plate:
                vehicle.license_plate = license_plate
                updated_fields.append("license_plate")

            if make:
                make_doc_name = frappe.db.get_value("Vehicle Make", {"make": make}, "name")
                if not make_doc_name:
                    mk = frappe.get_doc({"doctype": "Vehicle Make", "make": make}).insert(ignore_permissions=True)
                    make_doc_name = mk.name
                vehicle.make = make_doc_name
                updated_fields.append("make")

            if model:
                model_doc_name = frappe.db.get_value("Vehicle Model", {"model": model}, "name")
                if not model_doc_name:
                    mdl = frappe.get_doc({"doctype": "Vehicle Model", "model": model}).insert(ignore_permissions=True)
                    model_doc_name = mdl.name
                vehicle.model = model_doc_name
                updated_fields.append("model")

            vehicle.save(ignore_permissions=True)
            message["vehicle"] = {
                "name": vehicle.name,
                "license_plate": vehicle.license_plate,
                "make": frappe.get_value("Vehicle Make", vehicle.make, "make"),
                "model": frappe.get_value("Vehicle Model", vehicle.model, "model"),
                "updated_fields": updated_fields
            }
        except frappe.DoesNotExistError:
            message["vehicle_error"] = f"Vehicle '{vehicle_id}' not found"
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Update Vehicle API Error")
            message["vehicle_error"] = str(e)

    frappe.db.commit()

    if not message:
        return {"status": "error", "message": "No Customer or Vehicle ID provided"}

    result["status"] = "success"
    result["message"] = message

    return result

# -------------------------------------------------------
#......................Delete Customer...................
# -------------------------------------------------------

@frappe.whitelist()
def delete_customer_and_vehicles(customer_id, force=False):
    """
    Delete a Customer AND all linked Vehicles.
    :param customer_id: Customer document name (e.g., CUST-0001)
    :param force: pass true to force delete even if linked
    """

    from car_repair_service.api.utils import ensure_authenticated
    ensure_authenticated()

    if not customer_id:
        return {"status": "error", "message": "Customer ID is required"}

    try:
        # Check customer exists
        customer = frappe.get_doc("Customer", customer_id)

        # Find all vehicles linked to this customer
        vehicles = frappe.db.get_all(
            "Vehicle",
            filters={"custom_customer_name": customer_id},
            fields=["name"]
        )

        deleted_vehicles = []

        # Delete all vehicles first
        for v in vehicles:
            try:
                frappe.delete_doc(
                    doctype="Vehicle",
                    name=v.name,
                    force=frappe.utils.cint(force),
                    ignore_permissions=True
                )
                deleted_vehicles.append(v.name)

            except frappe.LinkExistsError as e:
                return {
                    "status": "error",
                    "message": f"Cannot delete vehicle '{v.name}', linked to other documents",
                    "linked_doctype": str(e)
                }

        # Now delete the customer
        frappe.delete_doc(
            doctype="Customer",
            name=customer_id,
            force=frappe.utils.cint(force),
            ignore_permissions=True
        )

        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Customer '{customer_id}' and all linked vehicles deleted",
            "customer_id": customer_id,
            
        }

    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"Customer '{customer_id}' not found"}

    except Exception as e:
        frappe.log_error(title="Delete Customer + Vehicles Error", message=frappe.get_traceback())
        return {"status": "error", "message": str(e)}




# --------------------------------------------------------
#....................List all Customers & Vehicle.........
# --------------------------------------------------------
@frappe.whitelist()
def customer_vehicle_list(page=1, page_size=10, search=None, sort_by="c.creation", sort_order="desc"):
    """Return Customer + Vehicle list with pagination, search, sorting"""

    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    vals = {}

    # SEARCH FILTER
    search_filter = ""
    if search:
        search_filter = """
            AND (
                c.customer_name LIKE %(search)s
                OR c.email_id LIKE %(search)s
                OR c.mobile_no LIKE %(search)s
                OR v.license_plate LIKE %(search)s
                OR vmk.make LIKE %(search)s
                OR vmd.model LIKE %(search)s
            )
        """
        vals["search"] = f"%{search}%"

    # ALLOWED SORT FIELDS
    allowed_sort_fields = {
        "customer_name": "c.customer_name",
        "email": "c.email_id",
        "phone": "c.mobile_no",
        "license_plate": "v.license_plate",
        "make": "vmk.make",
        "model": "vmd.model",
        "customer_creation": "c.creation",
        "vehicle_creation": "v.creation",
    }

    sort_by = allowed_sort_fields.get(sort_by, "c.creation")
    sort_order = "asc" if sort_order.lower() == "asc" else "desc"

    # MAIN QUERY
    query = f"""
        SELECT
            c.name AS customer_id,
            c.customer_name,
            c.email_id,
            c.mobile_no,
           
            v.license_plate,
            
            vmk.make AS make,
            vmd.model AS model

        FROM `tabCustomer` c
        LEFT JOIN `tabVehicle` v 
            ON v.custom_customer_name = c.name

        LEFT JOIN `tabVehicle Make` vmk
            ON vmk.name = v.make

        LEFT JOIN `tabVehicle Model` vmd
            ON vmd.name = v.model

        WHERE c.disabled = 0
        {search_filter}
        ORDER BY {sort_by} {sort_order}
        LIMIT %(limit)s OFFSET %(offset)s
    """

    vals["limit"] = page_size
    vals["offset"] = offset
    data = frappe.db.sql(query, vals, as_dict=True)

    # COUNT QUERY
    count_query = f"""
        SELECT COUNT(*)
        FROM `tabCustomer` c
        LEFT JOIN `tabVehicle` v 
            ON v.custom_customer_name = c.name
        LEFT JOIN `tabVehicle Make` vmk ON vmk.name = v.make
        LEFT JOIN `tabVehicle Model` vmd ON vmd.name = v.model
        WHERE c.disabled = 0
        {search_filter}
    """

    total = frappe.db.sql(count_query, vals)[0][0]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": data
    }
