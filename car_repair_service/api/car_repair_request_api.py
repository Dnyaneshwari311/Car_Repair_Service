import frappe
from frappe import _
import json

# ====================================================
# CREATE Car Repair Request (with Auto Customer + Email)
# ====================================================
# @frappe.whitelist(allow_guest=True)
# def create_car_repair_request(data):
#     """
#     Create a new Car Repair Request, auto-create Customer, Vehicle Make/Model, and send confirmation email
#     """
#     import json
#     import frappe

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

#         if make:
#             if not frappe.db.exists("Vehicle Make", {"make": make}):
#                 vehicle_make = frappe.new_doc("Vehicle Make")
#                 vehicle_make.make = make
#                 vehicle_make.insert(ignore_permissions=True)
#                 frappe.msgprint(f"✅ Created new Vehicle Make: {make}")

#         if model:
#             if not frappe.db.exists("Vehicle Model", {"model": model}):
#                 vehicle_model = frappe.new_doc("Vehicle Model")
#                 vehicle_model.model = model
#                 vehicle_model.insert(ignore_permissions=True)
#                 frappe.msgprint(f"✅ Created new Vehicle Model: {model}")

#         # ====================================================
#         # ✅ Step 3: Create Car Repair Request
#         # ====================================================
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

#         # ✅ Link correct Customer name (instead of literal text)
#         if "customer" in doc.as_dict():
#             doc.customer = customer_id
#         elif "customer_name" in doc.as_dict():
#             doc.customer_name = customer_id

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

#         # ====================================================
#         # ✅ Step 4: Send Email Notification
#         # ====================================================
#         if email:
#             try:
#                 frappe.sendmail(
#                     recipients=[email],
#                     subject=f"Car Repair Request Received - {doc.name}",
#                     message=f"""
#                         <p>Hello {customer_name},</p>
#                         <p>Your car repair request (<b>{doc.name}</b>) has been received successfully.</p>
#                         <p>Our service advisor will contact you soon.</p>
#                         <p><b>Summary:</b></p>
#                         <ul>
#                             <li><b>Car:</b> {doc.make or ''} {doc.model or ''}</li>
#                             <li><b>License Plate:</b> {doc.license_plate or ''}</li>
#                             <li><b>Service Type:</b> {doc.service_type or ''}</li>
#                             <li><b>Priority:</b> {doc.priority or ''}</li>
#                         </ul>
#                         <p>Thank you for choosing our service!</p>
#                         <br>
#                         <p>Best Regards,<br>Car Service Center</p>
#                     """,
#                 )
#             except Exception as email_err:
#                 frappe.log_error("Car Repair Request Email Error", str(email_err))

#         return {
#             "status": "success",
#             "message": "Car Repair Request created successfully (Customer + Make/Model + Email handled)",
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
    (Email is handled by after_insert event)
    """
    try:
        data = json.loads(data) if isinstance(data, str) else data

        # ====================================================
        # ✅ Step 1: Auto-create Customer if not exists
        # ====================================================
        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")

        customer_id = None

        if email and customer_name:
            existing_customer = frappe.db.exists("Customer", {"email_id": email})
            if not existing_customer:
                customer = frappe.new_doc("Customer")
                customer.customer_name = customer_name
                customer.email_id = email
                customer.mobile_no = phone
                customer.customer_group = "Individual"
                customer.territory = "All Territories"
                customer.insert(ignore_permissions=True)
                frappe.msgprint(f"✅ Customer {customer.customer_name} created successfully.")
                customer_id = customer.name
            else:
                customer_id = existing_customer
        else:
            frappe.throw("Missing customer_name or email for Customer creation")

        # ====================================================
        # ✅ Step 2: Ensure Vehicle Make & Model exist
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
        # ✅ Step 3: Create Car Repair Request
        # ====================================================
        frappe.flags.in_create_car_repair_api = True  # helps avoid re-trigger in hooks

        doc = frappe.new_doc("Car Repair Request")
        fields = [
            "email", "phone", "make", "model", "assign_adviser",
            "car", "license_plate", "chassis_no", "car_manufacturing_year",
            "odometer_photo", "priority", "service_type", "repair_request_date",
            "driver_name", "driver_mob_no", "odometer_value", "fuel_level",
            "vehicle_pick_up", "customer_signature", "remark", "fuel_type"
        ]

        # --- Set all main fields dynamically ---
        for f in fields:
            if f in data:
                doc.set(f, data[f])

        # ✅ Link correct Customer name
        doc.customer = customer_id

        # --- Child Table: Vehicle Concerns ---
        if "vehicle_concern" in data and isinstance(data["vehicle_concern"], list):
            for vc in data["vehicle_concern"]:
                doc.append("vehicle_concern", {"vehicle_concern": vc.get("vehicle_concern")})

        # --- Child Table: Car Repair Images ---
        if "car_repair_images" in data and isinstance(data["car_repair_images"], list):
            for img in data["car_repair_images"]:
                doc.append("car_repair_images", {"image": img.get("image")})

        # --- Save document ---
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Email is sent automatically in after_insert hook
        return {
            "status": "success",
            "message": "Car Repair Request created successfully (Customer + Make/Model handled)",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error("Create Car Repair Request Error", str(e))
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
