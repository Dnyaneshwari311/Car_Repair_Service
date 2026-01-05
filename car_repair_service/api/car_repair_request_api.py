import frappe
from frappe import _
import json
from frappe.utils.file_manager import save_file
from frappe.utils import get_url
from car_repair_service.api.utils import get_paginated_data

@frappe.whitelist(allow_guest=False)
def create_car_repair_request(data):
    """
    Create a new Car Repair Request with:
    - Auto-created Customer
    - Vehicle Make/Model validation
    - Child table and attach fields (odometer + images)
    """
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
            frappe.throw(_("Missing customer_name or email"))

        # ---------------------------
        # DUPLICATE CHECK
        # ---------------------------
        existing_crr = frappe.get_all(
            "Car Repair Request",
            filters={
                "customer_name": customer_name,
                "car": car,
                "license_plate": license_plate
            },
            limit=1
        )
        if existing_crr:
            return {
                "status": "exists",
                "status_code": 200,
                "message": f"Car Repair Request already exists: {existing_crr[0].name}",
                "name": existing_crr[0].name
            }

        # ---------------------------
        # CUSTOMER CREATE / FETCH
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
        # CREATE CAR REPAIR REQUEST
        # ---------------------------
        doc = frappe.new_doc("Car Repair Request")

        fields = [
            "email", "phone", "make", "model", "assign_adviser",
            "car", "license_plate", "chassis_no",
            "car_manufacturing_year", "priority",
            "service_type", "repair_request_date",
            "driver_name", "driver_mob_no",
            "odometer_value", "odometer_value_current",
            "fuel_level", "customer_signature",
            "remark", "fuel_type"
        ]

        for f in fields:
            if f in data:
                doc.set(f, data[f])

        doc.customer = customer_doc.name
        doc.customer_name = customer_doc.customer_name

        doc.insert(ignore_permissions=True, ignore_mandatory=True)

        # ---------------------------
        # ODOMETER PHOTO
        # ---------------------------
        odometer_upload = files.get("odometer_photo")
        if not odometer_upload or not odometer_upload.filename:
            frappe.throw(_("Odometer Photo is required"))

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
        # CAR REPAIR IMAGES (MULTIPLE PER VIEW)
        # ---------------------------
        IMAGE_FIELD_MAP = {
            "front_view": "Front View",
            "back_view": "Back View",
            "left_view": "Left View",
            "right_view": "Right View",
        }

        for field, image_type in IMAGE_FIELD_MAP.items():
            uploads = files.getlist(field)
            for upload in uploads:
                if not upload or not upload.filename:
                    continue

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

        if not doc.car_repair_images:
            frappe.throw(_("At least one Car Repair Image is required"))

        # ---------------------------
        # SAVE FINAL DOCUMENT
        # ---------------------------
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # ---------------------------
        # FORMAT RESPONSE IMAGES
        # ---------------------------
        IMAGE_TYPE_KEY_MAP = {
            "Front View": "front_view",
            "Back View": "back_view",
            "Left View": "left_view",
            "Right View": "right_view",
        }

        formatted_images = {
            "front_view": [],
            "back_view": [],
            "left_view": [],
            "right_view": []
        }

        for row in doc.car_repair_images:
            key = IMAGE_TYPE_KEY_MAP.get(row.image_type)
            if key:
                formatted_images[key].append(row.image)

        # ---------------------------
        # FINAL RESPONSE
        # ---------------------------
        return {
            "status": "success",
            "status_code": 201,
            "message": "Car Repair Request created successfully",
            "name": doc.name,
            "car_repair_images": formatted_images
        }

    except Exception as e:
        frappe.log_error(
            title="Create Car Repair Request Error",
            message=frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": str(e)
        }









# =======================================================
# Create Car Diagnosis From Car Repair Request
# =======================================================


