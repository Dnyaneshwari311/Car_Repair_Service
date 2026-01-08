# import frappe
# from frappe import _
# import json
# from frappe.utils.file_manager import save_file
# from frappe.utils import get_url
# from car_repair_service.api.utils import get_paginated_data
# from car_repair_service.api.role_validation import validate_api_access



# import base64
# import os
# import mimetypes


# from frappe.utils.file_manager import get_file

# def file_url_to_base64(file_url):
#     if not file_url:
#         return None

#     # Get the File document
#     file_doc = frappe.get_doc("File", {"file_url": file_url})
#     content = file_doc.get_content()  # Returns bytes

#     mime_type, _ = mimetypes.guess_type(file_doc.file_name)
#     mime_type = mime_type or "image/png"

#     encoded = base64.b64encode(content).decode()
#     return f"data:{mime_type};base64,{encoded}"


# @frappe.whitelist(allow_guest=False)
# def create_car_repair_request(data):
#     validate_api_access("Car Repair Request")

#     try:
#         data = json.loads(data) if isinstance(data, str) else data
#         files = frappe.request.files

#         # ---------------------------
#         # BASIC DATA
#         # ---------------------------
#         customer_name = data.get("customer_name")
#         email = data.get("email")
#         phone = data.get("phone")
#         car = data.get("car")
#         license_plate = data.get("license_plate")

#         if not customer_name or not email:
#             frappe.throw(_("Missing customer_name or email"))

#         # ---------------------------
#         # DUPLICATE CHECK
#         # ---------------------------
#         existing_crr = frappe.get_all(
#             "Car Repair Request",
#             filters={
#                 "customer_name": customer_name,
#                 "car": car,
#                 "license_plate": license_plate
#             },
#             limit=1
#         )
#         if existing_crr:
#             return {
#                 "status": "exists",
#                 "status_code": 200,
#                 "message": f"Car Repair Request already exists: {existing_crr[0].name}",
#                 "name": existing_crr[0].name
#             }

#         # ---------------------------
#         # CUSTOMER CREATE / FETCH
#         # ---------------------------
#         customer_name_db = frappe.db.exists("Customer", {"email_id": email})
#         if customer_name_db:
#             customer_doc = frappe.get_doc("Customer", customer_name_db)
#         else:
#             customer_doc = frappe.new_doc("Customer")
#             customer_doc.customer_name = customer_name
#             customer_doc.email_id = email
#             customer_doc.mobile_no = phone
#             customer_doc.customer_group = "Individual"
#             customer_doc.territory = "All Territories"
#             customer_doc.insert(ignore_permissions=True)

#         # ---------------------------
#         # VEHICLE MAKE / MODEL
#         # ---------------------------
#         make = data.get("make")
#         model = data.get("model")

#         if make and not frappe.db.exists("Vehicle Make", {"make": make}):
#             frappe.get_doc({"doctype": "Vehicle Make", "make": make}).insert(ignore_permissions=True)

#         if model and not frappe.db.exists("Vehicle Model", {"model": model}):
#             frappe.get_doc({"doctype": "Vehicle Model", "model": model}).insert(ignore_permissions=True)

#         # ---------------------------
#         # CREATE CAR REPAIR REQUEST
#         # ---------------------------
#         doc = frappe.new_doc("Car Repair Request")

#         fields = [
#             "email", "phone", "make", "model", "assign_adviser",
#             "car", "license_plate", "chassis_no",
#             "car_manufacturing_year", "priority",
#             "service_type", "repair_request_date",
#             "driver_name", "driver_mob_no",
#             "odometer_value", "odometer_value_current",
#             "fuel_level", "remark", "fuel_type","assigned_to",
#             "vehicle_pickup_required", "pickup_address",
#             "same_as_pick_up_address", "drop_address"
#         ]

#         for f in fields:
#             if f in data:
#                 doc.set(f, data[f])

#         doc.customer = customer_doc.name
#         doc.customer_name = customer_doc.customer_name

#         doc.insert(ignore_permissions=True, ignore_mandatory=True)
         
#          # ---------------------------
#         # SIGNATURE FILE
#         # ---------------------------
#         # ---------------------------
#         # SIGNATURE IMAGE
#         # ---------------------------
#         signature_upload = files.get("signature")
#         if not signature_upload or not signature_upload.filename:
#             frappe.throw(_("Signature image is required"))

#         signature_file = save_file(
#             fname=signature_upload.filename,
#             content=signature_upload.stream.read(),
#             dt="Car Repair Request",
#             dn=doc.name,
#             is_private=0
#         )
#         doc.signature = signature_file.file_url

                
#         # ---------------------------
#         # CUSTOMER SIGNATURE
#         # ---------------------------
#         # signature_upload = files.get("customer_signature")
#         # if not signature_upload or not signature_upload.filename:
#         #     frappe.throw(_("Customer Signature is required"))

#         # signature_file = save_file(
#         #     fname=signature_upload.filename,
#         #     content=signature_upload.stream.read(),
#         #     dt="Car Repair Request",
#         #     dn=doc.name,
#         #     is_private=0
#         # )
#         # doc.customer_signature = signature_file.file_url

#         # ---------------------------
#         # ODOMETER PHOTO
#         # ---------------------------
#         odometer_upload = files.get("odometer_photo")
#         if not odometer_upload or not odometer_upload.filename:
#             frappe.throw(_("Odometer Photo is required"))

