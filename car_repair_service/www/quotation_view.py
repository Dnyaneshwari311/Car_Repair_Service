# quotation_view.py
import frappe
from frappe.utils import get_url

def get_context(context):
    """
    context is passed to the Jinja template (quotation_view.html).
    URL: /quotation_view?name=QUO-0001
    """
    quotation_name = frappe.form_dict.get("name")
    token = frappe.form_dict.get("token")  # optional security token

    if not quotation_name:
        frappe.throw("Missing quotation id")

    # optional: token validation (implement if you use tokens)
    # if token and not validate_token(quotation_name, token):
    #     frappe.throw("Invalid or expired token")

    try:
        q = frappe.get_doc("Quotation", quotation_name)
    except Exception:
        frappe.throw("Quotation not found")

    # prepare items list for template
    items = []
    for r in q.get("items") or []:
        items.append({
            "item_name": r.item_name or r.item_code,
            "description": r.description,
            "qty": r.qty,
            "rate": r.rate,
            "amount": r.amount
        })

    # approval/reject endpoints (use your whitelisted methods)
    approve_url = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={q.name}"
    reject_url = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={q.name}"

    # If you use tokens, append &token={token} to approve/reject links.

    context.quotation = q
    context.items = items
    context.approve_url = approve_url
    context.reject_url = reject_url
    context.page_title = f"Quotation {q.name}"
    return context
