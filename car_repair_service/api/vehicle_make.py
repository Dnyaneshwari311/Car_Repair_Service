import frappe

@frappe.whitelist(methods=["GET"])
def get_vehicle_makes():
    try:
        makes = frappe.get_all(
            "Vehicle Make",
            fields=[ "make"],
            order_by="make asc"
        )

        return {
            "status": "success",
            "message": "Vehicle makes fetched successfully",
            "data": makes
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Vehicle Make List API Error")
        return {
            "status": "error",
            "message": str(e)
        }
