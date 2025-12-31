import frappe
from frappe import _
import json
from car_repair_service.api.utils import get_paginated_data

# ====================================================
# CREATE Car Repair Request (with Auto Customer + Email)
# ====================================================
@frappe.whitelist(allow_guest=False)
def create_car_repair_request(data):
    
    
    """
    Create a new Car Repair Request:
    - Auto-creates Customer if not exists
    - Ensures Vehicle Make/Model exist
    - Inserts Car Repair Request record
    - Populates customer_name field
    - Skips creation if Car Repair Request already exists
    """
    try:
        data = json.loads(data) if isinstance(data, str) else data

        customer_name = data.get("customer_name")
        email = data.get("email")
        phone = data.get("phone")
        car = data.get("car")
        license_plate = data.get("license_plate")

        if not customer_name or not email:
            frappe.throw("Missing customer_name or email for Customer creation")

        # ====================================================
        # Step 0: Skip if Car Repair Request already exists
        # ====================================================
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

        # ====================================================
        # Step 1: Auto-create Customer if not exists
        # ====================================================
        existing_customer_name = frappe.db.exists("Customer", {"email_id": email})
        if existing_customer_name:
            customer_doc = frappe.get_doc("Customer", existing_customer_name)
        else:
            customer_doc = frappe.new_doc("Customer")
            customer_doc.customer_name = customer_name
            customer_doc.email_id = email
            customer_doc.mobile_no = phone
            customer_doc.customer_group = "Individual"
            customer_doc.territory = "All Territories"
            customer_doc.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Customer {customer_doc.customer_name} created successfully.")

        # ====================================================
        # Step 2: Ensure Vehicle Make & Model exist
        # ====================================================
        make = data.get("make")
        model = data.get("model")

        if make and not frappe.db.exists("Vehicle Make", {"make": make}):
            vehicle_make = frappe.new_doc("Vehicle Make")
            vehicle_make.make = make
            vehicle_make.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Created new Vehicle Make: {make}")

        if model and not frappe.db.exists("Vehicle Model", {"model": model}):
            vehicle_model = frappe.new_doc("Vehicle Model")
            vehicle_model.model = model
            vehicle_model.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Created new Vehicle Model: {model}")

        # ====================================================
        # Step 3: Create Car Repair Request
        # ====================================================
        frappe.flags.in_create_car_repair_api = True  # avoids re-trigger in hooks

        doc = frappe.new_doc("Car Repair Request")

        fields = [
            "email", "phone", "make", "model", "assign_adviser",
            "car", "license_plate", "chassis_no", "car_manufacturing_year",
            "odometer_photo", "priority", "service_type", "repair_request_date",
            "driver_name", "driver_mob_no", "odometer_value","odometer_value_current", "fuel_level",
            "customer_signature", "remark", "fuel_type"
        ]
        for f in fields:
            if f in data:
                doc.set(f, data[f])

        # ✅ Link correct Customer
        doc.customer = customer_doc.name
        doc.customer_name = customer_doc.customer_name

        # --- Child Table: Vehicle Concerns ---
        for vc in data.get("vehicle_concern", []):
            doc.append("vehicle_concern", {"vehicle_concern": vc.get("vehicle_concern")})

        # --- Child Table: Car Repair Images ---
        for img in data.get("car_repair_images", []):
            doc.append("car_repair_images", {"image": img.get("image")})

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 201,
            "message": "Car Repair Request created successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error("Create Car Repair Request Error", str(e))
        return {"status": "error", "message": str(e)}







# import frappe
# from frappe import _
# import json
# from frappe.utils.file_manager import save_file

# # ====================================================
# # CREATE Car Repair Request (with Auto Customer + Email)
# # ====================================================
# @frappe.whitelist(allow_guest=False)
# def create_car_repair_request(data):
#     """
#     Create a new Car Repair Request:
#     - Auto-creates Customer if not exists
#     - Ensures Vehicle Make/Model exist
#     - Inserts Car Repair Request safely
#     - Uploads mandatory Attach Image correctly
#     - Handles mandatory child table
#     """

