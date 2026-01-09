import frappe
from frappe import _
# from car_repair_service.api.utils import ensure_authenticated
from car_repair_service.api.role_validation import validate_api_access



# -----------------------------
# CREATE CAR DIAGNOSIS
# -----------------------------
@frappe.whitelist(allow_guest=False)
def create_car_diagnosis(customer_name=None, customer=None):
    validate_api_access("Car Diagnosis")
    
    """
    Create a Car Diagnosis record:
    - Prefill from last Car Repair Request for this customer
    - Auto-fill Reference No from Car Repair Request
    """
    try:
        if not customer_name and not customer:
            frappe.throw(_("Please provide either customer_name or customer"))

        if customer and not customer_name:
            customer_name = frappe.db.get_value("Customer", customer, "customer_name")

        # Fetch latest Car Repair Request
        last_request = frappe.get_all(
            "Car Repair Request",
            filters={"customer_name": customer_name},
            fields=[
                "name", "car", "car_model", "license_plate", "chassis_no",
                "email", "phone", "repair_request_date", "priority",
                "vehicle_pick_up", "customer_signature","signature"
            ],
            order_by="creation desc",
            limit_page_length=1
        )
        frappe.clear_messages()

        if not last_request:
            return {"status": "not_found", "message": "No Car Repair Request found"}

        req_name = last_request[0]["name"]
        req_doc = frappe.get_doc("Car Repair Request", req_name)

        # Create new Car Diagnosis
        diagnosis = frappe.new_doc("Car Diagnosis")
        diagnosis.customer_name = req_doc.customer_name
        diagnosis.customer = getattr(req_doc, "customer", None)
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
        diagnosis.reference_no = req_doc.name
        diagnosis.signature = req_doc.signature

        # Copy child tables
        if hasattr(req_doc, "vehicle_concern"):
            for vc in req_doc.vehicle_concern:
                diagnosis.append("vehicle_concern", {"vehicle_concern": vc.vehicle_concern})

        if hasattr(req_doc, "car_repair_images"):
            for img in req_doc.car_repair_images:
                if img.image:
                    diagnosis.append("car_repair_images", {"image": img.image})

        diagnosis.insert(ignore_permissions=True)
        frappe.db.commit()

        # return {"status": "success", "name": diagnosis.name}
        frappe.clear_messages()

        return {
            "status": "success",
            "status_code": 200,
            "message": f"Car Diagnosis created from Car Repair Request {req_name}",
            "car_diagnosis_id": diagnosis.name
        }

    except Exception as e:
        frappe.log_error("Error creating Car Diagnosis", str(e))
        return {"status": "error", "message": str(e)}





# -----------------------------
# CAR DIAGNOSIS GET BY ID(GET SINGLE RECORD)
# -----------------------------

from urllib.parse import urljoin


@frappe.whitelist(allow_guest=False)
def car_diagnosis_get(name):
    validate_api_access("Car Diagnosis")
    
    """
    Get Car Diagnosis by name (primary key)
    Returns details with child tables and full URLs for image fields
    """
    if not name:
        frappe.throw("Car Diagnosis name is required")

    fields = [
        "name", "customer_name", "car", "model", "license_plate",
        "chassis_no", "email_id", "phone", "date_of_receipt",
        "priority", "vehicle_pick_up", "reference_no", "customer_signature",
        "creation", "modified"
    ]

    # Fetch main record
    records = frappe.get_all("Car Diagnosis", filters={"name": name}, fields=fields)
    if not records:
        return {}

    diagnosis = records[0]

    # Build full image URL
    host_url = frappe.request.host_url.rstrip("/")
    image_fields = ["customer_signature"]
    for f in image_fields:
        if diagnosis.get(f):
            diagnosis[f] = urljoin(host_url, diagnosis[f])

    # ✅ Use actual child table DocType names (replace with yours)
    vehicle_concerns = frappe.get_all(
        "Vehicle Concern",
        filters={"parent": name},
        fields=["vehicle_concern"]
    )

    car_repair_images = frappe.get_all(
        "Car Repair Images",
        filters={"parent": name},
        fields=["image"]
    )

    for img in car_repair_images:
        if img.get("image"):
            img["image"] = urljoin(host_url, img["image"])

    diagnosis["vehicle_concern"] = vehicle_concerns
    diagnosis["car_repair_images"] = car_repair_images

    return diagnosis






