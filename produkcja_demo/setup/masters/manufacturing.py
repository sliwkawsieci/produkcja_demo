import frappe

_WORKSTATIONS = [
	{
		"workstation_name": "CNC Tokarka 1",
		"hour_rate_labour": 150.0,
		"shift_start": "06:00:00",
		"shift_end": "22:00:00",
		"description": "Tokarka CNC HAAS ST-20, zakres: fi5-fi200, max długość 500mm",
	},
	{
		"workstation_name": "CNC Tokarka 2",
		"hour_rate_labour": 150.0,
		"shift_start": "06:00:00",
		"shift_end": "22:00:00",
		"description": "Tokarka CNC Mazak QT-250, zakres: fi5-fi250, max długość 600mm",
	},
	{
		"workstation_name": "CNC Frezarka 3-osiowa",
		"hour_rate_labour": 200.0,
		"shift_start": "06:00:00",
		"shift_end": "22:00:00",
		"description": "Frezarka 3-osiowa DMG Mori CMX 600V, stół 600x500mm",
	},
	{
		"workstation_name": "Centrum Obróbcze 5-osiowe",
		"hour_rate_labour": 350.0,
		"shift_start": "06:00:00",
		"shift_end": "14:00:00",
		"description": "Centrum 5-osiowe DMU 50, stół obrotowy fi630mm, 1 zmiana",
	},
	{
		"workstation_name": "Stanowisko Kontroli Jakości",
		"hour_rate_labour": 80.0,
		"shift_start": "06:00:00",
		"shift_end": "22:00:00",
		"description": "CMM Zeiss Contura + przyrządy pomiarowe, tolerancje do IT5",
	},
]

