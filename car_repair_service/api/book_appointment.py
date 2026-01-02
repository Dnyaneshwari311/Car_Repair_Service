import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime
from car_repair_service.api.role_validation import validate_api_access




from frappe.utils import getdate, get_time, now_datetime, nowdate


@frappe.whitelist(allow_guest=False)
def create_book_appointment(data):
    try:
        data = frappe.parse_json(data)

        # ---------------------------
        #   EXTRACT CORE DATA
        # ---------------------------
        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")
        license_plate = data.get("license_plate")
        make = data.get("make")
        model = data.get("model")

        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")
        description = data.get("description") 
        
        # Pickup logic fields
        vehicle_pickup_required = data.get("vehicle_pickup_required")
        pickup_address = data.get("pickup_address")
        same_as_pick_up_address = data.get("same_as_pick_up_address")  # 0 or 1
        drop_address = data.get("drop_address")

        # ---------------------------
        #   STRICT DATE VALIDATION
        # ---------------------------
        if not appointment_date:
            return {
                "status": "error",
                "message": "Appointment date is required"
            }

        appointment_date = getdate(appointment_date)
        today = getdate(nowdate())

        # ❌ BACK DATE NOT ALLOWED
        if appointment_date < today:
            return {
                "status": "error",
                "message": "Back date is not allowed. Please select today or a future date."
            }

        # ---------------------------
        #   TIME VALIDATION (TODAY ONLY)
        # ---------------------------
        if appointment_date == today:
            if not appointment_time:
                return {
                    "status": "error",
                    "message": "Appointment time is required for today"
                }

            appointment_time = get_time(appointment_time)
            current_time = now_datetime().time()

            # if appointment_time <= current_time:
            #     return {
            #         "status": "error",
            #         "message": "Please select a future time"
            #     }

        # ---------------------------
        #   AUTO CREATE MASTERS
        # ---------------------------
        if not frappe.db.exists("Customer", {"customer_name": customer_name}):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "email_id": email,
                "mobile_no": phone,
                "territory": "All Territories"
            }).insert(ignore_permissions=True)

        make_name = frappe.db.exists("Vehicle Make",make)
        if not make_name:
            make_name = frappe.get_doc({
                "doctype": "Vehicle Make",
                "make": make
            }).insert(ignore_permissions=True).name

        model_name = frappe.db.exists("Vehicle Model",model)
        if not model_name:
            model_name = frappe.get_doc({
                "doctype": "Vehicle Model",
                "model": model,
                # "make": make_name
            }).insert(ignore_permissions=True).name

        if not frappe.db.exists("Vehicle", {"license_plate": license_plate}):
            frappe.get_doc({
                "doctype": "Vehicle",
                "license_plate": license_plate,
                "make": make_name,
                "model": model_name,
                "custom_customer_name": customer_name
            }).insert(ignore_permissions=True)

        # ----------------------------------------
        #   PREVENT DUPLICATE APPOINTMENTS
        # ----------------------------------------
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

        # ----------------------------------------
        #   PICKUP / DROP LOGIC
        # ----------------------------------------
        if vehicle_pickup_required == "Yes, Pickup my vehicle" and same_as_pick_up_address == 1:
            drop_address = pickup_address

        # ---------------------------
        #   CREATE APPOINTMENT
        # ---------------------------
        appointment = frappe.get_doc({
            "doctype": "Book Appointment",
            "customer_name": customer_name,
            "email": email,
            "phone": phone,
            "license_plate": license_plate,
            "make": make_name,
            "model": model_name,
            "service_type": data.get("service_type"),
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "vehicle_pickup_required": vehicle_pickup_required,
            "pickup_address": pickup_address,
            "same_as_pick_up_address": same_as_pick_up_address,
            "drop_address": drop_address,
            "status": "Open"
        })

        appointment.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_messages()
        return {
            "status": "success",
            "status_code":200,
            "message": "Appointment booked successfully",
            "appointment_id": appointment.name
        }

    except Exception as e:
        frappe.log_error(str(e), "Create Appointment Error")
        return {
            "status": "error",
            "message": str(e)
        }









