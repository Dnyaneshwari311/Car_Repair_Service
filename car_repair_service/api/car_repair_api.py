import frappe
from frappe import _
from frappe.utils.data import now

@frappe.whitelist(allow_guest=False)
def create_car_repair(data):
    """
    Create a new Car Repair record
    Expects data as JSON string
    """
    import json
    if isinstance(data, str):
        data = json.loads(data)

    try:
        car_repair_doc = frappe.get_doc({
            "doctype": "Car repair",
            "customer_name": data.get("customer_name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "status": data.get("status", "pending"),
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
            "list_of_damage": data.get("list_of_damage", [])  # child table
        })
        car_repair_doc.insert()
        frappe.db.commit()
        return {"status": "success", "message": "Car Repair created", "data": car_repair_doc.name}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Car Repair Create API Error")
        return {"status": "error", "message": str(e)}
