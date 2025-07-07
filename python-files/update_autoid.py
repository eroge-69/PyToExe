import pandas as pd
import sqlalchemy
import os
from config import *


def compare_using_both_databases(wg_connection_string, inf_connection_string, output_path, pagaotorenticodi,
                                 wg_schema=None, inf_schema=None):
    # Create database connections
    print("Connecting to databases...")
    wg_engine = sqlalchemy.create_engine(wg_connection_string)
    inf_engine = sqlalchemy.create_engine(inf_connection_string)

    # Extract data from WG database
    print("Extracting data from WG database...")
    # Include schema name in the table names if provided
    wg_schema_prefix = f"{wg_schema}." if wg_schema else ""

    wg_query = f"""
        select 
        (CASE when a.ID_ORIGEN = 12 then 0 when a.ID_ORIGEN = 14 then 8 when a.ID_ORIGEN = 13 then 9 when a.ID_ORIGEN = 15 then 10 when a.ID_ORIGEN = 16 then 11 ELSE a.ID_ORIGEN end)  as AUTOORICODI, 
        t.NRO_TARJETA as TARJENUME, 
        a.FECHA_AUTORIZACION AUTOFECHA,
        a.IMPORTE as AUTOIMPOR,
        (CASE WHEN a.ID_MONEDA = 32 then 1 WHEN a.ID_MONEDA = 840 then 2 else a.ID_MONEDA END) as MONECODI, 
        CASE WHEN a.ID_ESTADO = 0 THEN a.ID_ESTADO ELSE 3 END as ESTACODI, 
        a.ID_COMERCIO as COMERCODI, 
        a.COD_COMERCIO_EXTERNO as COMEREXTCODI, 
        CASE WHEN a.ID_COD_MOVIMIENTO = 1 THEN 1
             WHEN a.ID_COD_MOVIMIENTO = 9 THEN 3
             WHEN a.ID_COD_MOVIMIENTO = 2 THEN 5
             ELSE NULL
        END as PLANCODI, 
        a.COD_AUTO_ENTIDAD as AUTOCOMPRO,
        'DBO' as USUACODI, 
        0 as AUTOINTEIMPOR, 
        0 as AUTOINTEIVAIMPOR, 
        COALESCE(a.COMERCIO_DESCRIPCION,'Sin Descripción') as AUTOCOMERISODESCRI,
        a.ID_AUTORIZACION AS ID_AUTORIZACION_WG
        from {wg_schema_prefix}AUTORIZACION a 
        LEFT outer join {wg_schema_prefix}TARJETAS t on t.ID_ENTIDAD = a.ID_ENTIDAD and t.NRO_TARJETA = a.NRO_TARJETA  AND T.ID_CUENTA = A.ID_CUENTA
        WHERE a.ID_ESTADO IN (0, 2, 3, 5, 6)
        AND A.NRO_TARJETA = 'F1E1356711A3F7348434F19F4A9E5CEF'
        AND a.PRESENTACION_PROCESADA = 0
    """

    df1 = pd.read_sql(wg_query, wg_engine, dtype=object)
    df1.to_csv('autorizaciones_wg.csv')

    # Extract data from INF database
    print("Extracting data from INF database...")
    # Include schema name in the table names if provided
    inf_schema_prefix = f"{inf_schema}." if inf_schema else ""

    inf_query = f"""
        SELECT 
            AUTOORICODI,
            TARJENUME,
            AUTOFECHA,
            AUTOIMPOR,
            MONECODI,
            ESTACODI,
            COMERCODI,
            AUTOCOMERISOID AS COMEREXTCODI,
            PLANCODI,
            AUTOCOMPRO,            
            AUTOINTEIMPOR,
            AUTOINTEIVAIMPOR,
            AUTOCOMERISODESCRI,
            AUTOID AS ID_AUTORIZACION_INF
        FROM {inf_schema_prefix}AUTORIZACION a 
        WHERE PAGAOTORENTICODI = {pagaotorenticodi}
        AND TARJENUME = 'F1E1356711A3F7348434F19F4A9E5CEF'
    """

    df2 = pd.read_sql(inf_query, inf_engine, dtype=object)
    df2.to_csv('autorizaciones_inf.csv')
    # Common columns to merge on
    common_columns = ['tarjenume', 'autofecha', 'monecodi',
                      'autocompro','autocomerisodescri']

    # Merge the dataframes on common columns
    merged_df = pd.merge(df1, df2, on=common_columns, how='inner')

    # Select only the id_autorizacion columns for the final outputs
    result_df = merged_df[['id_autorizacion_wg', 'id_autorizacion_inf']]

    # Remove duplicates
    result_df = result_df.drop_duplicates()

    # Save to new CSV files
    result_df.to_csv(output_path, index=False)

    print(f"Successfully created merged CSV file at: {output_path}")
    print(f"Total records in merged file: {len(result_df)}")

