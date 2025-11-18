# Copyright (c) 2025, dnyaneshwari and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class CarRepairRequest(Document):
# 	pass
import frappe
from frappe.model.document import Document

class CarRepairRequest(Document):
    def after_insert(self):
        if self.car:
            vehicle = frappe.get_doc("Vehicle", self.car)

            updated = False  # Track if any value is updated

            # Sync chassis number if not already set in Vehicle
            if self.chassis_no and not vehicle.chassis_no:
                vehicle.chassis_no = self.chassis_no
                updated = True

            # Sync fuel type if not already set in Vehicle
            if self.fuel_type and not vehicle.fuel_type:
                vehicle.fuel_type = self.fuel_type  # (Fuel Type is a Select field in Vehicle)
                updated = True

            # Sync odometer value as last_odometer in Vehicle
            if self.odometer_value:
               vehicle.db_set("last_odometer", self.odometer_value, commit=True)


            # Save if any changes were made
            if updated:
                vehicle.save(ignore_permissions=True)
