




import frappe
from frappe import _

@frappe.whitelist()
def create_car_repair_request(appointment_name):
    """
    Create a Car Repair Request from a Book Appointment.
    - Automatically creates a Customer if not found.
    - The 'car' field (Data) will display the license_plate from the appointment.
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
        # Handle Odometer Photo (Optional)
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
            "car": appointment.license_plate,  # <-- Display license_plate directly
            "license_plate": appointment.license_plate,
            "make": appointment.make,
            "model": appointment.model,
            "service_type": appointment.service_type,
            "reason_for_repair": appointment.reason_for_repair,
            "appointment": appointment.name,
            "status": "Open",
            "odometer_photo": odometer_photo,
            "customer_signature": appointment.get("customer_signature") or None,
            "vehicle_pickup_required": appointment.vehicle_pickup_required,
            "pickup_address": appointment.pickup_address,
            "same_as_pick_up_address": appointment.same_as_pick_up_address or 0,
            "drop_address": appointment.drop_address,
            "assigned_to": appointment.assigned_to
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
        frappe.msgprint(f"Before Insert - Customer Name: {repair.customer_name}, Car: {repair.car}")
        repair.insert(ignore_permissions=True)
        frappe.db.commit()

        # -------------------------------
        # Restore field requirements
        # -------------------------------
        if odometer_field:
            odometer_field.reqd = original_required_odometer
        if images_field:
            images_field.reqd = original_required_images

        frappe.msgprint(f"After Insert - Saved: {repair.name}, Customer Name: {repair.customer_name}, Car: {repair.car}")
        return repair.name

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Create Car Repair Request Error")
        frappe.throw(_("Error while creating Car Repair Request: ") + str(e))
