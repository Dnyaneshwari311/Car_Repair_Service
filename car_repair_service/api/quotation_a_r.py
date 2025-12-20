


        
        
        
        
        
import frappe
from frappe import _
from frappe.utils import now_datetime, get_url

# -------------------------
# Approve Quotation
# -------------------------
@frappe.whitelist(allow_guest=True)
def approve_quotation(quotation):
    """Approve quotation and always create/update Car Repair after approval"""

    q = frappe.get_doc("Quotation", quotation)

    # ✅ Only set workflow state if NOT already approved
    if q.get("workflow_state") != "Approved":
        frappe.db.set_value("Quotation", quotation, "workflow_state", "Approved")

    # ✅ Reload the quotation after update
    q = frappe.get_doc("Quotation", quotation)

    # Step 2: Track approval timestamps by role
    current_user = frappe.session.user if frappe.session.user != "Guest" else None
    roles = frappe.get_roles(current_user) if current_user else []

    if "Customer" in roles and not q.get("custom_customer_approved_on"):
        frappe.db.set_value("Quotation", quotation, "custom_customer_approved_on", now_datetime())
    elif "Service Provider" in roles and not q.get("custom_service_provider_approved_on"):
        frappe.db.set_value("Quotation", quotation, "custom_service_provider_approved_on", now_datetime())

    frappe.db.commit()

    # ✅ Step 3: Always CREATE or UPDATE Car Repair (quotation-based)
    create_or_update_car_repair(q)

    # Step 4: HTML Response
    title = q.get("title") or q.name
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
    """Reject quotation and track rejection timestamps by role"""

    frappe.db.set_value("Quotation", quotation, "workflow_state", "Rejected")
    q = frappe.get_doc("Quotation", quotation)

    current_user = frappe.session.user if frappe.session.user != "Guest" else None
    roles = frappe.get_roles(current_user) if current_user else []

    if "Customer" in roles and not q.get("custom_customer_rejected_on"):
        frappe.db.set_value("Quotation", quotation, "custom_customer_rejected_on", now_datetime())
    elif "Service Provider" in roles and not q.get("custom_service_provider_rejected_on"):
        frappe.db.set_value("Quotation", quotation, "custom_service_provider_rejected_on", now_datetime())

    frappe.db.commit()

    title = q.get("title") or q.name
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





# ------------------------------previous quotation updated code-------------------------------

# def create_or_update_car_repair(q):
#     """Create or Update Car Repair from a Quotation."""

#     car_diagnosis_id = q.get("custom_car_diagnosis")
#     if not car_diagnosis_id:
#         return None

#     # Get Car Diagnosis
#     try:
#         diagnosis = frappe.get_doc("Car Diagnosis", car_diagnosis_id)
#     except Exception:
#         return None

#     # Find existing Car Repair linked to this quotation or diagnosis
#     existing_repair_name = frappe.db.get_value("Car repair", {"quotation": q.name})
#     if not existing_repair_name:
#         existing_repair_name = frappe.db.get_value("Car repair", {"car_diagnosis": diagnosis.name})

#     # Vehicle info
#     vehicle = None
#     if diagnosis.get("car"):
#         try:
#             vehicle = frappe.get_doc("Vehicle", diagnosis.car)
#         except Exception:
#             vehicle = None

#     # Quotation details
#     customer_name = (
#         q.get("customer")
#         or q.get("party_name")
#         or q.get("customer_name")
#         or diagnosis.get("customer_name")
#     )
#     email = q.get("contact_email") or diagnosis.get("email_id")
#     phone = q.get("contact_no") or q.get("contact_mobile") or diagnosis.get("phone")

#     # Prepare child items (list_of_damage)
#     quotation_items = q.get("items") or []
#     child_rows = []
#     for qi in quotation_items:
#         qi = qi.as_dict() if hasattr(qi, "as_dict") else dict(qi)
#         # child_rows.append({
#         #     "damage_description": qi.get("description") or qi.get("item_name") or "",
#         #     "assigned_to": qi.get("assigned_to") or "",
#         #     "part_required": qi.get("item_code") or qi.get("item_name") or "",
#         #     "estimated_cost": qi.get("amount") or qi.get("rate") or 0
#         # })
        
        
#         child_rows.append({
#             "damage_description": qi.get("description") or qi.get("item_name") or "",
#             "assigned_to": qi.get("assigned_to") or "",
#             "part_required": qi.get("item_code") or qi.get("item_name") or "",
            
#             # Quantity from quotation item
#             "quantity": qi.get("qty") or 0,

