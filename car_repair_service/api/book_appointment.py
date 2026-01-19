import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime
from car_repair_service.api.role_validation import validate_api_access




from frappe.utils import getdate, get_time, nowdate, now_datetime

@frappe.whitelist(allow_guest=False)
def create_book_appointment(data):
    """
    Create Book Appointment
    - Only Receptionist and Administrator are allowed
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        # ----------------------------------
        # ROLE CHECK
        # ----------------------------------
        if not ("Receptionist" in roles or "Administrator" in roles):
            frappe.throw(
                "You are not allowed to create Book Appointments",
                frappe.PermissionError
            )

        # ----------------------------------
        # PARSE JSON
        # ----------------------------------
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

        vehicle_pickup_required = data.get("vehicle_pickup_required")
        pickup_address = data.get("pickup_address")
        same_as_pick_up_address = data.get("same_as_pick_up_address")
        drop_address = data.get("drop_address")
        assigned_to = data.get("assigned_to")

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

        if appointment_date < today:
            return {
                "status": "error",
                "message": "Back date is not allowed. Please select today or a future date."
            }

        # ---------------------------
        #   TIME VALIDATION
        # ---------------------------
        if appointment_date == today:
            if not appointment_time:
                return {
                    "status": "error",
                    "message": "Appointment time is required for today"
                }

            appointment_time = get_time(appointment_time)
            current_time = now_datetime().time()
            
            
        if appointment_time <= current_time:
                return {
                    "status": "error",
                    "message": "Past time is not allowed. Please select a future time."
                }
        else:
            if appointment_time:
                appointment_time = get_time(appointment_time)   

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

        make_name = frappe.db.exists("Vehicle Make", {"make": make})
        if not make_name:
            make_name = frappe.get_doc({
                "doctype": "Vehicle Make",
                "make": make
            }).insert(ignore_permissions=True).name

        model_name = frappe.db.exists("Vehicle Model", {"model": model})
        if not model_name:
            model_name = frappe.get_doc({
                "doctype": "Vehicle Model",
                "model": model,
                "make": make_name
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
        if (
            vehicle_pickup_required == "Yes, Pickup my vehicle"
            and same_as_pick_up_address == 1
        ):
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
            "make": make,
            "model": model,
            "service_type": data.get("service_type"),
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "vehicle_pickup_required": vehicle_pickup_required,
            "pickup_address": pickup_address,
            "same_as_pick_up_address": same_as_pick_up_address,
            "drop_address": drop_address,
            "status": "Open",
            "description": description,
            "assigned_to": assigned_to
        })

        appointment.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Appointment booked successfully",
            "appointment_id": appointment.name
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Create Appointment Error"
        )
        return {
            "status": "error",
            "message": str(e)
        }







@frappe.whitelist(allow_guest=False)
def confirm_book_appointment(appointment_name):
    """
    Confirm a Book Appointment
    Only Receptionist or Administrator can confirm
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        # ----------------------------------
        # ROLE CHECK
        # ----------------------------------
        allowed_roles = ["Receptionist", "Administrator"]

        if not any(role in roles for role in allowed_roles):
            frappe.throw(
                "You are not allowed to confirm appointments",
                frappe.PermissionError
            )

        # ----------------------------------
        # FETCH APPOINTMENT
        # ----------------------------------
        appointment = frappe.get_doc("Book Appointment", appointment_name)

        # Prevent reconfirm
        if appointment.status == "Confirmed":
            return {
                "status": "exists",
                "message": "Appointment is already confirmed",
                "appointment": appointment.name
            }

        # Prevent confirming cancelled appointment
        if appointment.status == "Cancelled":
            frappe.throw("Cancelled appointment cannot be confirmed")

        # ----------------------------------
        # CONFIRM APPOINTMENT
        # ----------------------------------
        appointment.status = "Confirmed"
        appointment.save(ignore_permissions=True)

        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Appointment confirmed successfully",
            "appointment": appointment.name
        }

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Confirm Book Appointment Error"
        )
        frappe.throw(str(e))













from frappe.utils import getdate, nowdate

