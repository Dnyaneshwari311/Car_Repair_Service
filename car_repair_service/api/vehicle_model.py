import frappe
from frappe import _

@frappe.whitelist(methods=["GET"])
def get_vehicle_models(
    make=None,
    search=None,
    page=1,
    page_size=10,
    sort_by="model",
    sort_order="asc"
):
    """
    Fetch Vehicle Models with optional Make filter.
    Supports filtering by:
    - Vehicle Make.name (ID)
    - Vehicle Make.make (label)
    """

    try:
        # -----------------------------
        # PAGINATION
        # -----------------------------
        page = int(page)
        page_size = int(page_size)
        start = (page - 1) * page_size

        # -----------------------------
        # CONDITIONS
        # -----------------------------
        conditions = []
        values = {}

        # -----------------------------
        # MAKE FILTER (FIXED)
        # -----------------------------
        if make:
            conditions.append("""
                (
                    vm.make = %(make)s
                    OR vm.make IN (
                        SELECT mk.name
                        FROM `tabVehicle Make` mk
                        WHERE mk.make = %(make)s
                    )
                )
            """)
            values["make"] = make

        # -----------------------------
        # SEARCH FILTER
        # -----------------------------
        if search:
            conditions.append("vm.model LIKE %(search)s")
            values["search"] = f"%{search}%"

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # -----------------------------
        # SORT PROTECTION
        # -----------------------------
        if sort_by not in ["model"]:
            sort_by = "model"

        if sort_order.lower() not in ["asc", "desc"]:
            sort_order = "asc"

        # -----------------------------
        # MAIN DATA QUERY
        # -----------------------------
        data = frappe.db.sql(
            f"""
            SELECT
                vm.name,
                vm.model,
                vm.make AS make_id,
                mk.make AS make_name
            FROM `tabVehicle Model` vm
            LEFT JOIN `tabVehicle Make` mk
                ON mk.name = vm.make
            {where_clause}
            ORDER BY vm.{sort_by} {sort_order}
            LIMIT %(start)s, %(page_size)s
            """,
            {
                **values,
                "start": start,
                "page_size": page_size
            },
            as_dict=True
        )

        # -----------------------------
        # TOTAL COUNT
        # -----------------------------
        total = frappe.db.sql(
            f"""
            SELECT COUNT(*)
            FROM `tabVehicle Model` vm
            LEFT JOIN `tabVehicle Make` mk
                ON mk.name = vm.make
            {where_clause}
            """,
            values
        )[0][0]

        # -----------------------------
        # RESPONSE
        # -----------------------------
        return {
            "status": "success",
            "message": "Vehicle models fetched successfully" if data else "No vehicle models found",
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Vehicle Model API Error")
        return {
            "status": "error",
            "message": str(e)
        }
