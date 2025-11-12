import frappe
from frappe import _
import json

# ====================================================
# CREATE Car Repair Request (with Auto Customer + Email)
# ====================================================


# @frappe.whitelist(allow_guest=True)
# def create_car_repair_request(data):
#     """
#     Create a new Car Repair Request:
#     - Auto-creates Customer if not exists
#     - Ensures Vehicle Make/Model exist
#     - Inserts Car Repair Request record
#     (Email is handled by after_insert event)
#     """
#     try:
#         data = json.loads(data) if isinstance(data, str) else data

#         # ====================================================
#         # ✅ Step 1: Auto-create Customer if not exists
#         # ====================================================
#         customer_name = data.get("customer_name")
#         email = data.get("email")
#         phone = data.get("phone")

#         customer_id = None

#         if email and customer_name:
#             existing_customer = frappe.db.exists("Customer", {"email_id": email})
#             if not existing_customer:
#                 customer = frappe.new_doc("Customer")
#                 customer.customer_name = customer_name
#                 customer.email_id = email
#                 customer.mobile_no = phone
#                 customer.customer_group = "Individual"
#                 customer.territory = "All Territories"
#                 customer.insert(ignore_permissions=True)
#                 frappe.msgprint(f"✅ Customer {customer.customer_name} created successfully.")
#                 customer_id = customer.name
#             else:
#                 customer_id = existing_customer
#         else:
#             frappe.throw("Missing customer_name or email for Customer creation")

#         # ====================================================
#         # ✅ Step 2: Ensure Vehicle Make & Model exist
#         # ====================================================
#         make = data.get("make")
#         model = data.get("model")

#         if make and not frappe.db.exists("Vehicle Make", {"make": make}):
#             vehicle_make = frappe.new_doc("Vehicle Make")
#             vehicle_make.make = make
#             vehicle_make.insert(ignore_permissions=True)
#             frappe.msgprint(f"✅ Created new Vehicle Make: {make}")

#         if model and not frappe.db.exists("Vehicle Model", {"model": model}):
#             vehicle_model = frappe.new_doc("Vehicle Model")
#             vehicle_model.model = model
#             vehicle_model.insert(ignore_permissions=True)
#             frappe.msgprint(f"✅ Created new Vehicle Model: {model}")

#         # ====================================================
#         # ✅ Step 3: Create Car Repair Request
#         # ====================================================
#         frappe.flags.in_create_car_repair_api = True  # helps avoid re-trigger in hooks

#         doc = frappe.new_doc("Car Repair Request")
#         fields = [
#             "email", "phone", "make", "model", "assign_adviser",
#             "car", "license_plate", "chassis_no", "car_manufacturing_year",
#             "odometer_photo", "priority", "service_type", "repair_request_date",
#             "driver_name", "driver_mob_no", "odometer_value", "fuel_level",
#             "vehicle_pick_up", "customer_signature", "remark", "fuel_type"
#         ]

#         # --- Set all main fields dynamically ---
#         for f in fields:
#             if f in data:
#                 doc.set(f, data[f])

#         # ✅ Link correct Customer name
#         doc.customer = customer_id

#         # --- Child Table: Vehicle Concerns ---
#         if "vehicle_concern" in data and isinstance(data["vehicle_concern"], list):
#             for vc in data["vehicle_concern"]:
#                 doc.append("vehicle_concern", {"vehicle_concern": vc.get("vehicle_concern")})

#         # --- Child Table: Car Repair Images ---
#         if "car_repair_images" in data and isinstance(data["car_repair_images"], list):
#             for img in data["car_repair_images"]:
#                 doc.append("car_repair_images", {"image": img.get("image")})

#         # --- Save document ---
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()

#         # Email is sent automatically in after_insert hook
#         return {
#             "status": "success",
#             "message": "Car Repair Request created successfully (Customer + Make/Model handled)",
#             "name": doc.name
#         }

#     except Exception as e:
#         frappe.log_error("Create Car Repair Request Error", str(e))
#         return {"status": "error", "message": str(e)}







