import numpy as np
from tabulate import tabulate

def solicitar_valor_float(message):
    valueInput = float(input(message))
    return valueInput

def solicitar_valor_int(message):
    valueInput = int(input(message))
    return valueInput

def solicitar_valor_string(message):
    valueInput = input(message).upper()
    return valueInput

def solicitar_valor_multiples(message, cantidad):
    datos = []

    for i in range(cantidad):
        valueInput = float(input(f"{message} #{i + 1} => "))
        datos.append(valueInput)

    return datos

def calcularFcPrimaConDataEstadistica(fc) :
    k = 0.0
    desviacionEstandar = 0.0
    datos = []

    # Se ingresa la cantidad de intentos
    cantidadIntentos = solicitar_valor_int('Ingrese la cantidad de Intentos (15 - 20 - 25 - 30) => ')

    # Se determina el K
    if( cantidadIntentos == 15 ) :
        k = 1.16
    elif ( cantidadIntentos == 20 ) :
        k = 1.08
    elif ( cantidadIntentos == 25 ) :
        k = 1.03
    elif ( cantidadIntentos == 30 ) :
        k = 1.00
    
    datos = solicitar_valor_multiples('Favor ingresar el valor', cantidadIntentos)

    # Calcular la desviacion estandar
    desviacionEstandar = np.std(datos, ddof=1)

    # Se calcula FC Prima
    if( fc <= 35 ) :
        result1 = fc + 1.34 * k * desviacionEstandar
        result2 = fc + 2.33 * k * desviacionEstandar - 3.5
        if( result1 > result2 ) :
            return result1
        else :
            return result2
    elif( fc > 35 ) :
        result1 = fc + 1.34 * k * desviacionEstandar
        result2 = 0.90 * fc + 2.33 * k * desviacionEstandar
        if( result1 > result2 ) :
            return result1
        else :
            return result2

def calcularFcPrimaSinDataEstadistica(fc) :
    
    if ( fc < 21 ) :
        return fc + 7
    elif ( fc >= 21 and fc < 35 ) :
        return fc + 8
    elif ( fc > 35 ) :
        return (1.10 * fc) + 5

def calcularPesoAguaPorcentajeAire(asentamiento, tmn) :

    datostmn = {
        "9,5": "207,228,237,243",
        "12,5": "199,216,222,228",
        "19": "190,205,207,216",
        "37,5" : "166,178,181,190"
    }

    datosporcentajeAire = {
        "9,5": "3",
        "12,5": "2.5",
        "19": "2",
        "37,5" : "1"
    }

    if( asentamiento >= 25 and asentamiento <= 50) :
        
        if( tmn == 9.5 ):
            pesoAgua = datostmn["9,5"].split(',')[0]
            porcentajeAire = datosporcentajeAire["9,5"]
        elif( tmn == 12.5 ) :
            pesoAgua = datostmn["12,5"].split(',')[0]
            porcentajeAire = datosporcentajeAire["12,5"]
        elif( tmn == 19 ) :
            pesoAgua = datostmn["19"].split(',')[0]
            porcentajeAire = datosporcentajeAire["19"]
        elif( tmn == 37.5 ) :
            pesoAgua = datostmn["37,5"].split(',')[0]
            porcentajeAire = datosporcentajeAire["37,5"]

    elif ( asentamiento >= 75 and asentamiento <= 100 ) :
        
        if( tmn == 9.5 ):
            pesoAgua = datostmn["9,5"].split(',')[1]
            porcentajeAire = datosporcentajeAire["9,5"]
        elif( tmn == 12.5 ) :
            pesoAgua = datostmn["12,5"].split(',')[1]
            porcentajeAire = datosporcentajeAire["12,5"]
        elif( tmn == 19 ) :
            pesoAgua = datostmn["19"].split(',')[1]
            porcentajeAire = datosporcentajeAire["19"]
        elif( tmn == 37.5 ) :
            pesoAgua = datostmn["37,5"].split(',')[1]
            porcentajeAire = datosporcentajeAire["37,5"]

    elif ( asentamiento >= 125 and asentamiento <= 150 ) :
        
        if( tmn == 9.5 ):
            pesoAgua = datostmn["9,5"].split(',')[2]
            porcentajeAire = datosporcentajeAire["9,5"]
        elif( tmn == 12.5 ) :
            pesoAgua = datostmn["12,5"].split(',')[2]
            porcentajeAire = datosporcentajeAire["12,5"]
        elif( tmn == 19 ) :
            pesoAgua = datostmn["19"].split(',')[2]
            porcentajeAire = datosporcentajeAire["19"]
        elif( tmn == 37.5 ) :
            pesoAgua = datostmn["37,5"].split(',')[2]
            porcentajeAire = datosporcentajeAire["37,5"]

    elif ( asentamiento >= 151 and asentamiento <= 175 ) :

        if( tmn == 9.5 ):
            pesoAgua = datostmn["9,5"].split(',')[3]
            porcentajeAire = datosporcentajeAire["9,5"]
        elif( tmn == 12.5 ) :
            pesoAgua = datostmn["12,5"].split(',')[3]
            porcentajeAire = datosporcentajeAire["12,5"]
        elif( tmn == 19 ) :
            pesoAgua = datostmn["19"].split(',')[3]
            porcentajeAire = datosporcentajeAire["19"]
        elif( tmn == 37.5 ) :
            pesoAgua = datostmn["37,5"].split(',')[3]
            porcentajeAire = datosporcentajeAire["37,5"]
    
    return float(pesoAgua), float(porcentajeAire)