from frappe.utils import getdate, nowdate

@frappe.whitelist(allow_guest=False)
def create_car_repair_request(appointment_name, status=None):
    """
    Create a Car Repair Request from a Book Appointment
    """

    try:
        # ---------------------------
        # FETCH APPOINTMENT
        # ---------------------------
        appointment = frappe.get_doc("Book Appointment", appointment_name)

        # ---------------------------
        # OPTIONAL STATUS UPDATE FROM JSON
        # ---------------------------
        if status:
            if status != "Confirmed":
                frappe.throw("Only 'Confirmed' status is allowed to create Car Repair Request")

            # appointment.status = status
            # appointment.save(ignore_permissions=True)
            if appointment.status != "Confirmed":
                appointment.status = "Confirmed"
                appointment.save(ignore_permissions=True)


        # ---------------------------
        # AUTO-CANCEL BACKDATED APPOINTMENT
        # ---------------------------
        # if appointment.appointment_date and getdate(appointment.appointment_date) < getdate(nowdate()):
        #     appointment.status = "Cancelled"
        #     appointment.save(ignore_permissions=True)

        #     frappe.throw(
        #         "Appointment date is in the past. Appointment has been automatically Cancelled."
        #     )

        # ---------------------------
        # STATUS VALIDATION
        # ---------------------------
        if appointment.status != "Confirmed":
            frappe.throw(
                "Car Repair Request can only be created when Appointment is Confirmed"
            )

        # ---------------------------
        # PREVENT DUPLICATE REQUEST
        # ---------------------------
        existing_request = frappe.db.exists(
            "Car Repair Request",
            {"appointment": appointment.name}
        )
        if existing_request:
            frappe.clear_messages()

            return {
                "status": "exists",
                "message": "Car Repair Request already exists",
                "car_repair_request": existing_request
            }

        # ---------------------------
        # PICKUP / DROP LOGIC
        # ---------------------------
        pickup_address = appointment.pickup_address
        drop_address = appointment.drop_address

        if (
            appointment.vehicle_pickup_required == "Yes, Pickup my vehicle"
            and appointment.same_as_pick_up_address == 1
        ):
            drop_address = pickup_address

        # ---------------------------
        # CREATE CAR REPAIR REQUEST
        # ---------------------------
        repair = frappe.get_doc({
            "doctype": "Car Repair Request",
            "appointment": appointment.name,
            "customer_name": appointment.customer_name,
            "email": appointment.email,
            "phone": appointment.phone,
            "license_plate": appointment.license_plate,
            "make": appointment.make,
            "model": appointment.model,
            "service_type": appointment.service_type,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "vehicle_pickup_required": appointment.vehicle_pickup_required,
            "pickup_address": pickup_address,
            "drop_address": drop_address,
            "status": "Pending"
        })

        # ---------------------------
        # OPTIONAL MEDIA FIELDS
        # ---------------------------
        if getattr(appointment, "odometer_photo", None):
            repair.odometer_photo = appointment.odometer_photo

        if getattr(appointment, "car_repair_images", None):
            for img in appointment.car_repair_images:
                repair.append("car_repair_images", {
                    "image": img.image
                })

        # ---------------------------
        # INSERT DOCUMENT
        # ---------------------------
        repair.flags.ignore_mandatory = True
        repair.insert(ignore_permissions=True)

        # ---------------------------
        # UPDATE APPOINTMENT STATUS TO COMPLETE
        # ---------------------------
        appointment.status = "Complete"
        appointment.save(ignore_permissions=True)
        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Car Repair Request created successfully",
            "car_repair_request": repair.name
        }

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Create Car Repair Request Error"
        )
        frappe.throw(str(e))





