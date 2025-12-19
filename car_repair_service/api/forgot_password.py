import frappe
import random
import string
from frappe.utils import now_datetime, add_to_date
from car_repair_service.api.utils import api_error


# Step 1: Send OTP
@frappe.whitelist(allow_guest=True, methods=["POST"])
def send_forgot_password_otp(email):
    user = frappe.db.get_value("User", {"email": email}, "name")
    if not user:
        return api_error("User with this email does not exist.")

    # Generate 6 digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    expiry_time = add_to_date(now_datetime(), minutes=10)

    # Store OTP & expiry
    frappe.db.set_value("User", user, {
        "otp": otp,
        "otp_expire_time": expiry_time
    })

    try:
        frappe.sendmail(
            recipients=[email],
            subject="Password Reset OTP",
            message=f"Your OTP for password reset is {otp}. It will expire in 10 minutes."
        )
    except Exception as e:
        frappe.log_error(message=str(e), title="OTP Email Error")

    return {
        "status": "success",
        "status_code": 201,
        "message": "OTP sent to your email."
    }


# # Step 2: Verify OTP
# @frappe.whitelist(allow_guest=True, methods=["POST"])
# def verify_forgot_password_otp(email, otp):
#     stored_otp, expiry_time = frappe.db.get_value(
#         "User", {"email": email}, ["otp", "otp_expire_time"]
#     )

#     if not stored_otp:
#         return api_error("No OTP found. Please request OTP again.")

#     if now_datetime() > expiry_time:
#         return api_error("OTP expired. Please request OTP again.")

#     if otp != stored_otp:
#         return api_error("Invalid OTP.")

#     return {
#         "status": "success",
#         "status_code": 200,
#         "msg": "OTP verified successfully."
#     }
@frappe.whitelist(allow_guest=True, methods=["POST"])
def verify_forgot_password_otp(email, otp):
    if not email or not otp:
        return api_error("Email and OTP are required.")

    stored_otp, expiry_time = frappe.db.get_value(
        "User", {"email": email}, ["otp", "otp_expire_time"]
    )

    if not stored_otp:
        return api_error("No OTP found. Please request OTP again.")

    if not expiry_time:
        return api_error("OTP expired. Please request OTP again.")

    if now_datetime() > expiry_time:
        return api_error("OTP expired. Please request OTP again.")

    # ✅ FIX: convert both to string
    if str(otp).strip() != str(stored_otp).strip():
        return api_error("Invalid OTP.")

    return {
        "status": "success",
        "status_code": 200,
        "message": "OTP verified successfully."
    }


# Step 3: Reset password using OTP
@frappe.whitelist(allow_guest=True, methods=["POST"])
def reset_password_with_otp(email, otp, new_password, confirm_password):
    if not email or not otp or not new_password or not confirm_password:
        return api_error("All fields are required.")

    if new_password != confirm_password:
        return api_error("Passwords do not match.")

    stored_otp, expiry_time = frappe.db.get_value(
        "User", {"email": email}, ["otp", "otp_expire_time"]
    )

    if not stored_otp:
        return api_error("No OTP found. Please request OTP again.")

    if not expiry_time:
        return api_error("OTP expired. Please request OTP again.")

    if now_datetime() > expiry_time:
        return api_error("OTP expired. Please request OTP again.")

    # ✅ FIX: compare correctly
    if str(otp).strip() != str(stored_otp).strip():
        return api_error("Invalid OTP.")

    # Update password safely
    user = frappe.get_doc("User", {"email": email})
    user.new_password = new_password
    user.save(ignore_permissions=True)

    # Clear OTP fields
    frappe.db.set_value("User", user.name, {
        "otp": 0,
        "otp_expire_time": None
    })

    return {
        "status": "success",
        "status_code": 200,
        "message": "Password updated successfully."
    }





# import frappe
# import random
# import string
# from frappe.utils import now_datetime, add_to_date
# from car_repair_service.api.utils import api_error  # Your existing helper