@frappe.whitelist(allow_guest=True)
def create_car_repair_request(data):
    """
    Create a new Car Repair Request:
    - Auto-creates Customer if not exists
    - Ensures Vehicle Make/Model exist
    - Inserts Car Repair Request record
    - Populates customer_name field
    (Email is handled by after_insert event)
    """
    try:
        data = json.loads(data) if isinstance(data, str) else data

        # ====================================================
        # Step 1: Auto-create Customer if not exists
        # ====================================================
        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")

        if not customer_name or not email:
            frappe.throw("Missing customer_name or email for Customer creation")

        existing_customer_name = frappe.db.exists("Customer", {"email_id": email})
        if existing_customer_name:
            customer_doc = frappe.get_doc("Customer", existing_customer_name)
        else:
            customer_doc = frappe.new_doc("Customer")
            customer_doc.customer_name = customer_name
            customer_doc.email_id = email
            customer_doc.mobile_no = phone
            customer_doc.customer_group = "Individual"
            customer_doc.territory = "All Territories"
            customer_doc.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Customer {customer_doc.customer_name} created successfully.")

        # ====================================================
        # Step 2: Ensure Vehicle Make & Model exist
        # ====================================================
        make = data.get("make")
        model = data.get("model")

        if make and not frappe.db.exists("Vehicle Make", {"make": make}):
            vehicle_make = frappe.new_doc("Vehicle Make")
            vehicle_make.make = make
            vehicle_make.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Created new Vehicle Make: {make}")

        if model and not frappe.db.exists("Vehicle Model", {"model": model}):
            vehicle_model = frappe.new_doc("Vehicle Model")
            vehicle_model.model = model
            vehicle_model.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Created new Vehicle Model: {model}")

        # ====================================================
        # Step 3: Create Car Repair Request
        # ====================================================
        frappe.flags.in_create_car_repair_api = True  # avoids re-trigger in hooks

        doc = frappe.new_doc("Car Repair Request")

        # --- Main fields to set dynamically ---
        fields = [
            "email", "phone", "make", "model", "assign_adviser",
            "car", "license_plate", "chassis_no", "car_manufacturing_year",
            "odometer_photo", "priority", "service_type", "repair_request_date",
            "driver_name", "driver_mob_no", "odometer_value", "fuel_level",
            "vehicle_pick_up", "customer_signature", "remark", "fuel_type"
        ]
        for f in fields:
            if f in data:
                doc.set(f, data[f])

        # ✅ Link correct Customer and set customer_name
        doc.customer = customer_doc.name
        doc.customer_name = customer_doc.customer_name

        # --- Child Table: Vehicle Concerns ---
        for vc in data.get("vehicle_concern", []):
            doc.append("vehicle_concern", {"vehicle_concern": vc.get("vehicle_concern")})

        # --- Child Table: Car Repair Images ---
        for img in data.get("car_repair_images", []):
            doc.append("car_repair_images", {"image": img.get("image")})

        # --- Insert document ---
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Car Repair Request created successfully (Customer + Make/Model handled)",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error("Create Car Repair Request Error", str(e))
        return {"status": "error", "message": str(e)}




# =======================================================
# Create Car Diagnosis From Car Repair Request
# =======================================================


@frappe.whitelist(allow_guest=True)
def create_car_diagnosis(customer_name=None, customer=None):
    """
    Create a Car Diagnosis record:
    - Prefill from last Car Repair Request for this customer
    """
    try:
        if not customer_name and not customer:
            frappe.throw(_("Please provide either customer_name or customer"))

        # If customer link is provided, fetch customer_name
        if customer and not customer_name:
            customer_name = frappe.db.get_value("Customer", customer, "customer_name")

        # Fetch latest Car Repair Request
        last_request = frappe.get_all(
            "Car Repair Request",
            filters={"customer_name": customer_name},
            fields=[
                "name", "car", "car_model", "license_plate", "chassis_no",
                "email", "phone", "repair_request_date", "priority",
                "vehicle_pick_up", "customer_signature"
            ],
            order_by="creation desc",
            limit_page_length=1
        )

        if not last_request:
            return {"status": "not_found", "message": "No Car Repair Request found for this customer"}

        req_name = last_request[0]["name"]

        # Fetch full Car Repair Request including child tables
        req_doc = frappe.get_doc("Car Repair Request", req_name)

        # Create new Car Diagnosis
        diagnosis = frappe.new_doc("Car Diagnosis")
        diagnosis.customer_name = req_doc.customer_name

        # Only assign customer link if it exists
        if hasattr(req_doc, "customer"):
            diagnosis.customer = req_doc.customer

        diagnosis.car = req_doc.car
        diagnosis.model = req_doc.car_model
        diagnosis.license_plate = req_doc.license_plate
        diagnosis.chassis_no = req_doc.chassis_no
        diagnosis.email_id = req_doc.email
        diagnosis.phone = req_doc.phone
        diagnosis.date_of_receipt = req_doc.repair_request_date
        diagnosis.priority = req_doc.priority
        diagnosis.vehicle_pick_up = req_doc.vehicle_pick_up
        diagnosis.customer_signature = req_doc.customer_signature

        # Child tables: vehicle_concern
        if hasattr(req_doc, "vehicle_concern"):
            for vc in req_doc.vehicle_concern:
                diagnosis.append("vehicle_concern", {"vehicle_concern": vc.vehicle_concern})

        # Child tables: car_repair_images
        if hasattr(req_doc, "car_repair_images"):
            for img in req_doc.car_repair_images:
                diagnosis.append("car_repair_images", {"image": img.image})

        # Insert document
        diagnosis.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Car Diagnosis created from Car Repair Request {req_name}",
            "name": diagnosis.name
        }

    except Exception as e:
        frappe.log_error("Error creating Car Diagnosis", str(e))
        return {"status": "error", "message": str(e)}







