import frappe

_CUSTOMERS = [
	{
		"customer_name": "AUTOMOTIVE PARTS S.A.",
		"customer_type": "Company",
		"notes": "Klient motoryzacyjny — regularne zamówienia seryjne na wałki i tulejki",
	},
	{
		"customer_name": "MACH-TECH Sp. z o.o.",
		"customer_type": "Company",
		"notes": "Producent maszyn — zamówienia na korpusy i tarcze CNC",
	},
	{
		"customer_name": "AERO COMPONENTS Ltd.",
		"customer_type": "Company",
		"notes": "Klient lotniczy — zamówienia pilne o wysokim priorytecie, wymagania jakościowe AS9100",
	},
]

_SUPPLIERS = [
	{
		"supplier_name": "STALPOL Sp. z o.o.",
		"supplier_type": "Company",
		"supplier_group": "All Supplier Groups",
		"notes": "Dostawca prętów stalowych C45 i NC6, termin dostawy 7-14 dni",
	},
	{
		"supplier_name": "ALUMINIUM CENTRUM Sp. z o.o.",
		"supplier_type": "Company",
		"supplier_group": "All Supplier Groups",
		"notes": "Dostawca prętów aluminiowych Al6061, termin dostawy 5-10 dni",
	},
]


def setup_parties(company):
	_create_customers(company)
	_create_suppliers(company)


def _get_root_territory():
	"""Return root territory name (locale-agnostic)."""
	root = frappe.db.get_value("Territory", {"is_group": 1}, "name")
	return root or "All Territories"


def _create_customers(company):
	customer_group = _get_fallback_customer_group()
	territory = _get_root_territory()

	for c in _CUSTOMERS:
		if frappe.db.exists("Customer", c["customer_name"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": c["customer_name"],
				"customer_type": c.get("customer_type", "Company"),
				"customer_group": customer_group,
				"territory": territory,
				"default_currency": "PLN",
			}
		)
		doc.insert(ignore_permissions=True)


def _get_root_supplier_group():
	"""Return root supplier group name (locale-agnostic)."""
	root = frappe.db.get_value("Supplier Group", {"is_group": 1}, "name")
	return root or frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups"


def _create_suppliers(company):
	supplier_group = _get_root_supplier_group()
	for s in _SUPPLIERS:
		if frappe.db.exists("Supplier", s["supplier_name"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": s["supplier_name"],
				"supplier_type": s.get("supplier_type", "Company"),
				"supplier_group": supplier_group,
				"default_currency": "PLN",
				"country": "Poland",
			}
		)
		doc.insert(ignore_permissions=True)


def _get_fallback_customer_group():
	"""Return first available non-group customer group (locale-agnostic)."""
	groups = frappe.db.get_all(
		"Customer Group",
		filters={"is_group": 0},
		pluck="name",
		limit=1,
	)
	if groups:
		return groups[0]
	# Last resort: use whatever root group exists
	root = frappe.db.get_value("Customer Group", {}, "name")
	return root or "All Customer Groups"