# # -----------------------------
# # Step 1: Send OTP
# # -----------------------------
# @frappe.whitelist(allow_guest=True, methods=["POST"])
# def send_forgot_password_otp(email):
#     user_name = frappe.db.get_value("User", {"email": email}, "name")
#     if not user_name:
#         return api_error("User with this email does not exist.")

#     # Generate 6-digit OTP
#     otp = ''.join(random.choices(string.digits, k=6))
#     expiry_time = add_to_date(now_datetime(), minutes=10)

#     # Insert or update User OTP record
#     user_otp = frappe.db.get_value("User OTP", {"user": user_name}, "name")
#     if user_otp:
#         frappe.db.set_value("User OTP", user_otp, {
#             "otp": otp,
#             "otp_expire_time": expiry_time
#         })
#     else:
#         doc = frappe.get_doc({
#             "doctype": "User OTP",
#             "user": user_name,
#             "otp": otp,
#             "otp_expire_time": expiry_time
#         })
#         doc.insert()

#     # Send OTP via email
#     try:
#         frappe.sendmail(
#             recipients=[email],
#             subject="Password Reset OTP",
#             message=f"Your OTP is {otp}. It will expire in 10 minutes."
#         )
#     except Exception as e:
#         frappe.log_error(message=str(e), title="OTP Email Error")

#     return {
#         "status": "success",
#         "status_code": 201,
#         "msg": "OTP sent to your email."
#     }


# # -----------------------------
# # Step 2: Verify OTP
# # -----------------------------
# @frappe.whitelist(allow_guest=True, methods=["POST"])
# def verify_forgot_password_otp(email, otp):
#     if not email or not otp:
#         return api_error("Email and OTP are required.")

#     user_name = frappe.db.get_value("User", {"email": email}, "name")
#     if not user_name:
#         return api_error("User not found.")

#     try:
#         user_otp_record = frappe.get_doc("User OTP", {"user": user_name})
#     except frappe.DoesNotExistError:
#         return api_error("No OTP found. Please request OTP again.")

#     if not user_otp_record.otp or not user_otp_record.otp_expire_time:
#         return api_error("OTP expired. Please request OTP again.")

#     if now_datetime() > user_otp_record.otp_expire_time:
#         return api_error("OTP expired. Please request OTP again.")

#     if str(otp).strip() != str(user_otp_record.otp).strip():
#         return api_error("Invalid OTP.")

#     return {
#         "status": "success",
#         "status_code": 200,
#         "msg": "OTP verified successfully."
#     }


# # -----------------------------
# # Step 3: Reset Password using OTP
# # -----------------------------
# @frappe.whitelist(allow_guest=True, methods=["POST"])
# def reset_password_with_otp(email, otp, new_password, confirm_password):
#     if not email or not otp or not new_password or not confirm_password:
#         return api_error("All fields are required.")

#     if new_password != confirm_password:
#         return api_error("Passwords do not match.")

#     user_name = frappe.db.get_value("User", {"email": email}, "name")
#     if not user_name:
#         return api_error("User not found.")

#     try:
#         user_otp_record = frappe.get_doc("User OTP", {"user": user_name})
#     except frappe.DoesNotExistError:
#         return api_error("No OTP found. Please request OTP again.")

#     if not user_otp_record.otp or not user_otp_record.otp_expire_time:
#         return api_error("OTP expired. Please request OTP again.")

#     if now_datetime() > user_otp_record.otp_expire_time:
#         return api_error("OTP expired. Please request OTP again.")

#     if str(otp).strip() != str(user_otp_record.otp).strip():
#         return api_error("Invalid OTP.")

#     # Reset user password
#     user = frappe.get_doc("User", user_name)
#     user.new_password = new_password
#     user.save(ignore_permissions=True)

#     # Clear OTP record
#     user_otp_record.otp = None
#     user_otp_record.otp_expire_time = None
#     user_otp_record.save()

#     return {
#         "status": "success",
#         "status_code": 200,
#         "msg": "Password updated successfully."
#     }