#             # Estimated cost = quotation rate or amount
#             "estimated_cost": qi.get("rate") or qi.get("amount") or 0,

#             # Amount = qty × rate
#             "amount": (qi.get("qty") or 0) * (qi.get("rate") or 0)
#         })


#     # ✅ COMMON FIELDS from Car Diagnosis
#     delivery_date = diagnosis.get("estimated_delivery_date")
#     delivery_time = diagnosis.get("estimated_delivery_time")
#     vehicle_pick_up = diagnosis.get("vehicle_pick_up")  # 🆕 checkbox
#     customer_signature = diagnosis.get("customer_signature")  # 🆕 signature field

#     # 🆕 Copy vehicle_concern child table
#     diagnosis_concerns = diagnosis.get("vehicle_concern") or []
#     concern_rows = []
#     for c in diagnosis_concerns:
#         c = c.as_dict() if hasattr(c, "as_dict") else dict(c)
#         concern_rows.append({
#             "vehicle_concern": c.get("vehicle_concern") or ""
#         })

#     # -------------------------------------------------------------
#     # UPDATE EXISTING CAR REPAIR
#     # -------------------------------------------------------------
#     if existing_repair_name:
#         repair = frappe.get_doc("Car repair", existing_repair_name)

#         # ✅ Preserve previous signature if already set
#         existing_signature = repair.get("customer_signature") or customer_signature

#         repair.car_diagnosis = diagnosis.name
#         repair.car = diagnosis.get("car")
#         # repair.model = vehicle.model if vehicle else ""
#         # repair.model = get_model_name(vehicle.model) if vehicle else ""
#         # repair.model = frappe.db.get_value("Vehicle Model", vehicle.model, "model")
#         repair.model = frappe.db.get_value("Vehicle Model", vehicle.model, "model")


#         repair.license_plate = vehicle.license_plate if vehicle else ""
#         repair.customer_name = customer_name
#         repair.email = email
#         repair.phone = phone
#         repair.quotation = q.name
#         repair.reference_no = diagnosis.get("reference_no")
#         repair.estimated_delivery_date = delivery_date
#         repair.estimated_delivery_time = delivery_time
#         repair.vehicle_pick_up = vehicle_pick_up
#         repair.customer_signature = existing_signature  # 🆕 sync signature
#         # repair.assign_adviser = employee
#         # Replace list_of_damage
#         repair.set("list_of_damage", [])
#         for row in child_rows:
#             repair.append("list_of_damage", row)

#         # Replace vehicle_concern
#         repair.set("vehicle_concern", [])
#         for row in concern_rows:
#             repair.append("vehicle_concern", row)

#         repair.estimated_total = (
#             q.get("grand_total")
#             or q.get("rounded_total")
#             or q.get("net_total")
#             or q.get("total")
#             or 0
#         )

#         repair.save(ignore_permissions=True)
#         frappe.db.commit()
#         return repair.name
    

#     # -------------------------------------------------------------
#     # CREATE NEW CAR REPAIR
#     # -------------------------------------------------------------
#     new_repair_data = {
#         "doctype": "Car repair",
#         "car_diagnosis": diagnosis.name,
#         "car": diagnosis.get("car"),
#         # "model": vehicle.model if vehicle else "",
#         # "model": get_model_name(vehicle.model) if vehicle else "",
#         "model": frappe.db.get_value("Vehicle Model", vehicle.model, "model") if vehicle else "",

#         "license_plate": vehicle.license_plate if vehicle else "",
#         "customer_name": customer_name,
#         "email": email,
#         "phone": phone,
#         "quotation": q.name,
#         "reference_no": diagnosis.get("reference_no"),
#         "estimated_delivery_date": delivery_date,
#         "estimated_delivery_time": delivery_time,
#         "vehicle_pick_up": vehicle_pick_up,  # 🆕 checkbox
#         "customer_signature": customer_signature,  # 🆕 signature
#         # "assign_adviser": employee,
#         "list_of_damage": [],
#         "vehicle_concern": []  # 🆕 child table
#     }
    
#     repair = frappe.get_doc(new_repair_data)
#     repair.insert(ignore_permissions=True)  
    
#     # Add damages
#     for row in child_rows:
#         repair.append("list_of_damage", row)

#     # Add concerns
#     for row in concern_rows:
#         repair.append("vehicle_concern", row)

#     repair.estimated_total = (
#         q.get("grand_total")
#         or q.get("rounded_total")
#         or q.get("net_total")
#         or q.get("total")
#         or 0
#     )
    
