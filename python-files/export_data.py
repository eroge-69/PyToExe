# export_data.py

import oracledb
import pandas as pd
import sys
import os
import configparser

def read_config(config_path='export_data.conf'):
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        raise FileNotFoundError("Configuration file not found.")
    config.read(config_path)
    return config['oracle']['user'], config['oracle']['password'], config['oracle']['dsn']

def main():
    try:
        if len(sys.argv) != 3:
            print("Usage: export_data.exe \"<SQL_QUERY>\" \"<OUTPUT_FILE_PATH>\"")
            return

        sql_query = sys.argv[1]
        output_file = sys.argv[2]

        user, password, dsn = read_config()

        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        df = pd.read_sql(sql_query, conn)

        if output_file.lower().endswith('.csv'):
            df.to_csv(output_file, index=False)
        elif output_file.lower().endswith('.xlsx'):
            df.to_excel(output_file, index=False, engine='xlsxwriter')

        print("Success")

    except Exception as e:
        print("Error:", e)

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
