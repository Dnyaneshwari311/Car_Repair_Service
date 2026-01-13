# import frappe

# @frappe.whitelist(methods=["GET"])
# def get_vehicle_makes():
#     try:
#         makes = frappe.get_all(
#             "Vehicle Make",
#             fields=[ "make"],
#             order_by="make asc"
#         )

#         return {
#             "status": "success",
#             "message": "Vehicle makes fetched successfully",
#             "data": makes
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Vehicle Make List API Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }

import frappe

@frappe.whitelist(methods=["GET"])
def get_vehicle_makes(
    search=None,
    page=1,
    page_size=10,
    sort_by="make",
    sort_order="asc"
):
    """
    API: Vehicle Make List
    """

    try:
        page = int(page)
        page_size = int(page_size)
        start = (page - 1) * page_size

        filters = []

        if search:
            filters.append(["make", "like", f"%{search}%"])

        # Safety: allow sorting only on valid fields
        if sort_by not in ["make"]:
            sort_by = "make"

        if sort_order not in ["asc", "desc"]:
            sort_order = "asc"

        makes = frappe.get_all(
            "Vehicle Make",
            filters=filters,
            fields=["make"],
            order_by=f"{sort_by} {sort_order}",
            start=start,
            page_length=page_size
        )

        total = frappe.db.count(
            "Vehicle Make",
            filters=filters
        )

        return {
            "status": "success",
            "message": "Vehicle makes fetched successfully",
            "data": makes,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Vehicle Make List API Error")
        return {
            "status": "error",
            "message": str(e)
        }