@frappe.whitelist(allow_guest=False)
def create_car_repair_request(appointment_name, status=None):
    """
    Create Car Repair Request from Book Appointment
    Permission:
    - Employee: only assigned appointment
    - Receptionist / Administrator: all
    - Adviser: not allowed
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        is_admin = "Administrator" in roles
        is_receptionist = "Receptionist" in roles
        is_employee = "Employee" in roles

        # ----------------------------------
        # BLOCK ADVISER
        # ----------------------------------
        if "Adviser" in roles and not (is_admin or is_receptionist):
            frappe.throw(
                "Adviser is not allowed to create Car Repair Request",
                frappe.PermissionError
            )

        # ----------------------------------
        # FETCH APPOINTMENT
        # ----------------------------------
        appointment = frappe.get_doc("Book Appointment", appointment_name)

        # ----------------------------------
        # EMPLOYEE ASSIGNMENT CHECK
        # ----------------------------------
        if is_employee and not (is_admin or is_receptionist):
            employee = frappe.db.get_value(
                "Employee",
                {"user_id": user},
                "name"
            )

            if not employee:
                frappe.throw(
                    "Employee not linked with this user",
                    frappe.PermissionError
                )

            if appointment.assigned_to != employee:
                frappe.throw(
                    "You can only create Car Repair Request for appointments assigned to you",
                    frappe.PermissionError
                )

        # ---------------------------
        # OPTIONAL STATUS UPDATE FROM JSON
        # ---------------------------
        if status:
            if status != "Confirmed":
                frappe.throw(
                    "Only 'Confirmed' status is allowed to create Car Repair Request"
                )

            if appointment.status != "Confirmed":
                appointment.status = "Confirmed"
                appointment.save(ignore_permissions=True)

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
        # OPTIONAL MEDIA
        # ---------------------------
        if getattr(appointment, "odometer_photo", None):
            repair.odometer_photo = appointment.odometer_photo

        if getattr(appointment, "car_repair_images", None):
            for img in appointment.car_repair_images:
                repair.append("car_repair_images", {
                    "image": img.image
                })

        # ---------------------------
        # SAVE REQUEST
        # ---------------------------
        repair.flags.ignore_mandatory = True
        repair.save(ignore_permissions=True)
        appointment.status = "Complete"
        appointment.save(ignore_permissions=True)
        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Car Repair Request created successfully",
            "car_repair_request": repair.name
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Create Car Repair Request Error"
        )
        frappe.throw(str(e))






@frappe.whitelist()
def get_appointment_list(search=None, status=None):
    """
    Returns list of items which have variants (has_variants = 1)
    Permission is automatically applied based on logged-in user
    """
    print("request params::::::::::::",search, status)
    user = frappe.session.user
    print("user ..",user)
    employee = frappe.db.get_value(
    "Employee",
    {"user_id": frappe.session.user},
    ["name", "employee_name", "designation"],
    as_dict=True
)
    print("employee ...",employee)

    filters = {
        "status": status,
        "assigned_to":employee.name
    }
    print("filter object::::::::::::", filters)

    # Optional search by item code or name
    # if search:
    appointment_list = frappe.get_all(
        "Book Appointment",
        filters=filters,
        fields=["name", "customer_name", "email", "phone","status","license_plate","make","model","service_type","appointment_date","appointment_time",
                "vehicle_pickup_required","pickup_address","assigned_to","drop_address","status","description"],
        
        # limit_page_length=limit
    )
    
    print("appointment_list:::::::::::::", appointment_list)
    return appointment_list

    # return frappe.get_list(
    #     "Book Appointment",
    #     filters=filters,
    #     fields=["name", "customer_name", "email", "phone", "status"],
    #     # limit_page_length=limit
    # )





@frappe.whitelist(allow_guest=False)
def get_book_appointments(search=None, status=None):
    """
    Role rules:
    - Employee: only assigned appointments
    - Receptionist / Administrator: all
    - Adviser: no access
    Returns structured response like:
    {
        "status": "success",
        "data": [ ...appointments... ]
    }
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        # ----------------------------------
        # BLOCK ADVISER
        # ----------------------------------
        if "Advisor" in roles and not (
            "Receptionist" in roles or "Administrator" in roles
        ):
            frappe.throw(
                "You are not allowed to view Book Appointments",
                frappe.PermissionError
            )

        filters = {}

        # ----------------------------------
        # STATUS FILTER
        # ----------------------------------
        if status:
            filters["status"] = status

        # ----------------------------------
        # ROLE-BASED FILTER
        # ----------------------------------
        if "Employee" in roles and not (
            "Receptionist" in roles or "Administrator" in roles
        ):
            employee = frappe.db.get_value(
                "Employee",
                {"user_id": user},
                "name"
            )

            if not employee:
                frappe.throw(
                    "Employee not linked with this user",
                    frappe.PermissionError
                )

            filters["assigned_to"] = employee

        # ----------------------------------
        # FETCH DATA
        # ----------------------------------
        appointments = frappe.get_all(
            "Book Appointment",
            filters=filters,
            fields=[
                "name", "customer_name", "email", "phone", "license_plate",
                "make", "model", "service_type", "appointment_date",
                "appointment_time", "vehicle_pickup_required",
                "pickup_address", "assigned_to", "drop_address",
                "status", "description", "creation", "modified"
            ]
        )

        # ----------------------------------
        # SEARCH FILTER
        # ----------------------------------
        if search:
            search_lower = search.lower()
            appointments = [
                appt for appt in appointments
                if search_lower in (appt.get("name") or "").lower()
                or search_lower in (appt.get("customer_name") or "").lower()
                or search_lower in (appt.get("phone") or "").lower()
                or search_lower in (appt.get("license_plate") or "").lower()
            ]

        # -------------------------
        # STANDARD RESPONSE FORMAT
        # -------------------------
        return {
            "status": "success",
            "pagination": {
                "current_page": 1,
                "page_size": len(appointments),
                "total_records": len(appointments),
                "total_pages": 1
            },
            "data": appointments
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Fetch Book Appointments Error"
        )
        return {
            "status": "error",
            "message": str(e)
        }