#         odometer_file = save_file(
#             fname=odometer_upload.filename,
#             content=odometer_upload.stream.read(),
#             dt="Car Repair Request",
#             dn=doc.name,
#             is_private=0
#         )
#         doc.odometer_photo = odometer_file.file_url

#         # ---------------------------
#         # VEHICLE CONCERNS
#         # ---------------------------
#         for vc in data.get("vehicle_concern", []):
#             doc.append("vehicle_concern", {
#                 "vehicle_concern": vc.get("vehicle_concern")
#             })

#         # ---------------------------
#         # CAR REPAIR IMAGES
#         # ---------------------------
#         IMAGE_FIELD_MAP = {
#             "front_view": "Front View",
#             "back_view": "Back View",
#             "left_view": "Left View",
#             "right_view": "Right View",
#         }

#         for field, image_type in IMAGE_FIELD_MAP.items():
#             for upload in files.getlist(field):
#                 if upload and upload.filename:
#                     file_doc = save_file(
#                         fname=upload.filename,
                        
#                         content=upload.stream.read(),
#                         dt="Car Repair Request",
#                         dn=doc.name,
#                         is_private=0
#                     )
#                     doc.append("car_repair_images", {
#                         "image": file_doc.file_url,
#                         "image_type": image_type
#                     })

#         if not doc.car_repair_images:
#             frappe.throw(_("At least one Car Repair Image is required"))

#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
#         frappe.clear_messages()
#         signature_base64 = file_url_to_base64(doc.customer_signature)

#         return {
#             "status": "success",
#             "status_code": 201,
#             "message": "Car Repair Request created successfully",
#             "name": doc.name,

#             # THIS IS NOW BASE64 (NOT FILE PATH)
#             # "customer_signature": signature_base64
#         }


#     except Exception as e:
#         frappe.log_error("Create Car Repair Request Error", frappe.get_traceback())
#         return {"status": "error", "message": str(e)}








import frappe
from frappe import _
import json
import base64
import mimetypes

from frappe.utils.file_manager import save_file
from car_repair_service.api.role_validation import validate_api_access


# --------------------------------------------------
# FILE → BASE64
# --------------------------------------------------
def file_url_to_base64(file_url):
    if not file_url:
        return None

    file_doc = frappe.get_doc("File", {"file_url": file_url})
    content = file_doc.get_content()

    mime_type, _ = mimetypes.guess_type(file_doc.file_name)
    mime_type = mime_type or "image/png"

    encoded = base64.b64encode(content).decode()
    return f"data:{mime_type};base64,{encoded}"


