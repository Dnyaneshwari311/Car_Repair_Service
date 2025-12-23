import frappe

@frappe.whitelist(methods=["POST"])
def create_item(data=None):
    """
    Create a new Item
    """
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        # Create Item doc
        item = frappe.get_doc({
            "doctype": "Item",
            **data
        })
        item.insert()  # insert, but not submit
        frappe.db.commit()
        return {"status": "success", "message": f"Item {item.name} created", "data": item.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}





@frappe.whitelist()
def list_items(
    page=1,
    page_size=20,
    sort_by="modified",
    sort_order="desc",
    search=None,
    item_group=None,
    is_stock_item=None
):
    """
    List Items with optional filters, search, and pagination
    """

    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # -------------------------
    # Build filters
    # -------------------------
    filters = {}
    if item_group:
        filters["item_group"] = item_group
    if is_stock_item is not None:
        filters["is_stock_item"] = 1 if str(is_stock_item).lower() in ("1", "true") else 0

    # -------------------------
    # Search across item_code and item_name
    # -------------------------
    or_filters = []
    if search:
        or_filters.append(["item_code", "like", f"%{search}%"])
        or_filters.append(["item_name", "like", f"%{search}%"])

    # -------------------------
    # Get items
    # -------------------------
    items = frappe.get_all(
        "Item",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=["name", "item_code", "item_name", "item_group", "is_stock_item", "modified"],
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # Total count
    total = frappe.db.count("Item", filters=filters)

    return {
        "status": "success",
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