#     repair.insert(ignore_permissions=True)
#     frappe.db.commit()
#     return repair.name






# -----------------------------------previouse code witout assign adviser----------------------------------



# def create_or_update_car_repair(q):
#     """Create or Update Car Repair from Quotation and Car Diagnosis."""

#     car_diagnosis_id = q.get("custom_car_diagnosis")
#     if not car_diagnosis_id:
#         return None

#     try:
#         diagnosis = frappe.get_doc("Car Diagnosis", car_diagnosis_id)
#     except Exception:
#         return None

#     # -------------------------------------------------------------
#     # Find existing Car Repair
#     # -------------------------------------------------------------
#     existing_repair_name = frappe.db.get_value("Car repair", {"quotation": q.name})
#     if not existing_repair_name:
#         existing_repair_name = frappe.db.get_value(
#             "Car repair", {"car_diagnosis": diagnosis.name}
#         )

#     # -------------------------------------------------------------
#     # Vehicle Info
#     # -------------------------------------------------------------
#     vehicle = None
#     if diagnosis.get("car"):
#         try:
#             vehicle = frappe.get_doc("Vehicle", diagnosis.car)
#         except Exception:
#             pass

#     # -------------------------------------------------------------
#     # Customer Info
#     # -------------------------------------------------------------
#     customer_name = (
#         q.get("customer")
#         or q.get("party_name")
#         or q.get("customer_name")
#         or diagnosis.get("customer_name")
#     )
#     email = q.get("contact_email") or diagnosis.get("email_id")
#     phone = q.get("contact_no") or q.get("contact_mobile") or diagnosis.get("phone")

#     # -------------------------------------------------------------
#     # Prepare list_of_damage (Diagnosis + Quotation)
#     # -------------------------------------------------------------
#     child_rows = []
#     seen = set()

#     # -------------------------
#     # 1️⃣ FROM CAR DIAGNOSIS (SOURCE OF TRUTH)
#     # -------------------------
#     diagnosis_rows = diagnosis.get("car_diagnosis_detail") or []

#     for row in diagnosis_rows:
#         row = row.as_dict() if hasattr(row, "as_dict") else dict(row)

#         desc = (row.get("damage_description") or "").strip()
#         if not desc or desc.lower() in seen:
#             continue

#         seen.add(desc.lower())

#         child_rows.append({
#             "damage_description": desc,
#             "assigned_to": row.get("assigned_to") or "",
#             "part_required": row.get("part_required") or "",
#             "quantity": row.get("quantity") or 0,
#             "estimated_cost": row.get("estimated_cost") or 0,
#             "amount": (
#                 (row.get("quantity") or 0) *
#                 (row.get("estimated_cost") or 0)
#             )
#         })

    

#     # -------------------------------------------------------------
#     # Common fields from Diagnosis
#     # -------------------------------------------------------------
#     delivery_date = diagnosis.get("estimated_delivery_date")
#     delivery_time = diagnosis.get("estimated_delivery_time")
#     vehicle_pick_up = diagnosis.get("vehicle_pick_up")
#     customer_signature = diagnosis.get("customer_signature")

#     # Vehicle concerns
#     concern_rows = []
#     for c in diagnosis.get("vehicle_concern") or []:
#         c = c.as_dict() if hasattr(c, "as_dict") else dict(c)
#         concern_rows.append({
#             "vehicle_concern": c.get("vehicle_concern") or ""
#         })
#     employee = None

#     # 1️⃣ Check if Quotation has an assigned adviser
#     if q.get("assign_adviser"):
#         employee = q.get("assign_adviser")

#     # 2️⃣ Otherwise, use current logged-in user if linked to Employee
#     if not employee:
#         employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")


#     # -------------------------------------------------------------
#     # UPDATE EXISTING CAR REPAIR
#     # -------------------------------------------------------------
#     if existing_repair_name:
#         repair = frappe.get_doc("Car repair", existing_repair_name)

#         existing_signature = repair.customer_signature or customer_signature

#         repair.car_diagnosis = diagnosis.name
#         repair.car = diagnosis.get("car")
#         repair.model = (
#             frappe.db.get_value("Vehicle Model", vehicle.model, "model")
#             if vehicle else ""
#         )
#         repair.license_plate = vehicle.license_plate if vehicle else ""
#         repair.customer_name = customer_name
#         repair.email = email
#         repair.phone = phone
#         repair.quotation = q.name
#         repair.reference_no = diagnosis.get("reference_no")
#         repair.estimated_delivery_date = delivery_date
#         repair.estimated_delivery_time = delivery_time
#         repair.vehicle_pick_up = vehicle_pick_up
#         repair.customer_signature = existing_signature
#         repair.assign_adviser = employee