# --------------------------------------------------
# CREATE CAR REPAIR REQUEST
# --------------------------------------------------
@frappe.whitelist(allow_guest=False)
def create_car_repair_request(data):
    validate_api_access("Car Repair Request")

    try:
        data = json.loads(data) if isinstance(data, str) else data
        files = frappe.request.files

        # ---------------------------
        # BASIC DATA
        # ---------------------------
        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")
        car = data.get("car")
        license_plate = data.get("license_plate")

        if not customer_name or not email:
            frappe.throw(_("Missing customer name or email"))

        # ---------------------------
        # PICKUP LOGIC
        # ---------------------------
        vehicle_pickup_required = data.get("vehicle_pickup_required")
        is_pickup = vehicle_pickup_required == "Yes, Pickup my vehicle"

        # ---------------------------
        # DUPLICATE CHECK
        # ---------------------------
        existing = frappe.get_all(
            "Car Repair Request",
            filters={
                "customer_name": customer_name,
                "car": car,
                "license_plate": license_plate
            },
            limit=1
        )

        if existing:
            return {
                "status": "exists",
                "status_code": 200,
                "message": f"Car Repair Request already exists: {existing[0].name}",
                "name": existing[0].name
            }

        # ---------------------------
        # CUSTOMER
        # ---------------------------
        customer_name_db = frappe.db.exists("Customer", {"email_id": email})

        if customer_name_db:
            customer_doc = frappe.get_doc("Customer", customer_name_db)
        else:
            customer_doc = frappe.new_doc("Customer")
            customer_doc.customer_name = customer_name
            customer_doc.email_id = email
            customer_doc.mobile_no = phone
            customer_doc.customer_group = "Individual"
            customer_doc.territory = "All Territories"
            customer_doc.insert(ignore_permissions=True)

        # ---------------------------
        # VEHICLE MAKE / MODEL
        # ---------------------------
        make = data.get("make")
        model = data.get("model")

        if make and not frappe.db.exists("Vehicle Make", {"make": make}):
            frappe.get_doc({"doctype": "Vehicle Make", "make": make}).insert(ignore_permissions=True)

        if model and not frappe.db.exists("Vehicle Model", {"model": model}):
            frappe.get_doc({"doctype": "Vehicle Model", "model": model}).insert(ignore_permissions=True)

        # ---------------------------
        # CREATE DOCUMENT
        # ---------------------------
        doc = frappe.new_doc("Car Repair Request")

        fields = [
            "email", "phone", "make", "model", "assign_adviser",
            "car", "license_plate", "chassis_no",
            "car_manufacturing_year", "priority",
            "service_type", "repair_request_date",
            "driver_name", "driver_mob_no",
            "odometer_value", "odometer_value_current",
            "fuel_level", "remark", "fuel_type",
            "assigned_to", "vehicle_pickup_required",
            "pickup_address", "same_as_pick_up_address",
            "drop_address"
        ]

        for f in fields:
            if f in data:
                doc.set(f, data[f])

        doc.customer = customer_doc.name
        doc.customer_name = customer_doc.customer_name

        doc.insert(ignore_permissions=True, ignore_mandatory=True)

        # ---------------------------
        # SIGNATURE (ONLY IF PICKUP)
        # ---------------------------
        signature_upload = files.get("signature")

        if is_pickup:
            if not signature_upload or not signature_upload.filename:
                frappe.throw(_("Signature is required when vehicle pickup is selected"))

            signature_file = save_file(
                fname=signature_upload.filename,
                content=signature_upload.stream.read(),
                dt="Car Repair Request",
                dn=doc.name,
                is_private=0
            )
            doc.signature = signature_file.file_url
        else:
            doc.signature = None

        # ---------------------------
        # ODOMETER PHOTO (ALWAYS REQUIRED)
        # ---------------------------
        odometer_upload = files.get("odometer_photo")

        if not odometer_upload or not odometer_upload.filename:
            frappe.throw(_("Odometer photo is required"))

        odometer_file = save_file(
            fname=odometer_upload.filename,
            content=odometer_upload.stream.read(),
            dt="Car Repair Request",
            dn=doc.name,
            is_private=0
        )
        doc.odometer_photo = odometer_file.file_url

        # ---------------------------
        # VEHICLE CONCERNS
        # ---------------------------
        for vc in data.get("vehicle_concern", []):
            doc.append("vehicle_concern", {
                "vehicle_concern": vc.get("vehicle_concern")
            })

        # ---------------------------
        # CAR REPAIR IMAGES (ONLY IF PICKUP)
        # ---------------------------
        IMAGE_FIELD_MAP = {
            "front_view": "Front View",
            "back_view": "Back View",
            "left_view": "Left View",
            "right_view": "Right View"
        }

        for field, image_type in IMAGE_FIELD_MAP.items():
            for upload in files.getlist(field):
                if upload and upload.filename:
                    file_doc = save_file(
                        fname=upload.filename,
                        content=upload.stream.read(),
                        dt="Car Repair Request",
                        dn=doc.name,
                        is_private=0
                    )
                    doc.append("car_repair_images", {
                        "image": file_doc.file_url,
                        "image_type": image_type
                    })

        if is_pickup and not doc.car_repair_images:
            frappe.throw(_("At least one Car Repair Image is required when vehicle pickup is selected"))

        # ---------------------------
        # SAVE
        # ---------------------------
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 201,
            "message": "Car Repair Request created successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error("Create Car Repair Request Error", frappe.get_traceback())
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }








# =======================================================
# Create Car Diagnosis From Car Repair Request
# =======================================================


@frappe.whitelist(allow_guest=False)
def create_car_diagnosis(customer_name=None, customer=None):
    validate_api_access("Car Diagnosis")
    
    """
    Create a Car Diagnosis record:
    - Prefill from last Car Repair Request for this customer
    - Auto-fill Reference No from Car Repair Request
    - Skip creation if Car Diagnosis already exists for this request
    """
    try:
        if not customer_name and not customer:
            frappe.throw(_("Please provide either customer_name or customer"))

        # If customer link is provided, fetch customer_name
        if customer and not customer_name:
            customer_name = frappe.db.get_value("Customer", customer, "customer_name")

        # Fetch latest Car Repair Request
        last_request = frappe.get_all(
            "Car Repair Request",
            filters={"customer_name": customer_name},
            fields=[
                "name", "car", "car_model", "license_plate", "chassis_no",
                "email", "phone", "repair_request_date", "priority",
                "vehicle_pick_up", "customer_signature","assign_adviser"
            ],
            order_by="creation desc",
            limit_page_length=1
        )

        if not last_request:
            return {"status": "not_found", "message": "No Car Repair Request found for this customer"}

        req_name = last_request[0]["name"]

        # Check if Car Diagnosis already exists for this Car Repair Request
        existing_diagnosis = frappe.db.exists("Car Diagnosis", {"reference_no": req_name})
        if existing_diagnosis:
            return {
                "status": "skipped",
                "message": f"Car Diagnosis already exists for Car Repair Request {req_name}",
                "name": existing_diagnosis
            }

        # Fetch full Car Repair Request including child tables
        req_doc = frappe.get_doc("Car Repair Request", req_name)

        # Create new Car Diagnosis
        diagnosis = frappe.new_doc("Car Diagnosis")
        diagnosis.customer_name = req_doc.customer_name

        # Only assign customer link if it exists
        if hasattr(req_doc, "customer"):
            diagnosis.customer = req_doc.customer

        diagnosis.car = req_doc.car
        diagnosis.model = req_doc.car_model
        diagnosis.license_plate = req_doc.license_plate
        diagnosis.chassis_no = req_doc.chassis_no
        diagnosis.email_id = req_doc.email
        diagnosis.phone = req_doc.phone
        diagnosis.date_of_receipt = req_doc.repair_request_date
        diagnosis.priority = req_doc.priority
        diagnosis.vehicle_pick_up = req_doc.vehicle_pick_up
        diagnosis.customer_signature = req_doc.customer_signature
        diagnosis.assign_adviser =req_doc.assign_adviser
        
        
        if req_doc.signature:
            diagnosis.signature = req_doc.signature


        # ✅ Auto-fill Reference No from Car Repair Request
        diagnosis.reference_no = req_doc.name

        # Child table: Vehicle Concern
        if hasattr(req_doc, "vehicle_concern"):
            for vc in req_doc.vehicle_concern:
                diagnosis.append("vehicle_concern", {"vehicle_concern": vc.vehicle_concern})

        # Child table: Car Repair Images
        if hasattr(req_doc, "car_repair_images"):
            for img in req_doc.car_repair_images:
                if img.image: 
                    diagnosis.append("car_repair_images", {"image": img.image})

        # Insert document
        diagnosis.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 201,
            "message": f"Car Diagnosis created from Car Repair Request {req_name}",
            "name": diagnosis.name
        }

    except Exception as e:
        frappe.log_error("Error creating Car Diagnosis", str(e))
        return {"status": "error", "message": str(e)}







