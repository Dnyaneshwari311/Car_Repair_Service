# import frappe
# import json

# @frappe.whitelist()
# def create_customer_and_vehicle(data):
#     data = json.loads(data)

#     # -------------------------------
#     # 1️⃣ CREATE OR GET CUSTOMER
#     # -------------------------------
#     customer_name = data.get("customer_name")
#     customer = frappe.db.exists("Customer", {"customer_name": customer_name})

#     if customer:
#         customer = frappe.get_doc("Customer", customer)
#     else:
#         customer = frappe.get_doc({
#             "doctype": "Customer",
#             "customer_name": customer_name,
#             "email_id": data.get("email"),
#             "mobile_no": data.get("phone")
#         }).insert(ignore_permissions=True)
#         frappe.db.commit()

#     # -------------------------------
#     # 2️⃣ CREATE OR GET VEHICLE MAKE
#     # -------------------------------
#     make = data.get("make")
#     make_exists = frappe.db.exists("Vehicle Make", {"make_name": make})

#     if not make_exists:
#         make_doc = frappe.get_doc({
#             "doctype": "Vehicle Make",
#             "make_name": make
#         }).insert(ignore_permissions=True)
#         make_name = make_doc.name
#         frappe.db.commit()
#     else:
#         make_name = make_exists

#     # -------------------------------
#     # 3️⃣ CREATE OR GET VEHICLE MODEL
#     # -------------------------------
#     model = data.get("model")
#     model_exists = frappe.db.exists("Vehicle Model", {"model_name": model})

#     if not model_exists:
#         model_doc = frappe.get_doc({
#             "doctype": "Vehicle Model",
#             "model_name": model,
#             "vehicle_make": make_name
#         }).insert(ignore_permissions=True)
#         model_name = model_doc.name
#         frappe.db.commit()
#     else:
#         model_name = model_exists

#     # -------------------------------
#     # 4️⃣ CREATE VEHICLE
#     # -------------------------------
#     license_plate = data.get("liscense_plate")

#     # Check if same vehicle exists
#     existing_vehicle = frappe.db.exists("Vehicle", {"license_plate": license_plate})
#     if existing_vehicle:
#         vehicle = frappe.get_doc("Vehicle", existing_vehicle)
#     else:
#         vehicle = frappe.get_doc({
#             "doctype": "Vehicle",
#             "license_plate": license_plate,
#             "make": make_name,
#             "model": model_name,
#             "custom_customer_name": customer.name,   # ✅ customer link
#             "email": data.get("email"),              # if field exists
#             "phone": data.get("phone")               # if field exists
#         }).insert(ignore_permissions=True)
#         frappe.db.commit()

#     # -------------------------------
#     # ✅ RETURN VALUES TO FORM
#     # -------------------------------
#     return {
#         "customer": customer.name,
#         "vehicle": vehicle.name,
#         "license_plate": vehicle.license_plate,
#         "make": vehicle.make,
#         "model": vehicle.model
#     }





# import frappe
# import json

# @frappe.whitelist()
# def create_customer_and_vehicle(data):
#     data = json.loads(data) if isinstance(data, str) else data

#     # CUSTOMER
#     customer_name = data.get("customer_name")
#     customer = frappe.db.exists("Customer", {"customer_name": customer_name})
#     if customer:
#         customer = frappe.get_doc("Customer", customer)
#     else:
#         customer = frappe.get_doc({
#             "doctype": "Customer",
#             "customer_name": customer_name,
#             "email_id": data.get("email"),
#             "mobile_no": data.get("phone")
#         }).insert(ignore_permissions=True)

#     # VEHICLE MAKE
#     make = data.get("make")
#     make_exists = frappe.db.exists("Vehicle Make", make)
#     if not make_exists:
#         make_doc = frappe.get_doc({
#             "doctype": "Vehicle Make",
#             "make": make
#         }).insert(ignore_permissions=True)
#         make_name = make_doc.name
#     else:
#         make_name = make_exists

#     # VEHICLE MODEL
#     model = data.get("model")
#     model_exists = frappe.db.exists("Vehicle Model", model)
#     if not model_exists:
#         model_doc = frappe.get_doc({
#             "doctype": "Vehicle Model",
#             "model": model
#         }).insert(ignore_permissions=True)
#         model_name = model_doc.name
#     else:
#         model_name = model_exists