@frappe.whitelist(allow_guest=False)
def create_car_diagnosis(customer_name=None, customer=None):
    
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
                "vehicle_pick_up", "customer_signature"
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




@frappe.whitelist(allow_guest=False)
def create_quotation_from_car_diagnosis(diagnosis_name):
    """
    API: Create a Quotation from a Car Diagnosis record.
    - Reuses Item if item_code OR item_name exists
    - Creates Item only when truly missing
    - Prevents duplicate Item Name error
    """

    try:
        # ==============================
        # Fetch Diagnosis
        # ==============================
        diag = frappe.get_doc("Car Diagnosis", diagnosis_name)

        if not diag.customer_name:
            frappe.throw(_("Customer not found in Car Diagnosis"))

        # ==============================
        # Create Quotation
        # ==============================
        qtn = frappe.new_doc("Quotation")
        qtn.quotation_to = "Customer"
        qtn.party_name = diag.customer_name
        qtn.remarks = f"Quotation based on Car Diagnosis: {diag.name}"
        qtn.custom_car_diagnosis = diag.name

        if getattr(diag, "email_id", None):
            qtn.contact_email = diag.email_id

        added_items = False

        # ==============================
        # Add Items from Diagnosis
        # ==============================
        for d in getattr(diag, "car_diagnosis_detail", []):
            if not d.part_required:
                continue

            part_name = d.part_required.strip()

            # ----------------------------------
            # Resolve Item SAFELY
            # ----------------------------------
            existing_item = None

            # 1️⃣ Check Item Code
            if frappe.db.exists("Item", part_name):
                existing_item = part_name

            # 2️⃣ Check Item Name
            else:
                existing_item = frappe.db.get_value(
                    "Item",
                    {"item_name": part_name},
                    "name"
                )

            # 3️⃣ Create only if not found
            if not existing_item:
                item_doc = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": part_name,
                    "item_name": part_name,
                    "stock_uom": "Nos",
                    "item_group": "Products",  # change if needed
                    "is_stock_item": 0
                })
                item_doc.insert(ignore_permissions=True)
                existing_item = item_doc.name

            # ----------------------------------
            # Safe qty & rate
            # ----------------------------------
            try:
                qty = float(d.quantity) if d.quantity else 1.0
                if qty <= 0:
                    qty = 1.0
            except:
                qty = 1.0

            try:
                rate = float(d.estimated_cost) if d.estimated_cost else 0.0
            except:
                rate = 0.0

            uom = frappe.db.get_value("Item", existing_item, "stock_uom") or "Nos"

            # ----------------------------------
            # Append Quotation Item
            # ----------------------------------
            item = qtn.append("items", {})
            item.item_code = existing_item
            item.item_name = part_name
            item.qty = qty
            item.rate = rate
            item.uom = uom
            item.amount = qty * rate

            added_items = True

        # ==============================
        # Fallback Item (No Parts)
        # ==============================
        if not added_items:
            description = (
                getattr(diag, "issues", None)
                or getattr(diag, "problem_description", None)
            )
            if description:
                item = qtn.append("items", {})
                item.item_name = description
                item.qty = 1.0
                item.rate = 0.0
                item.uom = "Nos"
                item.amount = 0.0

        # ==============================
        # Vehicle Info
        # ==============================
        vehicle_field = "vehicle" if "vehicle" in qtn.as_dict() else "custom_vehicle"
        if getattr(diag, "car", None):
            setattr(qtn, vehicle_field, diag.car)

        # ==============================
        # Final Safety Validation
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
    

#     try:
#         extra_params = {"search": search} if search else {}
#         base_url = frappe.request.host_url.rstrip("/") + frappe.request.path

#         # -------------------------
#         # SINGLE RECORD
#         # -------------------------
#         if name:
#             if not frappe.db.exists("Car Repair Request", name):
#                 return {
#                     "status": "error",
#                     "message": f"Car Repair Request '{name}' not found"
#                 }

