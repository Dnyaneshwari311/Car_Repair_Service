# import frappe
# from frappe import _

# @frappe.whitelist()
# def create_car_repair_request(appointment_name):
#     """Create a Car Repair Request from Book Appointment"""
#     # Fetch appointment doc
#     appointment = frappe.get_doc("Book Appointment", appointment_name)

#     # ✅ Check if a Car Repair Request already exists
#     existing = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
#     if existing:
#         return existing  # Return existing record name

#     # ✅ Create new Car Repair Request
#     repair = frappe.new_doc("Car Repair Request")
#     repair.customer_name = appointment.customer_name
#     repair.email = appointment.email
#     repair.phone = appointment.phone
#     repair.license_plate = appointment.license_plate
#     repair.make = appointment.make
#     repair.model = appointment.model
#     repair.service_type = appointment.service_type
#     repair.reason_for_repair = appointment.reason_for_repair
#     repair.appointment = appointment.name

#     repair.insert(ignore_permissions=True)
#     frappe.db.commit()

#     return repair.name
# import frappe
# from frappe import _

# @frappe.whitelist()
# def create_car_repair_request(appointment_name):
#     appointment = frappe.get_doc("Book Appointment", appointment_name)

#     frappe.msgprint(f"Fetched Customer Name from Appointment: {appointment.customer_name}")

#     existing = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
#     if existing:
#         return existing

#     repair = frappe.new_doc("Car Repair Request")
#     repair.update({
#         "customer_name": appointment.customer_name or "",
#         "email": appointment.email,
#         "phone": appointment.phone,
#         "license_plate": appointment.license_plate,
#         "make": appointment.make,
#         "model": appointment.model,
#         "service_type": appointment.service_type,
#         "reason_for_repair": appointment.reason_for_repair,
#         "appointment": appointment.name
#     })

#     frappe.msgprint(f"Before Insert - Customer Name: {repair.customer_name}")
#     repair.insert(ignore_permissions=True)
#     frappe.db.commit()

#     frappe.msgprint(f"After Insert - Saved: {repair.name}, Customer Name: {repair.customer_name}")

#     return repair.name



# .........................before adding odometer photo and signature....................

# import frappe
# from frappe import _

# @frappe.whitelist()
# def create_car_repair_request(appointment_name):
#     appointment = frappe.get_doc("Book Appointment", appointment_name)

#     frappe.msgprint(f"Fetched Customer Name from Appointment: {appointment.customer_name}")

#     existing = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
#     if existing:
#         return existing

#     # if your appointment has only text for customer_name, try finding or creating a Customer first
#     customer_name = appointment.customer_name
#     customer = frappe.db.exists("Customer", {"customer_name": customer_name})
#     if not customer:
#         frappe.msgprint(f"Customer not found, creating new customer: {customer_name}")
#         customer_doc = frappe.get_doc({
#             "doctype": "Customer",
#             "customer_name": customer_name,
#             "email_id": appointment.email,
#             "mobile_no": appointment.phone
#         }).insert(ignore_permissions=True)
#         customer = customer_doc.name

#     repair = frappe.new_doc("Car Repair Request")
#     repair.update({
#         "customer_name": customer,  # ✅ now link to actual Customer record
#         "email": appointment.email,
#         "phone": appointment.phone,
#         "license_plate": appointment.license_plate,
#         "make": appointment.make,
#         "model": appointment.model,
#         "service_type": appointment.service_type,
#         "reason_for_repair": appointment.reason_for_repair,
#         "appointment": appointment.name,
#         "status": "Open"  # ✅ default status
#     })

#     frappe.msgprint(f"Before Insert - Customer Name: {repair.customer_name}")
#     repair.insert(ignore_permissions=True)
#     frappe.db.commit()

#     frappe.msgprint(f"After Insert - Saved: {repair.name}, Customer Name: {repair.customer_name}")

#     return repair.name


# import frappe
# from frappe import _

# @frappe.whitelist()
# def create_car_repair_request(appointment_name):
#     """
#     Create a Car Repair Request from a given Book Appointment.
#     Automatically creates a Customer if not found,
#     and ensures all mandatory fields (like images) are handled safely.
#     """

#     try:
#         # -------------------------------
#         # Fetch Appointment
#         # -------------------------------
#         appointment = frappe.get_doc("Book Appointment", appointment_name)
#         frappe.msgprint(f"Fetched Customer Name from Appointment: {appointment.customer_name}")

#         # -------------------------------
#         # Avoid duplicate Car Repair Request
#         # -------------------------------
#         existing = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
#         if existing:
#             frappe.msgprint(_("Existing Car Repair Request found: ") + existing)
#             return existing

#         # -------------------------------
#         # Find or Create Customer
#         # -------------------------------
#         customer_name = appointment.customer_name
#         customer = frappe.db.exists("Customer", {"customer_name": customer_name})
#         if not customer:
#             frappe.msgprint(f"Customer not found, creating new customer: {customer_name}")
#             customer_doc = frappe.get_doc({
#                 "doctype": "Customer",
#                 "customer_name": customer_name,
#                 "email_id": appointment.email,
#                 "mobile_no": appointment.phone
#             }).insert(ignore_permissions=True)
#             customer = customer_doc.name

#         # -------------------------------
#         # Handle Odometer Photo (Mandatory)
#         # -------------------------------
#         odometer_photo = appointment.get("odometer_photo")
#         if not odometer_photo:
#             # ✅ Fallback image to satisfy mandatory validation
#             odometer_photo = "/files/no-image.jpg"

