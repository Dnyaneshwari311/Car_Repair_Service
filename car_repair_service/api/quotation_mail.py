
import frappe
from frappe.utils import get_url

def send_quotation_email_with_links(doc, subject_prefix="Quotation"):
    """
    Send email to customer with direct link to the custom quotation page.
    Only "Open Quotation" button in email.
    """

    if not doc.contact_email:
        return

    # Skip sending creation email if workflow already Approved/Rejected
    if subject_prefix == "New Quotation" and doc.workflow_state in ["Approved", "Rejected"]:
        return

    # For updated email, send only if workflow_state is Approved
    if subject_prefix == "Updated Quotation" and doc.workflow_state != "Approved":
        return

    # Avoid duplicate email with same subject
    subject = f"{subject_prefix} {doc.name}"
    if frappe.db.exists("Communication", {
        "reference_doctype": "Quotation",
        "reference_name": doc.name,
        "subject": subject
    }):
        return

    frappe.db.commit()
    doc.reload()

    quotation_link = f"{get_url()}/quotation_view?name={doc.name}"

    message_intro = f"Quotation <b>{doc.name}</b> has been created for your review." \
        if subject_prefix=="New Quotation" else \
        f"Your approved quotation <b>{doc.name}</b> has been updated. Please review again."

    message = f"""
    Dear Customer,<br><br>
    {message_intro}<br><br>
    
    You can view the quotation here:<br>
    <a href="{quotation_link}" style="display:inline-block; padding:10px 14px; background:#1976d2; color:#fff; text-decoration:none; border-radius:6px;">
        Open Quotation
    </a><br><br>
    
    Regards,<br>
    Car Repair Team
    """

    frappe.sendmail(
        recipients=[doc.contact_email],
        subject=subject,
        message=message
    )

    frappe.logger().info(f"[Quotation Email] Sent for {doc.name}")


# ---------------------------
# Wrapper functions for old names (used in hooks)
# ---------------------------

def send_quotation_created_email(doc, method):
    """Send email after quotation is created"""
    send_quotation_email_with_links(doc, subject_prefix="New Quotation")

def send_quotation_update_email(doc, method):
    """Send email after approved quotation is updated"""
    send_quotation_email_with_links(doc, subject_prefix="Updated Quotation")