# ======================================================
# Create Quotation From Car Diagnosis
# ======================================================


@frappe.whitelist(allow_guest=True)
def create_quotation_from_car_diagnosis(diagnosis_name):
    """
    API: Create a Quotation from a Car Diagnosis record.
    """
    try:
        diag = frappe.get_doc("Car Diagnosis", diagnosis_name)
        if not diag.customer_name:
            frappe.throw(_("Customer not found in Car Diagnosis"))

        qtn = frappe.new_doc("Quotation")
        qtn.quotation_to = "Customer"
        qtn.party_name = diag.customer_name
        qtn.remarks = f"Quotation based on Car Diagnosis: {diag.name}"
        qtn.custom_car_diagnosis = diag.name

        if getattr(diag, "email_id", None):
            qtn.contact_email = diag.email_id

        for d in getattr(diag, "car_diagnosis_detail", []):
            if getattr(d, "part_required", None):
                item = frappe.model.add_child(qtn, "items")
                item.item_code = d.part_required
                item.item_name = d.part_required

                # Safe qty/rate
                try:
                    item.qty = float(d.quantity) if d.quantity not in (None, '', ' ') else 1.0
                except:
                    item.qty = 1.0

                try:
                    item.rate = float(d.estimated_cost) if d.estimated_cost not in (None, '', ' ') else 0.0
                except:
                    item.rate = 0.0

                uom = frappe.db.get_value("Item", d.part_required, "stock_uom")
                if uom:
                    item.uom = uom

        if getattr(diag, "issues", None) and not getattr(diag, "car_diagnosis_detail", None):
            child = frappe.model.add_child(qtn, "items")
            child.item_name = diag.issues
            child.qty = 1.0
            child.rate = 0.0

        vehicle_field = "vehicle" if "vehicle" in qtn.as_dict() else "custom_vehicle"
        if getattr(diag, "car", None):
            setattr(qtn, vehicle_field, diag.car)

        qtn.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Quotation created from Car Diagnosis {diag.name}",
            "quotation_name": qtn.name
        }

    except Exception as e:
        frappe.log_error(f"Error creating Quotation from Car Diagnosis {diagnosis_name}", str(e))
        return {"status": "error", "message": str(e)}