#     try:
#         # ------------------------------------------------
#         # Parse data & files
#         # ------------------------------------------------
#         data = json.loads(data) if isinstance(data, str) else data
#         files = frappe.request.files or {}

#         # ------------------------------------------------
#         # Validate basic data
#         # ------------------------------------------------
#         customer_name = data.get("customer_name")
#         email = data.get("email")
#         phone = data.get("phone")

#         if not customer_name or not email:
#             frappe.throw(_("customer_name and email are mandatory"))

#         # ------------------------------------------------
#         # Skip if request already exists
#         # ------------------------------------------------
#         existing = frappe.get_all(
#             "Car Repair Request",
#             filters={
#                 "customer_name": customer_name,
#                 "car": data.get("car"),
#                 "license_plate": data.get("license_plate")
#             },
#             limit=1
#         )
#         if existing:
#             return {
#                 "status": "exists",
#                 "status_code": 200,
#                 "name": existing[0].name,
#                 "message": "Car Repair Request already exists"
#             }

#         # ------------------------------------------------
#         # Customer (Auto-create)
#         # ------------------------------------------------
#         customer_name_db = frappe.db.exists("Customer", {"email_id": email})
#         if customer_name_db:
#             customer = frappe.get_doc("Customer", customer_name_db)
#         else:
#             customer = frappe.new_doc("Customer")
#             customer.customer_name = customer_name
#             customer.email_id = email
#             customer.mobile_no = phone
#             customer.customer_group = "Individual"
#             customer.territory = "All Territories"
#             customer.insert(ignore_permissions=True)

#         # ------------------------------------------------
#         # Vehicle Make / Model
#         # ------------------------------------------------
#         if data.get("make") and not frappe.db.exists("Vehicle Make", {"make": data.get("make")}):
#             frappe.get_doc({
#                 "doctype": "Vehicle Make",
#                 "make": data.get("make")
#             }).insert(ignore_permissions=True)

#         if data.get("model") and not frappe.db.exists("Vehicle Model", {"model": data.get("model")}):
#             frappe.get_doc({
#                 "doctype": "Vehicle Model",
#                 "model": data.get("model")
#             }).insert(ignore_permissions=True)

#         # ------------------------------------------------
#         # Create Car Repair Request (INSERT FIRST)
#         # ------------------------------------------------
#         doc = frappe.new_doc("Car Repair Request")

#         fields = [
#             "email", "phone", "make", "model", "assign_adviser",
#             "car", "license_plate", "chassis_no", "car_manufacturing_year",
#             "priority", "service_type", "repair_request_date",
#             "driver_name", "driver_mob_no", "odometer_value",
#             "odometer_value_current", "fuel_level", "vehicle_pick_up",
#             "customer_signature", "remark", "fuel_type"
#         ]

#         for f in fields:
#             if f in data:
#                 doc.set(f, data.get(f))

#         doc.customer = customer.name
#         doc.customer_name = customer.customer_name

#         # 🚨 Insert without mandatory check (Attach Image reason)
#         doc.insert(ignore_permissions=True, ignore_mandatory=True)

#         # ------------------------------------------------
#         # Mandatory ODOMETER PHOTO (Attach Image)
#         # ------------------------------------------------
#         odometer_upload = files.get("odometer_photo")
#         if not odometer_upload or not odometer_upload.filename:
#             frappe.throw(_("Odometer Photo is mandatory"))

#         odometer_file = save_file(
#             fname=odometer_upload.filename,
#             content=odometer_upload.stream.read(),
#             dt="Car Repair Request",
#             dn=doc.name,
#             is_private=0
#         )
#         doc.odometer_photo = odometer_file.file_url

#         # ------------------------------------------------
#         # Vehicle Concerns (Child Table)
#         # ------------------------------------------------
#         for vc in data.get("vehicle_concern", []):
#             doc.append("vehicle_concern", {
#                 "vehicle_concern": vc.get("vehicle_concern")
#             })

#         # ------------------------------------------------
#         # Mandatory Car Repair Images (Child Table)
#         # ------------------------------------------------
#         image_fields = ["image", "back_view", "right_view", "left_view"]

#         image_row = doc.append("car_repair_images", {})
#         has_image = False

