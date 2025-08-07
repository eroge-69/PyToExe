# Thông tin kết nối Oracle
username = 'MDMS'
password = 'oracle123'
host = '10.179.0.10'
port = 1521
service = 'DBPLCRF'

# Tạo chuỗi kết nối
dsn = cx_Oracle.makedsn(host, port, service_name=service)

# Câu lệnh SQL
query = """
SELECT ROW_NUMBER ()
       OVER (PARTITION BY aa.MA_TRAM ORDER BY aa.tentram)
       AS STT, aa.*
FROM (
    WITH DM_DIEMDO AS (
        SELECT A.ASSETID, A.ORGID, A.SERIALNUM, B.METER_TYPE, A.ASSETDESC, B.KIEU_CTO, A.ASSETID_PARENT
        FROM A_ASSET A
        JOIN ZAG_MDMS_DIEMDO B ON A.ASSETID = B.OBJID
        WHERE A.TYPEID = 'DIEMDO' AND A.ORGID LIKE 'PB11%'
    ),
    DM_TRAM AS (
        SELECT A.ASSETID, A.ASSETDESC
        FROM A_ASSET A
        WHERE A.TYPEID = 'TRAM' AND A.ORGID LIKE 'PB11%'
    ),
    CHISO_3PHA_MIN AS (
        SELECT MA_DIEMDO, MIN(ROWID) AS MIN_ID
        FROM IMIS_VCUMVALS
        WHERE NGAYGIO >= TRUNC(SYSDATE) AND NGAYGIO < TRUNC(SYSDATE) + 1 AND MA_DIEMDO LIKE ('PB11' || '%')
        GROUP BY MA_DIEMDO
    )
    SELECT 
        B.assetid_parent MA_TRAM,
        C.assetdesc TENTRAM,
        B.assetid,
        B.assetdesc,
        B.SERIALNUM,
        B.meter_type,
        A.NGAYGIO,
        A.IMPORTKWH,
        A.Vol_phase,
        A.Curent_phase,
        NULL AS Bieu1,
        NULL AS Bieu2,
        NULL AS Bieu3,
        NULL AS bieugiao,
        NULL AS bieugiao1,
        NULL AS bieugiao2,
        NULL AS bieugiao3,
        0 AS V_B,
        0 AS A_B,
        0 AS V_C,
        0 AS A_C,
        A.C1 AS VOCONGGIAO,
        A.C2 AS VOCONGNHAN
    FROM DM_DIEMDO B
    JOIN DM_TRAM C ON C.ASSETID = B.ASSETID_PARENT
    LEFT JOIN (
        SELECT *
        FROM DCU_CHISO
        WHERE NGAYGIO >= TRUNC(SYSDATE) AND NGAYGIO < TRUNC(SYSDATE) + 1 AND MA_DIEMDO LIKE ('PB11' || '%')
    ) A ON A.ma_diemdo = B.assetid
    WHERE B.ORGID LIKE 'PB11%' AND B.KIEU_CTO = 'CTO1PHA'

    UNION ALL

    SELECT 
        B.assetid_parent MA_TRAM,
        C.assetdesc TENTRAM,
        B.assetid,
        B.assetdesc,
        B.SERIALNUM,
        B.METER_TYPE,
        A.NGAYGIO,
        A.IMPORTKWH,
        A.V_A,
        A.A_A,
        A.IMPBT,
        A.IMPCD,
        A.IMPTD,
        A.EXPORTKWH,
        A.EXPBT,
        A.EXPCD,
        A.EXPTD,
        A.V_B,
        A.A_B,
        A.V_C,
        A.A_C,
        A.C1 AS VOCONGGIAO,
        A.C2 AS VOCONGNHAN
    FROM DM_DIEMDO B
    JOIN DM_TRAM C ON C.ASSETID = B.ASSETID_PARENT
    LEFT JOIN (
        SELECT A.*
        FROM IMIS_VCUMVALS A
        JOIN CHISO_3PHA_MIN B ON B.MIN_ID = A.ROWID
    ) A ON A.ma_diemdo = B.assetid
    WHERE B.ORGID LIKE 'PB11%' AND B.KIEU_CTO IN ('CTO1PHA_3GIA', 'CTO3PHA')
) aa
"""

# Kết nối và chạy truy vấn
try:
    with cx_Oracle.connect(username, password, dsn) as conn:
        df = pd.read_sql(query, conn)
        df.to_excel("du_lieu_diem_do.xlsx", index=False)
        print("✅ Đã xuất dữ liệu thành công ra file: du_lieu_diem_do.xlsx")
except Exception as e:
    print("❌ Lỗi khi kết nối hoặc truy vấn:", e)