def calcularAC(fcPrima, pesoAgua) :
    ac = 0.0
    c = 0.0
    yCero = 0.0
    yUno = 0.0
    xCero = 0.0
    xUno = 0.0

    dataBase = {
        "48" : "0.34",
        "41" : "0.41",
        "35" : "0.48",
        "27" : "0.57",
        "21" : "0.68",
        "14" : "0.82"
    }

    if( fcPrima == 48 or fcPrima == 41 or fcPrima == 35 or fcPrima == 27 or fcPrima == 21 or fcPrima == 14 ) :
        ac = float(dataBase[str(fcPrima)])
    else :
        if(fcPrima > 14 and fcPrima < 21):
            yCero = float(dataBase["21"])
            yUno = float(dataBase["14"])
            xCero = 21
            xUno = 14
        elif (fcPrima > 21 and fcPrima < 27) :
            yCero = float(dataBase["27"])
            yUno = float(dataBase["21"])
            xCero = 27
            xUno = 21
        elif (fcPrima > 27 and fcPrima < 35) :
            yCero = float(dataBase["35"])
            yUno = float(dataBase["27"])
            xCero = 35
            xUno = 27
        elif (fcPrima > 35 and fcPrima < 41) :
            yCero = float(dataBase["41"])
            yUno = float(dataBase["35"])
            xCero = 41
            xUno = 35
        elif (fcPrima > 41 and fcPrima < 48) :
            yCero = float(dataBase["48"])
            yUno = float(dataBase["41"])
            xCero = 48
            xUno = 41

        ac = round(yCero + ( (yUno - yCero) / (xUno - xCero) ) * (fcPrima - xCero), 2)

    c = round( round(pesoAgua, 2) / ac, 2)

    return ac , c

def calcularAGAF(tmn, mf) :
    volumenMasivoAG = 0.0

    datosVolumenAG = {
        "9,5": "0.50-0.48-0.46-0.44",
        "12,5": "0.59-0.57-0.55-0.53",
        "19": "0.66-0.64-0.62-0.60",
        "37,5" : "0.75-0.73-0.71-0.69"
    }

    if( mf == 2.40) :
        
        if( tmn == 9.5 ):
            volumenMasivoAG = datosVolumenAG["9,5"].split('-')[0]
        elif( tmn == 12.5 ) :
            volumenMasivoAG = datosVolumenAG["12,5"].split('-')[0]
        elif( tmn == 19 ) :
            volumenMasivoAG = datosVolumenAG["19"].split('-')[0]
        elif( tmn == 37.5 ) :
            volumenMasivoAG = datosVolumenAG["37,5"].split('-')[0]

    elif ( mf == 2.60 ) :

        if( tmn == 9.5 ):
            volumenMasivoAG = datosVolumenAG["9,5"].split('-')[1]
        elif( tmn == 12.5 ) :
            volumenMasivoAG = datosVolumenAG["12,5"].split('-')[1]
        elif( tmn == 19 ) :
            volumenMasivoAG = datosVolumenAG["19"].split('-')[1]
        elif( tmn == 37.5 ) :
            volumenMasivoAG = datosVolumenAG["37,5"].split('-')[1]

    elif ( mf == 2.80 ) :

        if( tmn == 9.5 ):
            volumenMasivoAG = datosVolumenAG["9,5"].split('-')[2]
        elif( tmn == 12.5 ) :
            volumenMasivoAG = datosVolumenAG["12,5"].split('-')[2]
        elif( tmn == 19 ) :
            volumenMasivoAG = datosVolumenAG["19"].split('-')[2]
        elif( tmn == 37.5 ) :
            volumenMasivoAG = datosVolumenAG["37,5"].split('-')[2]

    elif ( mf == 3.00 ) :

        if( tmn == 9.5 ):
            volumenMasivoAG = datosVolumenAG["9,5"].split('-')[3]
        elif( tmn == 12.5 ) :
            volumenMasivoAG = datosVolumenAG["12,5"].split('-')[3]
        elif( tmn == 19 ) :
            volumenMasivoAG = datosVolumenAG["19"].split('-')[3]
        elif( tmn == 37.5 ) :
            volumenMasivoAG = datosVolumenAG["37,5"].split('-')[3]

    pesoUnitarioTotalSeco = solicitar_valor_int("Favor ingresar el Peso Unitario Total Compatado de AG => ")
    porcentajeAgua = solicitar_valor_float("Favor ingresar el Porcentaje de Agua (W) de AG => ")

    yb = pesoUnitarioTotalSeco / ( 1 + (porcentajeAgua / 100) ) / 1

    pesoAG = float(yb) * float(volumenMasivoAG)
    pesoAF = pesoAG * 0.75

    return round(pesoAG, 2), round(pesoAF, 2)

