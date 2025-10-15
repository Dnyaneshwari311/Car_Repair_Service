import frappe
from frappe.utils import now_datetime

# -------------------------------
# Central logging function
# -------------------------------
def log_to_history(doc_type, doc_name, action, remarks=None, user=None):
    """
    Log an action into Car Repair History Log for any DocType.
    """
    user = user or frappe.session.user or "System"
    frappe.get_doc({
        "doctype": "Car Repair History Log",
        "document_type": doc_type,
        "document_name": doc_name,
        "action": action,
        "performed_by": user,
        "timestamp": now_datetime(),
        "remarks": remarks or ""
    }).insert(ignore_permissions=True)
    frappe.db.commit()


# -------------------------------
# Hook handlers for doc_events
# -------------------------------
def log_doc_created(doc, method=None):
    log_to_history(doc.doctype, doc.name, "Created")

def log_doc_updated(doc, method=None):
    log_to_history(doc.doctype, doc.name, "Updated")

def log_doc_submitted(doc, method=None):
    log_to_history(doc.doctype, doc.name, "Submitted")

def log_doc_cancelled(doc, method=None):
    log_to_history(doc.doctype, doc.name, "Cancelled")
