
# import frappe
# from frappe.utils import get_url
# from frappe import _


# def send_quotation_created_email(doc, method):
#     """Send email when a new quotation is created"""
#     if not doc.contact_email:
#         return

#     # Skip if workflow state is Approved or Rejected
#     if doc.workflow_state in ["Approved", "Rejected"]:
#         return

#     subject = f"New Quotation {doc.name} Created"
#     message_intro = f"A new quotation <b>{doc.name}</b> has been created for your review."

#     send_email_with_pdf(doc, subject, message_intro)


# def send_quotation_update_email(doc, method):
#     """Send email when an existing approved quotation is updated"""
#     if not doc.contact_email:
#         return

#     # Only send email if quotation is already approved
#     if doc.workflow_state != "Approved":
#         return

#     subject = f"Quotation {doc.name} Updated After Approval"
#     message_intro = f"Your approved quotation <b>{doc.name}</b> has been updated. Please review again."

#     send_email_with_pdf(doc, subject, message_intro)


# def send_email_with_pdf(doc, subject, message_intro):
#     """Helper function to send email with PDF attachment"""
#     # Avoid duplicate email with same subject
#     if frappe.db.exists("Communication", {
#         "reference_doctype": "Quotation",
#         "reference_name": doc.name,
#         "subject": subject
#     }):
#         return

#     frappe.db.commit()
#     doc.reload()
#     pdf_file = frappe.get_print("Quotation", doc.name, print_format="Standard", as_pdf=True)
#     filename = f"Quotation-{doc.name}.pdf"

#     approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
#     reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"

#     message = f"""
#     Dear Customer,<br><br>
#     {message_intro}<br><br>
#     <a href="{approve_link}">✅ Approve Quotation</a> | 
#     <a href="{reject_link}">❌ Reject Quotation</a><br><br>
#     Regards,<br>
#     Car Repair Team
#     """

#     frappe.sendmail(
#         recipients=[doc.contact_email],
#         subject=subject,
#         message=message,
#         attachments=[{"fname": filename, "fcontent": pdf_file}]
#     )

#     frappe.logger().info(f"[Quotation Email] Sent for {doc.name}")





# import frappe
# from frappe.utils import get_url
# from frappe import _


# def send_quotation_created_email(doc, method):
#     """Send email when a new quotation is created"""
#     if not doc.contact_email:
#         return

#     # Skip if workflow state is Approved or Rejected
#     if doc.workflow_state in ["Approved", "Rejected"]:
#         return

#     subject = f"New Quotation {doc.name} Created"
#     message_intro = f"A new quotation <b>{doc.name}</b> has been created for your review."

#     send_quotation_email_with_links(doc, subject, message_intro)


# def send_quotation_update_email(doc, method):
#     """Send email when an existing approved quotation is updated"""
#     if not doc.contact_email:
#         return

#     # Only send email if quotation is already approved
#     if doc.workflow_state != "Approved":
#         return

#     subject = f"Quotation {doc.name} Updated After Approval"
#     message_intro = f"Your approved quotation <b>{doc.name}</b> has been updated. Please review again."

#     send_quotation_email_with_links(doc, subject, message_intro)


# def send_quotation_email_with_links(doc, subject, message_intro):
#     """Helper function to send email with approve/reject links (no PDF)"""
#     # Avoid duplicate email with same subject
#     if frappe.db.exists("Communication", {
#         "reference_doctype": "Quotation",
#         "reference_name": doc.name,
#         "subject": subject
#     }):
#         return

#     frappe.db.commit()
#     doc.reload()

#     # Link to ERPNext Quotation form
#     quotation_link = f"{get_url()}/app/quotation/{doc.name}"

#     # Approve/Reject API links
#     approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
#     reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"

