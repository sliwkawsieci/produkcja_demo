import frappe


def after_install():
	frappe.set_user("Administrator")

	# Ensure root department exists (prevents LinkValidationError during setup)
	_ensure_root_department()

	from produkcja_demo.setup.masters.company import setup_company
	from produkcja_demo.setup.masters.items import setup_items
	from produkcja_demo.setup.masters.parties import setup_parties
	from produkcja_demo.setup.masters.manufacturing import setup_manufacturing
	from produkcja_demo.setup.transactions.stock import setup_initial_stock
	from produkcja_demo.setup.transactions.sales_orders import setup_sales_orders
	from produkcja_demo.setup.transactions.production_plan import setup_production_plan
	from produkcja_demo.setup.transactions.purchase_orders import setup_purchase_orders

	try:
		frappe.publish_realtime("produkcja_demo_setup", {"status": "started"})

		company, warehouses = setup_company()
		setup_items(company, warehouses)
		setup_parties(company)
		setup_manufacturing(company)
		setup_initial_stock(company, warehouses)
		so_names = setup_sales_orders(company)
		setup_production_plan(company, warehouses, so_names)
		setup_purchase_orders(company)

		frappe.db.commit()
		frappe.publish_realtime("produkcja_demo_setup", {"status": "completed"})
	except Exception:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "produkcja_demo: setup failed")
		raise


def _ensure_root_department():
	"""Create root department if it doesn't exist."""
	# Check if root department already exists (by is_group and parent_department)
	root = frappe.db.get_value(
		"Department",
		{"is_group": 1, "parent_department": ""},
		"name"
	)
	if root:
		return  # Root department already exists

	# Create new root department
	doc = frappe.get_doc(
		{
			"doctype": "Department",
			"department_name": "All Departments",
			"is_group": 1,
		}
	)
	doc.insert(ignore_permissions=True)
