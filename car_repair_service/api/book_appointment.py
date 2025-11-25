import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime


# ---------------------------------------------------------
# ..............Create Book Appointment....................
# ---------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def create_book_appointment(data):
   
    """
    Create a new Book Appointment with validation.
    Auto-create Customer, Vehicle Make, Vehicle Model, and Vehicle if not found.
    Skip appointment creation if a matching one exists.
    """
    try:
        data = frappe.parse_json(data)

        # Extract core data
        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")
        license_plate = data.get("license_plate")
        make = data.get("make")
        model = data.get("model")

        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")

        # Validate appointment date and time
        today = nowdate()
        if appointment_date < today:
            return {"status": "error", "message": "Appointment date cannot be in the past"}

        if appointment_date == today and appointment_time:
            current_time = now_datetime().strftime("%H:%M")
            if appointment_time < current_time:
                return {"status": "error", "message": "Appointment time cannot be in the past"}

        # === Auto-create or fetch Customer ===
        customer_exists = frappe.db.exists("Customer", {"customer_name": customer_name})
        if not customer_exists:
            customer_doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "email_id": email,
                "mobile_no": phone,
                "territory": "All Territories"
            })
            customer_doc.insert(ignore_permissions=True)

        # === Auto-create or fetch Vehicle Make ===
        make_name = frappe.db.exists("Vehicle Make", {"make": make})
        if not make_name:
            make_doc = frappe.get_doc({
                "doctype": "Vehicle Make",
                "make": make
            })
            make_doc.insert(ignore_permissions=True)
            make_name = make_doc.name

        # === Auto-create or fetch Vehicle Model ===
        model_name = frappe.db.exists("Vehicle Model", {"model": model})
        if not model_name:
            model_doc = frappe.get_doc({
                "doctype": "Vehicle Model",
                "model": model,
                "make": make_name
            })
            model_doc.insert(ignore_permissions=True)
            model_name = model_doc.name

        # === Auto-create or fetch Vehicle ===
        vehicle_exists = frappe.db.exists("Vehicle", {"license_plate": license_plate})
        if not vehicle_exists:
            vehicle_doc = frappe.get_doc({
                "doctype": "Vehicle",
                "license_plate": license_plate,
                "make": make_name,
                "model": model_name,
                "custom_customer_name": customer_name
            })
            vehicle_doc.insert(ignore_permissions=True)

        # === Prevent duplicate appointments and skip creation ===
        existing_appointment = frappe.db.exists("Book Appointment", {
            "customer_name": customer_name,
            "license_plate": license_plate,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time
        })
        if existing_appointment:
            return {
                "status": "success",
                "message": "Appointment already exists. Skipping creation.",
                "appointment_id": existing_appointment
            }

        # === Create new Book Appointment ===
        appointment = frappe.get_doc({
            "doctype": "Book Appointment",
            "customer_name": customer_name,
            "email": email,
            "phone": phone,
            "license_plate": license_plate,
            "make": make,
            "model": model,
            "service_type": data.get("service_type"),
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "vehicle_pickup_required": data.get("vehicle_pickup_required"),
            "pickup_address": data.get("pickup_address"),
            "status": "Open"
        })

        appointment.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Appointment booked successfully",
            "appointment_id": appointment.name
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Create Appointment Error")
        return {"status": "error", "message": str(e)}

# ..............Create Book Appointment..................

# @frappe.whitelist()
# def create_book_appointment(data):
    
#     """
#     Create a new Book Appointment.
#     Expects JSON data:
#     {
#         "customer_name": "John Doe",
#         "email": "john@example.com",
#         "phone": "9876543210",
#         "license_plate": "MH12AB1234",
#         "make": "Maruti",
#         "model": "Swift",
#         "service_type": "Repair",
#         "appointment_date": "2025-11-07",
#         "appointment_time": "10:00",
#         "vehicle_pickup_required": "Yes, Pickup my vehicle",
#         "pickup_address": "123 Street, Pune"
#     }
#     """
#     try:
#         print("TOKEN RECEIVED:", frappe.get_request_header("Authorization"))
#         print("CURRENT USER:", frappe.session.user)


#         data = frappe.parse_json(data)

#         # Create new document
#         doc = frappe.get_doc({
#             "doctype": "Book Appointment",
#             "customer_name": data.get("customer_name"),
#             "email": data.get("email"),
#             "phone": data.get("phone"),
#             "license_plate": data.get("license_plate"),
#             "make": data.get("make"),
#             "model": data.get("model"),
#             "service_type": data.get("service_type"),
#             "appointment_date": data.get("appointment_date"),
#             "appointment_time": data.get("appointment_time"),
#             "vehicle_pickup_required": data.get("vehicle_pickup_required"),
#             "pickup_address": data.get("pickup_address"),
#             "status": "Open"
#         })

