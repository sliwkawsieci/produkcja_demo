import frappe
from frappe.utils import add_days, today


def setup_purchase_orders(company):
	_create_stal_replenishment_po(company)


def _create_stal_replenishment_po(company):
	supplier = "STALPOL Sp. z o.o."

	# Idempotency: skip if PO for this supplier already exists
	if frappe.db.exists(
		"Purchase Order",
		{"company": company, "supplier": supplier, "docstatus": 1},
	):
		return

	schedule_date = add_days(today(), 14)

	doc = frappe.get_doc(
		{
			"doctype": "Purchase Order",
			"supplier": supplier,
			"company": company,
			"transaction_date": today(),
			"schedule_date": schedule_date,
			"currency": "PLN",
			"conversion_rate": 1,
			"instructions": (
				"MRP: Uzupełnienie zapasów stali C45 fi25mm na podstawie planu produkcji. "
				"Dostawa na magazyn surowców."
			),
			"items": [
				{
					"doctype": "Purchase Order Item",
					"item_code": "STAL-C45-25",
					"qty": 1000.0,
					"rate": 8.50,
					"uom": "Kg",
					"stock_uom": "Kg",
					"conversion_factor": 1.0,
					"schedule_date": schedule_date,
				}
			],
		}
	)
	try:
		doc.insert(ignore_permissions=True)
		doc.submit()
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			"produkcja_demo: could not create Purchase Order for STALPOL",
		)
