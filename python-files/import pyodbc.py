import pyodbc
import sys
from datetime import datetime

# ----- Configuration -----
SERVER = 'PERISA20'
DATABASE = 'Holoo1'
USERNAME = 'sa'
PASSWORD = 'Tnc@123'
LOG_FILE = 'update_prices.log'
ROUND_BASE = 10000

# ----- Input from user -----
try:
    yuan_price = int(input("Enter Yuan price in Rials (integer): ").strip())
except ValueError:
    print("Invalid input. Please enter an integer.")
    sys.exit(1)

# ----- Logging helper -----
def log(message):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} - {message}\n")

# ----- Connect to SQL Server -----
try:
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    )
    cursor = conn.cursor()
except Exception as e:
    log(f"[ERROR] Connection failed: {e}")
    print(f"[ERROR] Connection failed. See {LOG_FILE}")
    sys.exit(1)

# ----- Create function if not exists -----
try:
    cursor.execute("""
    IF OBJECT_ID('dbo.CalcPrice', 'FN') IS NOT NULL
        DROP FUNCTION dbo.CalcPrice;
    """)
    cursor.execute(f"""
    CREATE FUNCTION dbo.CalcPrice
    (
        @Place NVARCHAR(50),
        @Other NVARCHAR(50),
        @YuanPrice INT,
        @RoundBase DECIMAL(18,4)
    )
    RETURNS BIGINT
    AS
    BEGIN
        DECLARE @PlaceVal DECIMAL(18,4);
        DECLARE @OtherVal DECIMAL(18,4);

        SET @PlaceVal = CASE 
                            WHEN ISNUMERIC(REPLACE(@Place, '%', '')) = 1
                                 THEN CAST(REPLACE(@Place, '%', '') AS DECIMAL(18,4))
                            ELSE 0
                        END;

        SET @OtherVal = CASE 
                            WHEN ISNUMERIC(REPLACE(@Other, '%', '')) = 1
                                 AND CHARINDEX('%', @Other) > 0
                                 THEN (@PlaceVal * @YuanPrice) *
                                      (CAST(REPLACE(@Other, '%', '') AS DECIMAL(18,4)) / 100.0)
                            WHEN ISNUMERIC(REPLACE(@Other, '%', '')) = 1
                                 THEN CAST(REPLACE(@Other, '%', '') AS DECIMAL(18,4))
                            ELSE 0
                        END;

        RETURN CAST(ROUND(((@PlaceVal * @YuanPrice) + @OtherVal) / @RoundBase, 0) * @RoundBase AS BIGINT);
    END
    """)
    conn.commit()
except Exception as e:
    log(f"[ERROR] Creating function failed: {e}")
    print(f"[ERROR] Creating function failed. See {LOG_FILE}")
    sys.exit(1)

# ----- Update ARTICLE table -----
try:
    update_sql = f"""
    UPDATE [ARTICLE]
    SET 
        Sel_Price  = dbo.CalcPrice([Place], [Other9],  {yuan_price}, {ROUND_BASE}),
        Sel_Price2 = dbo.CalcPrice([Place], [Other10], {yuan_price}, {ROUND_BASE}),
        Sel_Price3 = dbo.CalcPrice([Place], [Other8],  {yuan_price}, {ROUND_BASE})
    WHERE 
        [Place]  IS NOT NULL AND LTRIM(RTRIM([Place]))  <> '' AND
        [Other8] IS NOT NULL AND LTRIM(RTRIM([Other8])) <> '' AND
        [Other9] IS NOT NULL AND LTRIM(RTRIM([Other9])) <> '' AND
        [Other10] IS NOT NULL AND LTRIM(RTRIM([Other10])) <> '';
    """
    cursor.execute(update_sql)
    conn.commit()
    rows_updated = cursor.rowcount
    log(f"[OK] Update successful. Rows updated: {rows_updated}")
    print(f"[OK] Update successful. Rows updated: {rows_updated}")
except Exception as e:
    log(f"[ERROR] Update failed: {e}")
    print(f"[ERROR] Update failed. See {LOG_FILE}")
finally:
    cursor.close()
    conn.close()
