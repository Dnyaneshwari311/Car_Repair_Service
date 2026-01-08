import frappe
from frappe import _
from frappe.utils.data import now
from car_repair_service.api.role_validation import validate_api_access


@frappe.whitelist(allow_guest=False)
def create_car_repair(data):
    import json
    if isinstance(data, str):
        data = json.loads(data)
    validate_api_access("Car repair")
    try:
        allowed_status = ["Pending", "In Progress", "Completed"]

        # Normalize status
        status = data.get("status", "Pending")
        status = status.title()

        if status.lower() == "in progress":
            status = "In Progress"

        if status not in allowed_status:
            return {"status": "error",
                    "message": f"Invalid status '{status}'. Allowed: {allowed_status}"}

        car_repair_doc = frappe.get_doc({
            "doctype": "Car repair",
            "customer_name": data.get("customer_name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "status": status,
            "reference_number": data.get("reference_number"),
            "car_diagnosis": data.get("car_diagnosis"),
            "quotation": data.get("quotation"),
            "estimated_delivery_date": data.get("estimated_delivery_date"),
            "estimated_delivery_time": data.get("estimated_delivery_time"),
            "car": data.get("car"),
            "license_plate": data.get("license_plate"),
            "model": data.get("model"),
            "car_manufacturing_year": data.get("car_manufacturing_year"),
            "vehicle_pick_up": data.get("vehicle_pick_up"),
            "customer_signature": data.get("customer_signature"),
            "remark": data.get("remark"),
            "list_of_damage": data.get("list_of_damage", [])
        })

        car_repair_doc.insert()
        frappe.db.commit()

        return {"status": "success",
                "message": "Car Repair created",
                "data": car_repair_doc.name}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Car Repair Create API Error")
        return {"status": "error", "message": str(e)}








@frappe.whitelist(allow_guest=False)
def delete_car_repair(name):
    try:
        frappe.delete_doc("Car repair", name, force=1)
        frappe.db.commit()

        return {"status": "success", "message": "Car Repair Deleted"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Car Repair Delete API Error")
        return {"status": "error", "message": str(e)}






# @frappe.whitelist(allow_guest=False)
# def update_car_repair():
#     import json
    
#     name = frappe.form_dict.get("name")
#     data = frappe.form_dict.get("data")

#     if not name:
#         return {"status": "error", "message": "Missing 'name' parameter"}

#     if not data:
#         return {"status": "error", "message": "Missing 'data' parameter"}

#     if isinstance(data, str):
#         data = json.loads(data)

#     try:
#         doc = frappe.get_doc("Car repair", name)

#         # helper: check if row contains at least one valid field
#         def is_valid_row(row):
#             if not row or not isinstance(row, dict):
#                 return False

#             # row is {} → skip
#             if len(row.keys()) == 0:
#                 return False

#             # check if row contains at least one non-empty value
#             for field in ["damage_description", "part_required", "status", "quantity", "estimated_cost", "assigned_to"]:
#                 if row.get(field) not in [None, "", 0]:
#                     return True

#             return False  # all empty → skip

#         # 1. Status override
#         if "status" in data:
#             doc._api_status_override = True
#             doc.status = data.get("status")

#         # 2. Update simple parent fields
#         for field, value in data.items():
#             if field not in ["status", "list_of_damage"]:
#                 doc.set(field, value)

#         # 3. Update/Add child rows
#         if "list_of_damage" in data:

#             existing_rows = {row.name: row for row in doc.list_of_damage}

#             for row in data["list_of_damage"]:
#                 # 🔥 SUPER IMPORTANT: skip invalid/empty row
#                 if not is_valid_row(row):
#                     continue

#                 row_name = row.get("name")

#                 if row_name and row_name in existing_rows:
#                     # update row
#                     child = existing_rows[row_name]
#                     child.damage_description = row.get("damage_description")
#                     child.part_required = row.get("part_required")
#                     child.status = row.get("status")
#                     child.quantity = row.get("quantity")
#                     child.estimated_cost = row.get("estimated_cost")
#                     child.assigned_to = row.get("assigned_to")
#                 else:
#                     # add new row
#                     doc.append("list_of_damage", {
#                         "damage_description": row.get("damage_description"),
#                         "part_required": row.get("part_required"),
#                         "status": row.get("status"),
#                         "quantity": row.get("quantity"),
#                         "estimated_cost": row.get("estimated_cost"),
#                         "assigned_to": row.get("assigned_to")
#                     })

#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Car Repair Updated",
#             "data": doc.name
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Car Repair Update API Error")
#         return {"status": "error", "message": str(e)}





# @frappe.whitelist(allow_guest=False)
# def update_car_repair():
#     validate_api_access("Car repair")
#     data = frappe.form_dict.get("data")

#     if not data:
#         return {"status": "error", "message": "Missing 'data' parameter"}

#     if isinstance(data, str):
#         data = json.loads(data)

#     # Get name from data
#     name = data.get("name")
#     if not name:
#         return {"status": "error", "message": "Missing 'name' parameter in data"}

#     try:
#         doc = frappe.get_doc("Car repair", name)

#         # helper: check if row contains at least one valid field
#         def is_valid_row(row):
#             if not row or not isinstance(row, dict):
#                 return False
#             if len(row.keys()) == 0:
#                 return False
#             for field in [
#                 "damage_description",
#                 "part_required",
#                 "status",
#                 "quantity",
#                 "estimated_cost",
#                 "assigned_to",
#                 "amount"
#             ]:
#                 if row.get(field) not in [None, "", 0]:
#                     return True
#             return False

#         # 1. Status override
#         if "status" in data:
#             doc._api_status_override = True
#             doc.status = data.get("status")

#         # 2. Update simple parent fields
#         for field, value in data.items():
#             if field not in ["status", "list_of_damage", "name"]:
#                 doc.set(field, value)

#         # 3. Update/Add child rows
#         if "list_of_damage" in data:
#             existing_rows = {row.name: row for row in doc.list_of_damage}

#             for row in data["list_of_damage"]:
#                 if not is_valid_row(row):
#                     continue

#                 # Auto-calculate amount if not provided
#                 qty = row.get("quantity") or 0
#                 cost = row.get("estimated_cost") or 0
#                 amount = row.get("amount")
#                 if amount in [None, "", 0]:
#                     amount = qty * cost

#                 row_name = row.get("name")
#                 if row_name and row_name in existing_rows:
#                     # Update existing row
#                     child = existing_rows[row_name]
#                     child.damage_description = row.get("damage_description")
#                     child.part_required = row.get("part_required")
#                     child.status = row.get("status")
#                     child.quantity = qty
#                     child.estimated_cost = cost
#                     child.assigned_to = row.get("assigned_to")
#                     child.amount = amount
#                 else:
#                     # Append new row
#                     doc.append("list_of_damage", {
#                         "damage_description": row.get("damage_description"),
#                         "part_required": row.get("part_required"),
#                         "status": row.get("status"),
#                         "quantity": qty,
#                         "estimated_cost": cost,
#                         "assigned_to": row.get("assigned_to"),
#                         "amount": amount
#                     })

#         # Save the document
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code":200,
#             "message": "Car Repair Updated",
#             "data": doc.name
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Car Repair Update API Error")
#         return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=False)
def update_car_repair():
    validate_api_access("Car repair")
    data = frappe.form_dict.get("data")

    if not data:
        return {"status": "error", "message": "Missing 'data' parameter"}

    if isinstance(data, str):
        data = json.loads(data)

    name = data.get("name")
    if not name:
        return {"status": "error", "message": "Missing 'name' parameter in data"}

    try:
        doc = frappe.get_doc("Car repair", name)

        UPDATE_FIELDS = [
            "damage_description",
            "part_required",
            "status",
            "quantity",
            "estimated_cost",
            "amount"
        ]

        def is_assigned_only(row):
            # Assigned_to exists and no other fields have values
            if not row.get("assigned_to"):
                return False
            for f in UPDATE_FIELDS:
                if row.get(f) not in [None, "", 0]:
                    return False
            return True

        # Update parent fields
        for field, value in data.items():
            if field not in ["status", "list_of_damage", "name"]:
                doc.set(field, value)

        # Child table logic
        if "list_of_damage" in data:
            existing_rows = {row.name: row for row in doc.list_of_damage if row.name}

            for row in data["list_of_damage"]:

                qty = row.get("quantity") or 0
                cost = row.get("estimated_cost") or 0
                amount = row.get("amount") or (qty * cost)

                row_name = row.get("name")

                # --- Assigned_to only update ---
                if is_assigned_only(row):
                    if row_name and row_name in existing_rows:
                        child = existing_rows[row_name]
                        # Update the assigned_to field
                        child.assigned_to = row.get("assigned_to")
                        frappe.msgprint(f"Assigned_to updated for row: {row_name}")  # Optional debug
                    else:
                        frappe.log_error(f"Assigned_to update skipped, row_name missing or invalid: {row}", "Car Repair API")
                    continue

                # --- Full data: always create new row ---
                doc.append("list_of_damage", {
                    "damage_description": row.get("damage_description"),
                    "part_required": row.get("part_required"),
                    "status": row.get("status"),
                    "quantity": qty,
                    "estimated_cost": cost,
                    "assigned_to": row.get("assigned_to"),
                    "amount": amount
                })

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_messages()
        return {
            "status": "success",
            "status_code": 200,
            "message": "Car Repair Updated",
            # "data": doc.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Car Repair Update API Error")
        return {"status": "error", "message": str(e)}






# @frappe.whitelist(allow_guest=False)
# def list_car_repair():
#     try:
#         page = int(frappe.form_dict.get("page", 1))
#         limit = int(frappe.form_dict.get("limit", 20))
#         status = frappe.form_dict.get("status")
#         customer_name = frappe.form_dict.get("customer_name")
#         reference_number = frappe.form_dict.get("reference_number")
#         search = frappe.form_dict.get("search")
#         sort_by = frappe.form_dict.get("sort_by", "creation")
#         sort_order = frappe.form_dict.get("sort_order", "desc")

#         start = (page - 1) * limit

#         filters = {}

#         if status:
#             filters["status"] = status

#         if customer_name:
#             filters["customer_name"] = ["like", f"%{customer_name}%"]

#         if reference_number:
#             filters["reference_number"] = ["like", f"%{reference_number}%"]

#         # Apply search to multiple fields
#         search_filters = []
#         if search:
#             search_filters = [
#                 ["Car repair", "customer_name", "like", f"%{search}%"],
#                 ["Car repair", "phone", "like", f"%{search}%"],
#                 ["Car repair", "email", "like", f"%{search}%"],
#                 ["Car repair", "car", "like", f"%{search}%"],
#                 ["Car repair", "reference_number", "like", f"%{search}%"]
#             ]

#         # -------------------------
#         # Query documents
#         # -------------------------
#         car_repairs = frappe.db.get_list(
#             "Car repair",
#             filters=filters,
#             fields=[
#                 "name", "customer_name", "phone", "email", "status",
#                 "reference_number", "car", "license_plate",
#                 "model", "estimated_delivery_date", "estimated_delivery_time",
#                 "creation"
#             ],
#             or_filters=search_filters,
#             order_by=f"{sort_by} {sort_order}",
#             start=start,
#             page_length=limit
#         )

#         # -------------------------
#         # Fetch child table rows
#         # -------------------------
#         for item in car_repairs:
#             item["list_of_damage"] = frappe.get_all(
#                 "Car Repair Damage",
#                 filters={"parent": item["name"]},
#                 fields=[
#                     "name",
#                     "damage_description",
#                     "part_required",
#                     "status",
#                     "quantity",
#                     "estimated_cost",
#                     "assigned_to"
#                 ]
#             )

#         total_count = frappe.db.count("Car repair", filters)

#         return {
#             "status": "success",
#             "message": "Car Repair List",
#             "page": page,
#             "limit": limit,
#             "total": total_count,
#             "data": car_repairs
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Car Repair List API Error")
#         return {"status": "error", "message": str(e)}







@frappe.whitelist(allow_guest=False)
def list_car_repairs(page=1, page_size=20, status=None, search=None, sort_by="creation", sort_order="desc"):
    validate_api_access("Car repair")
    try:
        page = int(page)
        page_size = int(page_size)

        # -------------------------
        # VALIDATE SORT
        # -------------------------
        allowed_sort_fields = [
            "creation", "modified", "customer_name", "status"
        ]
        if sort_by not in allowed_sort_fields:
            sort_by = "creation"

        sort_order = "DESC" if sort_order.lower() == "desc" else "ASC"
        start = (page - 1) * page_size

        # -------------------------
        # WHERE CONDITIONS
        # -------------------------
        conditions = []
        values = {}

        if status:
            conditions.append("status = %(status)s")
            values["status"] = status

        if search:
            conditions.append("""
                (
                    name LIKE %(search)s OR
                    customer_name LIKE %(search)s OR
                    phone LIKE %(search)s OR
                    email LIKE %(search)s OR
                    car LIKE %(search)s
                )
            """)
            values["search"] = f"%{search}%"

        where_clause = " AND ".join(conditions)
        if where_clause:
            where_clause = "WHERE " + where_clause

        # -------------------------
        # DATA QUERY
        # -------------------------
        data = frappe.db.sql(f"""
            SELECT
                name,
                customer_name,
                phone,
                email,
                status,
                car,
                license_plate,
                model,
                estimated_delivery_date,
                estimated_delivery_time,
                creation
            FROM `tabCar repair`
            {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %(start)s, %(page_size)s
        """, {
            **values,
            "start": start,
            "page_size": page_size
        }, as_dict=True)

        # -------------------------
        # CHILD TABLE
        # -------------------------
        for row in data:
            row["list_of_damage"] = frappe.get_all(
                "Car Repair Damage",
                filters={"parent": row["name"]},
                fields=[
                    "name",
                    "damage_description",
                    "part_required",
                    "status",
                    "quantity",
                    "estimated_cost",
                    "assigned_to"
                ]
            )

        # -------------------------
        # COUNT QUERY
        # -------------------------
        total_records = frappe.db.sql(f"""
            SELECT COUNT(*)
            FROM `tabCar repair`
            {where_clause}
        """, values)[0][0]

        total_pages = (total_records + page_size - 1) // page_size

        return {
            "status": "success",
            "filters": {
                "status": status or "All",
                "search": search or ""
            },
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages
            },
            "data": data
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Car Repair List API Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=False)
def get_car_repair_by_id(name):
    validate_api_access("Car repair")
    try:
        if not name:
            return {
                "status": "error",
                "message": "Missing 'name' parameter"
            }

        # Check existence
        if not frappe.db.exists("Car repair", name):
            return {
                "status": "error",
                "message": f"Car Repair '{name}' not found"
            }

        doc = frappe.get_doc("Car repair", name)

        # Parent data
        data = {
            "name": doc.name,
            "customer_name": doc.customer_name,
            "phone": doc.phone,
            "email": doc.email,
            "status": doc.status,
            # "reference_number": doc.reference_number,
            "car_diagnosis": doc.car_diagnosis,
            "quotation": doc.quotation,
            "estimated_delivery_date": doc.estimated_delivery_date,
            "estimated_delivery_time": doc.estimated_delivery_time,
            "car": doc.car,
            "license_plate": doc.license_plate,
            "model": doc.model,
            "car_manufacturing_year": doc.car_manufacturing_year,
            "vehicle_pick_up": doc.vehicle_pick_up,
            "customer_signature": doc.customer_signature,
            "remark": doc.remark,
            "creation": doc.creation,
            "modified": doc.modified
        }

        # Child table
        data["list_of_damage"] = []
        for row in doc.list_of_damage:
            data["list_of_damage"].append({
                "name": row.name,
                "damage_description": row.damage_description,
                "part_required": row.part_required,
                "status": row.status,
                "quantity": row.quantity,
                "estimated_cost": row.estimated_cost,
                "assigned_to": row.assigned_to
            })

        return {
            "status": "success",
            "message": "Car Repair Details",
            "data": data
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Car Repair Get By ID API Error")
        return {
            "status": "error",
            "message": str(e)
        }
