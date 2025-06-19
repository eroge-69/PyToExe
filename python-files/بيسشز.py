import pyodbc
import pandas as pd
from sqlalchemy import create_engine

class SQLServerLocalConnection:
    def __init__(self, server='localhost', database='master', username='', password='', trusted_connection=True):
        """
        ����� ����� SQL Server ����
        
        :param server: ��� ������� (�������: localhost �� .\\SQLEXPRESS)
        :param database: ��� ����� �������� (�������: master)
        :param username: ��� �������� (������� ��� ��� Trusted_Connection=True)
        :param password: ���� ������ (�������)
        :param trusted_connection: ������� ������ Windows (�������: True)
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection
        self.connection = None
        self.engine = None
        
    def create_connection_string(self):
        """����� connection string �������"""
        if self.trusted_connection:
            return f"DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
        else:
            return f"DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
    
    def connect(self):
        """����� ����� ������ ��������"""
        try:
            conn_str = self.create_connection_string()
            self.connection = pyodbc.connect(conn_str)
            print("�� ������� ����� �� SQL Server!")
            return True
        except pyodbc.Error as e:
            print(f"��� �� �������: {e}")
            return False
    
    def create_sqlalchemy_engine(self):
        """����� ���� SQLAlchemy ��������� �� pandas"""
        try:
            if self.trusted_connection:
                conn_str = f"mssql+pyodbc://{self.server}/{self.database}?driver=SQL+Server&trusted_connection=yes"
            else:
                conn_str = f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver=SQL+Server"
            
            self.engine = create_engine(conn_str)
            print("�� ����� ���� SQLAlchemy �����!")
            return True
        except Exception as e:
            print(f"��� �� ����� ������: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """����� ������� ������ �������"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # ��� ��� ��������� �� ����� ���� ���� ������
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return results
            else:
                self.connection.commit()
                return {"message": "�� ����� ����� �����", "rows_affected": cursor.rowcount}
        except pyodbc.Error as e:
            print(f"��� �� ����� ���������: {e}")
            return None
    
    def test_connection(self):
        """������ ������� �������� ����"""
        query = "SELECT @@VERSION AS sql_version;"
        result = self.execute_query(query)
        if result:
            print("����� ������ �������:")
            print(result[0]['sql_version'])
            return True
        return False
    
    def get_tables_list(self):
        """������ ��� ����� ������� �� ����� ��������"""
        query = """
        SELECT 
            TABLE_SCHEMA AS schema_name,
            TABLE_NAME AS table_name,
            TABLE_TYPE AS table_type
        FROM 
            INFORMATION_SCHEMA.TABLES
        ORDER BY 
            TABLE_SCHEMA, TABLE_NAME;
        """
        return self.execute_query(query)
    
    def get_table_structure(self, table_name, schema_name='dbo'):
        """������ ��� ���� ���� ����"""
        query = f"""
        SELECT 
            COLUMN_NAME AS column_name,
            DATA_TYPE AS data_type,
            CHARACTER_MAXIMUM_LENGTH AS max_length,
            IS_NULLABLE AS is_nullable,
            COLUMN_DEFAULT AS column_default
        FROM 
            INFORMATION_SCHEMA.COLUMNS
        WHERE 
            TABLE_SCHEMA = '{schema_name}' AND 
            TABLE_NAME = '{table_name}'
        ORDER BY 
            ORDINAL_POSITION;
        """
        return self.execute_query(query)
    
    def close(self):
        """����� �������"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("�� ����� �������.")
        if self.engine:
            self.engine.dispose()
            self.engine = None

# ===== ���� ��������� =====
if __name__ == "__main__":
    # 1. ����� ����� �������� ������ Windows (Trusted Connection)
    print("\n--- ������ ������� ������ �������� Windows Authentication ---")
    local_conn = SQLServerLocalConnection(server='.\\SQLEXPRESS', database='master')
    
    if local_conn.connect():
        # ������ �������
        local_conn.test_connection()
        
        # ������ ��� ����� �������
        tables = local_conn.get_tables_list()
        print("\n������� �� ����� ��������:")
        for table in tables[:5]:  # ��� ��� 5 ����� ��� ��������
            print(f"{table['schema_name']}.{table['table_name']} ({table['table_type']})")
        
        # ��� ��� ���� ����� ��� ���� ��� ����
        if tables:
            first_table = tables[0]
            structure = local_conn.get_table_structure(first_table['table_name'], first_table['schema_name'])
            print(f"\n���� ���� {first_table['schema_name']}.{first_table['table_name']}:")
            for col in structure:
                print(f"- {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']})")
        
        # ������� SQLAlchemy �� pandas
        if local_conn.create_sqlalchemy_engine():
            query = "SELECT TOP 5 name, database_id, create_date FROM sys.databases"
            df = pd.read_sql(query, local_conn.engine)
            print("\n����� ��������� �������� pandas:")
            print(df)
        
        local_conn.close()
    
    # 2. ����� ����� �������� ��� ������ ����� ���� (��� ��� �����)
    print("\n--- ������ ������� �������� ��� ������ ����� ���� ---")
    auth_conn = SQLServerLocalConnection(
        server='localhost',
        database='master',
        username='your_username',
        password='your_password',
        trusted_connection=False
    )
    
    if auth_conn.connect():
        auth_conn.test_connection()
        auth_conn.close()