def main():

    print("========= Bienvenido ===========")
    # INICIO: Primera Parte Calcular Fc Prima
    fcPrima = 0.0

    fc = solicitar_valor_float("Favor Ingresar el Fc => ")

    hasDataEstadistico = solicitar_valor_string("Cuenta con Datos Estadisticos (SI / NO) => ")

    if( hasDataEstadistico == "NO" ) :
        fcPrima = round(calcularFcPrimaSinDataEstadistica(fc), 2)
    elif ( hasDataEstadistico == "SI" ) :
        fcPrima = round(calcularFcPrimaConDataEstadistica(fc), 2)
    else :
        print('Debe digital un valor entre SI / NO')
    
    print(f"El f`cr es: {fcPrima}")
    # FIN: Primera Parte Calcular Fc Prima

    # INICIO: Segunda Parte Peso Agua, porcentaje de Aire
    pesoAgua = 0
    porcentajeAire = 0.0
    asentamiento = solicitar_valor_int("Favor ingresar el Asentamiento => ")
    tmn = solicitar_valor_float("Favor ingresar el Tamaño Maximo Nominal (TMN) (9.5 - 12.5 - 19 - 37.5) => ")

    pesoAgua, porcentajeAire = calcularPesoAguaPorcentajeAire(asentamiento, tmn)

    print(f"El Peso de Agua es: {pesoAgua}")
    print(f"El Porcentaje de Aire es: {porcentajeAire}")
    # FIN: Segunda Parte Peso Agua, porcentaje de Aire

    # INICIO: Tercera Parte Relacion AC  
    ac , c = calcularAC(fcPrima , pesoAgua)

    print(f"La relacion A/C es: {ac}")
    print(f"El Peso del cemento es: {c}")
    # FIN: Tercera Parte Relacion AC

    # INICIO: Cuarta Parte A.G y A.F
    mf = solicitar_valor_float("Favor ingresar el Modulo de Finura (MF) (2.40 - 2.60 - 2.80 - 3.00) => ")

    gsAG = solicitar_valor_float("Favor ingresar el gravedad especifica aparente (gsAG) => ")
    gsAF = solicitar_valor_float("Favor ingresar el gravedad especifica aparente (gsAF) => ")
    
    pesoAG , pesoAF = calcularAGAF(tmn, mf)
    
    print(f"El Peso Agregado Grueso es: {pesoAG}")
    print(f"El Peso Agregado Fino es: {pesoAF}")

    # FIN: Cuarta Parte A.G y A.F

    # INICIO: Mostrar resultado
    dosificacionArena = round(pesoAF / c, 2)
    dosificacionPiedra = round(pesoAG / c, 2)
    dosificacionAgua = round(pesoAgua / c, 2)
    datos = [
        ["Cemento"         , "Seco", c              , "1"],
        ["Arena"           , "Seco", pesoAF         , dosificacionArena],
        ["Piedra"          , "Seco", pesoAG         , dosificacionPiedra],
        ["Agua"            , " - " , pesoAgua       , dosificacionAgua],
        ["Porcentaje Agua" , "%"   , porcentajeAire , " - "]
    ]

    cabeceras = ["Material", "Condiccion", "Peso (KG)", "Dosificacion"]

    print(tabulate(datos, headers=cabeceras, tablefmt="grid", floatfmt=".2f"))
    print("========= Hasta Luego ===========")
    # FIN: Mostrar resultado

main()
