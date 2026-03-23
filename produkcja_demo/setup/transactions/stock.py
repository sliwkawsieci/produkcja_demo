import frappe

_INITIAL_STOCK = [
	{"item_code": "STAL-C45-25", "qty": 500.0, "basic_rate": 8.50},
	{"item_code": "STAL-C45-50", "qty": 300.0, "basic_rate": 9.20},
	{"item_code": "ALU-6061-30", "qty": 200.0, "basic_rate": 22.00},
	{"item_code": "STAL-NC6-40", "qty": 150.0, "basic_rate": 28.00},
]


def setup_initial_stock(company, warehouses):
	raw_warehouse = warehouses["raw"]
	for entry in _INITIAL_STOCK:
		_create_material_receipt(company, raw_warehouse, entry)


def _create_material_receipt(company, warehouse, entry):
	item_code = entry["item_code"]

	# Skip if stock already exists for this item in this warehouse
	existing_qty = frappe.db.get_value(
		"Bin",
		{"item_code": item_code, "warehouse": warehouse},
		"actual_qty",
	)
	if existing_qty and existing_qty > 0:
		return

	se = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"company": company,
			"items": [
				{
					"doctype": "Stock Entry Detail",
					"item_code": item_code,
					"qty": entry["qty"],
					"t_warehouse": warehouse,
					"basic_rate": entry["basic_rate"],
					"uom": frappe.db.get_value("Item", item_code, "stock_uom"),
					"conversion_factor": 1.0,
				}
			],
		}
	)
	try:
		se.insert(ignore_permissions=True)
		se.submit()
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"produkcja_demo: could not create stock receipt for {item_code}",
		)