#             doc = frappe.get_doc("Car Repair Request", name)
#             data = doc.as_dict()

#             data["vehicle_concern"] = [
#                 {"vehicle_concern": vc.vehicle_concern}
#                 for vc in doc.get("vehicle_concern", [])
#             ]

#             data["car_repair_images"] = [
#                 {"image": frappe.utils.get_url(img.image)}
#                 for img in doc.get("car_repair_images", [])
#             ]

#             if data.get("odometer_photo"):
#                 data["odometer_photo"] = frappe.utils.get_url(data["odometer_photo"])

#             return {
#                 "status": "success",
#                 "data": data
#             }

#         # -------------------------
#         # PAGINATED LIST
#         # -------------------------
#         fields = [
#             "name", "customer_name", "email", "phone",
#             "make", "model", "license_plate", "assign_adviser",
#             "car_manufacturing_year", "odometer_photo",
#             "priority", "service_type", "repair_request_date",
#             "reason_for_repair", "odometer_value","odometer_value_current", "customer_signature"
#         ]

#         search_fields = [
#             "customer_name", "make", "model", "license_plate",
#             "service_type", "priority"
#         ]

#         raw = get_paginated_data(
#             doctype="Car Repair Request",
#             fields=fields,
#             search=search,
#             filters={},
#             sort_by=sort_by,
#             sort_order=sort_order,
#             page=int(page),
#             page_size=int(page_size),
#             search_fields=search_fields,
#             is_pagination=frappe.utils.sbool(is_pagination),
#             base_url=base_url,
#             extra_params=extra_params
#         )

#         # ----------------------------------------
#         #  NORMALIZE RAW RESPONSE SAFELY
#         # ----------------------------------------
#         if isinstance(raw, dict):
#             data_list = raw.get("data", [])
#         elif isinstance(raw, list):
#             data_list = raw
#             raw = {"data": raw}    # convert list → dict
#         else:
#             data_list = []
#             raw = {"data": []}

#         # ----------------------------------------
#         # Add child images + convert URLs
#         # ----------------------------------------
#         for row in data_list:

#             images = frappe.db.get_all(
#                 "Car Repair Images",
#                 filters={"parent": row["name"], "parenttype": "Car Repair Request"},
#                 fields=["image"]
#             )

#             row["car_repair_images"] = [
#                 frappe.utils.get_url(i["image"]) for i in images
#             ]

#             if row.get("odometer_photo"):
#                 row["odometer_photo"] = frappe.utils.get_url(row["odometer_photo"])

#         return raw

#     except Exception as e:
#         frappe.log_error(title="Get Car Repair Request Error", message=str(e))
#         return {
#             "status": "error",
#             "message": f"Internal Server Error: {str(e)}"
#         }



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
#                 return {
#                     "status": "error",
#                     "message": f"Car Repair Request '{name}' not found"
#                 }

#             doc = frappe.get_doc("Car Repair Request", name)
#             data = doc.as_dict()

#             # vehicle concerns
#             data["vehicle_concern"] = [
#                 {"vehicle_concern": vc.vehicle_concern}
#                 for vc in doc.get("vehicle_concern", [])
#             ]

#             # grouped images
#             grouped_images = empty_image_structure()
#             for img in doc.get("car_repair_images", []):
#                 key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
#                 if key:
#                     grouped_images[key].append(
#                         frappe.utils.get_url(img.image)
#                     )

#             data["car_repair_images"] = grouped_images

#             if data.get("odometer_photo"):
#                 data["odometer_photo"] = frappe.utils.get_url(
#                     data["odometer_photo"]
#                 )

#             return {
#                 "status": "success",
#                 "data": data
#             }

#         # -------------------------
#         # PAGINATED LIST
#         # -------------------------
#         fields = [
#             "name", "customer_name", "email", "phone",
#             "make", "model", "license_plate", "assign_adviser",
#             "car_manufacturing_year", "odometer_photo",
#             "priority", "service_type", "repair_request_date",
#             "reason_for_repair", "odometer_value",
#             "odometer_value_current", "customer_signature"
#         ]