#         # 🔥 REPLACE DAMAGES
#         repair.set("list_of_damage", [])
#         for row in child_rows:
#             repair.append("list_of_damage", row)

#         # Replace concerns
#         repair.set("vehicle_concern", [])
#         for row in concern_rows:
#             repair.append("vehicle_concern", row)

#         repair.estimated_total = (
#             q.get("grand_total")
#             or q.get("rounded_total")
#             or q.get("net_total")
#             or q.get("total")
#             or 0
#         )

#         repair.save(ignore_permissions=True)
#         frappe.db.commit()
#         return repair.name

#     # -------------------------------------------------------------
#     # CREATE NEW CAR REPAIR
#     # -------------------------------------------------------------
#     repair = frappe.get_doc({
#         "doctype": "Car repair",
#         "car_diagnosis": diagnosis.name,
#         "car": diagnosis.get("car"),
#         "model": (
#             frappe.db.get_value("Vehicle Model", vehicle.model, "model")
#             if vehicle else ""
#         ),
#         "license_plate": vehicle.license_plate if vehicle else "",
#         "customer_name": customer_name,
#         "email": email,
#         "phone": phone,
#         "quotation": q.name,
#         "reference_no": diagnosis.get("reference_no"),
#         "estimated_delivery_date": delivery_date,
#         "estimated_delivery_time": delivery_time,
#         "vehicle_pick_up": vehicle_pick_up,
#         "customer_signature": customer_signature,
#         "assign_adviser": employee,
#         "list_of_damage": [],
#         "vehicle_concern": []
#     })

#     repair.insert(ignore_permissions=True)

#     for row in child_rows:
#         repair.append("list_of_damage", row)

#     for row in concern_rows:
#         repair.append("vehicle_concern", row)

#     repair.estimated_total = (
#         q.get("grand_total")
#         or q.get("rounded_total")
#         or q.get("net_total")
#         or q.get("total")
#         or 0
#     )

#     repair.save(ignore_permissions=True)
#     frappe.db.commit()
#     return repair.name



