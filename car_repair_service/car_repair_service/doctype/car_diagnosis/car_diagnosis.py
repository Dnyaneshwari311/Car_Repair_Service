# Copyright (c) 2025, dnyaneshwari and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CarDiagnosis(Document):
	pass


def before_save(doc):
    for d in doc.car_diagnosis_detail:
        if d.item_code and d.quantity:
            price = frappe.get_value(
                "Item Price",
                {"item_code": d.item_code, "selling": 1},
                "price_list_rate"
            )
            if price:
                d.estimated_cost = d.quantity * price