# ======================================================
# Create Quotation From Car Diagnosis
# ======================================================




# @frappe.whitelist(allow_guest=False)
# def create_quotation_from_car_diagnosis(diagnosis_name):
#     """
#     API: Create a Quotation from a Car Diagnosis record.
#     - Reuses Item if item_code OR item_name exists
#     - Creates Item only when truly missing
#     - Prevents duplicate Item Name error
#     """

#     try:
#         # ==============================
#         # Fetch Diagnosis
#         # ==============================
#         diag = frappe.get_doc("Car Diagnosis", diagnosis_name)

#         if not diag.customer_name:
#             frappe.throw(_("Customer not found in Car Diagnosis"))

#         # ==============================
#         # Create Quotation
#         # ==============================
#         qtn = frappe.new_doc("Quotation")
#         qtn.quotation_to = "Customer"
#         qtn.party_name = diag.customer_name
#         qtn.remarks = f"Quotation based on Car Diagnosis: {diag.name}"
#         qtn.custom_car_diagnosis = diag.name

#         if getattr(diag, "email_id", None):
#             qtn.contact_email = diag.email_id

#         added_items = False

#         # ==============================
#         # Add Items from Diagnosis
#         # ==============================
#         for d in getattr(diag, "car_diagnosis_detail", []):
#             if not d.part_required:
#                 continue

#             part_name = d.part_required.strip()

#             # ----------------------------------
#             # Resolve Item SAFELY
#             # ----------------------------------
#             existing_item = None

#             # 1️⃣ Check Item Code
#             if frappe.db.exists("Item", part_name):
#                 existing_item = part_name

#             # 2️⃣ Check Item Name
#             else:
#                 existing_item = frappe.db.get_value(
#                     "Item",
#                     {"item_name": part_name},
#                     "name"
#                 )

#             # 3️⃣ Create only if not found
#             if not existing_item:
#                 item_doc = frappe.get_doc({
#                     "doctype": "Item",
#                     "item_code": part_name,
#                     "item_name": part_name,
#                     "stock_uom": "Nos",
#                     "item_group": "Products",  # change if needed
#                     "is_stock_item": 0
#                 })
#                 item_doc.insert(ignore_permissions=True)
#                 existing_item = item_doc.name

#             # ----------------------------------
#             # Safe qty & rate
#             # ----------------------------------
#             try:
#                 qty = float(d.quantity) if d.quantity else 1.0
#                 if qty <= 0:
#                     qty = 1.0
#             except:
#                 qty = 1.0

#             try:
#                 rate = float(d.estimated_cost) if d.estimated_cost else 0.0
#             except:
#                 rate = 0.0

#             uom = frappe.db.get_value("Item", existing_item, "stock_uom") or "Nos"

#             # ----------------------------------
#             # Append Quotation Item
#             # ----------------------------------
#             item = qtn.append("items", {})
#             item.item_code = existing_item
#             item.item_name = part_name
#             item.qty = qty
#             item.rate = rate
#             item.uom = uom
#             item.amount = qty * rate

#             added_items = True

#         # ==============================
#         # Fallback Item (No Parts)
#         # ==============================
#         if not added_items:
#             description = (
#                 getattr(diag, "issues", None)
#                 or getattr(diag, "problem_description", None)
#             )
#             if description:
#                 item = qtn.append("items", {})
#                 item.item_name = description
#                 item.qty = 1.0
#                 item.rate = 0.0
#                 item.uom = "Nos"
#                 item.amount = 0.0

#         # ==============================
#         # Vehicle Info
#         # ==============================
#         vehicle_field = "vehicle" if "vehicle" in qtn.as_dict() else "custom_vehicle"
#         if getattr(diag, "car", None):
#             setattr(qtn, vehicle_field, diag.car)

#         # ==============================
#         # Final Safety Validation
#         # ==============================
#         for item in qtn.items:
#             item.qty = float(item.qty or 1.0)
#             item.rate = float(item.rate or 0.0)
#             item.amount = item.qty * item.rate

#         # ==============================
#         # Insert Quotation
#         # ==============================
#         qtn.flags.ignore_permissions = True
#         qtn.set_missing_values()
#         qtn.calculate_taxes_and_totals()
#         qtn.insert(ignore_permissions=True)

