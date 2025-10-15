# import frappe

# @frappe.whitelist(allow_guest=True)
# def approve_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Approved")  # Workflow must have this state
#     frappe.db.commit()
#     return "Quotation Approved"

# @frappe.whitelist(allow_guest=True)
# def reject_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Rejected")  # Workflow must have this state
#     frappe.db.commit()
#     return "Quotation Rejected"



# import frappe
# from frappe import _

# @frappe.whitelist(allow_guest=True)
# def approve_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Approved")
#     frappe.db.commit()

#     html = f"""
#     <html>
#     <head><title>Quotation Approved</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: green;">Quotation {q.name} Approved ✅</h2>
#         <p>Thank you! Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")

# @frappe.whitelist(allow_guest=True)
# def reject_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Rejected")
#     frappe.db.commit()

#     html = f"""
#     <html>
#     <head><title>Quotation Rejected</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: red;">Quotation {q.name} Rejected ❌</h2>
#         <p>Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")




# import frappe

# @frappe.whitelist(allow_guest=True)
# def approve_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Approved")
#     frappe.db.commit()

#     title = q.title or q.name  # fallback to ID if title is empty

#     html = f"""
#     <html>
#     <head><title>Quotation Approved</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: green;">Quotation "{title}" Approved ✅</h2>
#         <p>Thank you! Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")

# @frappe.whitelist(allow_guest=True)
# def reject_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Rejected")
#     frappe.db.commit()

#     title = q.title or q.name

#     html = f"""
#     <html>
#     <head><title>Quotation Rejected</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: red;">Quotation "{title}" Rejected ❌</h2>
#         <p>Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")

# import frappe
# from frappe import _

# @frappe.whitelist(allow_guest=True)
# def approve_quotation(quotation):
#     # Step 1: Approve Quotation
#     frappe.db.set_value("Quotation", quotation, "workflow_state", "Approved")
#     frappe.db.commit()

#     # Reload Quotation
#     q = frappe.get_doc("Quotation", quotation)

#     car_repair_docname = None

#     # Step 2: Create Car Repair if linked Car Diagnosis exists
#     if q.get("car_diagnosis"):
#         try:
#             diagnosis = frappe.get_doc("Car Diagnosis", q.car_diagnosis)
#         except frappe.DoesNotExistError:
#             frappe.msgprint(f"Linked Car Diagnosis {q.car_diagnosis} does not exist.")
#             diagnosis = None
#         except Exception as e:
#             frappe.msgprint(f"Error fetching Car Diagnosis: {e}")
#             diagnosis = None

#         if diagnosis:
#             # Prevent duplicate Car Repair
#             if diagnosis.get("car_diagnosis_detail") and not frappe.db.exists("Car repair", {"car_diagnosis": diagnosis.name}):
#                 # Fetch Vehicle if exists
#                 vehicle = None
#                 if diagnosis.get("car"):
#                     try:
#                         vehicle = frappe.get_doc("Vehicle", diagnosis.car)
#                     except frappe.DoesNotExistError:
#                         frappe.msgprint(f"Linked Vehicle {diagnosis.car} does not exist.")
#                     except Exception as e:
#                         frappe.msgprint(f"Error fetching Vehicle: {e}")

#                 # Create Car Repair
#                 repair = frappe.get_doc({
#                     "doctype": "Car repair",
#                     "car_diagnosis": diagnosis.name,
#                     "car": diagnosis.get("car"),
#                     "model": vehicle.model if vehicle else "",
#                     "license_plate": vehicle.license_plate if vehicle else "",
#                     "customer_name": diagnosis.get("customer_name") or q.customer,
#                     "email": diagnosis.get("email_id") or q.contact_email,
#                     "phone": diagnosis.get("phone") or q.contact_no,
#                     "list_of_damage": []
#                 })

#                 # Copy damage items
#                 for damage in diagnosis.get("car_diagnosis_detail") or []:
#                     repair.append("list_of_damage", {
#                         "damage_description": damage.get("damage_description") or "",
#                         "assigned_to": damage.get("assigned_to") or "",
#                         "part_required": damage.get("part_required") or "",
#                         "estimated_cost": damage.get("estimated_cost") or 0
#                     })

#                 repair.insert(ignore_permissions=True)
#                 frappe.db.commit()
#                 car_repair_docname = repair.name

#     # Step 3: Prepare link to Car Repair if created
#     car_repair_url = f"{frappe.utils.get_url()}/app/car-repair/{car_repair_docname}" if car_repair_docname else None

