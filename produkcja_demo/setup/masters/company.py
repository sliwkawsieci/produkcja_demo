import frappe

COMPANY_NAME = "CNC Precision Sp. z o.o."
COMPANY_ABBR = "CNC"


def _get_unique_abbr(base_abbr):
	"""Return base_abbr if free, otherwise append a digit until unique."""
	if not frappe.db.exists("Company", {"abbr": base_abbr}):
		return base_abbr
	for i in range(1, 100):
		candidate = f"{base_abbr}{i}"
		if not frappe.db.exists("Company", {"abbr": candidate}):
			return candidate
	return base_abbr  # fallback — validation will catch true duplicates

_WAREHOUSES = [
	{"warehouse_name": "Magazyn Surowców", "key": "raw"},
	{"warehouse_name": "Produkcja WIP", "key": "wip"},
	{"warehouse_name": "Magazyn Wyrobów", "key": "fg"},
]


def setup_company():
	"""Create the demo company and warehouses. Returns (company_name, warehouses_dict)."""
	_ensure_pln_enabled()
	company = _create_company()
	warehouses = _create_warehouses(company)
	_configure_manufacturing_settings(warehouses)
	return company, warehouses


def _ensure_pln_enabled():
	if frappe.db.exists("Currency", "PLN"):
		frappe.db.set_value("Currency", "PLN", "enabled", 1)


def _create_company():
	# Check for exact name match first
	if frappe.db.exists("Company", COMPANY_NAME):
		abbr = frappe.db.get_value("Company", COMPANY_NAME, "abbr")
		frappe.local.cnc_demo_abbr = abbr
		return COMPANY_NAME

	# Check for any leftover "CNC Precision" company from a previous install attempt
	existing = frappe.db.get_value(
		"Company",
		{"company_name": ["like", "CNC Precision%"]},
		["name", "abbr"],
		as_dict=True,
	)
	if existing:
		frappe.local.cnc_demo_abbr = existing.abbr
		return existing.name

	abbr = _get_unique_abbr(COMPANY_ABBR)

	doc = frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": COMPANY_NAME,
			"abbr": abbr,
			"default_currency": "PLN",
			"country": "Poland",
			"enable_perpetual_inventory": 1,
			"chart_of_accounts_based_on": "Standard Template",
			"chart_of_accounts": "Standard",
		}
	)
	# Skip automatic warehouse creation in on_update hook
	frappe.local.flags.ignore_chart_of_accounts = True
	doc.insert(ignore_permissions=True)
	frappe.local.flags.ignore_chart_of_accounts = False

	# Store the actual abbr used so warehouse names are computed correctly
	frappe.local.cnc_demo_abbr = abbr
	return COMPANY_NAME


def _create_warehouses(company):
	warehouses = {}
	for wh in _WAREHOUSES:
		name = _get_or_create_warehouse(company, wh["warehouse_name"])
		warehouses[wh["key"]] = name
	return warehouses


def _get_or_create_warehouse(company, warehouse_name):
	# ERPNext autonames warehouse as "<warehouse_name> - <abbr>"
	abbr = getattr(frappe.local, "cnc_demo_abbr", None) or frappe.db.get_value(
		"Company", company, "abbr"
	)
	expected_name = f"{warehouse_name} - {abbr}"
	if frappe.db.exists("Warehouse", expected_name):
		return expected_name

	doc = frappe.get_doc(
		{
			"doctype": "Warehouse",
			"warehouse_name": warehouse_name,
			"company": company,
			"is_group": 0,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _configure_manufacturing_settings(warehouses):
	try:
		ms = frappe.get_doc("Manufacturing Settings")
		ms.default_wip_warehouse = warehouses["wip"]
		ms.default_fg_warehouse = warehouses["fg"]
		ms.save(ignore_permissions=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "produkcja_demo: could not set Manufacturing Settings")