def compare_using_only_infinitus(inf_connection_string, output_path, pagaotorenticodi,
                                 inf_schema=None):
    print("Connecting to databases...")
    inf_engine = sqlalchemy.create_engine(inf_connection_string)

    # Extract data from INF database
    print("Extracting data from INF database...")
    # Include schema name in the table names if provided
    inf_schema_prefix = f"{inf_schema}." if inf_schema else ""

    inf_query = f"""
        SELECT a.AUTOID ID_AUTORIZACION_INF, mw.ID_AUTORIZACION_WG, 'NO' AS PRESENTADA 
        FROM {inf_schema_prefix}AUTORIZACION a 
        INNER JOIN {inf_schema_prefix}MIGRAAUTORIZACIONES_WFG mw ON mw.INTARJENUME = a.TARJENUME 
            AND A.AUTOFECHA = MW.INAUTOFECHA 
            AND A.MONECODI = MW.INAUTOMONECODI 
            AND A.AUTOCOMPRO = MW.INAUTOCOMPRO -- AND AUTOCOMPRO = '138214'
            AND a.AUTOCOMERISODESCRI = mw.IAUTOCOMERISODESCRI 
            AND A.AUTOIMPOR*100 = MW.INAUTOIMPOR 
            AND A.AUTOINTEIMPOR = MW.IAUTOINTEIMPOR 
            AND a.AUTOINTEIVAIMPOR  = mw.IAUTOINTEIVAIMPOR 
            AND MW.ESTADO = 1        
        WHERE a.PAGAOTORENTICODI = {pagaotorenticodi}
                
        UNION ALL
        
        SELECT ConsumosMigradosAInf.AUTOID ID_AUTORIZACION_INF, CAST(ConsumosDesdeWFG.AUTOID AS varchar(100)) ID_AUTORIZACION_WG, 'SI' AS PRESENTADA
        FROM {inf_schema_prefix}MIGRACONSUMOS_WFG ConsumosDesdeWFG
        INNER JOIN {inf_schema_prefix}GENIALMIGRACONSUCUOTA ConsumosMigradosAInf ON 
                                 ConsumosDesdeWFG.MARCACODI           = ConsumosMigradosAInf.MARCACODI AND
                                 ConsumosDesdeWFG.SOLINUME            = ConsumosMigradosAInf.SOLINUME AND 
                                 ConsumosDesdeWFG.ADINUME             = ConsumosMigradosAInf.ADINUME AND 
                                 ConsumosDesdeWFG.CONSUFECHA          = ConsumosMigradosAInf.CONSUFECHA AND 
                                 ConsumosDesdeWFG.CONSUCOMPRO         = ConsumosMigradosAInf.CONSUCOMPRO AND 
                                 --ConsumosDesdeWFG.CONSUOPERCODI       = ConsumosMigradosAInf.CONSUOPERCODI AND 
                                 ConsumosDesdeWFG.COMEREXTCODI        = ConsumosMigradosAInf.COMEREXTCODI AND 
                                 ConsumosDesdeWFG.MONECODI            = ConsumosMigradosAInf.MONECODI AND 
                                 ConsumosDesdeWFG.CUOTASCANT          = ConsumosMigradosAInf.CUOTASCANT AND 
                                 ConsumosDesdeWFG.CONSUIMPORTOTAL     = ConsumosMigradosAInf.CONSUIMPORTOTAL AND 
                                 ConsumosDesdeWFG.CONSUTASA           = ConsumosMigradosAInf.CONSUTASA    
        INNER JOIN {inf_schema_prefix}AUTORIZACION a ON a.AUTOID = ConsumosMigradosAInf.AUTOID
        WHERE a.PAGAOTORENTICODI = {pagaotorenticodi}
    """

    df = pd.read_sql(inf_query, inf_engine, dtype=object)

    # Save to new CSV files
    df.to_csv(output_path, index=False)

    print(f"Successfully created mapping CSV file at: {output_path}")
    print(f"Total records mapped in file: {len(df)}")

if __name__ == "__main__":
    # Oracle connection strings
    # For Oracle, you can specify the schema in either:
    # 1. The connection string with username being the schema owner
    # 2. In the SQL queries by prefixing tables with schema name

    # Build connection strings

    #WG connection string is commented because now everything is in Infinitus
    #wg_connection_string = f"oracle+cx_oracle://{wg_db_username}:{wg_db_password}@{wg_db_host}:{wg_db_port}/?service_name={wg_db_service}"
    inf_connection_string = f"oracle+cx_oracle://{inf_db_username}:{inf_db_password}@{inf_db_host}:{inf_db_port}/?service_name={inf_db_service}"

    pagaotorenticodi = entidad

    # Output file path
    output_path = "autorizacion_mapping.csv"

    # Commented because now everything is in Infinitus
    # compare_using_both_databases(wg_connection_string, inf_connection_string, output_path,
    #                              pagaotorenticodi,
    #                              wg_db_schema, inf_db_schema)


    compare_using_only_infinitus(inf_connection_string, output_path, pagaotorenticodi,
                                 inf_db_schema)