#         search_fields = [
#             "customer_name", "make", "model",
#             "license_plate", "service_type", "priority"
#         ]

#         raw = get_paginated_data(
#             doctype="Car Repair Request",
#             fields=fields,
#             search=search,
#             filters={},
#             sort_by=sort_by,
#             sort_order=sort_order,
#             page=int(page),
#             page_size=int(page_size),
#             search_fields=search_fields,
#             is_pagination=frappe.utils.sbool(is_pagination),
#             base_url=base_url,
#             extra_params=extra_params
#         )

#         # normalize
#         if isinstance(raw, dict):
#             data_list = raw.get("data", [])
#         else:
#             data_list = raw
#             raw = {"data": data_list}

#         # ----------------------------------------
#         # ADD GROUPED CHILD IMAGES
#         # ----------------------------------------
#         for row in data_list:
#             row["car_repair_images"] = empty_image_structure()

#             images = frappe.db.get_all(
#                 "Car Repair Images",
#                 filters={
#                     "parent": row["name"],
#                     "parenttype": "Car Repair Request"
#                 },
#                 fields=["image", "image_type"]
#             )

#             for img in images:
#                 key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
#                 if key:
#                     row["car_repair_images"][key].append(
#                         frappe.utils.get_url(img.image)
#                     )

#             if row.get("odometer_photo"):
#                 row["odometer_photo"] = frappe.utils.get_url(
#                     row["odometer_photo"]
#                 )

#         return raw

#     except Exception as e:
#         frappe.log_error(
#             title="Get Car Repair Request Error",
#             message=frappe.get_traceback()
#         )
#         return {
#             "status": "error",
#             "message": f"Internal Server Error: {str(e)}"
#         }









@frappe.whitelist(allow_guest=False)
def get_car_repair_request(
    name=None, 
    page=1, 
    page_size=10, 
    sort_by="creation", 
    sort_order="desc", 
    search=None, 
    is_pagination=False
):
    import frappe
    try:
        extra_params = {"search": search} if search else {}
        base_url = frappe.request.host_url.rstrip("/") + frappe.request.path

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
        # SINGLE RECORD
        # -------------------------
        if name:
            if not frappe.db.exists("Car Repair Request", name):
                return {"status": "error", "message": f"Car Repair Request '{name}' not found"}

            doc = frappe.get_doc("Car Repair Request", name)
            data = doc.as_dict()

            # Vehicle concerns
            data["vehicle_concern"] = [
                {"vehicle_concern": vc.vehicle_concern} for vc in doc.get("vehicle_concern", [])
            ]

            # Images
            grouped_images = empty_image_structure()
            for img in doc.get("car_repair_images", []):
                key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
                if key:
                    grouped_images[key].append(frappe.utils.get_url(img.image))
            data["car_repair_images"] = grouped_images

            # Odometer photo
            if data.get("odometer_photo"):
                data["odometer_photo"] = frappe.utils.get_url(data["odometer_photo"])

            return {"status": "success", "data": data}

        # -------------------------
        # PAGINATED LIST
        # -------------------------
        fields = [
            "name", "customer_name", "email", "phone",
            "make", "model", "license_plate", "assign_adviser",
            "car_manufacturing_year", "odometer_photo",
            "priority", "service_type", "repair_request_date",
            "reason_for_repair", "odometer_value",
            "odometer_value_current", "customer_signature","driver_name","driver_mob_no","fuel_type"
        ]

        search_fields = ["name", "customer_name", "make", "model", "license_plate", "service_type", "priority"]

        # -------------------------
        # FIXED: Do NOT pass filters with ["like", ...] manually
        # Let get_paginated_data handle search internally
        filters = {}

        raw = get_paginated_data(
            doctype="Car Repair Request",
            fields=fields,
            search=search,
            search_fields=search_fields,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=int(page),
            page_size=int(page_size),
            is_pagination=frappe.utils.sbool(is_pagination),
            base_url=base_url,
            extra_params=extra_params
        )

        # normalize
        data_list = raw.get("data", []) if isinstance(raw, dict) else raw
        raw = {"data": data_list}

        # -------------------------
        # ADD GROUPED CHILD IMAGES
        # -------------------------
        for row in data_list:
            row["car_repair_images"] = empty_image_structure()
            images = frappe.db.get_all(
                "Car Repair Images",
                filters={"parent": row["name"], "parenttype": "Car Repair Request"},
                fields=["image", "image_type"]
            )
            for img in images:
                key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
                if key:
                    row["car_repair_images"][key].append(frappe.utils.get_url(img.image))

            if row.get("odometer_photo"):
                row["odometer_photo"] = frappe.utils.get_url(row["odometer_photo"])

        return raw

    except Exception as e:
        frappe.log_error(title="Get Car Repair Request Error", message=frappe.get_traceback())
        return {"status": "error", "message": f"Internal Server Error: {str(e)}"}






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
# @frappe.whitelist(allow_guest=False)
# def update_car_repair_request(name, data):
   