#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code": 201,
#             "message": f"Quotation created successfully from Car Diagnosis {diag.name}",
#             "quotation_name": qtn.name
#         }

#     except Exception as e:
#         frappe.log_error(
#             f"Error creating Quotation from Car Diagnosis {diagnosis_name}",
#             frappe.get_traceback()
#         )
#         return {
#             "status": "error",
#             "message": str(e)
#         }




@frappe.whitelist(allow_guest=False)
def create_quotation_from_car_diagnosis(diagnosis_name):
    """
    API: Create a Quotation from a Car Diagnosis record.
    - Reuses Item if item_code OR item_name exists
    - Creates Item only when truly missing
    - Copies vehicle, model & license plate for Car Repair flow
    """

    try:
        # ==============================
        # Fetch Diagnosis
        # ==============================
        diag = frappe.get_doc("Car Diagnosis", diagnosis_name)

        if not diag.customer_name:
            frappe.throw(_("Customer not found in Car Diagnosis"))

        # ==============================
        # Fetch Vehicle (SOURCE OF TRUTH)
        # ==============================
        vehicle = None
        if diag.get("car") and frappe.db.exists("Vehicle", diag.car):
            vehicle = frappe.get_doc("Vehicle", diag.car)

        # ==============================
        # Create Quotation
        # ==============================
        qtn = frappe.new_doc("Quotation")
        qtn.quotation_to = "Customer"
        qtn.party_name = diag.customer_name
        qtn.remarks = f"Quotation based on Car Diagnosis: {diag.name}"
        qtn.custom_car_diagnosis = diag.name

        if diag.get("email_id"):
            qtn.contact_email = diag.email_id

        # ==============================
        # Vehicle Info (🔥 REQUIRED FIX)
        # ==============================
        vehicle_field = "vehicle" if "vehicle" in qtn.as_dict() else "custom_vehicle"

        if diag.get("car"):
            setattr(qtn, vehicle_field, diag.car)

        # ✅ EXACT FIELD NAMES
        qtn.liscense_plate = vehicle.license_plate if vehicle else ""
        qtn.model = vehicle.model if vehicle else ""

        added_items = False

        # ==============================
        # Add Items from Diagnosis
        # ==============================
        for d in diag.get("car_diagnosis_detail") or []:
            if not d.part_required:
                continue

            part_name = d.part_required.strip()

            # ----------------------------------
            # Resolve Item safely
            # ----------------------------------
            existing_item = None

            if frappe.db.exists("Item", part_name):
                existing_item = part_name
            else:
                existing_item = frappe.db.get_value(
                    "Item", {"item_name": part_name}, "name"
                )

            if not existing_item:
                item_doc = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": part_name,
                    "item_name": part_name,
                    "stock_uom": "Nos",
                    "item_group": "Products",
                    "is_stock_item": 0
                })
                item_doc.insert(ignore_permissions=True)
                existing_item = item_doc.name

            qty = float(d.quantity) if d.quantity and float(d.quantity) > 0 else 1.0
            rate = float(d.estimated_cost) if d.estimated_cost else 0.0
            uom = frappe.db.get_value("Item", existing_item, "stock_uom") or "Nos"

            item = qtn.append("items", {})
            item.item_code = existing_item
            item.item_name = part_name
            item.qty = qty
            item.rate = rate
            item.uom = uom
            item.amount = qty * rate

            added_items = True

        # ==============================
        # Fallback Item
        # ==============================
        if not added_items:
            description = diag.get("issues") or diag.get("problem_description")
            if description:
                item = qtn.append("items", {})
                item.item_name = description
                item.qty = 1.0
                item.rate = 0.0
                item.uom = "Nos"
                item.amount = 0.0

        # ==============================
        # Final Validation
        # ==============================
        for item in qtn.items:
            item.qty = float(item.qty or 1.0)
            item.rate = float(item.rate or 0.0)
            item.amount = item.qty * item.rate

        # ==============================
        # Insert Quotation
        # ==============================
        qtn.flags.ignore_permissions = True
        qtn.set_missing_values()
        qtn.calculate_taxes_and_totals()
        qtn.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 201,
            "message": f"Quotation created successfully from Car Diagnosis {diag.name}",
            "quotation_name": qtn.name
        }

    except Exception as e:
        frappe.log_error(
            f"Error creating Quotation from Car Diagnosis {diagnosis_name}",
            frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": str(e)
        }









# @frappe.whitelist(allow_guest=False)
# def get_car_repair_request(
#     name=None, 
#     page=1, 
#     page_size=10, 
#     sort_by="creation", 
#     sort_order="desc", 
#     search=None, 
#     is_pagination=False
# ):
#     import frappe
#     try:
#         extra_params = {"search": search} if search else {}
#         base_url = frappe.request.host_url.rstrip("/") + frappe.request.path

#         IMAGE_TYPE_KEY_MAP = {
#             "Front View": "front_view",
#             "Back View": "back_view",
#             "Left View": "left_view",
#             "Right View": "right_view"
#         }

#         def empty_image_structure():
#             return {
#                 "front_view": [],
#                 "back_view": [],
#                 "left_view": [],
#                 "right_view": []
#             }

#         # -------------------------
#         # SINGLE RECORD
#         # -------------------------
#         if name:
#             if not frappe.db.exists("Car Repair Request", name):
#                 return {"status": "error", "message": f"Car Repair Request '{name}' not found"}

