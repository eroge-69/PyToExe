import requests
import pyodbc
import time

class DeleteTerminal:
    def __init__(self):
        self.url_base = 'http://172.19.7.177/ntmss/api/v1/terminal/'
        self.headers = {
            'Content-Type': "application/xml",
            'ntms-api-username': "PEPAPI"
        }

    def convert_tid_to_api_id(self, tid: str) -> str:
        if len(tid) < 2:
            return None
        tid_no_first = tid[1:]
        api_id = tid_no_first[:-1] + '01'
        return api_id

    def delete_terminal(self, tid: str):
        api_id = self.convert_tid_to_api_id(tid)
        if not api_id:
            print(f"Nieprawidłowy Terminal ID: {tid}")
            return False
        url = self.url_base + api_id
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 200:
            print(f"Terminal {tid} (API ID: {api_id}) został usunięty.")
            return True
        else:
            print(f"Błąd {response.status_code} podczas usuwania terminala {tid} (API ID: {api_id})")
            print("Treść odpowiedzi:", response.text)
            return False

SERVER = 'tposmgr'
DATABASE = 'cro_device_mgr'
DRIVER = '{ODBC Driver 17 for SQL Server}'

def wykonaj_zapytanie(tid):
    sql_script = f"""
    USE [{DATABASE}];

    CREATE TABLE #tPP (tid VARCHAR(8));
    INSERT INTO #tPP VALUES ('{tid}');

    DECLARE @tid VARCHAR(8), @c INT = 1;
    DECLARE crt CURSOR FAST_FORWARD LOCAL FOR
        SELECT tid
        FROM #tPP t
        INNER JOIN VCM_POS_DIRECTORY d WITH (NOLOCK) ON t.tid = d.TRM_ID
        WHERE d.TRM_DOWNLOADED <> 'B';

    OPEN crt;

    FETCH NEXT FROM crt INTO @tid;
    WHILE @@FETCH_STATUS = 0
    BEGIN
        PRINT 'TID ' + CAST(@c AS VARCHAR(100)) + ' : ' + @tid;
        EXEC cro_devmgr_generatefilesforTID '', @tid, 'Y';
        SET @c = @c + 1;
        FETCH NEXT FROM crt INTO @tid;
    END;

    CLOSE crt;
    DEALLOCATE crt;

    DROP TABLE #tPP;
    """

    try:
        conn = pyodbc.connect(
            f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
        )
        cursor = conn.cursor()
        cursor.execute(sql_script)

        messages = []
        while True:
            if cursor.messages:
                for msg in cursor.messages:
                    messages.append(msg[1])
            if cursor.nextset():
                continue
            break

        conn.commit()
        return True, messages

    except Exception as e:
        return False, [str(e)]

def main():
    tid = input("Podaj TID (dokładnie 8 cyfr): ").strip()
    if not (len(tid) == 8 and tid.isdigit()):
        print("TID musi mieć dokładnie 8 cyfr.")
        return

    deleteTID = DeleteTerminal()
    if not deleteTID.delete_terminal(tid):
        print("Przerwano z powodu błędu podczas usuwania terminala.")
        return

    print("Czekam 10 sekund przed wykonaniem zapytania SQL...")
    time.sleep(10)

    success, messages = wykonaj_zapytanie(tid)
    if success:
        print(f"TID {tid} wysłany poprawnie.")
        if messages:
            print("\n Wiadomości SQL Server:")
            for m in messages:
                print(" -", m)
    else:
        print(f"Błąd podczas wykonywania zapytania SQL: {messages[0][:250]}")

if __name__ == "__main__":
    main()