#     """
#     Update an existing Car Repair Request.
#     - Supports partial updates (only provided fields)
#     - Updates child tables (vehicle_concern, car_repair_images)
#     """
#     import json

#     try:
#         # Ensure request payload is parsed
#         data = json.loads(data) if isinstance(data, str) else data

#         # Validate if document exists
#         if not frappe.db.exists("Car Repair Request", name):
#             return {"status": "error", "message": f"Car Repair Request '{name}' not found"}

#         doc = frappe.get_doc("Car Repair Request", name)

#         # ✅ Allowed updatable fields
#         updatable_fields = [
#             "email", "phone", "make", "model", "assign_adviser", "car", "license_plate",
#             "chassis_no", "car_manufacturing_year", "odometer_photo", "priority",
#             "service_type", "repair_request_date", "driver_name", "driver_mob_no",
#             "odometer_value", "fuel_level", "vehicle_pick_up", "customer_signature",
#             "remark", "fuel_type"
#         ]

#         # ✅ Update only provided fields
#         for f in updatable_fields:
#             if f in data:
#                 doc.set(f, data[f])

#         # ✅ Update child table: Vehicle Concerns
#         if "vehicle_concern" in data and isinstance(data["vehicle_concern"], list):
#             doc.set("vehicle_concern", [])
#             for vc in data["vehicle_concern"]:
#                 if vc.get("vehicle_concern"):
#                     doc.append("vehicle_concern", {"vehicle_concern": vc["vehicle_concern"]})

#         # ✅ Update child table: Car Repair Images
#         if "car_repair_images" in data and isinstance(data["car_repair_images"], list):
#             doc.set("car_repair_images", [])
#             for img in data["car_repair_images"]:
#                 if img.get("image"):
#                     doc.append("car_repair_images", {"image": img["image"]})

#         # ✅ Save changes
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code":201,
#             "message": f"Car Repair Request '{name}' updated successfully",
#             "updated_data": doc.as_dict()
#         }

#     except Exception as e:
#         frappe.log_error(title="Update Car Repair Request Error", message=str(e))
#         return {"status": "error", "message": str(e)}




# @frappe.whitelist(allow_guest=False)
# def update_car_repair_request(data):
#     """
#     Update an existing Car Repair Request
#     - `name` is expected INSIDE data
#     - Partial updates supported
#     - Vehicle concern update
#     - Grouped car repair images update
#     """
#     import json
#     try:
#         # -------------------------
#         # PARSE PAYLOAD
#         # -------------------------
#         # payload = json.loads(data) if isinstance(data, str) else data
#         # data = payload.get("data", {})