#             doc = frappe.get_doc("Car Repair Request", name)
#             data = doc.as_dict()

#             # Vehicle concerns
#             data["vehicle_concern"] = [
#                 {"vehicle_concern": vc.vehicle_concern} for vc in doc.get("vehicle_concern", [])
#             ]

#             # Images
#             grouped_images = empty_image_structure()
#             for img in doc.get("car_repair_images", []):
#                 key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
#                 if key:
#                     grouped_images[key].append(frappe.utils.get_url(img.image))
#             data["car_repair_images"] = grouped_images

#             # Odometer photo
#             if data.get("odometer_photo"):
#                 data["odometer_photo"] = frappe.utils.get_url(data["odometer_photo"])

#             return {"status": "success", "data": data}

#         # -------------------------
#         # PAGINATED LIST
#         # -------------------------
#         fields = [
#             "name", "customer_name", "email", "phone",
#             "make", "model", "license_plate", "assign_adviser",
#             "car_manufacturing_year", "odometer_photo",
#             "priority", "service_type", "repair_request_date",
#             "reason_for_repair", "odometer_value",
#             "odometer_value_current", "customer_signature","driver_name","driver_mob_no","fuel_type"
#         ]

#         search_fields = ["name", "customer_name", "make", "model", "license_plate", "service_type", "priority"]

#         # -------------------------
#         # FIXED: Do NOT pass filters with ["like", ...] manually
#         # Let get_paginated_data handle search internally
#         filters = {}

#         raw = get_paginated_data(
#             doctype="Car Repair Request",
#             fields=fields,
#             search=search,
#             search_fields=search_fields,
#             filters=filters,
#             sort_by=sort_by,
#             sort_order=sort_order,
#             page=int(page),
#             page_size=int(page_size),
#             is_pagination=frappe.utils.sbool(is_pagination),
#             base_url=base_url,
#             extra_params=extra_params
#         )

#         # normalize
#         data_list = raw.get("data", []) if isinstance(raw, dict) else raw
#         raw = {"data": data_list}

#         # -------------------------
#         # ADD GROUPED CHILD IMAGES
#         # -------------------------
#         for row in data_list:
#             row["car_repair_images"] = empty_image_structure()
#             images = frappe.db.get_all(
#                 "Car Repair Images",
#                 filters={"parent": row["name"], "parenttype": "Car Repair Request"},
#                 fields=["image", "image_type"]
#             )
#             for img in images:
#                 key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
#                 if key:
#                     row["car_repair_images"][key].append(frappe.utils.get_url(img.image))

#             if row.get("odometer_photo"):
#                 row["odometer_photo"] = frappe.utils.get_url(row["odometer_photo"])

#         return raw

#     except Exception as e:
#         frappe.log_error(title="Get Car Repair Request Error", message=frappe.get_traceback())
#         return {"status": "error", "message": f"Internal Server Error: {str(e)}"}






# @frappe.whitelist(allow_guest=False)
# def get_car_repair_request(
#     page=1,
#     page_size=10,
#     sort_by="creation",
#     sort_order="desc",
#     search=None,
#     is_pagination=True
# ):
#     import frappe
#     import math

#     try:
#         IMAGE_TYPE_KEY_MAP = {
#             "Front View": "front_view",
#             "Back View": "back_view",
#             "Left View": "left_view",
#             "Right View": "right_view"
#         }

#         def empty_image_structure():
#             return {
#                 "front_view": [],
#                 "back_view": [],
#                 "left_view": [],
#                 "right_view": []
#             }

#         # -------------------------
#         # Fields to fetch
#         # -------------------------
#         fields = [
#             "name", "customer_name", "email", "phone",
#             "make", "model", "license_plate", "assign_adviser",
#             "car_manufacturing_year", "odometer_photo",
#             "priority", "service_type", "repair_request_date",
#             "reason_for_repair", "odometer_value",
#             "odometer_value_current", "customer_signature",
#             "driver_name","driver_mob_no","fuel_type"
#         ]

#         search_fields = ["name", "customer_name", "make", "model", "license_plate", "service_type", "priority"]

#         # -------------------------
#         # Fetch all records
#         # -------------------------
#         all_data = frappe.get_all(
#             "Car Repair Request",
#             fields=fields,
#             order_by=f"{sort_by} {sort_order}",
#             as_list=False
#         )

#         # -------------------------
#         # Apply search if provided
#         # -------------------------
#         if search:
#             search_lower = search.lower()
#             all_data = [
#                 row for row in all_data
#                 if any(search_lower in str(row.get(f, "")).lower() for f in search_fields)
#             ]

#         total_records = len(all_data)
#         page = int(page)
#         page_size = int(page_size) if int(page_size) > 0 else total_records
#         total_pages = math.ceil(total_records / page_size) if page_size else 1

#         # -------------------------
#         # Apply pagination only if requested
#         # -------------------------
#         if frappe.utils.sbool(is_pagination):
#             start = (page - 1) * page_size
#             end = start + page_size
#             data_to_return = all_data[start:end]
#         else:
#             data_to_return = all_data  # return all