_OPERATIONS = [
	{"name": "Toczenie CNC", "workstation": "CNC Tokarka 1"},
	{"name": "Frezowanie CNC", "workstation": "CNC Frezarka 3-osiowa"},
	{"name": "Wiercenie i Gwintowanie", "workstation": "CNC Tokarka 2"},
	{"name": "Obróbka 5-osiowa", "workstation": "Centrum Obróbcze 5-osiowe"},
	{"name": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości"},
]

# BOMs — WIP items must come before finished goods that use them
_BOMS = [
	# --- WIP sub-items first ---
	{
		"item": "WIP-KORPUS-01",
		"items": [
			{"item_code": "STAL-C45-50", "qty": 1.0, "uom": "Kg"},
		],
		"operations": [
			{"operation": "Toczenie CNC", "workstation": "CNC Tokarka 1", "time_in_mins": 25, "hour_rate": 150},
		],
	},
	{
		"item": "WIP-TARCZA-01",
		"items": [
			{"item_code": "ALU-6061-30", "qty": 0.5, "uom": "Kg"},
		],
		"operations": [
			{"operation": "Frezowanie CNC", "workstation": "CNC Frezarka 3-osiowa", "time_in_mins": 30, "hour_rate": 200},
		],
	},
	# --- Finished goods ---
	{
		"item": "WALEK-01",
		"items": [
			{"item_code": "STAL-C45-25", "qty": 0.45, "uom": "Kg"},
		],
		"operations": [
			{"operation": "Toczenie CNC", "workstation": "CNC Tokarka 1", "time_in_mins": 25, "hour_rate": 150},
			{"operation": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości", "time_in_mins": 10, "hour_rate": 80},
		],
	},
	{
		"item": "WALEK-02",
		"items": [
			{"item_code": "STAL-C45-50", "qty": 0.80, "uom": "Kg"},
		],
		"operations": [
			{"operation": "Toczenie CNC", "workstation": "CNC Tokarka 1", "time_in_mins": 35, "hour_rate": 150},
			{"operation": "Wiercenie i Gwintowanie", "workstation": "CNC Tokarka 2", "time_in_mins": 15, "hour_rate": 150},
			{"operation": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości", "time_in_mins": 10, "hour_rate": 80},
		],
	},
	{
		"item": "KORPUS-01",
		"items": [
			{"item_code": "STAL-C45-50", "qty": 1.2, "uom": "Kg"},
			{"item_code": "WIP-KORPUS-01", "qty": 1.0, "uom": "szt."},
		],
		"operations": [
			{"operation": "Frezowanie CNC", "workstation": "CNC Frezarka 3-osiowa", "time_in_mins": 45, "hour_rate": 200},
			{"operation": "Wiercenie i Gwintowanie", "workstation": "CNC Tokarka 2", "time_in_mins": 20, "hour_rate": 150},
			{"operation": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości", "time_in_mins": 15, "hour_rate": 80},
		],
	},
	{
		"item": "TARCZA-01",
		"items": [
			{"item_code": "ALU-6061-30", "qty": 0.6, "uom": "Kg"},
			{"item_code": "WIP-TARCZA-01", "qty": 1.0, "uom": "szt."},
		],
		"operations": [
			{"operation": "Frezowanie CNC", "workstation": "CNC Frezarka 3-osiowa", "time_in_mins": 40, "hour_rate": 200},
			{"operation": "Obróbka 5-osiowa", "workstation": "Centrum Obróbcze 5-osiowe", "time_in_mins": 60, "hour_rate": 350},
			{"operation": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości", "time_in_mins": 20, "hour_rate": 80},
		],
	},
	{
		"item": "TULEJA-01",
		"items": [
			{"item_code": "STAL-C45-25", "qty": 0.30, "uom": "Kg"},
		],
		"operations": [
			{"operation": "Toczenie CNC", "workstation": "CNC Tokarka 1", "time_in_mins": 20, "hour_rate": 150},
			{"operation": "Wiercenie i Gwintowanie", "workstation": "CNC Tokarka 2", "time_in_mins": 15, "hour_rate": 150},
			{"operation": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości", "time_in_mins": 8, "hour_rate": 80},
		],
	},
	{
		"item": "SWORZEH-01",
		"items": [
			{"item_code": "STAL-NC6-40", "qty": 0.25, "uom": "Kg"},
		],
		"operations": [
			{"operation": "Toczenie CNC", "workstation": "CNC Tokarka 1", "time_in_mins": 30, "hour_rate": 150},
			{"operation": "Wiercenie i Gwintowanie", "workstation": "CNC Tokarka 2", "time_in_mins": 10, "hour_rate": 150},
			{"operation": "Kontrola Jakości", "workstation": "Stanowisko Kontroli Jakości", "time_in_mins": 10, "hour_rate": 80},
		],
	},
]


def setup_manufacturing(company):
	_create_workstations(company)
	_create_operations()
	_create_boms(company)


def _create_workstations(company):
	for ws in _WORKSTATIONS:
		if frappe.db.exists("Workstation", ws["workstation_name"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Workstation",
				"workstation_name": ws["workstation_name"],
				"hour_rate_labour": ws["hour_rate_labour"],
				"description": ws.get("description", ""),
				"company": company,
				"working_hours": [
					{
						"doctype": "Workstation Working Hour",
						"enabled": 1,
						"start_time": ws["shift_start"],
						"end_time": ws["shift_end"],
					}
				],
			}
		)
		doc.insert(ignore_permissions=True)


def _create_operations():
	for op in _OPERATIONS:
		if frappe.db.exists("Operation", op["name"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Operation",
				"name": op["name"],
				"workstation": op["workstation"],
			}
		)
		doc.insert(ignore_permissions=True)


def _create_boms(company):
	for bom_def in _BOMS:
		item_code = bom_def["item"]
		if frappe.db.exists("BOM", {"item": item_code, "is_default": 1, "docstatus": 1}):
			continue

		bom_items = []
		for raw in bom_def["items"]:
			bom_items.append(
				{
					"doctype": "BOM Item",
					"item_code": raw["item_code"],
					"qty": raw["qty"],
					"uom": raw["uom"],
					"stock_uom": raw["uom"],
					"include_item_in_manufacturing": 1,
				}
			)

		bom_ops = []
		for op in bom_def.get("operations", []):
			bom_ops.append(
				{
					"doctype": "BOM Operation",
					"operation": op["operation"],
					"workstation": op["workstation"],
					"time_in_mins": op["time_in_mins"],
					"hour_rate": op["hour_rate"],
					"operating_cost": op["hour_rate"] * op["time_in_mins"] / 60.0,
				}
			)

		doc = frappe.get_doc(
			{
				"doctype": "BOM",
				"item": item_code,
				"company": company,
				"currency": "PLN",
				"conversion_rate": 1,
				"quantity": 1,
				"is_default": 1,
				"is_active": 1,
				"with_operations": 1,
				"items": bom_items,
				"operations": bom_ops,
			}
		)
		try:
			doc.insert(ignore_permissions=True)
			doc.submit()
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"produkcja_demo: could not create BOM for {item_code}",
			)