#         for field in image_fields:
#             upload = files.get(field)
#             if upload and upload.filename:
#                 file_doc = save_file(
#                     fname=upload.filename,
#                     content=upload.stream.read(),
#                     dt="Car Repair Request",
#                     dn=doc.name,
#                     is_private=0
#                 )
#                 image_row.set(field, file_doc.file_url)
#                 has_image = True

#         if not has_image:
#             frappe.throw(_("At least one Car Repair Image is required"))

#         # ------------------------------------------------
#         # Final Save (mandatory validation passes)
#         # ------------------------------------------------
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code": 200,
#             "name": doc.name,
#             "message": "Car Repair Request created successfully"
#         }

#     except Exception as e:
#         frappe.log_error(
#             title="Create Car Repair Request API Error",
#             message=frappe.get_traceback()
#         )
#         return {
#             "status": "error",
#             "message": str(e)
#         }



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


# @frappe.whitelist()
# def create_car_diagnosis(customer_name=None, customer=None):
#     """
#     Create a Car Diagnosis record:
#     - Prefill from last Car Repair Request for this customer
#     - Auto-fill Reference No from Car Repair Request
#     """
#     try:
#         if not customer_name and not customer:
#             frappe.throw(_("Please provide either customer_name or customer"))

#         # If customer link is provided, fetch customer_name
#         if customer and not customer_name:
#             customer_name = frappe.db.get_value("Customer", customer, "customer_name")

#         # Fetch latest Car Repair Request
#         last_request = frappe.get_all(
#             "Car Repair Request",
#             filters={"customer_name": customer_name},
#             fields=[
#                 "name", "car", "car_model", "license_plate", "chassis_no",
#                 "email", "phone", "repair_request_date", "priority",
#                 "vehicle_pick_up", "customer_signature"
#             ],
#             order_by="creation desc",
#             limit_page_length=1
#         )

#         if not last_request:
#             return {"status": "not_found", "message": "No Car Repair Request found for this customer"}

#         req_name = last_request[0]["name"]

#         # Fetch full Car Repair Request including child tables
#         req_doc = frappe.get_doc("Car Repair Request", req_name)

#         # Create new Car Diagnosis
#         diagnosis = frappe.new_doc("Car Diagnosis")
#         diagnosis.customer_name = req_doc.customer_name

#         # Only assign customer link if it exists
#         if hasattr(req_doc, "customer"):
#             diagnosis.customer = req_doc.customer

#         diagnosis.car = req_doc.car
#         diagnosis.model = req_doc.car_model
#         diagnosis.license_plate = req_doc.license_plate
#         diagnosis.chassis_no = req_doc.chassis_no
#         diagnosis.email_id = req_doc.email
#         diagnosis.phone = req_doc.phone
#         diagnosis.date_of_receipt = req_doc.repair_request_date
#         diagnosis.priority = req_doc.priority
#         diagnosis.vehicle_pick_up = req_doc.vehicle_pick_up
#         diagnosis.customer_signature = req_doc.customer_signature

#         # ✅ Auto-fill Reference No from Car Repair Request
#         if not diagnosis.reference_no and req_doc.name:
#             diagnosis.reference_no = req_doc.name

#         # Child table: Vehicle Concern
#         if hasattr(req_doc, "vehicle_concern"):
#             for vc in req_doc.vehicle_concern:
#                 diagnosis.append("vehicle_concern", {"vehicle_concern": vc.vehicle_concern})

#         # Child table: Car Repair Images
#         if hasattr(req_doc, "car_repair_images"):
#             for img in req_doc.car_repair_images:
#               if img.image: 
#                 diagnosis.append("car_repair_images", {"image": img.image})

#         # Insert document
#         diagnosis.insert(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code":201,
#             "message": f"Car Diagnosis created from Car Repair Request {req_name}",
#             "name": diagnosis.name
#         }

#     except Exception as e:
#         frappe.log_error("Error creating Car Diagnosis", str(e))
#         return {"status": "error", "message": str(e)}




# ======================================================
# Create Quotation From Car Diagnosis
# ======================================================


# @frappe.whitelist(allow_guest=False)
# def create_quotation_from_car_diagnosis(diagnosis_name):
    