# ----------------------------------------------------------------------------
# ...................Get Single Book Appointement Id..........................
# ----------------------------------------------------------------------------



@frappe.whitelist(allow_guest=False)
def get_book_appointment(appointment_id):
    """
    Get a single Book Appointment by ID
    - Administrator & Receptionist → can view all
    - Assigned Adviser (Employee) → can view only assigned
    """
    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        is_admin = "Administrator" in roles
        is_receptionist = "Receptionist" in roles
        is_employee = "Employee" in roles

        # --------------------------------
        # FETCH APPOINTMENT
        # --------------------------------
        doc = frappe.get_doc("Book Appointment", appointment_id)

        # --------------------------------
        # EMPLOYEE LINK (ONLY FOR EMPLOYEE)
        # --------------------------------
        employee = None
        if is_employee:
            employee = frappe.db.get_value(
                "Employee",
                {"user_id": user},
                "name"
            )

        # --------------------------------
        # PERMISSION CHECK
        # --------------------------------
        if is_admin or is_receptionist:
            # Full access
            pass

        elif is_employee and employee:
            if doc.assigned_to != employee:
                frappe.throw(
                    _("You can only view appointments assigned to you"),
                    frappe.PermissionError
                )

        else:
            frappe.throw(
                _("You are not allowed to view this appointment"),
                frappe.PermissionError
            )

        # --------------------------------
        # RESPONSE DATA
        # --------------------------------
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
            "same_as_pick_up_address": doc.same_as_pick_up_address,
            "drop_address": doc.drop_address,
            "assigned_to": doc.assigned_to,
            "status": doc.status,
            "description": doc.description,
            "creation": doc.creation,
            "modified": doc.modified
        }

        frappe.clear_messages()
        return {
            "status": "success",
            "status_code": 200,
            "data": data
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Get Book Appointment Error"
        )
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }




# -----------------------------------------------------------------
# .................update book appointment.........................
# -----------------------------------------------------------------


from frappe.utils import getdate, get_time

@frappe.whitelist(allow_guest=False)
def update_book_appointment(data):
    """
    Update Book Appointment
    - Only Receptionist and Administrator are allowed
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        # ----------------------------------
        # ROLE CHECK
        # ----------------------------------
        if not ("Receptionist" in roles or "Administrator" in roles):
            frappe.throw(
                "You are not allowed to update Book Appointments",
                frappe.PermissionError
            )

        # ----------------------------------
        # PARSE JSON PAYLOAD
        # ----------------------------------
        data = frappe.parse_json(data)

        appointment_id = data.pop("appointment_id", None)
        if not appointment_id:
            return {
                "status": "error",
                "message": "appointment_id is required"
            }

        appointment_id = str(appointment_id).strip().strip("'").strip('"')

        # ----------------------------------
        # CHECK EXISTENCE
        # ----------------------------------
        if not frappe.db.exists("Book Appointment", appointment_id):
            return {
                "status": "error",
                "message": f"Book Appointment {appointment_id} not found"
            }

        # ----------------------------------
        # DATE / TIME VALIDATION
        # ----------------------------------
        if "appointment_date" in data:
            try:
                data["appointment_date"] = getdate(data["appointment_date"])
            except Exception:
                return {
                    "status": "error",
                    "message": "Invalid appointment_date format. Use YYYY-MM-DD"
                }

        if "appointment_time" in data:
            try:
                data["appointment_time"] = get_time(data["appointment_time"])
            except Exception:
                return {
                    "status": "error",
                    "message": "Invalid appointment_time format. Use HH:MM"
                }

        # ----------------------------------
        # UPDATE DOCUMENT
        # ----------------------------------
        doc = frappe.get_doc("Book Appointment", appointment_id)
        doc.update(data)
        doc.save(ignore_permissions=True)

        frappe.db.commit()
        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Appointment updated successfully",
            "appointment_id": doc.name,
            "updated_fields": data
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Update Appointment Error"
        )
        return {
            "status": "error",
            "message": str(e)
        }



# ------------------------------------------------------------------
# ................Delete Book Appointement..........................
# ------------------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def delete_book_appointment(appointment_id):
    """
    Delete a Book Appointment
    Only Receptionist or Administrator can delete
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        # ----------------------------------
        # ROLE CHECK
        # ----------------------------------
        allowed_roles = ["Receptionist", "Administrator"]

        if not any(role in roles for role in allowed_roles):
            frappe.throw(
                "You are not allowed to delete Book Appointments",
                frappe.PermissionError
            )

        # ----------------------------------
        # CHECK EXISTENCE
        # ----------------------------------
        if not frappe.db.exists("Book Appointment", appointment_id):
            return {
                "status": "error",
                "status_code": 404,
                "message": f"Book Appointment '{appointment_id}' not found"
            }

        # ----------------------------------
        # DELETE DOCUMENT
        # ----------------------------------
        frappe.delete_doc(
            "Book Appointment",
            appointment_id,
            ignore_permissions=True
        )

        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 200,
            "message": f"Appointment '{appointment_id}' deleted successfully"
        }

    except frappe.PermissionError:
        # PermissionError already handled by frappe.throw
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Delete Book Appointment Error"
        )
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }




