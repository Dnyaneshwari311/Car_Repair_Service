import frappe
from frappe import _
import json
from car_repair_service.api.utils import get_paginated_data


# -------------------------
# Create Vehicle
# -------------------------_

@frappe.whitelist(allow_guest=False)
def create_vehicle(data=None):
    
    try:
        if not data:
            data = frappe.request.get_json(silent=True)

        if not data:
            frappe.throw(_("Missing 'data' parameter"))

        if isinstance(data, str):
            data = json.loads(data)

        license_plate = data.get("license_plate")
        make = data.get("make")
        model = data.get("model")
        chassis_no = data.get("chassis_no")

        if not (license_plate and make and model):
            frappe.throw(_("License Plate, Make, and Model are mandatory"))

        # Create Make if not exists
        make_name = frappe.db.exists("Vehicle Make", {"make": make})
        if not make_name:
            make_doc = frappe.get_doc({"doctype": "Vehicle Make", "make": make})
            make_doc.insert(ignore_permissions=True)
            make_name = make_doc.name
        else:
            make_doc = frappe.get_doc("Vehicle Make", make_name)

        # Create Model if not exists
        model_name = frappe.db.exists("Vehicle Model", {"model": model})
        if not model_name:
            model_doc = frappe.get_doc({"doctype": "Vehicle Model", "model": model})
            model_doc.insert(ignore_permissions=True)
            model_name = model_doc.name
        else:
            model_doc = frappe.get_doc("Vehicle Model", model_name)

        # Create or update Vehicle
        vehicle_name = frappe.db.exists("Vehicle", {"license_plate": license_plate})
        if vehicle_name:
            vehicle = frappe.get_doc("Vehicle", vehicle_name)
            vehicle.update({
                "make": make_name,
                "model": model_name,
                "chassis_no": chassis_no or vehicle.chassis_no
            })
            vehicle.save(ignore_permissions=True)
            action = "updated"
        else:
            vehicle = frappe.get_doc({
                "doctype": "Vehicle",
                "license_plate": license_plate,
                "make": make_name,
                "model": model_name,
                "chassis_no": chassis_no
            }).insert(ignore_permissions=True)
            action = "created"

        # Replace make and model values with display names
        vehicle_info = vehicle.as_dict()
        vehicle_info["make"] = make_doc.make      # Human readable
        vehicle_info["model"] = model_doc.model    # Human readable
        frappe.clear_messages()
        return {
            "status": "success",
            "status_code":201,
            "message": f"Vehicle {action} successfully",
            "vehicle":vehicle.name
           
        }

    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {"status": "error", "message": str(e)}

# -------------------------
# Get Vehicle by License Plate
# -------------------------
@frappe.whitelist(allow_guest=False)
def get_vehicle(license_plate):
   
    """
    Fetch a single vehicle using its license_plate.
    """
    vehicle = frappe.get_value("Vehicle", {"license_plate": license_plate}, "*")
    if not vehicle:
        frappe.throw("Vehicle not found", frappe.DoesNotExistError)

    return {"status": "success", 
            "status_code":201,
            "vehicle": vehicle}


# -------------------------
# Update Vehicle
# -------------------------


@frappe.whitelist(allow_guest=False)
def update_vehicle(license_plate, data=None):
  
    """
    Update vehicle details. Only passed fields will be updated.
    Example JSON:
    {
        "make": "Tata",
        "model": "Punch",
        "chassis_no": "12345XYZ",
        "customer": "Customer Name"
    }
    """
    try:
        if not data:
            data = frappe.request.get_json(silent=True)

        if not data:
            frappe.throw(_("Missing 'data' parameter"))

        # Convert string to dict if needed
        if isinstance(data, str):
            data = json.loads(data)

        # Fetch Vehicle by license_plate
        vehicle = frappe.get_doc("Vehicle", {"license_plate": license_plate})

        updated_fields = []

        # Handle Make
        if "make" in data:
            make = data.get("make")
            make_name = frappe.db.exists("Vehicle Make", {"make": make})
            if not make_name:
                make_doc = frappe.get_doc({"doctype": "Vehicle Make", "make": make})
                make_doc.insert(ignore_permissions=True)
                make_name = make_doc.name
            vehicle.set("make", make_name)
            updated_fields.append("make")

        # Handle Model
        if "model" in data:
            model = data.get("model")
            model_name = frappe.db.exists("Vehicle Model", {"model": model})
            if not model_name:
                model_doc = frappe.get_doc({"doctype": "Vehicle Model", "model": model})
                model_doc.insert(ignore_permissions=True)
                model_name = model_doc.name
            vehicle.set("model", model_name)
            updated_fields.append("model")

        # Handle other fields
        for key, value in data.items():
            if key not in ["make", "model"] and vehicle.get(key) is not None:
                vehicle.set(key, value)
                updated_fields.append(key)

        vehicle.save(ignore_permissions=True)

        vehicle_info = vehicle.as_dict()

        # Get readable make and model
        if vehicle.make:
            vehicle_info["make"] = frappe.db.get_value("Vehicle Make", vehicle.make, "make")
        if vehicle.model:
            vehicle_info["model"] = frappe.db.get_value("Vehicle Model", vehicle.model, "model")
        frappe.clear_messages()
        return {
            "status": "success",
            "message": _("Vehicle updated successfully"),
            "updated_fields": updated_fields,
            "vehicle": vehicle_info
        }

    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {"status": "error", "message": str(e)}


