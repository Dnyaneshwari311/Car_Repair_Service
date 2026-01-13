import frappe

@frappe.whitelist(methods=["GET"])
def get_vehicle_models():
    """
    API: Get list of Vehicle Models (Display Name Only)
    """

    try:
        models = frappe.get_all(
            "Vehicle Model",
            fields=["model"],
            order_by="model asc"
        )

        return {
            "status": "success",
            "message": "Vehicle models fetched successfully",
            "data": models
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Vehicle Model List API Error")
        return {
            "status": "error",
            "message": str(e)
        }