#         # -------------------------
#         # Add grouped child images
#         # -------------------------
#         for row in data_to_return:
#             row["car_repair_images"] = empty_image_structure()
#             images = frappe.db.get_all(
#                 "Car Repair Images",
#                 filters={"parent": row["name"], "parenttype": "Car Repair Request"},
#                 fields=["image", "image_type"]
#             )
#             for img in images:
#                 key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
#                 if key:
#                     row["car_repair_images"][key].append(frappe.utils.get_url(img.image))

#             if row.get("odometer_photo"):
#                 row["odometer_photo"] = frappe.utils.get_url(row["odometer_photo"])

#         return {
#             "status": "success",
#             "data": data_to_return,
#             "total_records": total_records,
#             "total_pages": total_pages,
#             "page": page,
#             "page_size": page_size,
#             "is_pagination": frappe.utils.sbool(is_pagination)
#         }

#     except Exception as e:
#         frappe.log_error(title="Get Car Repair Request Error", message=frappe.get_traceback())
#         return {"status": "error", "message": f"Internal Server Error: {str(e)}"}



@frappe.whitelist(allow_guest=False)
def get_car_repair_request(
    page=None,
    page_size=None,
    sort_by="creation",
    sort_order="desc",
    search=None
):
    import frappe
    import math
    validate_api_access("Car Repair Request")

    try:
        IMAGE_TYPE_KEY_MAP = {
            "Front View": "front_view",
            "Back View": "back_view",
            "Left View": "left_view",
            "Right View": "right_view"
        }

        def empty_image_structure():
            return {
                "front_view": [],
                "back_view": [],
                "left_view": [],
                "right_view": []
            }

        # -------------------------
        # Fields
        # -------------------------
        fields = [
            "name", "customer_name", "email", "phone",
            "make", "model", "license_plate", "assign_adviser",
            "car_manufacturing_year", "odometer_photo",
            "priority", "service_type", "repair_request_date",
            "reason_for_repair", "odometer_value",
            "odometer_value_current", "customer_signature",
            "driver_name", "driver_mob_no", "fuel_type"
        ]

        search_fields = [
            "name", "customer_name", "make",
            "model", "license_plate", "service_type", "priority"
        ]

        # -------------------------
        # Fetch all records
        # -------------------------
        all_data = frappe.get_all(
            "Car Repair Request",
            fields=fields,
            order_by=f"{sort_by} {sort_order}",
            as_list=False
        )

        # -------------------------
        # Search
        # -------------------------
        if search:
            search = search.lower()
            all_data = [
                row for row in all_data
                if any(search in str(row.get(f, "")).lower() for f in search_fields)
            ]

        total_records = len(all_data)

        # -------------------------
        # Auto pagination detection
        # -------------------------
        is_pagination = page is not None or page_size is not None

        if is_pagination:
            page = int(page or 1)
            page_size = int(page_size or 10)

            start = (page - 1) * page_size
            end = start + page_size
            data_to_return = all_data[start:end]

            total_pages = math.ceil(total_records / page_size)
        else:
            # FULL LIST
            data_to_return = all_data
            page = None
            page_size = None
            total_pages = 1

        # -------------------------
        # Add child images
        # -------------------------
        for row in data_to_return:
            row["car_repair_images"] = empty_image_structure()

            images = frappe.db.get_all(
                "Car Repair Images",
                filters={
                    "parent": row["name"],
                    "parenttype": "Car Repair Request"
                },
                fields=["image", "image_type"]
            )

            for img in images:
                key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
                if key:
                    row["car_repair_images"][key].append(
                        frappe.utils.get_url(img.image)
                    )

            if row.get("odometer_photo"):
                row["odometer_photo"] = frappe.utils.get_url(row["odometer_photo"])

        return {
            "status": "success",
            "data": data_to_return,
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "is_pagination": is_pagination
        }

    except Exception:
        frappe.log_error(
            title="Get Car Repair Request Error",
            message=frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": "Internal Server Error"
        }





@frappe.whitelist(allow_guest=False)
def get_car_repair_request_by_id(name):
    try:
        if not name:
            return {
                "status": "error",
                "message": "Car Repair Request ID is required"
            }

        if not frappe.db.exists("Car Repair Request", name):
            return {
                "status": "error",
                "message": f"Car Repair Request '{name}' not found"
            }

        IMAGE_TYPE_KEY_MAP = {
            "Front View": "front_view",
            "Back View": "back_view",
            "Left View": "left_view",
            "Right View": "right_view"
        }

        def empty_image_structure():
            return {
                "front_view": [],
                "back_view": [],
                "left_view": [],
                "right_view": []
            }

        doc = frappe.get_doc("Car Repair Request", name)
        data = doc.as_dict()

        # vehicle concerns
        data["vehicle_concern"] = [
            {"vehicle_concern": vc.vehicle_concern}
            for vc in doc.get("vehicle_concern", [])
        ]

        # grouped images
        grouped_images = empty_image_structure()
        for img in doc.get("car_repair_images", []):
            key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
            if key:
                grouped_images[key].append(
                    frappe.utils.get_url(img.image)
                )

        data["car_repair_images"] = grouped_images

        if data.get("odometer_photo"):
            data["odometer_photo"] = frappe.utils.get_url(
                data["odometer_photo"]
            )

        return {
            "status": "success",
            "status_code":200,
            "data": data
        }

    except Exception:
        frappe.log_error(
            title="Get Car Repair Request By ID Error",
            message=frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": "Internal Server Error"
        }