#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Appointment created successfully",
#             "appointment_id": doc.name
#         }

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Create Appointment Error")
#         return {"status": "error", 
#                 "message": str(e)}
        
        
#------------------------------------------------------------------------------------    
#.................Create Car Repair Request From Book Appointement...................  
# -----------------------------------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def create_car_repair_request(appointment_name):
   
    """
    Create a Car Repair Request from a Book Appointment
    """
    try:
        # Fetch Appointment
        appointment = frappe.get_doc("Book Appointment", appointment_name)

        # Check if already exists
        existing_request = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
        if existing_request:
            return {
                "status": "exists",
                "message": f"Car Repair Request already exists: {existing_request}",
                "car_repair_request": existing_request
            }

        # Create new Car Repair Request
        repair = frappe.new_doc("Car Repair Request")

        # ✅ Populate basic info from appointment
        repair.update({
            "appointment": appointment.name,
            "customer_name": appointment.customer_name,
            "email": appointment.email,
            "phone": appointment.phone,
            "license_plate": appointment.license_plate,
            "make": appointment.make,
            "model": appointment.model,
            "service_type": appointment.service_type,
            "pickup_address": appointment.pickup_address,
            "status": "Pending"
        })

        # ✅ Optional fields — handle missing gracefully
        if hasattr(appointment, "odometer_photo") and appointment.odometer_photo:
            repair.odometer_photo = appointment.odometer_photo

        if hasattr(appointment, "car_repair_images") and appointment.car_repair_images:
            for img in appointment.car_repair_images:
                repair.append("car_repair_images", {
                    "image": img.image
                })

        # ✅ Insert ignoring missing mandatory fields
        repair.flags.ignore_mandatory = True
        repair.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Car Repair Request created successfully",
            "car_repair_request": repair.name
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Create Car Repair Request Error")
        return {"status": "error", "message": str(e)}

# -------------------------------------------------------------------------------------
# .....................Get List Of Book Appointment,pagination,........................
# -------------------------------------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def get_book_appointments(page=1, page_size=10):
    
    """
    Get a paginated list of Book Appointments,
    including make and model details.
    """
    try:
        page = int(page)
        page_size = int(page_size)

        appointments = frappe.get_all(
            "Book Appointment",
            fields=[
                "name",
                "customer_name",
                "email",
                "phone",
                "license_plate",
                "make",
                "model",
                "service_type",
                "appointment_date",
                "appointment_time",
                "vehicle_pickup_required",
                "pickup_address",
                "status",
                "creation",
                "modified"
            ],
            start=(page - 1) * page_size,
            page_length=page_size,
            order_by="creation desc"
        )

        total_records = frappe.db.count("Book Appointment")
        total_pages = (total_records + page_size - 1) // page_size

        return {
            "status": "success",
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages
            },
            "data": appointments
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Fetch Appointments Error")
        return {"status": "error", "message": str(e)}



# ----------------------------------------------------------------------------
# ...................Get Single Book Appointement Id..........................
# ----------------------------------------------------------------------------

@frappe.whitelist(allow_guest=False)
def get_book_appointment(appointment_id):
   
    """
    Get a single Book Appointment by ID,
    including make and model details.
    """
    try:
        doc = frappe.get_doc("Book Appointment", appointment_id)
        data = {
            "name": doc.name,
            "customer_name": doc.customer_name,
            "email": doc.email,
            "phone": doc.phone,
            "license_plate": doc.license_plate,
            "make": doc.make,
            "model": doc.model,
            "service_type": doc.service_type,
            "appointment_date": doc.appointment_date,
            "appointment_time": doc.appointment_time,
            "vehicle_pickup_required": doc.vehicle_pickup_required,
            "pickup_address": doc.pickup_address,
            "status": doc.status,
            "creation": doc.creation,
            "modified": doc.modified
        }

        return {"status": "success", "data": data}

    except Exception as e:
        frappe.log_error(message=str(e), title="Get Appointment Error")
        return {"status": "error", "message": str(e)}




# -----------------------------------------------------------------
# .................update book appointment.........................
# -----------------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def update_book_appointment(appointment_id, data):
    
    """
    Update an existing Book Appointment.
    Expects JSON data (stringified) in 'data' — may include make, model, etc.
    """
    try:
        # Clean input ID (remove accidental quotes)
        appointment_id = str(appointment_id).strip().strip("'").strip('"')

        # Ensure appointment exists
        if not frappe.db.exists("Book Appointment", appointment_id):
            return {"status": "error", "message": f"Book Appointment {appointment_id} not found"}

        # Parse JSON payload
        data = frappe.parse_json(data)

        # Get and update the document
        doc = frappe.get_doc("Book Appointment", appointment_id)
        doc.update(data)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Appointment updated successfully",
            "appointment_id": doc.name,
            "updated_fields": data
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Update Appointment Error")
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------
# ................Delete Book Appointement..........................
# ------------------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def delete_book_appointment(appointment_id):
   
    """
    Delete a Book Appointment by ID.
    Example:
    {
        "appointment_id": "ad6ih2j92g"
    }
    """
    try:
        # Check if the appointment exists
        if not frappe.db.exists("Book Appointment", appointment_id):
            return {
                "status": "error",
                "message": f"Book Appointment '{appointment_id}' not found"
            }

        # Delete the record
        frappe.delete_doc("Book Appointment", appointment_id, ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Appointment '{appointment_id}' deleted successfully"
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Delete Appointment Error")
        return {
            "status": "error",
            "message": str(e)
        }