def create_or_update_car_repair(q):
    """Create or Update Car Repair from Quotation and Car Diagnosis."""

    car_diagnosis_id = q.get("custom_car_diagnosis")
    if not car_diagnosis_id:
        return None

    try:
        diagnosis = frappe.get_doc("Car Diagnosis", car_diagnosis_id)
    except Exception:
        return None

    # -------------------------------------------------------------
    # Find existing Car Repair
    # -------------------------------------------------------------
    existing_repair_name = frappe.db.get_value(
        "Car repair", {"quotation": q.name}
    )
    if not existing_repair_name:
        existing_repair_name = frappe.db.get_value(
            "Car repair", {"car_diagnosis": diagnosis.name}
        )

    # -------------------------------------------------------------
    # Vehicle Info
    # -------------------------------------------------------------
    vehicle = None
    if diagnosis.get("car"):
        try:
            vehicle = frappe.get_doc("Vehicle", diagnosis.car)
        except Exception:
            pass

    # -------------------------------------------------------------
    # Customer Info
    # -------------------------------------------------------------
    customer_name = (
        q.get("customer")
        or q.get("party_name")
        or q.get("customer_name")
        or diagnosis.get("customer_name")
    )

    email = q.get("contact_email") or diagnosis.get("email_id")
    phone = (
        q.get("contact_no")
        or q.get("contact_mobile")
        or diagnosis.get("phone")
    )

    # -------------------------------------------------------------
    # Prepare list_of_damage (Diagnosis = Source of Truth)
    # -------------------------------------------------------------
    child_rows = []
    seen = set()

    diagnosis_rows = diagnosis.get("car_diagnosis_detail") or []

    for row in diagnosis_rows:
        row = row.as_dict() if hasattr(row, "as_dict") else dict(row)

        desc = (row.get("damage_description") or "").strip()
        if not desc or desc.lower() in seen:
            continue

        seen.add(desc.lower())

        qty = row.get("quantity") or 0
        rate = row.get("estimated_cost") or 0

        child_rows.append({
            "damage_description": desc,
            "assigned_to": row.get("assigned_to") or "",
            "part_required": row.get("part_required") or "",
            "quantity": qty,
            "estimated_cost": rate,
            "amount": qty * rate
        })

    # -------------------------------------------------------------
    # Vehicle Concern
    # -------------------------------------------------------------
    concern_rows = []
    for c in diagnosis.get("vehicle_concern") or []:
        c = c.as_dict() if hasattr(c, "as_dict") else dict(c)
        concern_rows.append({
            "vehicle_concern": c.get("vehicle_concern") or ""
        })

    # -------------------------------------------------------------
    # Adviser Assignment (FIXED)
    # -------------------------------------------------------------
    employee = None

    # 1️⃣ Diagnosis adviser (TOP PRIORITY)
    if diagnosis.get("assign_adviser"):
        employee = diagnosis.get("assign_adviser")

    # 2️⃣ Quotation adviser
    elif q.get("assign_adviser"):
        employee = q.get("assign_adviser")

    # 3️⃣ Logged-in user
    else:
        employee = frappe.db.get_value(
            "Employee",
            {"user_id": frappe.session.user},
            "name"
        )

    # -------------------------------------------------------------
    # Common fields from Diagnosis
    # -------------------------------------------------------------
    delivery_date = diagnosis.get("estimated_delivery_date")
    delivery_time = diagnosis.get("estimated_delivery_time")
    vehicle_pick_up = diagnosis.get("vehicle_pick_up")
    customer_signature = diagnosis.get("customer_signature")

    estimated_total = (
        q.get("grand_total")
        or q.get("rounded_total")
        or q.get("net_total")
        or q.get("total")
        or 0
    )

    # -------------------------------------------------------------
    # UPDATE EXISTING CAR REPAIR
    # -------------------------------------------------------------
    if existing_repair_name:
        repair = frappe.get_doc("Car repair", existing_repair_name)

        repair.car_diagnosis = diagnosis.name
        repair.car = diagnosis.get("car")
        repair.model = (
            frappe.db.get_value("Vehicle Model", vehicle.model, "model")
            if vehicle else ""
        )
        repair.license_plate = vehicle.license_plate if vehicle else ""
        repair.customer_name = customer_name
        repair.email = email
        repair.phone = phone
        repair.quotation = q.name
        repair.reference_no = diagnosis.get("reference_no")
        repair.estimated_delivery_date = delivery_date
        repair.estimated_delivery_time = delivery_time
        repair.vehicle_pick_up = vehicle_pick_up
        repair.customer_signature = repair.customer_signature or customer_signature
        repair.assign_adviser = employee
        repair.estimated_total = estimated_total

        # Replace damages
        repair.set("list_of_damage", [])
        for row in child_rows:
            repair.append("list_of_damage", row)

        # Replace concerns
        repair.set("vehicle_concern", [])
        for row in concern_rows:
            repair.append("vehicle_concern", row)

        repair.save(ignore_permissions=True)
        frappe.db.commit()
        return repair.name

    # -------------------------------------------------------------
    # CREATE NEW CAR REPAIR
    # -------------------------------------------------------------
    repair = frappe.get_doc({
        "doctype": "Car repair",
        "car_diagnosis": diagnosis.name,
        "car": diagnosis.get("car"),
        "model": (
            frappe.db.get_value("Vehicle Model", vehicle.model, "model")
            if vehicle else ""
        ),
        "license_plate": vehicle.license_plate if vehicle else "",
        "customer_name": customer_name,
        "email": email,
        "phone": phone,
        "quotation": q.name,
        "reference_no": diagnosis.get("reference_no"),
        "estimated_delivery_date": delivery_date,
        "estimated_delivery_time": delivery_time,
        "vehicle_pick_up": vehicle_pick_up,
        "customer_signature": customer_signature,
        "assign_adviser": employee,
        "estimated_total": estimated_total,
        "list_of_damage": [],
        "vehicle_concern": []
    })

    repair.insert(ignore_permissions=True)

    for row in child_rows:
        repair.append("list_of_damage", row)

    for row in concern_rows:
        repair.append("vehicle_concern", row)

    repair.save(ignore_permissions=True)
    frappe.db.commit()
    return repair.name









# -------------------------
# Quotation Update Hook (Auto-sync Car Repair)
# -------------------------
def on_update(doc, method):
    """Triggered when a Quotation is updated — auto sync Car Repair."""
    try:
        if doc.workflow_state == "Approved":
            create_or_update_car_repair(doc)
    except Exception as e:
        frappe.log_error(f"Car Repair auto-sync failed: {str(e)}", "Quotation Update Hook")

        
        
        
        
        
        
        

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