#     message = f"""
#     Dear Customer,<br><br>
#     {message_intro}<br><br>
#     You can view the quotation here: <a href="{quotation_link}">Open Quotation</a><br><br>
#     Or take action directly from this email:<br>
#     <a href="{approve_link}" style="padding:10px 15px; background-color:green; color:white; text-decoration:none; border-radius:5px;">✅ Approve Quotation</a>
#     &nbsp;
#     <a href="{reject_link}" style="padding:10px 15px; background-color:red; color:white; text-decoration:none; border-radius:5px;">❌ Reject Quotation</a><br><br>
#     Regards,<br>
#     Car Repair Team
#     """

#     frappe.sendmail(
#         recipients=[doc.contact_email],
#         subject=subject,
#         message=message
#     )

#     frappe.logger().info(f"[Quotation Email] Sent for {doc.name}")






# import frappe
# from frappe.utils import get_url
# from frappe import _

# def send_quotation_created_email(doc, method):
#     """Send email when a new quotation is created"""
#     if not doc.contact_email:
#         return

#     # Skip if workflow state is Approved or Rejected
#     if doc.workflow_state in ["Approved", "Rejected"]:
#         return

#     subject = f"New Quotation {doc.name} Created"
#     send_quotation_email_with_html(doc, subject, new=True)


# def send_quotation_update_email(doc, method):
#     """Send email when an existing approved quotation is updated"""
#     if not doc.contact_email:
#         return

#     if doc.workflow_state != "Approved":
#         return

#     subject = f"Quotation {doc.name} Updated After Approval"
#     send_quotation_email_with_html(doc, subject, new=False)


# def send_quotation_email_with_html(doc, subject, new=True):
#     """Send quotation data in HTML format inside email with approve/reject links"""
    
#     # Avoid duplicate email
#     if frappe.db.exists("Communication", {
#         "reference_doctype": "Quotation",
#         "reference_name": doc.name,
#         "subject": subject
#     }):
#         return

#     doc.reload()

#     # Approve/Reject API links
#     approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
#     reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"
#     quotation_link = f"{get_url()}/app/quotation/{doc.name}"

#     # Generate HTML table for items
#     items_html = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse; width:100%;'>"
#     items_html += "<tr style='background-color:#f0f0f0;'><th>Item</th><th>Description</th><th>Qty</th><th>Rate</th><th>Amount</th></tr>"

#     for item in doc.get("items") or []:
#         items_html += f"<tr>" \
#                       f"<td>{item.item_code or ''}</td>" \
#                       f"<td>{item.description or ''}</td>" \
#                       f"<td>{item.qty or 0}</td>" \
#                       f"<td>{item.rate or 0}</td>" \
#                       f"<td>{item.amount or 0}</td>" \
#                       f"</tr>"

#     items_html += "</table>"

#     message_intro = f"A new quotation <b>{doc.name}</b> has been created for your review." if new else f"Your approved quotation <b>{doc.name}</b> has been updated. Please review again."

#     # Full email HTML
#     message = f"""
#     Dear Customer,<br><br>
#     {message_intro}<br><br>
#     <b>Quotation Details:</b><br>
#     <b>Customer:</b> {doc.customer_name or ''}<br>
#     <b>Date:</b> {doc.transaction_date}<br>
#     <b>Total:</b> {doc.grand_total}<br><br>
#     {items_html}<br>
#     <br>
#     You can view the quotation here: <a href="{quotation_link}">Open Quotation</a><br><br>
#     Or take action directly from this email:<br>
#     <a href="{approve_link}" style="padding:10px 15px; background-color:green; color:white; text-decoration:none; border-radius:5px;">✅ Approve Quotation</a>
#     &nbsp;
#     <a href="{reject_link}" style="padding:10px 15px; background-color:red; color:white; text-decoration:none; border-radius:5px;">❌ Reject Quotation</a><br><br>
#     Regards,<br>
#     Car Repair Team
#     """

#     frappe.sendmail(
#         recipients=[doc.contact_email],
#         subject=subject,
#         message=message
#     )

#     frappe.logger().info(f"[Quotation Email] Sent for {doc.name}")

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
