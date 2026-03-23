import frappe

_ITEM_GROUPS = [
	"Surowce",
	"Półprodukty WIP",
	"Wyroby Gotowe",
]

# key: warehouse dict key from setup_company()
_ITEMS = [
	# --- Raw Materials ---
	{
		"item_code": "STAL-C45-25",
		"item_name": "Pręt stalowy C45 fi25mm",
		"item_group": "Surowce",
		"stock_uom": "Kg",
		"valuation_rate": 8.50,
		"wh_key": "raw",
		"description": "Pręt stalowy ze stali C45, średnica 25mm, dostarczany w odcinkach 3m",
	},
	{
		"item_code": "STAL-C45-50",
		"item_name": "Pręt stalowy C45 fi50mm",
		"item_group": "Surowce",
		"stock_uom": "Kg",
		"valuation_rate": 9.20,
		"wh_key": "raw",
		"description": "Pręt stalowy ze stali C45, średnica 50mm, dostarczany w odcinkach 3m",
	},
	{
		"item_code": "ALU-6061-30",
		"item_name": "Pręt aluminiowy Al6061 fi30mm",
		"item_group": "Surowce",
		"stock_uom": "Kg",
		"valuation_rate": 22.00,
		"wh_key": "raw",
		"description": "Pręt aluminiowy stop 6061-T6, średnica 30mm",
	},
	{
		"item_code": "STAL-NC6-40",
		"item_name": "Pręt stalowy NC6 fi40mm",
		"item_group": "Surowce",
		"stock_uom": "Kg",
		"valuation_rate": 28.00,
		"wh_key": "raw",
		"description": "Pręt stalowy hartowany NC6, średnica 40mm",
	},
	# --- Semi-finished (WIP) ---
	{
		"item_code": "WIP-KORPUS-01",
		"item_name": "Półprodukt Korpus",
		"item_group": "Półprodukty WIP",
		"stock_uom": "szt.",
		"valuation_rate": 120.00,
		"wh_key": "wip",
		"description": "Korpus po obróbce zgrubnej, do dalszej obróbki wykańczającej",
	},
	{
		"item_code": "WIP-TARCZA-01",
		"item_name": "Półprodukt Tarcza",
		"item_group": "Półprodukty WIP",
		"stock_uom": "szt.",
		"valuation_rate": 95.00,
		"wh_key": "wip",
		"description": "Tarcza po obróbce zgrubnej, do frezowania wykańczającego",
	},
	# --- Finished Goods ---
	{
		"item_code": "WALEK-01",
		"item_name": "Wałek CNC Typ 01",
		"item_group": "Wyroby Gotowe",
		"stock_uom": "szt.",
		"valuation_rate": 145.00,
		"wh_key": "fg",
		"description": "Wałek precyzyjny fi25 x 150mm, tolerancja h6, Ra 0.8",
	},
	{
		"item_code": "WALEK-02",
		"item_name": "Wałek CNC Typ 02",
		"item_group": "Wyroby Gotowe",
		"stock_uom": "szt.",
		"valuation_rate": 280.00,
		"wh_key": "fg",
		"description": "Wałek stopniowany fi50 x 200mm z rowkiem wpustowym, tolerancja k6",
	},
	{
		"item_code": "KORPUS-01",
		"item_name": "Korpus CNC Typ 01",
		"item_group": "Wyroby Gotowe",
		"stock_uom": "szt.",
		"valuation_rate": 520.00,
		"wh_key": "fg",
		"description": "Korpus aluminiowy frezowany z otworami montażowymi, tolerancja H7",
	},
	{
		"item_code": "TARCZA-01",
		"item_name": "Tarcza CNC Typ 01",
		"item_group": "Wyroby Gotowe",
		"stock_uom": "szt.",
		"valuation_rate": 380.00,
		"wh_key": "fg",
		"description": "Tarcza 5-osiowa fi120 x 20mm z rowkami promieniowymi",
	},
	{
		"item_code": "TULEJA-01",
		"item_name": "Tuleja CNC Typ 01",
		"item_group": "Wyroby Gotowe",
		"stock_uom": "szt.",
		"valuation_rate": 75.00,
		"wh_key": "fg",
		"description": "Tuleja precyzyjna fi40/fi30 x 60mm z gwintem wewnętrznym M32x1.5",
	},
	{
		"item_code": "SWORZEH-01",
		"item_name": "Sworzeń CNC Typ 01",
		"item_group": "Wyroby Gotowe",
		"stock_uom": "szt.",
		"valuation_rate": 165.00,
		"wh_key": "fg",
		"description": "Sworzeń hartowany fi40 x 120mm, tolerancja f7, Ra 0.4",
	},
]


def setup_items(company, warehouses):
	_create_item_groups()
	_create_items(company, warehouses)


def _get_root_item_group():
	"""Return the root item group name (locale-agnostic)."""
	root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ""}, "name")
	return root or "All Item Groups"


def _create_item_groups():
	root = _get_root_item_group()
	for group_name in _ITEM_GROUPS:
		if frappe.db.exists("Item Group", group_name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": group_name,
				"parent_item_group": root,
				"is_group": 0,
			}
		)
		doc.insert(ignore_permissions=True)


def _create_items(company, warehouses):
	for item_def in _ITEMS:
		if frappe.db.exists("Item", item_def["item_code"]):
			continue

		warehouse_name = warehouses[item_def["wh_key"]]
		doc = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_def["item_code"],
				"item_name": item_def["item_name"],
				"item_group": item_def["item_group"],
				"stock_uom": item_def["stock_uom"],
				"valuation_rate": item_def["valuation_rate"],
				"description": item_def.get("description", item_def["item_name"]),
				"is_stock_item": 1,
				"include_item_in_manufacturing": 1,
				"item_defaults": [
					{
						"doctype": "Item Default",
						"company": company,
						"default_warehouse": warehouse_name,
					}
				],
			}
		)
		doc.insert(ignore_permissions=True)
