# import frappe
# from frappe.utils import get_url

# def send_quotation_email(doc, method):
#     if doc.contact_email:
#         # Check if email already sent (avoid duplicate mails)
#         already_sent = frappe.db.exists(
#             "Communication",
#             {
#                 "reference_doctype": "Quotation",
#                 "reference_name": doc.name,
#                 "subject": f"Quotation {doc.name} Approval Required"
#             }
#         )

#         if not already_sent:
#             approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
#             reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"

#             message = f"""
#                 Dear Customer,<br><br>
#                 A new quotation <b>{doc.name}</b> has been created for your approval.<br><br>
#                 <a href="{approve_link}">Approve Quotation</a> | 
#                 <a href="{reject_link}">Reject Quotation</a><br><br>
#                 Regards,<br>
#                 Car Repair Team
#             """

#             frappe.sendmail(
#                 recipients=[doc.contact_email],
#                 subject=f"Quotation {doc.name} Approval Required",
#                 message=message
#             )





# import frappe
# from frappe.utils import get_url

# def send_quotation_email(doc, method):
#     if doc.contact_email:
#         # Prevent duplicate emails
#         already_sent = frappe.db.exists(
#             "Communication",
#             {
#                 "reference_doctype": "Quotation",
#                 "reference_name": doc.name,
#                 "subject": f"Quotation {doc.name} Approval Required"
#             }
#         )

#         if not already_sent:
#             approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
#             reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"

#             # Generate PDF
#             pdf_file = frappe.get_print("Quotation", doc.name, print_format="Standard", as_pdf=True)
#             filename = f"Quotation-{doc.name}.pdf"

#             # Build email body
#             message = f"""
#                 Dear Customer,<br><br>
#                 A new quotation <b>{doc.name}</b> has been created for your approval.<br><br>
#                 <a href="{approve_link}">✅ Approve Quotation</a> | 
#                 <a href="{reject_link}">❌ Reject Quotation</a><br><br>
#                 Regards,<br>
#                 Car Repair Team
#             """

#             frappe.sendmail(
#                 recipients=[doc.contact_email],
#                 subject=f"Quotation {doc.name} Approval Required",
#                 message=message,
#                 attachments=[{"fname": filename, "fcontent": pdf_file}]
#             )import frappe


# import frappe
# from frappe.utils import get_url

# def send_quotation_email(doc, method):
#     """
#     Send Quotation email:
#     - On creation (new quotation)
#     - On update (existing quotation)
#     """

#     if not doc.contact_email:
#         return

#     # Skip if Approved or Rejected
#     if doc.workflow_state in ["Approved", "Rejected"]:
#         return

#     # Determine if new or update
#     if method == "after_insert" and doc.is_new():
#         subject = f"New Quotation {doc.name} Awaiting Your Approval"
#         message_intro = f"A new quotation <b>{doc.name}</b> has been created for your approval."
#     elif method == "on_update":
#         subject = f"Updated Quotation {doc.name} Awaiting Your Approval"
#         message_intro = f"Your quotation <b>{doc.name}</b> has been updated. Please review and approve again."
#     else:
#         return  # skip if not new or update

#     # Avoid duplicate emails for same subject
#     if frappe.db.exists("Communication", {
#         "reference_doctype": "Quotation",
#         "reference_name": doc.name,
#         "subject": subject
#     }):
#         return

#     # Ensure latest changes are committed
#     frappe.db.commit()
#     doc.reload()

#     # Generate PDF
#     pdf_file = frappe.get_print("Quotation", doc.name, print_format="Standard", as_pdf=True)
#     filename = f"Quotation-{doc.name}.pdf"

#     # Approval / rejection links
#     approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
#     reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"

#     # Build email message
#     message = f"""
#     Dear Customer,<br><br>
#     {message_intro}<br><br>
#     <a href="{approve_link}">✅ Approve Quotation</a> | 
#     <a href="{reject_link}">❌ Reject Quotation</a><br><br>
#     Regards,<br>
#     Car Repair Team
#     """

#     # Send email
#     frappe.sendmail(
#         recipients=[doc.contact_email],
#         subject=subject,
#         message=message,
#         attachments=[{"fname": filename, "fcontent": pdf_file}]
#     )

#     frappe.logger().info(f"[Quotation Email] Sent via {method} for {doc.name}")






import frappe
from frappe.utils import get_url
from frappe import _


def send_quotation_created_email(doc, method):
    """Send email when a new quotation is created"""
    if not doc.contact_email:
        return

    # Skip if workflow state is Approved or Rejected
    if doc.workflow_state in ["Approved", "Rejected"]:
        return

    subject = f"New Quotation {doc.name} Created"
    message_intro = f"A new quotation <b>{doc.name}</b> has been created for your review."

    send_email_with_pdf(doc, subject, message_intro)


def send_quotation_update_email(doc, method):
    """Send email when an existing approved quotation is updated"""
    if not doc.contact_email:
        return

    # Only send email if quotation is already approved
    if doc.workflow_state != "Approved":
        return

    subject = f"Quotation {doc.name} Updated After Approval"
    message_intro = f"Your approved quotation <b>{doc.name}</b> has been updated. Please review again."

    send_email_with_pdf(doc, subject, message_intro)


def send_email_with_pdf(doc, subject, message_intro):
    """Helper function to send email with PDF attachment"""
    # Avoid duplicate email with same subject
    if frappe.db.exists("Communication", {
        "reference_doctype": "Quotation",
        "reference_name": doc.name,
        "subject": subject
    }):
        return

    frappe.db.commit()
    doc.reload()
    pdf_file = frappe.get_print("Quotation", doc.name, print_format="Standard", as_pdf=True)
    filename = f"Quotation-{doc.name}.pdf"

    approve_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.approve_quotation?quotation={doc.name}"
    reject_link = f"{get_url()}/api/method/car_repair_service.api.quotation_a_r.reject_quotation?quotation={doc.name}"

    message = f"""
    Dear Customer,<br><br>
    {message_intro}<br><br>
    <a href="{approve_link}">✅ Approve Quotation</a> | 
    <a href="{reject_link}">❌ Reject Quotation</a><br><br>
    Regards,<br>
    Car Repair Team
    """

    frappe.sendmail(
        recipients=[doc.contact_email],
        subject=subject,
        message=message,
        attachments=[{"fname": filename, "fcontent": pdf_file}]
    )

    frappe.logger().info(f"[Quotation Email] Sent for {doc.name}")