#     # VEHICLE
#     license_plate = data.get("license_plate")
#     existing_vehicle = frappe.db.exists("Vehicle", {"license_plate": license_plate})

#     if existing_vehicle:
#         vehicle = frappe.get_doc("Vehicle", existing_vehicle)
#     else:
#         vehicle = frappe.get_doc({
#             "doctype": "Vehicle",
#             "license_plate": license_plate,
#             "make": make_name,
#             "model": model_name,
#             "custom_customer_name": customer.name,
#             "email": data.get("email"),
#             "phone": data.get("phone")
#         }).insert(ignore_permissions=True)

#     return {
#         "customer": customer.name,
#         "vehicle": vehicle.name,
#         "license_plate": vehicle.license_plate,
#         "make": vehicle.make,
#         "model": vehicle.model
#     }





# import frappe
# import json

# @frappe.whitelist()
# def create_customer_and_vehicle(data):
#     data = json.loads(data) if isinstance(data, str) else data

#     # CUSTOMER
#     customer_name = data.get("customer_name")
#     customer = frappe.db.exists("Customer", {"customer_name": customer_name})
#     if customer:
#         customer = frappe.get_doc("Customer", customer)
#     else:
#         customer = frappe.get_doc({
#             "doctype": "Customer",
#             "customer_name": customer_name,
#             "email_id": data.get("email"),
#             "mobile_no": data.get("phone")
#         }).insert(ignore_permissions=True)

#     # VEHICLE MAKE
#     make = data.get("make")
#     make_exists = frappe.db.exists("Vehicle Make", make)
#     if not make_exists:
#         make_doc = frappe.get_doc({
#             "doctype": "Vehicle Make",
#             "make": make
#         }).insert(ignore_permissions=True)
#         make_name = make_doc.name
#     else:
#         make_name = make_exists

#     # VEHICLE MODEL
#     model = data.get("model")
#     model_exists = frappe.db.exists("Vehicle Model", model)
#     if not model_exists:
#         model_doc = frappe.get_doc({
#             "doctype": "Vehicle Model",
#             "model": model
#         }).insert(ignore_permissions=True)
#         model_name = model_doc.name
#     else:
#         model_name = model_exists

#     # VEHICLE
#     license_plate = data.get("license_plate")
#     existing_vehicle = frappe.db.exists("Vehicle", {"license_plate": license_plate})

#     if existing_vehicle:
#         vehicle = frappe.get_doc("Vehicle", existing_vehicle)
#     else:
#         # Custom vehicle name: Model-LicensePlate
#         vehicle_name = f"{model}-{license_plate}"

#         vehicle = frappe.get_doc({
#             "doctype": "Vehicle",
#             "license_plate": license_plate,
#             "make": make_name,
#             "model": model_name,
#             "custom_customer_name": customer.name,
#             "email": data.get("email"),
#             "phone": data.get("phone")
#             # "email": customer.email_id,    # ✅ now taking from saved customer
#             # "phone": customer.mobile_no  
#         })

#         vehicle.set_new_name(vehicle_name)  # ✅ Set Name before insert
#         vehicle.insert(ignore_permissions=True)

#     return {
#         "customer": customer.name,
#         "vehicle": vehicle.name,
#         "license_plate": vehicle.license_plate,
#         "make": vehicle.make,
#         "model": vehicle.model,
#         "email": customer.email_id,     # ✅ return email
#         "phone": customer.mobile_no    
#     }





import frappe
import json