@frappe.whitelist(allow_guest=False)
def get_book_appointments(page=1, page_size=10, status=None):
    """
    Get a paginated list of Book Appointments
    with optional status-wise filtering.
    """
    try:
        page = int(page)
        page_size = int(page_size)

        # Build filters dynamically
        filters = {}
        if status:
            filters["status"] = status

        appointments = frappe.get_all(
            "Book Appointment",
            filters=filters,
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

        # Count with same filters
        total_records = frappe.db.count("Book Appointment", filters=filters)
        total_pages = (total_records + page_size - 1) // page_size

        return {
            "status": "success",
            "filters": {
                "status": status or "All"
            },
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
        frappe.clear_messages()
        return {"status": "success", 
                "status_code":200,
                "data": data}

    except Exception as e:
        frappe.log_error(message=str(e), title="Get Appointment Error")
        return {"status": "error", "message": str(e)}




# -----------------------------------------------------------------
# .................update book appointment.........................
# -----------------------------------------------------------------
# @frappe.whitelist(allow_guest=False)
# def update_book_appointment(appointment_id, data):
    
#     """
#     Update an existing Book Appointment.
#     Expects JSON data (stringified) in 'data' — may include make, model, etc.
#     """
#     try:
#         # Clean input ID (remove accidental quotes)
#         appointment_id = str(appointment_id).strip().strip("'").strip('"')

#         # Ensure appointment exists
#         if not frappe.db.exists("Book Appointment", appointment_id):
#             return {"status": "error", "message": f"Book Appointment {appointment_id} not found"}

#         # Parse JSON payload
#         data = frappe.parse_json(data)

#         # Get and update the document
#         doc = frappe.get_doc("Book Appointment", appointment_id)
#         doc.update(data)
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Appointment updated successfully",
#             "appointment_id": doc.name,
#             "updated_fields": data
#         }

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Update Appointment Error")
#         return {"status": "error", "message": str(e)}


from frappe.utils import getdate, get_time

@frappe.whitelist(allow_guest=False)
def update_book_appointment(data):
    import frappe
    from frappe.utils import getdate, get_time

    try:
        # Parse JSON payload
        data = frappe.parse_json(data)

        # Extract appointment_id
        appointment_id = data.pop("appointment_id", None)
        if not appointment_id:
            return {"status": "error", "message": "appointment_id is required"}

        # Clean appointment_id
        appointment_id = str(appointment_id).strip().strip("'").strip('"')

        # Check if appointment exists
        if not frappe.db.exists("Book Appointment", appointment_id):
            return {"status": "error", "message": f"Book Appointment {appointment_id} not found"}

        # Parse and validate appointment_date
        if "appointment_date" in data:
            try:
                data["appointment_date"] = getdate(data["appointment_date"])
            except Exception:
                return {"status": "error", "message": "Invalid appointment_date format. Use YYYY-MM-DD"}

        # Parse and validate appointment_time
        if "appointment_time" in data:
            try:
                data["appointment_time"] = get_time(data["appointment_time"])
            except Exception:
                return {"status": "error", "message": "Invalid appointment_time format. Use HH:MM"}

        # Get and update the document
        doc = frappe.get_doc("Book Appointment", appointment_id)
        doc.update(data)
        
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_messages()
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







@frappe.whitelist(allow_guest=False)
def cancel_book_appointment(appointment_name):
    try:
        appointment = frappe.get_doc("Book Appointment", appointment_name)

        # Prevent cancelling completed appointments
        if appointment.status == "Complete":
            frappe.throw("Completed appointment cannot be cancelled")

        # Allow cancellation from Open or Confirmed
        if appointment.status in ["Open", "Confirmed"]:
            appointment.status = "Cancelled"
            appointment.save(ignore_permissions=True)
            frappe.clear_messages()
            return {
                "status": "success",
                "status_code":201,
                "message": "Appointment cancelled successfully",
                "appointment_id": appointment.name
            }

        frappe.throw(f"Appointment cannot be cancelled from status {appointment.status}")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel Book Appointment Error")
        frappe.throw(str(e))