#     """
#     API: Create a Quotation from a Car Diagnosis record.
#     Returns the created Quotation name.
#     """
#     try:
#         diag = frappe.get_doc("Car Diagnosis", diagnosis_name)
#         if not diag.customer_name:
#             frappe.throw(_("Customer not found in Car Diagnosis"))

#         # Create Quotation
#         qtn = frappe.new_doc("Quotation")
#         qtn.quotation_to = "Customer"
#         qtn.party_name = diag.customer_name
#         qtn.remarks = f"Quotation based on Car Diagnosis: {diag.name}"
#         qtn.custom_car_diagnosis = diag.name

#         if getattr(diag, "email_id", None):
#             qtn.contact_email = diag.email_id

#         added_items = False

#         # Add items from car_diagnosis_detail
#         for d in getattr(diag, "car_diagnosis_detail", []):
#             if not getattr(d, "part_required", None):
#                 continue

#             # ✅ Force qty and rate to float
#             try:
#                 qty = float(d.quantity) if d.quantity not in (None, "", " ") else 1.0
#                 if qty <= 0:
#                     qty = 1.0
#             except:
#                 qty = 1.0

#             try:
#                 rate = float(d.estimated_cost) if d.estimated_cost not in (None, "", " ") else 0.0
#             except:
#                 rate = 0.0

#             # UOM from Item master
#             uom = frappe.db.get_value("Item", d.part_required, "stock_uom") or "Nos"

#             # Append item
#             item = qtn.append("items", {})
#             item.item_code = d.part_required
#             item.item_name = d.part_required
#             item.qty = qty
#             item.rate = rate
#             item.uom = uom
#             # ✅ Explicitly set amount to avoid NoneType * float
#             item.amount = qty * rate
#             added_items = True

#         # Fallback item if no parts
#         if not added_items:
#             description_field = getattr(diag, "issues", None) or getattr(diag, "problem_description", None)
#             if description_field:
#                 item = qtn.append("items", {})
#                 item.item_name = description_field
#                 item.qty = 1.0
#                 item.rate = 0.0
#                 item.uom = "Nos"
#                 item.amount = 0.0

#         # Vehicle info
#         vehicle_field = "vehicle" if "vehicle" in qtn.as_dict() else "custom_vehicle"
#         if getattr(diag, "car", None):
#             setattr(qtn, vehicle_field, diag.car)

#         # ✅ Ensure all items have numeric qty, rate, and amount
#         for item in qtn.items:
#             if item.qty in (None, "", 0):
#                 item.qty = 1.0
#             if item.rate in (None, "", 0):
#                 item.rate = 0.0
#             item.amount = float(item.qty) * float(item.rate)

#         # Insert Quotation
#         qtn.flags.ignore_permissions = True
#         qtn.set_missing_values()
#         qtn.calculate_taxes_and_totals()
#         qtn.insert(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code":201,
#             "message": f"Quotation created successfully from Car Diagnosis {diag.name}",
#             "quotation_name": qtn.name
#         }

