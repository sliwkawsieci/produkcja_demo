import frappe
from frappe.utils import add_days, now_datetime, today


def setup_production_plan(company, warehouses, so_names):
	"""
	1. Create and submit Production Plan from 3 planned SOs.
	2. Generate and submit Work Orders from the plan.
	3. Simulate WALEK-01 as In-Process (30 units transferred).
	4. Create urgent Work Order directly for SWORZEH-01.
	"""
	if not so_names:
		return

	pp_name = _create_production_plan(company, warehouses, so_names)
	if pp_name:
		_submit_work_orders(pp_name, warehouses)
		_simulate_walek_in_process(pp_name, warehouses)

	_create_urgent_work_order(company, warehouses, so_names)


def _create_production_plan(company, warehouses, so_names):
	# Idempotency: skip if a submitted PP already exists for this company
	existing = frappe.db.get_value(
		"Production Plan", {"company": company, "docstatus": 1}, "name"
	)
	if existing:
		return existing

	planned_keys = ["so_plan_1", "so_plan_2", "so_plan_3"]
	so_rows = []
	for key in planned_keys:
		if key in so_names:
			so_rows.append(
				{
					"doctype": "Production Plan Sales Order",
					"sales_order": so_names[key],
				}
			)

	if not so_rows:
		return None

	pp = frappe.new_doc("Production Plan")
	pp.company = company
	pp.get_items_from = "Sales Order"
	pp.for_warehouse = warehouses["raw"]

	for row in so_rows:
		pp.append("sales_orders", row)

	try:
		# Populate po_items from the Sales Orders
		pp.get_items()

		# Set planned start date on all items
		start_date = add_days(today(), 1)
		for item in pp.po_items:
			item.planned_start_date = start_date

		pp.insert(ignore_permissions=True)
		pp.submit()
		return pp.name
	except Exception:
		frappe.log_error(frappe.get_traceback(), "produkcja_demo: could not create Production Plan")
		return None


def _submit_work_orders(pp_name, warehouses):
	"""Call make_work_order() on the submitted Production Plan, then submit all generated WOs."""
	pp = frappe.get_doc("Production Plan", pp_name)

	try:
		pp.make_work_order()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "produkcja_demo: pp.make_work_order() failed")
		return

	draft_wos = frappe.db.get_all(
		"Work Order",
		filters={"production_plan": pp_name, "docstatus": 0},
		pluck="name",
	)

	for wo_name in draft_wos:
		try:
			wo = frappe.get_doc("Work Order", wo_name)
			if not wo.wip_warehouse:
				wo.wip_warehouse = warehouses["wip"]
			if not wo.fg_warehouse:
				wo.fg_warehouse = warehouses["fg"]
			wo.save(ignore_permissions=True)
			wo.submit()
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"produkcja_demo: could not submit Work Order {wo_name}",
			)


def _simulate_walek_in_process(pp_name, warehouses):
	"""Transfer materials for 30 units of WALEK-01 to put the WO In Process."""
	wo_name = frappe.db.get_value(
		"Work Order",
		{"production_plan": pp_name, "production_item": "WALEK-01", "docstatus": 1},
		"name",
	)
	if not wo_name:
		return

	try:
		from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry

		se_dict = make_stock_entry(wo_name, "Material Transfer for Manufacture", qty=30)
		se = frappe.get_doc(se_dict)
		# Ensure source warehouse is set
		for item in se.items:
			if not item.s_warehouse:
				item.s_warehouse = warehouses["raw"]
		se.insert(ignore_permissions=True)
		se.submit()
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			"produkcja_demo: could not simulate WALEK-01 In Process",
		)


def _create_urgent_work_order(company, warehouses, so_names):
	"""Create a high-priority Work Order for SWORZEH-01 directly from the urgent SO."""
	urgent_so = so_names.get("so_urgent")
	if not urgent_so:
		return

	# Idempotency: skip if WO for this SO already exists
	if frappe.db.exists(
		"Work Order", {"sales_order": urgent_so, "production_item": "SWORZEH-01", "docstatus": 1}
	):
		return

	bom_no = frappe.db.get_value(
		"BOM",
		{"item": "SWORZEH-01", "is_default": 1, "docstatus": 1},
		"name",
	)
	if not bom_no:
		frappe.log_error(
			"BOM for SWORZEH-01 not found",
			"produkcja_demo: urgent Work Order skipped",
		)
		return

	so_item_name = frappe.db.get_value(
		"Sales Order Item",
		{"parent": urgent_so, "item_code": "SWORZEH-01"},
		"name",
	)

	try:
		wo = frappe.get_doc(
			{
				"doctype": "Work Order",
				"production_item": "SWORZEH-01",
				"bom_no": bom_no,
				"qty": 20,
				"company": company,
				"fg_warehouse": warehouses["fg"],
				"wip_warehouse": warehouses["wip"],
				"sales_order": urgent_so,
				"sales_order_item": so_item_name,
				"expected_delivery_date": add_days(today(), 3),
				"planned_start_date": now_datetime(),
				"description": (
					"PILNE: AERO COMPONENTS — dostawa ekspresowa 3 dni. "
					"Priorytet maksymalny. Obróbka przed planową produkcją!"
				),
				"transfer_material_against": "Work Order",
			}
		)
		wo.set_work_order_operations()
		wo.set_required_items()
		wo.insert(ignore_permissions=True)
		wo.submit()
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			"produkcja_demo: could not create urgent Work Order for SWORZEH-01",
		)