# ====================================================
# READ / GET Car Repair Request (single or all)
# ====================================================
@frappe.whitelist(allow_guest=True)
def get_car_repair_request(name=None, page=1, page_size=10):
    """
    Fetch Car Repair Request(s):
    - If 'name' is provided → returns full document (with child tables)
    - If not → returns paginated list of Car Repair Requests (summary view)
    Supports:
    - Pagination: page, page_size
    """
    try:
        # -----------------------------------------
        # Fetch single record with details
        # -----------------------------------------
        if name:
            if not frappe.db.exists("Car Repair Request", name):
                return {
                    "status": "error",
                    "message": f"Car Repair Request '{name}' not found"
                }

            doc = frappe.get_doc("Car Repair Request", name)
            data = doc.as_dict()

            # Include child tables explicitly
            data["vehicle_concern"] = [
                {"vehicle_concern": vc.vehicle_concern}
                for vc in doc.get("vehicle_concern", [])
            ]

            data["car_repair_images"] = [
                {"image": img.image}
                for img in doc.get("car_repair_images", [])
            ]

            return {
                "status": "success",
                "message": f"Car Repair Request '{name}' fetched successfully",
                "data": data
            }

        # -----------------------------------------
        # Paginated list view
        # -----------------------------------------
        page = int(page) if str(page).isdigit() else 1
        page_size = int(page_size) if str(page_size).isdigit() else 10
        start = (page - 1) * page_size

        total_records = frappe.db.count("Car Repair Request")

        records = frappe.get_all(
            "Car Repair Request",
            fields=[
                "name", "customer_name", "email", "phone",
                "make", "model", "license_plate",
                "priority", "service_type", "repair_request_date"
            ],
            order_by="creation desc",
            start=start,
            page_length=page_size
        )

        total_pages = (total_records + page_size - 1) // page_size

        return {
            "status": "success",
            "message": "Car Repair Request list fetched successfully",
            "pagination": {
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None,
            },
            "data": records
        }

    except Exception as e:
        frappe.log_error(title="Get Car Repair Request Error", message=str(e))
        return {
            "status": "error",
            "message": f"Internal Server Error: {str(e)}"
        }

# ====================================================
# UPDATE Car Repair Request
# ====================================================
@frappe.whitelist(allow_guest=True)
def update_car_repair_request(name, data):
    """
    Update an existing Car Repair Request.
    - Supports partial updates (only provided fields)
    - Updates child tables (vehicle_concern, car_repair_images)
    """
    import json

    try:
        # Ensure request payload is parsed
        data = json.loads(data) if isinstance(data, str) else data

        # Validate if document exists
        if not frappe.db.exists("Car Repair Request", name):
            return {"status": "error", "message": f"Car Repair Request '{name}' not found"}

        doc = frappe.get_doc("Car Repair Request", name)

        # ✅ Allowed updatable fields
        updatable_fields = [
            "email", "phone", "make", "model", "assign_adviser", "car", "license_plate",
            "chassis_no", "car_manufacturing_year", "odometer_photo", "priority",
            "service_type", "repair_request_date", "driver_name", "driver_mob_no",
            "odometer_value", "fuel_level", "vehicle_pick_up", "customer_signature",
            "remark", "fuel_type"
        ]

        # ✅ Update only provided fields
        for f in updatable_fields:
            if f in data:
                doc.set(f, data[f])

        # ✅ Update child table: Vehicle Concerns
        if "vehicle_concern" in data and isinstance(data["vehicle_concern"], list):
            doc.set("vehicle_concern", [])
            for vc in data["vehicle_concern"]:
                if vc.get("vehicle_concern"):
                    doc.append("vehicle_concern", {"vehicle_concern": vc["vehicle_concern"]})

        # ✅ Update child table: Car Repair Images
        if "car_repair_images" in data and isinstance(data["car_repair_images"], list):
            doc.set("car_repair_images", [])
            for img in data["car_repair_images"]:
                if img.get("image"):
                    doc.append("car_repair_images", {"image": img["image"]})

        # ✅ Save changes
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Car Repair Request '{name}' updated successfully",
            "updated_data": doc.as_dict()
        }

    except Exception as e:
        frappe.log_error(title="Update Car Repair Request Error", message=str(e))
        return {"status": "error", "message": str(e)}


# ====================================================
# DELETE Car Repair Request
# ====================================================
@frappe.whitelist(allow_guest=True)
def delete_car_repair_request(name):
    """
    Delete an existing Car Repair Request by name.
    Safe delete with existence check and error handling.
    """
    try:
        # ✅ Check if the document exists
        if not frappe.db.exists("Car Repair Request", name):
            return {
                "status": "error",
                "message": f"Car Repair Request '{name}' not found"
            }

        # ✅ Perform delete
        frappe.delete_doc("Car Repair Request", name, ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Car Repair Request '{name}' deleted successfully"
        }

    except frappe.ValidationError as ve:
        frappe.log_error(title="Car Repair Request Delete Validation Error", message=str(ve))
        return {
            "status": "error",
            "message": f"Validation Error while deleting '{name}': {str(ve)}"
        }

    except Exception as e:
        frappe.log_error(title="Delete Car Repair Request Error", message=str(e))
        return {
            "status": "error",
            "message": f"Internal Server Error: {str(e)}"
        }
