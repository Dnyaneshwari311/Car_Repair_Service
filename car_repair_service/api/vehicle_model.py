# import frappe

# @frappe.whitelist(methods=["GET"])
# def get_vehicle_models():
#     """
#     API: Get list of Vehicle Models (Display Name Only)
#     """

#     try:
#         models = frappe.get_all(
#             "Vehicle Model",
#             fields=["model"],
#             order_by="model asc"
#         )

#         return {
#             "status": "success",
#             "message": "Vehicle models fetched successfully",
#             "data": models
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Vehicle Model List API Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }


import frappe

@frappe.whitelist(methods=["GET"])
def get_vehicle_models(
    make=None,
    search=None,
    page=1,
    page_size=10,
    sort_by="model",
    sort_order="asc"
):
    try:
        page = int(page)
        page_size = int(page_size)
        start = (page - 1) * page_size

        filters = []
        if make:
            filters.append(["make", "=", make])

        if search:
            filters.append(["model", "like", f"%{search}%"])

        # Sorting protection
        if sort_by not in ["model"]:
            sort_by = "model"
        if sort_order not in ["asc", "desc"]:
            sort_order = "asc"

        models = frappe.get_all(
            "Vehicle Model",
            filters=filters,
            fields=["model"],
            order_by=f"{sort_by} {sort_order}",
            start=start,
            page_length=page_size
        )

        total = frappe.db.count(
            "Vehicle Model",
            filters=filters
        )

        return {
            "status": "success",
            "message": "Vehicle models fetched successfully",
            "data": models,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Vehicle Model List API Error")
        return {
            "status": "error",
            "message": str(e)
        }