@frappe.whitelist()
def create_customer_and_vehicle(data):
    data = json.loads(data) if isinstance(data, str) else data

    # CUSTOMER
    customer_name = data.get("customer_name")
    customer = frappe.db.exists("Customer", {"customer_name": customer_name})
    if customer:
        customer = frappe.get_doc("Customer", customer)
    else:
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "email_id": data.get("email"),
            "mobile_no": data.get("phone")
        }).insert(ignore_permissions=True)

    # VEHICLE MAKE
    make = data.get("make")
    make_exists = frappe.db.exists("Vehicle Make", make)
    if not make_exists:
        make_doc = frappe.get_doc({
            "doctype": "Vehicle Make",
            "make": make
        }).insert(ignore_permissions=True)
        make_name = make_doc.name
    else:
        make_name = make_exists

    # VEHICLE MODEL
    model = data.get("model")
    model_exists = frappe.db.exists("Vehicle Model", model)
    if not model_exists:
        model_doc = frappe.get_doc({
            "doctype": "Vehicle Model",
            "model": model
        }).insert(ignore_permissions=True)
        model_name = model_doc.name
    else:
        model_name = model_exists

    # VEHICLE
    license_plate = data.get("license_plate")
    existing_vehicle = frappe.db.exists("Vehicle", {"license_plate": license_plate})

    if existing_vehicle:
        vehicle = frappe.get_doc("Vehicle", existing_vehicle)
    else:
        # Custom vehicle name: Model-LicensePlate
        vehicle_name = f"{model}-{license_plate}"

        vehicle = frappe.get_doc({
            "doctype": "Vehicle",
            "license_plate": license_plate,
            "make": make_name,
            "model": model_name,
            "custom_customer_name": customer.name,
            "email": data.get("email"),
            "phone": data.get("phone"),
            "chassis_no": data.get("chassis_no"),  # Set chassis_no
            "fuel_type": data.get("fuel_type")     # Set fuel_type
        })

        vehicle.set_new_name(vehicle_name)  # Set Name before insert
        vehicle.insert(ignore_permissions=True)

    return {
        "customer": customer.name,
        "vehicle": vehicle.name,
        "license_plate": vehicle.license_plate,
        "make": vehicle.make,
        "model": vehicle.model,
        "chassis_no": vehicle.chassis_no,   # Return chassis_no
        "fuel_type": vehicle.fuel_type,     # Return fuel_type
        "email": customer.email_id,
        "phone": customer.mobile_no    
    }





# import frappe
# import json

# @frappe.whitelist()
# def create_customer_and_vehicle(data):
#     data = json.loads(data) if isinstance(data, str) else data

#     # ✅ CUSTOMER
#     customer_name = data.get("customer_name")
#     customer = frappe.db.exists("Customer", {"customer_name": customer_name})
#     if customer:
#         customer = frappe.get_doc("Customer", customer)
#     else:
#         customer = frappe.get_doc({
#             "doctype": "Customer",
#             "customer_name": customer_name,
#             "email_id": data.get("email"),
#             "mobile_no": data.get("phone")
#         }).insert(ignore_permissions=True)

#     # ✅ VEHICLE MAKE
#     make = data.get("make")
#     make_exists = frappe.db.exists("Vehicle Make", make)
#     if not make_exists:
#         make_doc = frappe.get_doc({
#             "doctype": "Vehicle Make",
#             "make": make
#         }).insert(ignore_permissions=True)
#         make_name = make_doc.name
#     else:
#         make_name = make_exists

#     # ✅ VEHICLE MODEL
#     model = data.get("model")
#     model_exists = frappe.db.exists("Vehicle Model", model)
#     if not model_exists:
#         model_doc = frappe.get_doc({
#             "doctype": "Vehicle Model",
#             "model": model
#         }).insert(ignore_permissions=True)
#         model_name = model_doc.name
#     else:
#         model_name = model_exists

#     # ✅ VEHICLE (keep using license_plate inside Vehicle)
#     vehicle_number = data.get("vehicle_number")  # input field
#     license_plate = vehicle_number               # map to Vehicle.license_plate

#     existing_vehicle = frappe.db.exists("Vehicle", {"license_plate": license_plate})

#     if existing_vehicle:
#         vehicle = frappe.get_doc("Vehicle", existing_vehicle)
#     else:
#         # Custom vehicle name: Model-LicensePlate
#         vehicle_name = f"{model}-{license_plate}"

#         vehicle = frappe.get_doc({
#             "doctype": "Vehicle",
#             "license_plate": license_plate,  # ✅ Vehicle still expects this
#             "make": make_name,
#             "model": model_name,
#             "custom_customer_name": customer.name,
#             "email": data.get("email"),
#             "phone": data.get("phone")
#         })

#         vehicle.set_new_name(vehicle_name)
#         vehicle.insert(ignore_permissions=True)

#     return {
#         "customer": customer.name,
#         "vehicle": vehicle.name,
#         "vehicle_number": vehicle.license_plate,  # ✅ output still shows vehicle_number for consistency
#         "make": vehicle.make,
#         "model": vehicle.model,
#         "email": customer.email_id,
#         "phone": customer.mobile_no
#     }


