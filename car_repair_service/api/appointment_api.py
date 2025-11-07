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


import frappe
from frappe import _

@frappe.whitelist()
def create_car_repair_request(appointment_name):
    appointment = frappe.get_doc("Book Appointment", appointment_name)

    frappe.msgprint(f"Fetched Customer Name from Appointment: {appointment.customer_name}")

    existing = frappe.db.get_value("Car Repair Request", {"appointment": appointment_name}, "name")
    if existing:
        return existing

    # if your appointment has only text for customer_name, try finding or creating a Customer first
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

    repair = frappe.new_doc("Car Repair Request")
    repair.update({
        "customer_name": customer,  # ✅ now link to actual Customer record
        "email": appointment.email,
        "phone": appointment.phone,
        "license_plate": appointment.license_plate,
        "make": appointment.make,
        "model": appointment.model,
        "service_type": appointment.service_type,
        "reason_for_repair": appointment.reason_for_repair,
        "appointment": appointment.name,
        "status": "Open"  # ✅ default status
    })

    frappe.msgprint(f"Before Insert - Customer Name: {repair.customer_name}")
    repair.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.msgprint(f"After Insert - Saved: {repair.name}, Customer Name: {repair.customer_name}")

    return repair.name
