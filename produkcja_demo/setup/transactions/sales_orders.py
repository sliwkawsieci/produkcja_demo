import frappe
from frappe.utils import add_days, today

_SO_DEFINITIONS = [
	{
		"key": "so_plan_1",
		"customer": "AUTOMOTIVE PARTS S.A.",
		"delivery_days": 21,
		"items": [
			{"item_code": "WALEK-01", "qty": 100.0, "rate": 185.0},
		],
	},
	{
		"key": "so_plan_2",
		"customer": "MACH-TECH Sp. z o.o.",
		"delivery_days": 28,
		"items": [
			{"item_code": "TARCZA-01", "qty": 50.0, "rate": 420.0},
			{"item_code": "TULEJA-01", "qty": 30.0, "rate": 95.0},
		],
	},
	{
		"key": "so_plan_3",
		"customer": "AUTOMOTIVE PARTS S.A.",
		"delivery_days": 35,
		"items": [
			{"item_code": "KORPUS-01", "qty": 25.0, "rate": 680.0},
		],
	},
	{
		"key": "so_urgent",
		"customer": "AERO COMPONENTS Ltd.",
		"delivery_days": 3,
		"po_no": "PILNE-AERO-001",
		"instructions": "PILNE: Dostawa ekspresowa — priorytet maksymalny. Wymagany certyfikat materiałowy.",
		"items": [
			{"item_code": "SWORZEH-01", "qty": 20.0, "rate": 210.0},
		],
	},
]


def setup_sales_orders(company):
	"""Create and submit all demo Sales Orders. Returns dict of key -> SO name."""
	so_names = {}
	delivery_date_base = today()

	for so_def in _SO_DEFINITIONS:
		name = _get_existing_so(company, so_def)
		if name:
			so_names[so_def["key"]] = name
			continue

		delivery_date = add_days(delivery_date_base, so_def["delivery_days"])
		so_items = []
		for item in so_def["items"]:
			so_items.append(
				{
					"doctype": "Sales Order Item",
					"item_code": item["item_code"],
					"qty": item["qty"],
					"rate": item["rate"],
					"delivery_date": delivery_date,
					"uom": frappe.db.get_value("Item", item["item_code"], "stock_uom"),
					"conversion_factor": 1.0,
				}
			)

		doc_data = {
			"doctype": "Sales Order",
			"company": company,
			"customer": so_def["customer"],
			"transaction_date": today(),
			"delivery_date": delivery_date,
			"currency": "PLN",
			"conversion_rate": 1,
			"order_type": "Sales",
			"items": so_items,
		}

		if so_def.get("po_no"):
			doc_data["po_no"] = so_def["po_no"]
		if so_def.get("instructions"):
			doc_data["instructions"] = so_def["instructions"]

		try:
			doc = frappe.get_doc(doc_data)
			doc.insert(ignore_permissions=True)
			doc.submit()
			so_names[so_def["key"]] = doc.name
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"produkcja_demo: could not create Sales Order for {so_def['customer']}",
			)

	return so_names


def _get_existing_so(company, so_def):
	"""Return existing submitted SO name if it already exists (idempotency)."""
	filters = {
		"company": company,
		"customer": so_def["customer"],
		"docstatus": 1,
	}
	# For the urgent order, use po_no as unique identifier
	if so_def.get("po_no"):
		filters["po_no"] = so_def["po_no"]
		name = frappe.db.get_value("Sales Order", filters, "name")
		return name

	# For planned orders, check by customer + first item code
	first_item_code = so_def["items"][0]["item_code"]
	result = frappe.db.get_value(
		"Sales Order Item",
		{
			"item_code": first_item_code,
			"docstatus": 1,
			"parenttype": "Sales Order",
		},
		["parent"],
		as_dict=True,
	)
	if result:
		# Verify this SO belongs to our company and customer
		so_company = frappe.db.get_value("Sales Order", result.parent, "company")
		so_customer = frappe.db.get_value("Sales Order", result.parent, "customer")
		if so_company == company and so_customer == so_def["customer"]:
			return result.parent

	return None