#     except Exception as e:
#         frappe.log_error(f"Error creating Quotation from Car Diagnosis {diagnosis_name}", frappe.get_traceback())
#         return {"status": "error", "message": str(e)}






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
    

    try:
        extra_params = {"search": search} if search else {}
        base_url = frappe.request.host_url.rstrip("/") + frappe.request.path

        # -------------------------
        # SINGLE RECORD
        # -------------------------
        if name:
            if not frappe.db.exists("Car Repair Request", name):
                return {
                    "status": "error",
                    "message": f"Car Repair Request '{name}' not found"
                }

            doc = frappe.get_doc("Car Repair Request", name)
            data = doc.as_dict()

            data["vehicle_concern"] = [
                {"vehicle_concern": vc.vehicle_concern}
                for vc in doc.get("vehicle_concern", [])
            ]

            data["car_repair_images"] = [
                {"image": frappe.utils.get_url(img.image)}
                for img in doc.get("car_repair_images", [])
            ]

            if data.get("odometer_photo"):
                data["odometer_photo"] = frappe.utils.get_url(data["odometer_photo"])

            return {
                "status": "success",
                "data": data
            }

        # -------------------------
        # PAGINATED LIST
        # -------------------------
        fields = [
            "name", "customer_name", "email", "phone",
            "make", "model", "license_plate", "assign_adviser",
            "car_manufacturing_year", "odometer_photo",
            "priority", "service_type", "repair_request_date",
            "reason_for_repair", "odometer_value","odometer_value_current", "customer_signature"
        ]

        search_fields = [
            "customer_name", "make", "model", "license_plate",
            "service_type", "priority"
        ]

        raw = get_paginated_data(
            doctype="Car Repair Request",
            fields=fields,
            search=search,
            filters={},
            sort_by=sort_by,
            sort_order=sort_order,
            page=int(page),
            page_size=int(page_size),
            search_fields=search_fields,
            is_pagination=frappe.utils.sbool(is_pagination),
            base_url=base_url,
            extra_params=extra_params
        )

        # ----------------------------------------
        #  NORMALIZE RAW RESPONSE SAFELY
        # ----------------------------------------
        if isinstance(raw, dict):
            data_list = raw.get("data", [])
        elif isinstance(raw, list):
            data_list = raw
            raw = {"data": raw}    # convert list → dict
        else:
            data_list = []
            raw = {"data": []}

        # ----------------------------------------
        # Add child images + convert URLs
        # ----------------------------------------
        for row in data_list:

            images = frappe.db.get_all(
                "Car Repair Images",
                filters={"parent": row["name"], "parenttype": "Car Repair Request"},
                fields=["image"]
            )

            row["car_repair_images"] = [
                frappe.utils.get_url(i["image"]) for i in images
            ]

            if row.get("odometer_photo"):
                row["odometer_photo"] = frappe.utils.get_url(row["odometer_photo"])

        return raw

    except Exception as e:
        frappe.log_error(title="Get Car Repair Request Error", message=str(e))
        return {
            "status": "error",
            "message": f"Internal Server Error: {str(e)}"
        }


# ====================================================
# UPDATE Car Repair Request
# ====================================================
@frappe.whitelist(allow_guest=False)
def update_car_repair_request(name, data):
   
    """
    Update an existing Car Repair Request.
    - Supports partial updates (only provided fields)
    - Updates child tables (vehicle_concern, car_repair_images)
    """
    import json

    try:
        # Ensure request payload is parsed
        data = json.loads(data) if isinstance(data, str) else data

        # Validate if document exists
        if not frappe.db.exists("Car Repair Request", name):
            return {"status": "error", "message": f"Car Repair Request '{name}' not found"}

        doc = frappe.get_doc("Car Repair Request", name)

        # ✅ Allowed updatable fields
        updatable_fields = [
            "email", "phone", "make", "model", "assign_adviser", "car", "license_plate",
            "chassis_no", "car_manufacturing_year", "odometer_photo", "priority",
            "service_type", "repair_request_date", "driver_name", "driver_mob_no",
            "odometer_value", "fuel_level", "vehicle_pick_up", "customer_signature",
            "remark", "fuel_type"
        ]

        # ✅ Update only provided fields
        for f in updatable_fields:
            if f in data:
                doc.set(f, data[f])

        # ✅ Update child table: Vehicle Concerns
        if "vehicle_concern" in data and isinstance(data["vehicle_concern"], list):
            doc.set("vehicle_concern", [])
            for vc in data["vehicle_concern"]:
                if vc.get("vehicle_concern"):
                    doc.append("vehicle_concern", {"vehicle_concern": vc["vehicle_concern"]})

        # ✅ Update child table: Car Repair Images
        if "car_repair_images" in data and isinstance(data["car_repair_images"], list):
            doc.set("car_repair_images", [])
            for img in data["car_repair_images"]:
                if img.get("image"):
                    doc.append("car_repair_images", {"image": img["image"]})

        # ✅ Save changes
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "status_code":201,
            "message": f"Car Repair Request '{name}' updated successfully",
            "updated_data": doc.as_dict()
        }

    except Exception as e:
        frappe.log_error(title="Update Car Repair Request Error", message=str(e))
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