# -----------------------------
# UPDATE CAR DIAGNOSIS
# -----------------------------




@frappe.whitelist(allow_guest=False)
def update_car_diagnosis(name=None, data=None):
    validate_api_access("Car Diagnosis")

    """
    Update an existing Car Diagnosis record.
    - Updates main fields and Car Diagnosis Detail child table.
    - Supports partial updates.
    """

    import json

    try:
        # ✅ Parse data safely
        if not data:
            if frappe.request and frappe.request.data:
                try:
                    data = json.loads(frappe.request.data)
                except Exception:
                    data = frappe.form_dict
            else:
                data = frappe.form_dict

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                data = {}

        # ✅ Allow name to come from body if not provided
        if not name:
            name = data.get("name")

        if not name:
            return {"status": "error", "message": "Car Diagnosis name is required"}

        # ✅ Ensure record exists
        if not frappe.db.exists("Car Diagnosis", name):
            return {"status": "error", "message": f"Car Diagnosis '{name}' not found"}

        doc = frappe.get_doc("Car Diagnosis", name)

        # ✅ Allowed updatable fields
        updatable_fields = [
            "customer_name", "car", "model", "license_plate",
            "chassis_no", "phone", "email", "priority", "reference_no",
            "diagnosis_date", "remark", "customer_signature",
            "estimated_delivery_date", "estimated_delivery_time"
        ]

        # ✅ Update only provided fields
        for f in updatable_fields:
            if f in data:
                doc.set(f, data[f])

        # ✅ Update Car Diagnosis Detail child table
        if "car_diagnosis_detail" in data and isinstance(data["car_diagnosis_detail"], list):
            doc.set("car_diagnosis_detail", [])  # Clear existing rows

            for d in data["car_diagnosis_detail"]:
                if d.get("damage_description") or d.get("part_required"):
                    qty = d.get("quantity") or 0
                    cost = d.get("estimated_cost") or 0

                    amount = d.get("amount")
                    if amount is None:
                        amount = qty * cost  # ✅ Auto-calculate amount

                    doc.append("car_diagnosis_detail", {
                        "damage_description": d.get("damage_description"),
                        "part_required": d.get("part_required"),
                        "quantity": qty,
                        "estimated_cost": cost,
                        "amount": amount
                    })

        # ✅ Save document
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.clear_messages()
        return {
            "status": "success",
            "status_code": 200,
            "message": f"Car Diagnosis '{name}' updated successfully",
            "car_diagnosis_id": doc.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Car Diagnosis Error")
        return {"status": "error", "message": str(e)}










# -----------------------------
# DELETE CAR DIAGNOSIS
# -----------------------------
@frappe.whitelist(allow_guest=False)
def delete_car_diagnosis(name):
    
    """
    Delete a Car Diagnosis record.
    """
    try:
        if not frappe.db.exists("Car Diagnosis", name):
            return {"status": "not_found", "message": f"Car Diagnosis {name} not found"}

        frappe.delete_doc("Car Diagnosis", name, ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success",
                "status_code":200,
                "message": f"Car Diagnosis {name} deleted successfully"}

    except Exception as e:
        frappe.log_error("Error deleting Car Diagnosis", str(e))
        return {"status": "error", "message": str(e)}







# -----------------------------
# LIST CAR DIAGNOSIS (WITH PAGINATION, SEARCH, SORTING)
# -----------------------------







from urllib.parse import urljoin

@frappe.whitelist(allow_guest=False)
def car_diagnosis_list(page=1, page_size=10, search=None, sort_by="creation", sort_order="desc", is_pagination=False, **kwargs):
    validate_api_access("Car Diagnosis")
    
    try:
        is_pagination = frappe.utils.sbool(is_pagination)
        base_url = frappe.request.host_url.rstrip("/") + frappe.request.path
        del kwargs["cmd"]

        # 🔹 searchable fields
        search_fields = ["customer_name", "license_plate", "car", "reference_no"]

        # 🔹 fields to return from parent
        update_fields = [
            "name", "customer_name", "license_plate", "phone", "email_id", "priority",
            "reference_no", "estimated_delivery_date", "estimated_delivery_time",
            "creation", "modified", "customer_signature"
        ]

        # 🔹 filters
        filters = {}
        if kwargs.get("priority"):
            filters["priority"] = kwargs.get("priority")
        if kwargs.get("vehicle_pick_up"):
            filters["vehicle_pick_up"] = kwargs.get("vehicle_pick_up")

        # 🔹 search condition
        search_condition = ""
        if search:
            search_condition = " OR ".join(
                [f"{field} LIKE %(search)s" for field in search_fields]
            )

        # 🔹 build main query
        query = f"""
            SELECT {", ".join(update_fields)}
            FROM `tabCar Diagnosis`
            WHERE 1=1
        """

        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    query += f" AND `{key}` IN %({key})s"
                else:
                    query += f" AND `{key}`=%({key})s"

        if search_condition:
            query += f" AND ({search_condition})"

        query += f" ORDER BY `{sort_by}` {sort_order.upper()}"

        # 🔹 pagination
        if is_pagination:
            offset = (int(page) - 1) * int(page_size)
            query += f" LIMIT {offset}, {int(page_size)}"

        # 🔹 execute query
        values = filters.copy()
        if search:
            values["search"] = f"%{search}%"

        data = frappe.db.sql(query, values, as_dict=True)

        host_url = frappe.request.host_url.rstrip("/")

        image_fields = ["customer_signature"]

        # ---------------------------------------------------------------------
        # 🔹 ATTACH CHILD TABLE DATA
        # ---------------------------------------------------------------------
        for d in data:
            name = d.get("name")

            # 1️⃣ Vehicle Concern Table
            d["vehicle_concern"] = frappe.db.get_all(
                "Vehicle Concern",
                filters={"parent": name},
                fields=["vehicle_concern"]
            )

            # 2️⃣ Car Repair Images Table
            images = frappe.db.get_all(
                "Car Repair Images",
                filters={"parent": name},
                fields=["image"]
            )
            for img in images:
                if img.get("image"):
                    img["image"] = urljoin(host_url, img["image"])
            d["car_repair_images"] = images

            # # 3️⃣ Car Diagnosis Detail Table (UPDATED FIELDS)
            # diagnosis_details = frappe.db.get_all(
            #     "Car Repair Damage",
            #     filters={"parent": name},
            #     fields=[
            #         "damage_description",
            #         "part_required",
            #         "quantity",
            #         "estimated_cost",
            #         "assigned_to"
            #     ]
            # )
            # d["diagnosis_details"] = diagnosis_details
            
            
                        
            # 3️⃣ Car Diagnosis Detail Table (WITH AMOUNT)
            diagnosis_details = frappe.db.get_all(
                "Car Repair Damage",
                filters={"parent": name},
                fields=[
                    "damage_description",
                    "part_required",
                    "quantity",
                    "estimated_cost",
                    "amount",
                    "assigned_to"
                ]
            )

            # Safety fallback (if old records exist)
            for row in diagnosis_details:
                qty = frappe.utils.flt(row.get("quantity"))
                cost = frappe.utils.flt(row.get("estimated_cost"))
                if not row.get("amount"):
                    row["amount"] = qty * cost if qty > 0 and cost > 0 else 0

            d["diagnosis_details"] = diagnosis_details


            # 4️⃣ full URL for parent images
            for f in image_fields:
                if d.get(f):
                    d[f] = urljoin(host_url, d[f])

        # 🔹 total count
        total_count = frappe.db.count("Car Diagnosis", filters=filters)

        # 🔹 pagination metadata
        meta = {}
        if is_pagination:
            meta = {
                "page": int(page),
                "page_size": int(page_size),
                "total_records": total_count,
                "total_pages": (total_count // int(page_size)) + (1 if total_count % int(page_size) else 0),
                "next_page": int(page) + 1 if total_count > int(page) * int(page_size) else None,
                "previous_page": int(page) - 1 if int(page) > 1 else None,
                "base_url": base_url
            }

        return {
            "status": "success",
            "status_code": 200,
            "data": data,
            "pagination": meta if is_pagination else None
        }

    except Exception as e:
        frappe.log_error("Car Diagnosis List Error", frappe.get_traceback())
        return {"status": "error", "message": str(e)}