#         # -------------------------------
#         # Create Car Repair Request Document
#         # -------------------------------
#         repair = frappe.new_doc("Car Repair Request")
#         repair.update({
#             "customer_name": customer,
#             "email": appointment.email,
#             "phone": appointment.phone,
#             "license_plate": appointment.license_plate,
#             "make": appointment.make,
#             "model": appointment.model,
#             "service_type": appointment.service_type,
#             "reason_for_repair": appointment.reason_for_repair,
#             "appointment": appointment.name,
#             "status": "Open",
#             "odometer_photo": odometer_photo,
#             "customer_signature": appointment.get("customer_signature") or None
#         })

#         # -------------------------------
#         # Child Table: Car Repair Images (image field)
#         # -------------------------------
#         # If the child table is empty, add one valid row with an image
#         if hasattr(repair, "car_repair_images") and not repair.car_repair_images:
#             image_value = appointment.get("vehicle_photo") or odometer_photo
#             repair.append("car_repair_images", {
#                 "image": image_value   # <-- this is your image field
#             })

#         # -------------------------------
#         # Insert and Commit
#         # -------------------------------
#         frappe.msgprint(f"Before Insert - Customer Name: {repair.customer_name}")
#         repair.insert(ignore_permissions=True)
#         frappe.db.commit()

#         frappe.msgprint(f"After Insert - Saved: {repair.name}, Customer Name: {repair.customer_name}")
#         return repair.name

#     except Exception as e:
#         frappe.log_error(message=frappe.get_traceback(), title="Create Car Repair Request Error")
#         frappe.throw(_("Error while creating Car Repair Request: ") + str(e))





import frappe
from frappe import _

@frappe.whitelist()
def create_car_repair_request(appointment_name):
    """
    Create a Car Repair Request from a given Book Appointment.
    - Automatically creates a Customer if not found.
    - Temporarily disables mandatory validation for 'odometer_photo' and 'car_repair_images' during insert.
    - Ensures clean insert even when images are missing.
    """

    try:
        # -------------------------------
        # Fetch Appointment
        # -------------------------------
        appointment = frappe.get_doc("Book Appointment", appointment_name)
        frappe.msgprint(f"Fetched Customer Name from Appointment: {appointment.customer_name}")

        # -------------------------------
        # Avoid duplicate Car Repair Request
        # -------------------------------
        existing = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
        if existing:
            frappe.msgprint(_("Existing Car Repair Request found: ") + existing)
            return existing

        # -------------------------------
        # Find or Create Customer
        # -------------------------------
        customer_name = appointment.customer_name
        customer = frappe.db.exists("Customer", {"customer_name": customer_name})
        if not customer:
            frappe.msgprint(f"Customer not found, creating new customer: {customer_name}")
            customer_doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "email_id": appointment.email,
                "mobile_no": appointment.phone
            }).insert(ignore_permissions=True)
            customer = customer_doc.name

        # -------------------------------
        # Handle Odometer Photo (Can Be Blank)
        # -------------------------------
        odometer_photo = appointment.get("odometer_photo") or None

        # -------------------------------
        # Create Car Repair Request Document
        # -------------------------------
        repair = frappe.new_doc("Car Repair Request")
        repair.update({
            "customer_name": customer,
            "email": appointment.email,
            "phone": appointment.phone,
            "license_plate": appointment.license_plate,
            "make": appointment.make,
            "model": appointment.model,
            "service_type": appointment.service_type,
            "reason_for_repair": appointment.reason_for_repair,
            "appointment": appointment.name,
            "status": "Open",
            "odometer_photo": odometer_photo,
            "customer_signature": appointment.get("customer_signature") or None
        })

        # -------------------------------
        # Child Table: Car Repair Images (optional)
        # -------------------------------
        if hasattr(repair, "car_repair_images") and not repair.car_repair_images:
            image_value = appointment.get("vehicle_photo") or odometer_photo
            if image_value:
                repair.append("car_repair_images", {"image": image_value})

        # -------------------------------
        # Temporarily disable mandatory fields for programmatic creation
        # -------------------------------
        meta = frappe.get_meta("Car Repair Request")

        # Disable mandatory for 'odometer_photo'
        odometer_field = next((df for df in meta.fields if df.fieldname == "odometer_photo"), None)
        if odometer_field:
            original_required_odometer = odometer_field.reqd
            odometer_field.reqd = 0

        # Disable mandatory for 'car_repair_images'
        images_field = next((df for df in meta.fields if df.fieldname == "car_repair_images"), None)
        if images_field:
            original_required_images = images_field.reqd
            images_field.reqd = 0

        # -------------------------------
        # Insert and Commit
        # -------------------------------
        frappe.msgprint(f"Before Insert - Customer Name: {repair.customer_name}")
        repair.insert(ignore_permissions=True)
        frappe.db.commit()

        # -------------------------------
        # Restore field requirements
        # -------------------------------
        if odometer_field:
            odometer_field.reqd = original_required_odometer
        if images_field:
            images_field.reqd = original_required_images

        frappe.msgprint(f"After Insert - Saved: {repair.name}, Customer Name: {repair.customer_name}")
        return repair.name

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Create Car Repair Request Error")
        frappe.throw(_("Error while creating Car Repair Request: ") + str(e))