#         # name = data.get("name")
#         # if not name:
#         #     return {
#         #         "status": "error",
#         #         "message": "Missing 'name' inside data"
#         #     }
        
#         # -------------------------
#         # PARSE PAYLOAD (FLAT JSON)
#         # -------------------------
#         payload = json.loads(data) if isinstance(data, str) else data

#         # If old format exists, still support it
#         data = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload

#         name = data.get("name")
#         if not name:
#             return {
#                 "status": "error",
#                 "message": "Missing 'name'"
#             }

        
        
#         if not frappe.db.exists("Car Repair Request", name):
#             return {
#                 "status": "error",
#                 "message": f"Car Repair Request '{name}' not found"
#             }

#         doc = frappe.get_doc("Car Repair Request", name)

#         # -------------------------
#         # UPDATABLE FIELDS
#         # -------------------------
#         updatable_fields = [
#             "email", "phone", "make", "model", "assign_adviser",
#             "car", "license_plate", "chassis_no",
#             "car_manufacturing_year", "priority",
#             "service_type", "repair_request_date",
#             "driver_name", "driver_mob_no",
#             "odometer_value", "fuel_level",
#             "vehicle_pick_up", "customer_signature",
#             "remark", "fuel_type"
#         ]

#         for f in updatable_fields:
#             if f in data:
#                 doc.set(f, data[f])

#         # -------------------------
#         # VEHICLE CONCERNS
#         # -------------------------
#         if isinstance(data.get("vehicle_concern"), list):
#             doc.set("vehicle_concern", [])
#             for vc in data["vehicle_concern"]:
#                 if vc.get("vehicle_concern"):
#                     doc.append("vehicle_concern", {
#                         "vehicle_concern": vc["vehicle_concern"]
#                     })
                    
                    
                    
#                     def normalize_file_url(url):
#                         if not url:
#                             return None
#                         if url.startswith("http"):
#                             if "/files/" in url:
#                                 return "/files/" + url.split("/files/", 1)[1]
#                             return None
#                         return url

#         # -------------------------
#         # CAR REPAIR IMAGES (GROUPED)
#         # -------------------------
#         IMAGE_KEY_TYPE_MAP = {
#             "front_view": "Front View",
#             "back_view": "Back View",
#             "left_view": "Left View",
#             "right_view": "Right View"
#         }

#         if isinstance(data.get("car_repair_images"), dict):
#             # Clear existing images
#             doc.set("car_repair_images", [])

#             for view_key, urls in data["car_repair_images"].items():
#                 image_type = IMAGE_KEY_TYPE_MAP.get(view_key)
#                 if not image_type or not isinstance(urls, list):
#                     continue

#                 # for url in urls:
#                 #     if url:
#                 #         doc.append("car_repair_images", {
#                 #             "image": url,
#                 #             "image_type": image_type
#                 #         })
#                 for url in urls:
#                     file_path = normalize_file_url(url)
#                     if file_path:
#                         doc.append("car_repair_images", {
#                             "image": file_path,
#                             "image_type": image_type
#                         })


#         # -------------------------
#         # SAVE
#         # -------------------------
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         # -------------------------
#         # FORMAT RESPONSE (GROUPED)
#         # -------------------------
#         IMAGE_TYPE_KEY_MAP = {
#             "Front View": "front_view",
#             "Back View": "back_view",
#             "Left View": "left_view",
#             "Right View": "right_view"
#         }

#         grouped_images = {
#             "front_view": [],
#             "back_view": [],
#             "left_view": [],
#             "right_view": []
#         }

#         for img in doc.car_repair_images:
#             key = IMAGE_TYPE_KEY_MAP.get(img.image_type)
#             if key:
#                 grouped_images[key].append(
#                     frappe.utils.get_url(img.image)
#                 )