#     # Step 4: Return HTML response
#     title = q.title or q.name
#     html = f"""
#     <html>
#     <head><title>Quotation Approved</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: green;">Quotation "{title}" Approved ✅</h2>
#         <p>Thank you! Your response has been recorded successfully.</p>
        
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")


# @frappe.whitelist(allow_guest=True)
# def reject_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Rejected")
#     frappe.db.commit()

#     title = q.title or q.name
#     html = f"""
#     <html>
#     <head><title>Quotation Rejected</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: red;">Quotation "{title}" Rejected ❌</h2>
#         <p>Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")




import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def approve_quotation(quotation):
    from frappe.utils import now_datetime

    # Step 1: Approve Quotation
    frappe.db.set_value("Quotation", quotation, "workflow_state", "Approved")

    # Step 1.1: Add Approval Timestamp Logic
    q = frappe.get_doc("Quotation", quotation)

    # Determine who approved — using user roles or parameter
    current_user = frappe.session.user if frappe.session.user != "Guest" else None
    roles = frappe.get_roles(current_user) if current_user else []

    # If approval by Customer
    if "Customer" in roles and not q.customer_approved_on:
        frappe.db.set_value("Quotation", quotation, "customer_approved_on", now_datetime())

    # If approval by Service Provider
    elif "Service Provider" in roles and not q.service_provider_approved_on:
        frappe.db.set_value("Quotation", quotation, "service_provider_approved_on", now_datetime())

    frappe.db.commit()

    # Step 2: Create Car Repair if linked Car Diagnosis exists
    car_repair_docname = None

    if q.get("car_diagnosis"):
        try:
            diagnosis = frappe.get_doc("Car Diagnosis", q.car_diagnosis)
        except frappe.DoesNotExistError:
            frappe.msgprint(f"Linked Car Diagnosis {q.car_diagnosis} does not exist.")
            diagnosis = None
        except Exception as e:
            frappe.msgprint(f"Error fetching Car Diagnosis: {e}")
            diagnosis = None

        if diagnosis:
            if diagnosis.get("car_diagnosis_detail") and not frappe.db.exists("Car repair", {"car_diagnosis": diagnosis.name}):
                vehicle = None
                if diagnosis.get("car"):
                    try:
                        vehicle = frappe.get_doc("Vehicle", diagnosis.car)
                    except frappe.DoesNotExistError:
                        frappe.msgprint(f"Linked Vehicle {diagnosis.car} does not exist.")
                    except Exception as e:
                        frappe.msgprint(f"Error fetching Vehicle: {e}")

                repair = frappe.get_doc({
                    "doctype": "Car repair",
                    "car_diagnosis": diagnosis.name,
                    "car": diagnosis.get("car"),
                    "model": vehicle.model if vehicle else "",
                    "license_plate": vehicle.license_plate if vehicle else "",
                    "customer_name": diagnosis.get("customer_name") or q.customer,
                    "email": diagnosis.get("email_id") or q.contact_email,
                    "phone": diagnosis.get("phone") or q.contact_no,
                    "list_of_damage": []
                })

                for damage in diagnosis.get("car_diagnosis_detail") or []:
                    repair.append("list_of_damage", {
                        "damage_description": damage.get("damage_description") or "",
                        "assigned_to": damage.get("assigned_to") or "",
                        "part_required": damage.get("part_required") or "",
                        "estimated_cost": damage.get("estimated_cost") or 0
                    })

                repair.insert(ignore_permissions=True)
                frappe.db.commit()
                car_repair_docname = repair.name

    # Step 3: Prepare link to Car Repair if created
    car_repair_url = f"{frappe.utils.get_url()}/app/car-repair/{car_repair_docname}" if car_repair_docname else None

    # Step 4: Return HTML response
    title = q.title or q.name
    html = f"""
    <html>
    <head><title>Quotation Approved</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
        <h2 style="color: green;">Quotation "{title}" Approved ✅</h2>
        <p>Thank you! Your response has been recorded successfully.</p>
    </body>
    </html>
    """
    return frappe.utils.response.Response(html, status=200, mimetype="text/html")



# # padte.py
# import frappe
# from frappe.utils import now_datetime
# from frappe import _

# # -------------------------------
# # Central logging function
# # -------------------------------
# def log_to_history(doc_type, doc_name, action, remarks=None, user=None):
#     """
#     Log an action into Car Repair History Log for any DocType in the workflow.
#     """
#     user = user or frappe.session.user or "System"
#     frappe.get_doc({
#         "doctype": "Car Repair History Log",
#         "document_type": doc_type,
#         "document_name": doc_name,
#         "action": action,
#         "performed_by": user,
#         "timestamp": now_datetime(),
#         "remarks": remarks or ""
#     }).insert(ignore_permissions=True)
#     frappe.db.commit()


