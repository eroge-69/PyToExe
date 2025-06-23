
import xlwings as xw
import sys

def process_row(row_num):
    formulas = [
        "=VLOOKUP([@[MODEL NUMBER]]&LEFT([@[BRANCH PLANT]],3),ITEMCOST[[#All],[Concatenation]:[Currency Code - CRCD]],10,FALSE)",
        "=VLOOKUP([@[MODEL NUMBER]]&LEFT([@[BRANCH PLANT]],3),ITEMCOST[[#All],[Concatenation]:[Supplier Catalog Cost]],9,FALSE)",
        "=VLOOKUP(VLOOKUP([@[MODEL NUMBER]],ITEMCOST[[#All],[Item Number]:[Category ]],3,FALSE),LOOKUPS[[#All],[PRODUCT CATEGORY CODE]:[PRODUCT CATEGORY]],3,FALSE)",
        "=vlookup(VLOOKUP([@[MODEL NUMBER]],ITEMCOST[[#All],[Item Number]:[Brand ]],4,FALSE),LOOKUPS[[#All],[BRAND CODE]:[BRAND]],3,false)",
        "=vlookup(VLOOKUP([@[MODEL NUMBER]],ITEMCOST[[#All],[Item Number]:[License ]],5,FALSE),LOOKUPS[[#All],[LICENSE GROUP CODE]:[LICENSE GROUP]],3,false)",
        "=vlookup(VLOOKUP([@[MODEL NUMBER]],ITEMCOST[[#All],[Item Number]:[License Subgroup]],6,FALSE),LOOKUPS[[#All],[LICENSE PROPERTY CODE]:[LICENSE PROPERTY]],3,false)",
        "USD",
        "=VLOOKUP([@[MODEL NUMBER]],LOOKUPS[[#All],[ITEM NUMBER]:[FX MATERIAL COST W/O VAT (USD)]],4,FALSE)",
        "=VLOOKUP(XLOOKUP(IF(RIGHT([@SUPPLIER],6)==\"110972\",\"SUP110972\",IF(RIGHT([@SUPPLIER],6)==\"212623\",\"SUP212623\",\"SUP000000\"))&[@[MODEL NUMBER]],PLAT_PRODLINE_MC[[#All],[Business Unit]]&PLAT_PRODLINE_MC[[#All],[2nd Item Number]],PLAT_PRODLINE_MC[[#All],[CAT20 ]]),LOOKUPS[[#All],[PLATFORM CODE]:[PLATFORM]],3,FALSE)",
        "=IF([@[ORG]]==\"UW\",\"\",XLOOKUP(IF(RIGHT([@SUPPLIER],6)==\"110972\",\"SUP110972\",IF(RIGHT([@SUPPLIER],6)==\"212623\",\"SUP212623\",\"SUP000000\"))&[@[MODEL NUMBER]],PLAT_PRODLINE_MC[[#All],[Business Unit]]&PLAT_PRODLINE_MC[[#All],[2nd Item Number]],PLAT_PRODLINE_MC[[#All],[CAT21 ]]))",
        "=IF([@[ORG]]==\"UW\",\"\",XLOOKUP(IF(RIGHT([@SUPPLIER],6)==\"110972\",\"SUP110972\",IF(RIGHT([@SUPPLIER],6)==\"212623\",\"SUP212623\",\"SUP000000\"))&[@[MODEL NUMBER]],PLAT_PRODLINE_MC[[#All],[Business Unit]]&PLAT_PRODLINE_MC[[#All],[2nd Item Number]],PLAT_PRODLINE_MC[[#All],[MC]]))",
        "=IF([@[ORG]]==\"UW\",\"\",\"USD\")"
    ]

    app = xw.App(visible=False)
    wb = app.books.active
    ws = wb.sheets.active

    status = ws.range(f'H{row_num}').value
    target_range = ws.range(f'AC{row_num}:AN{row_num}')

    if status in ['Active', 'Sales Plan']:
        target_range.value = [formulas]
    else:
        target_range.clear_contents()

    wb.save()
    wb.close()
    app.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            row = int(sys.argv[1])
            process_row(row)
        except Exception as e:
            print(f"Error: {e}")