@frappe.whitelist(allow_guest=False)
def cancel_book_appointment(appointment_name):
    """
    Cancel Book Appointment
    - Employee: only their assigned appointment
    - Receptionist / Administrator: all
    - Assigned Adviser: not allowed
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        is_admin = "Administrator" in roles
        is_receptionist = "Receptionist" in roles
        is_employee = "Employee" in roles

        # ----------------------------------
        # GET EMPLOYEE LINKED TO USER
        # ----------------------------------
        employee = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            "name"
        )

        # ----------------------------------
        # FETCH APPOINTMENT
        # ----------------------------------
        appointment = frappe.get_doc("Book Appointment", appointment_name)

        # ----------------------------------
        # PERMISSION LOGIC
        # ----------------------------------

        # Receptionist & Admin → full access
        if not (is_admin or is_receptionist):

            # Employee must exist
            if not employee:
                frappe.throw(
                    "Employee not linked with this user",
                    frappe.PermissionError
                )

            # Employee can cancel ONLY if assigned
            if appointment.assigned_to != employee:
                frappe.throw(
                    "You can only cancel appointments assigned to you",
                    frappe.PermissionError
                )

        # ----------------------------------
        # STATUS VALIDATION
        # ----------------------------------
        if appointment.status == "Complete":
            frappe.throw("Completed appointment cannot be cancelled")

        if appointment.status not in ["Open", "Confirmed"]:
            frappe.throw(
                f"Appointment cannot be cancelled from status {appointment.status}"
            )

        # ----------------------------------
        # CANCEL APPOINTMENT
        # ----------------------------------
        appointment.status = "Cancelled"
        appointment.save(ignore_permissions=True)

        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment.name
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Cancel Book Appointment Error"
        )
        frappe.throw(str(e))






@frappe.whitelist(allow_guest=False)
def get_car_repair_request_by_appointment(appointment_id):
    """
    Get FULL Car Repair Request data using Book Appointment ID
    Permission:
    - Employee: only own created Car Repair Request
    - Receptionist / Administrator: all
    - Adviser: not allowed
    """

    validate_api_access("Book Appointment")

    try:
        user = frappe.session.user
        roles = frappe.get_roles(user)

        is_admin = "Administrator" in roles
        is_receptionist = "Receptionist" in roles
        is_employee = "Employee" in roles

        # ----------------------------------
        # BLOCK ADVISER
        # ----------------------------------
        if "Adviser" in roles and not (is_admin or is_receptionist):
            frappe.throw(
                "You are not allowed to view Car Repair Requests",
                frappe.PermissionError
            )

        # ----------------------------------
        # VALIDATE APPOINTMENT
        # ----------------------------------
        if not frappe.db.exists("Book Appointment", appointment_id):
            return {
                "status": "error",
                "message": f"Book Appointment '{appointment_id}' not found"
            }

        # ----------------------------------
        # FETCH CAR REPAIR REQUEST
        # ----------------------------------
        car_repair_request_id = frappe.db.exists(
            "Car Repair Request",
            {"appointment": appointment_id}
        )

        if not car_repair_request_id:
            return {
                "status": "success",
                "status_code": 200,
                "appointment_id": appointment_id,
                "car_repair_request": None,
                "message": "No Car Repair Request found for this appointment"
            }

        repair = frappe.get_doc("Car Repair Request", car_repair_request_id)

        # ----------------------------------
        # EMPLOYEE → ONLY OWN CREATED
        # ----------------------------------
        if is_employee and not (is_admin or is_receptionist):
            if repair.owner != user:
                frappe.throw(
                    "You are not allowed to view this Car Repair Request",
                    frappe.PermissionError
                )

        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "appointment_id": appointment_id,
            "data": repair.as_dict()
        }

    except frappe.PermissionError:
        raise

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Get Car Repair Request Error"
        )
        return {
            "status": "error",
            "message": str(e)
        }