# # -------------------------------
# # Quotation Approve / Reject
# # -------------------------------
# @frappe.whitelist(allow_guest=True)
# def approve_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)

#     # Update workflow state
#     q.db_set("workflow_state", "Approved")

#     # Determine role
#     roles = frappe.get_roles(frappe.session.user)
#     role_type = "Customer" if "Customer" in roles else "Service Provider" if "Service Provider" in roles else "Unknown"

#     # Optional timestamp fields
#     field_to_update = "customer_approved_on" if role_type=="Customer" else "service_provider_approved_on"
#     q.db_set(field_to_update, now_datetime())

#     # Log approval
#     log_to_history(
#         doc_type="Quotation",
#         doc_name=quotation,
#         action="Approved",
#         remarks=f"Quotation approved by {role_type}"
#     )

#     frappe.db.commit()

#     # Auto-create Car Repair if linked to Car Diagnosis
#     car_repair_docname = None
#     if q.get("car_diagnosis"):
#         try:
#             diagnosis = frappe.get_doc("Car Diagnosis", q.car_diagnosis)
#         except Exception as e:
#             frappe.msgprint(f"Error fetching Car Diagnosis: {e}")
#             diagnosis = None

#         if diagnosis and diagnosis.get("car_diagnosis_detail") and not frappe.db.exists("Car repair", {"car_diagnosis": diagnosis.name}):
#             vehicle = frappe.get_doc(diagnosis.car) if diagnosis.get("car") else None

#             repair = frappe.get_doc({
#                 "doctype": "Car repair",
#                 "car_diagnosis": diagnosis.name,
#                 "car": diagnosis.get("car"),
#                 "model": vehicle.model if vehicle else "",
#                 "license_plate": vehicle.license_plate if vehicle else "",
#                 "customer_name": diagnosis.get("customer_name") or q.customer,
#                 "email": diagnosis.get("email_id") or q.contact_email,
#                 "phone": diagnosis.get("phone") or q.contact_no,
#                 "list_of_damage": []
#             })

#             # Copy damages
#             for damage in diagnosis.get("car_diagnosis_detail") or []:
#                 repair.append("list_of_damage", {
#                     "damage_description": damage.get("damage_description") or "",
#                     "assigned_to": damage.get("assigned_to") or "",
#                     "part_required": damage.get("part_required") or "",
#                     "estimated_cost": damage.get("estimated_cost") or 0
#                 })

#             repair.insert(ignore_permissions=True)
#             frappe.db.commit()
#             car_repair_docname = repair.name

#             # Log Car Repair creation
#             log_to_history(
#                 doc_type="Car Repair",
#                 doc_name=repair.name,
#                 action="Created from Car Repair Request",
#                 remarks=f"Auto-created from Car Diagnosis {diagnosis.name}"
#             )

#     # Response HTML
#     title = q.title or q.name
#     html = f"""
#     <html>
#     <head><title>Quotation Approved</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: green;">Quotation "{title}" Approved ✅</h2>
#         <p>Thank you! Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")


# @frappe.whitelist(allow_guest=True)
# def reject_quotation(quotation):
#     q = frappe.get_doc("Quotation", quotation)
#     q.db_set("workflow_state", "Rejected")

#     # Determine role
#     roles = frappe.get_roles(frappe.session.user)
#     role_type = "Customer" if "Customer" in roles else "Service Provider" if "Service Provider" in roles else "Unknown"

#     # Log rejection
#     log_to_history(
#         doc_type="Quotation",
#         doc_name=quotation,
#         action="Rejected",
#         remarks=f"Quotation rejected by {role_type}"
#     )

#     frappe.db.commit()

#     title = q.title or q.name
#     html = f"""
#     <html>
#     <head><title>Quotation Rejected</title></head>
#     <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
#         <h2 style="color: red;">Quotation "{title}" Rejected ❌</h2>
#         <p>Your response has been recorded successfully.</p>
#     </body>
#     </html>
#     """
#     return frappe.utils.response.Response(html, status=200, mimetype="text/html")


# # -------------------------------
# # Generic logging for any DocType
# # -------------------------------
# def log_doc_action(doc, action, remarks=None):
#     """
#     Call this after creating/updating any DocType in the workflow.
#     """
#     log_to_history(
#         doc_type=doc.doctype,
#         doc_name=doc.name,
#         action=action,
#         remarks=remarks
#     )
