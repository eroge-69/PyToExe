# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 01:19:49 2024

@author: PC
"""

"""
El modulo 'asignacion_poligonos' se encarga principalmente de la asignación de
poligonos a todos los registros que conforman el dataset, de un total de 10
unidades del transporte público.
La ruta fue seccionada en polígonos con el fin de implementar un algoritmo que
estimara la dirección del viaje de la unidad de transporte, dado un subconjunto
de puntos.
"""

import pandas as pd
import fiona
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

#Adicion del driver que soporta los archivos KML
fiona.drvsupport.supported_drivers['KML'] = 'rw'

def asignacion_poligonos(control_fecha,file_path_placas_ids,file_path_dataset_fase_1,file_path_lines_kml,file_path_raiz):
    
    #Lectura de lista de placas como dataframe
    data_lista_placas = pd.read_csv(file_path_placas_ids,dtype={'Placa': 'str'})
    lista_placas = [] #
    
    #Ciclo para construir el arreglo con el listado del total de placas con el que se trabajara
    for index_placas, row_placas in data_lista_placas.iterrows():
        lista_placas.append(row_placas['Placa'])
    
    #Carga de CSV como dataframe
    data_frame = pd.read_csv(file_path_dataset_fase_1,parse_dates=[0],dtype={'Placa': 'str','Poligono_'+lista_placas[0]: 'str','Poligono_'+lista_placas[1]: 'str',
                                                              'Poligono_'+lista_placas[2]: 'str','Poligono_'+lista_placas[3]: 'str',
                                                              'Poligono_'+lista_placas[4]: 'str','Poligono_'+lista_placas[5]: 'str',
                                                              'Poligono_'+lista_placas[6]: 'str','Poligono_'+lista_placas[7]: 'str',
                                                              'Poligono_'+lista_placas[8]: 'str','Poligono_'+lista_placas[9]: 'str'});
    #Carga del KML como geodataframe
    geo_data_frame_ruta = gpd.read_file(file_path_lines_kml, driver='KML')
    
    #Separacion de la información de la ruta del geodataframe
    linea_upiita_raza = geo_data_frame_ruta.loc[0,'geometry']
    linea_raza_upiita = geo_data_frame_ruta.loc[1,'geometry']
    poligonos = geo_data_frame_ruta.loc[2:,['Name','geometry']]
    
    #Ordenamiento del dataframe
    data_frame = data_frame.sort_values(['Fecha_Hora'])
    
    #Separacion de datos
    manana = control_fecha + " 06:00:00"
    tarde = control_fecha + " 23:00:00"
    manana = datetime.strptime(manana, "%Y_%m_%d %H:%M:%S")
    tarde = datetime.strptime(tarde, "%Y_%m_%d %H:%M:%S")
    data_frame_laboral = data_frame.loc[(data_frame.Fecha_Hora > manana) & (data_frame.Fecha_Hora < tarde)]
    data_frame_no_laboral = data_frame.loc[(data_frame.Fecha_Hora <= manana) | (data_frame.Fecha_Hora >= tarde)]
    
    data_frame_laboral = data_frame_laboral.sort_values(['Fecha_Hora'])
    #Ciclo para asignar la pertenencia de poligonos a cada punto del dataset
    for index_placas, row_placas in data_lista_placas.iterrows():
        
        nombre_poligono = 'Poligono_' + row_placas['Placa']
        nombre_latitud = 'Latitud_' + row_placas['Placa']
        nombre_longitud = 'Longitud_' + row_placas['Placa']
        
        #Asignacion de poligonos
        for index_poligonos, row_poligonos in data_frame_laboral.iterrows():
            if pd.isna(row_poligonos[nombre_poligono]):
                punto_actual = Point(row_poligonos[nombre_longitud],row_poligonos[nombre_latitud])
                contador_poligonos = 2
                
                while (True):
                    if(poligonos.loc[contador_poligonos,'geometry'].contains(punto_actual)):
                        data_frame_laboral.loc[index_poligonos,nombre_poligono] = poligonos.loc[contador_poligonos,'Name']
                        break
                    elif(contador_poligonos == 20):
                        break
                    else:
                        contador_poligonos += 1
    
    #Union de dataframes
    data_frame_completo = pd.concat([data_frame_laboral,data_frame_no_laboral])
    
    #Ordenamiento del dataframe
    data_frame_completo = data_frame_completo.sort_values(['Fecha_Hora'])
    
    #Asignación de la columna Fecha_Hora como índice
    data_frame_completo = data_frame_completo.set_index(['Fecha_Hora'])
    
    data_frame_completo.to_csv(file_path_raiz + control_fecha + "/Dataset_interpolado_10_placas_fase_2.csv")