# ====================================================
# UPDATE Car Repair Request
# ====================================================
import frappe
import json
import base64
import uuid
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=False)
def update_car_repair_request():
    """
    Update Car Repair Request:
    - Append new images to existing child table (front/back/left/right)
    - Updates normal fields and odometer photo
    - Returns child table images as '/files/<filename>' for all images
    - Avoids duplicates
    """
    validate_api_access("Car Repair Request")

    try:
        # -------------------------
        # Get request data
        # -------------------------
        if frappe.form_dict.get("data"):
            data = frappe.form_dict.get("data")
            data = json.loads(data) if isinstance(data, str) else data
        else:
            data = dict(frappe.form_dict)

        # -------------------------
        # Validate 'name'
        # -------------------------
        name = data.get("name")
        if not name:
            return {"status": "error", "message": "Missing 'name'"}

        if not frappe.db.exists("Car Repair Request", name):
            return {"status": "error", "message": f"Car Repair Request '{name}' not found"}

        doc = frappe.get_doc("Car Repair Request", name)

        # -------------------------
        # Update normal fields
        # -------------------------
        updatable_fields = ["email", "phone", "make", "model", "license_plate", "priority", "remark"]
        for field in updatable_fields:
            if field in data and data[field]:
                doc.set(field, data[field])

        # -------------------------
        # Update odometer photo
        # -------------------------
        odometer_photo = data.get("odometer_photo")
        image_bytes = None
        if odometer_photo:
            try:
                image_bytes = base64.b64decode(odometer_photo)
            except Exception:
                file_obj = frappe.request.files.get("odometer_photo")
                if file_obj:
                    image_bytes = file_obj.read()

        if image_bytes:
            # filename = f"odometer_{uuid.uuid4()}.png"
            filename = "odometer.png"

            file_doc = save_file(
                filename,
                image_bytes,
                dt="Car Repair Request",
                dn=doc.name,
                is_private=0
            )
            doc.odometer_photo = f"/files/{file_doc.file_name}"  # store path

        # -------------------------
        # Image view map
        # -------------------------
        IMAGE_KEY_TYPE_MAP = {
            "front_view": "Front View",
            "back_view": "Back View",
            "left_view": "Left View",
            "right_view": "Right View"
        }

        if not hasattr(doc, "car_repair_images") or doc.car_repair_images is None:
            doc.car_repair_images = []

        # -------------------------
        # Track existing files to avoid duplicates
        # -------------------------
        existing_files = set()
        for row in doc.car_repair_images:
            if row.image:
                existing_files.add(row.image)  # now stores paths

        # -------------------------
        # Append new images from JSON payload
        # -------------------------
        images_payload = data.get("car_repair_images")
        if images_payload and isinstance(images_payload, dict):
            for view_key, images in images_payload.items():
                image_type = IMAGE_KEY_TYPE_MAP.get(view_key)
                if not image_type or not isinstance(images, list):
                    continue
                for img in images:
                    if not img:
                        continue
                    try:
                        image_bytes = base64.b64decode(img)
                    except Exception:
                        continue
                    # file_doc = save_file(
                    #     f"{uuid.uuid4()}.png",
                    #     image_bytes,
                    #     dt="Car Repair Request",
                    #     dn=doc.name,
                    #     is_private=0
                    # )
                    file_doc = save_file(
                        "image.png",   # or any readable name
                        image_bytes,
                        dt="Car Repair Request",
                        dn=doc.name,
                        is_private=0
                    )

                    
                    file_url = f"/files/{file_doc.file_name}"
                    if file_url not in existing_files:
                        doc.append("car_repair_images", {
                            "image": file_url,      # store path
                            "image_type": image_type
                        })
                        existing_files.add(file_url)

        # -------------------------
        # Append new images from form-data files
        # -------------------------
        for view_key, image_type in IMAGE_KEY_TYPE_MAP.items():
            files = frappe.request.files.getlist(view_key)
            for f in files:
                # file_doc = save_file(
                #     f"{uuid.uuid4()}_{f.filename}",
                #     f.read(),
                #     dt="Car Repair Request",
                #     dn=doc.name,
                #     is_private=0
                # )
                file_doc = save_file(
                    f.filename,   # 👈 ORIGINAL filename only
                    f.read(),
                    dt="Car Repair Request",
                    dn=doc.name,
                    is_private=0
                )

                file_url = f"/files/{file_doc.file_name}"
                if file_url not in existing_files:
                    doc.append("car_repair_images", {
                        "image": file_url,          # store path
                        "image_type": image_type
                    })
                    existing_files.add(file_url)

        # -------------------------
        # Save document
        # -------------------------
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # -------------------------
        # Prepare response with '/files/<filename>' for all images
        # -------------------------
        result_images = {k: [] for k in IMAGE_KEY_TYPE_MAP.keys()}

        for row in doc.car_repair_images:
            key = row.image_type.lower().replace(" ", "_")
            if row.image:
                result_images[key].append(row.image)  # already path

        return {
            "status": "success",
            "status_code": 200,
            "message": f"Car Repair Request '{name}' updated successfully",
            "car_repair_images": result_images
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Car Repair Request Error")
        return {"status": "error", "message": str(e)}


# ====================================================
# DELETE Car Repair Request
# ====================================================
@frappe.whitelist(allow_guest=False)
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