#         return {
#             "status": "success",
#             "status_code": 200,
#             "message": f"Car Repair Request '{name}' updated successfully",
#             "car_repair_images": grouped_images
#         }

#     except Exception as e:
#         frappe.log_error(
#             title="Update Car Repair Request Error",
#             message=frappe.get_traceback()
#         )
#         return {
#             "status": "error",
#             "message": str(e)
#         }

import base64
import uuid


@frappe.whitelist(allow_guest=False)
def update_car_repair_request(data):
    """
    FINAL PRODUCTION VERSION
    - Safe partial updates
    - View-wise image replacement
    - Mandatory validation handled correctly
    """

    try:
        # -------------------------
        # PARSE PAYLOAD
        # -------------------------
        payload = json.loads(data) if isinstance(data, str) else data
        data = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload

        name = data.get("name")
        if not name:
            return {"status": "error", "message": "Missing 'name'"}

        doc = frappe.get_doc("Car Repair Request", name)

        # -------------------------
        # EXISTING IMAGE COUNT (IMPORTANT)
        # -------------------------
        existing_image_count = len(doc.car_repair_images or [])

        # -------------------------
        # UPDATE NORMAL FIELDS
        # -------------------------
        updatable_fields = [
            "email", "phone", "make", "model",
            "license_plate", "priority", "remark"
        ]

        for field in updatable_fields:
            if field in data:
                doc.set(field, data[field])

        # -------------------------
        # HANDLE ODOMETER PHOTO (MANDATORY)
        # -------------------------
        if data.get("odometer_photo"):
            image_bytes = base64.b64decode(data["odometer_photo"])
            filename = f"odometer_{uuid.uuid4()}.png"

            file_doc = save_file(
                filename=filename,
                content=image_bytes,
                dt="Car Repair Request",
                dn=doc.name,
                is_private=0
            )

            doc.odometer_photo = file_doc.file_url

        # -------------------------
        # IMAGE VIEW MAP
        # -------------------------
        IMAGE_KEY_TYPE_MAP = {
            "front_view": "Front View",
            "back_view": "Back View",
            "left_view": "Left View",
            "right_view": "Right View"
        }

        # -------------------------
        # UPDATE IMAGES (SAFE)
        # -------------------------
        if isinstance(data.get("car_repair_images"), dict):

            for view_key, images in data["car_repair_images"].items():
                image_type = IMAGE_KEY_TYPE_MAP.get(view_key)

                if not image_type or not images:
                    continue

                # Remove old images of this view ONLY
                doc.car_repair_images = [
                    row for row in doc.car_repair_images
                    if row.image_type != image_type
                ]

                for img in images:
                    image_bytes = base64.b64decode(img)
                    filename = f"{uuid.uuid4()}.png"

                    file_doc = save_file(
                        filename=filename,
                        content=image_bytes,
                        dt="Car Repair Request",
                        dn=doc.name,
                        is_private=0
                    )

                    doc.append("car_repair_images", {
                        "image": file_doc.file_url,
                        "image_type": image_type
                    })

        # -------------------------
        # FINAL VALIDATION (CORRECT)
        # -------------------------
        final_image_count = len(doc.car_repair_images or [])

        if existing_image_count == 0 and final_image_count == 0:
            frappe.throw("At least one car image is required")

        # -------------------------
        # SAVE
        # -------------------------
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # -------------------------
        # RESPONSE
        # -------------------------
        result_images = {
            "front_view": [],
            "back_view": [],
            "left_view": [],
            "right_view": []
        }

        for row in doc.car_repair_images:
            key = row.image_type.lower().replace(" ", "_")
            result_images[key].append(get_url(row.image))

        return {
            "status": "success",
            "status_code": 200,
            "message": f"Car Repair Request '{name}' updated successfully",
            "car_repair_images": result_images
        }

    except Exception as e:
        frappe.log_error("Update Car Repair Request Error", frappe.get_traceback())
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
