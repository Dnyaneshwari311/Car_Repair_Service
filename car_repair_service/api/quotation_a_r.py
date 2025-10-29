




import frappe
from frappe import _
from frappe.utils import now_datetime, get_url

# -------------------------
# Approve Quotation
# -------------------------
@frappe.whitelist(allow_guest=True)
def approve_quotation(quotation):
    """Approve quotation and optionally create Car Repair"""
    
    # Step 1: Set workflow state to Approved
    frappe.db.set_value("Quotation", quotation, "workflow_state", "Approved")
    q = frappe.get_doc("Quotation", quotation)

    # Step 1.1: Add Approval Timestamp Logic
    current_user = frappe.session.user if frappe.session.user != "Guest" else None
    roles = frappe.get_roles(current_user) if current_user else []

    if "Customer" in roles and not q.custom_customer_approved_on:
        frappe.db.set_value("Quotation", quotation, "custom_customer_approved_on", now_datetime())
    elif "Service Provider" in roles and not q.service_provider_approved_on:
        frappe.db.set_value("Quotation", quotation, "custom_service_provider_approved_on", now_datetime())

    frappe.db.commit()

    # Step 2: Create Car Repair if linked Car Diagnosis exists
    car_repair_docname = create_car_repair_from_diagnosis(q)

    # Step 3: Return HTML response
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


# -------------------------
# Reject Quotation
# -------------------------
@frappe.whitelist(allow_guest=True)
def reject_quotation(quotation):
    """Reject a quotation and track rejection timestamps by role"""
    
    # Step 1: Set workflow state to Rejected
    frappe.db.set_value("Quotation", quotation, "workflow_state", "Rejected")
    q = frappe.get_doc("Quotation", quotation)

    # Step 1.1: Add Rejection Timestamp Logic
    current_user = frappe.session.user if frappe.session.user != "Guest" else None
    roles = frappe.get_roles(current_user) if current_user else []

    if "Customer" in roles and not q.custom_customer_rejected_on:
        frappe.db.set_value("Quotation", quotation, "custom_customer_rejected_on", now_datetime())
    elif "Service Provider" in roles and not q.service_provider_rejected_on:
        frappe.db.set_value("Quotation", quotation, "custom_service_provider_rejected_on", now_datetime())

    frappe.db.commit()

    # Step 2: Return HTML response
    title = q.title or q.name
    html = f"""
    <html>
    <head><title>Quotation Rejected</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
        <h2 style="color: red;">Quotation "{title}" Rejected ❌</h2>
        <p>Your response has been recorded successfully.</p>
    </body>
    </html>
    """
    return frappe.utils.response.Response(html, status=200, mimetype="text/html")


# -------------------------
# Helper: Create Car Repair from Diagnosis
# -------------------------
def create_car_repair_from_diagnosis(q):
    """Optional: create Car Repair if Car Diagnosis exists"""
    car_repair_docname = None

    if q.get("car_diagnosis"):
        try:
            diagnosis = frappe.get_doc("Car Diagnosis", q.car_diagnosis)
        except frappe.DoesNotExistError:
            diagnosis = None
        except Exception:
            diagnosis = None

        if diagnosis and diagnosis.get("car_diagnosis_detail") and not frappe.db.exists("Car repair", {"car_diagnosis": diagnosis.name}):
            vehicle = frappe.get_doc("Vehicle", diagnosis.car) if diagnosis.get("car") else None
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

    return car_repair_docname


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