# -------------------------
# Delete Vehicle
# -------------------------
@frappe.whitelist(allow_guest=False)
def delete_vehicle(license_plate):
    
    """
    Delete a vehicle by license_plate.
    """
    try:
        doc = frappe.get_doc("Vehicle", {"license_plate": license_plate})
        doc.delete()
        frappe.db.commit()

        return {"status": "success",
                "status_code":201, 
                "message": f"Vehicle '{license_plate}' deleted."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Vehicle Error")
        frappe.throw(str(e))











# @frappe.whitelist(allow_guest=False)
# def list_vehicle(filters=None, limit_start=0, limit_page_length=10):
   
#     """
#     Fetch paginated list of vehicles with optional filters.
#     Example:
#     /api/method/car_repair_service.api.vehicle_api.get_vehicles?filters={"make": "Tata"}&limit_start=0&limit_page_length=5
#     """
#     try:
#         # Convert filters from string to dict
#         if filters:
#             if isinstance(filters, str):
#                 filters = json.loads(filters)
#         else:
#             filters = {}

#         # Get total count for pagination
#         total_count = frappe.db.count("Vehicle", filters)

#         # Fetch paginated vehicles
#         vehicles = frappe.get_all(
#             "Vehicle",
#             filters=filters,
#             fields=[
#                 "name", "license_plate", "make", "model", "chassis_no","car_manufacturing_year", "modified","custom_customer_name"
#             ],
#             order_by="modified desc",
#             limit_start=int(limit_start),
#             limit_page_length=int(limit_page_length),
#         )

#         # Convert make/model to human-readable
#         for v in vehicles:
#             if v.get("make"):
#                 v["make"] = frappe.db.get_value("Vehicle Make", v["make"], "make")
#             if v.get("model"):
#                 v["model"] = frappe.db.get_value("Vehicle Model", v["model"], "model")

#         return {
#             "status": "success",
#             "message": _("Vehicles fetched successfully"),
#             "total": total_count,
#             "page_size": int(limit_page_length),
#             "page_start": int(limit_start),
#             "data": vehicles
#         }

#     except Exception as e:
#         frappe.local.response.http_status_code = 500
#         return {"status": "error", "message": str(e)}



@frappe.whitelist(allow_guest=False)
def list_vehicle(
    custom_customer_name=None,
    make=None,
    model=None,
    search=None,
    limit_start=0,
    limit_page_length=10
):
    """
    Fetch paginated list of vehicles
    Search works on:
    - Customer Name
    - Vehicle Make (linked doctype)
    - Vehicle Model (linked doctype)
    """

    try:
        conditions = []
        values = {}

        # -----------------------------
        # SEARCH (OR CONDITION)
        # -----------------------------
        if search:
            conditions.append("""
                (
                    v.custom_customer_name LIKE %(search)s OR
                    vm.make LIKE %(search)s OR
                    vmo.model LIKE %(search)s
                )
            """)
            values["search"] = f"%{search}%"

        # -----------------------------
        # CUSTOMER NAME FILTER
        # -----------------------------
        if custom_customer_name:
            conditions.append("v.custom_customer_name LIKE %(custom_customer_name)s")
            values["custom_customer_name"] = f"%{custom_customer_name}%"

        # -----------------------------
        # MAKE FILTER (DOCNAME)
        # -----------------------------
        if make:
            conditions.append("v.make = %(make)s")
            values["make"] = make

        # -----------------------------
        # MODEL FILTER (DOCNAME)
        # -----------------------------
        if model:
            conditions.append("v.model = %(model)s")
            values["model"] = model

        where_clause = " AND ".join(conditions)
        if where_clause:
            where_clause = "WHERE " + where_clause

        # -----------------------------
        # TOTAL COUNT
        # -----------------------------
        total_count = frappe.db.sql(
            f"""
            SELECT COUNT(*)
            FROM `tabVehicle` v
            LEFT JOIN `tabVehicle Make` vm ON vm.name = v.make
            LEFT JOIN `tabVehicle Model` vmo ON vmo.name = v.model
            {where_clause}
            """,
            values
        )[0][0]

        # -----------------------------
        # FETCH VEHICLES
        # -----------------------------
        vehicles = frappe.db.sql(
            f"""
            SELECT
                v.name,
                v.license_plate,
                v.make,
                vm.make AS make_name,
                v.model,
                vmo.model AS model_name,
                v.chassis_no,
                v.car_manufacturing_year,
                v.modified,
                v.custom_customer_name
            FROM `tabVehicle` v
            LEFT JOIN `tabVehicle Make` vm ON vm.name = v.make
            LEFT JOIN `tabVehicle Model` vmo ON vmo.name = v.model
            {where_clause}
            ORDER BY v.modified DESC
            LIMIT %(start)s, %(page_len)s
            """,
            {
                **values,
                "start": int(limit_start),
                "page_len": int(limit_page_length)
            },
            as_dict=True
        )

        return {
            "status": "success",
            "message": _("Vehicles fetched successfully"),
            "total": total_count,
            "page_size": int(limit_page_length),
            "page_start": int(limit_start),
            "data": vehicles,
        }

    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {
            "status": "error",
            "message": str(e)
        }




@frappe.whitelist(allow_guest=False)
def list_vehicle_by_customer(customer):
    """
    Fetch all license plates for a given customer.
    Example:
    /api/method/car_repair_service.api.vehicle_api.list_vehicle_by_customer?customer=Customer%20A
    """
    try:
        if not customer:
            frappe.throw("Customer name is required")

        # Fetch vehicles for this customer
        vehicles = frappe.get_all(
            "Vehicle",
            filters={"custom_customer_name": customer},
            fields=["license_plate"],
            order_by="modified desc"
        )

        # Extract license_plate values
        license_plates = [v["license_plate"] for v in vehicles]

        return {
            "status": "success",
            "message": _("License plates fetched successfully"),
            "customer": customer,
            "total": len(license_plates),
            "license_plates": license_plates
        }

    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {"status": "error", "message": str(e)}








import frappe
import json
from frappe import _

@frappe.whitelist(allow_guest=False)
def list_vehicles(
    filters=None,
    customer=None,
    limit_start=0,
    limit_page_length=10,
    only_license_plates=0
):
    """
    Fetch vehicles with optional pagination or only license plates by customer.

    Examples:
    1) Full vehicle list:
       /api/method/car_repair_service.api.vehicle_api.list_vehicle

    2) Vehicles by customer:
       /api/method/car_repair_service.api.vehicle_api.list_vehicle?customer=Customer%20A

    3) Only license plates:
       /api/method/car_repair_service.api.vehicle_api.list_vehicle?customer=Customer%20A&only_license_plates=1
    """
    try:
        # Convert flags
        only_license_plates = frappe.utils.sbool(only_license_plates)
        limit_start = int(limit_start)
        limit_page_length = int(limit_page_length)

        # Parse filters
        if filters:
            if isinstance(filters, str):
                filters = json.loads(filters)
        else:
            filters = {}

        # Customer filter
        if customer:
            filters["custom_customer_name"] = customer

        # ---------------------------
        # ONLY LICENSE PLATES MODE
        # ---------------------------
        if only_license_plates:
            if not customer:
                frappe.throw(_("Customer is required for license plate list"))

            vehicles = frappe.get_all(
                "Vehicle",
                filters=filters,
                fields=["license_plate"],
                order_by="modified desc"
            )

            license_plates = [v["license_plate"] for v in vehicles]

            return {
                "status": "success",
                "message": _("License plates fetched successfully"),
                "customer": customer,
                "total": len(license_plates),
                "license_plates": license_plates
            }

        # ---------------------------
        # FULL VEHICLE LIST MODE
        # ---------------------------
        total_count = frappe.db.count("Vehicle", filters)

        vehicles = frappe.get_all(
            "Vehicle",
            filters=filters,
            fields=[
                "name",
                "license_plate",
                "make",
                "model",
                "chassis_no",
                "car_manufacturing_year",
                "modified",
                "custom_customer_name"
            ],
            order_by="modified desc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

        # Convert make/model to readable names
        for v in vehicles:
            if v.get("make"):
                v["make"] = frappe.db.get_value("Vehicle Make", v["make"], "make")
            if v.get("model"):
                v["model"] = frappe.db.get_value("Vehicle Model", v["model"], "model")

        return {
            "status": "success",
            "message": _("Vehicles fetched successfully"),
            "total": total_count,
            "page_size": limit_page_length,
            "page_start": limit_start,
            "data": vehicles
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "list_vehicle API Error")
        frappe.local.response.http_status_code = 500
        return {
            "status": "error",
            "message": str(e)
        }
