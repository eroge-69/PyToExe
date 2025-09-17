# animalitos.py - Sistema de análisis para Lotería Animalitos
import os
import pickle
from datetime import datetime

class AnalizadorAnimalitos:
    def __init__(self):
        self.animales = [
            "Aguila", "Buey", "Burro", "Camello", "Canguro",
            "Carpa", "Cotorra", "Elefante", "Gallo", "Gato",
            "León", "Lobo", "Mariposa", "Perro", "Pescado",
            "Pez", "Rana", "Ratón", "Serpiente", "Tigre"
        ]
        self.frecuencias = {animal: 0 for animal in self.animales}
        self.total_resultados = 0
        self.historico = []
        self.ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cargar_datos()
    
    def guardar_datos(self):
        datos = {
            'frecuencias': self.frecuencias,
            'total_resultados': self.total_resultados,
            'historico': self.historico,
            'ultima_actualizacion': self.ultima_actualizacion
        }
        try:
            with open('animalitos_data.dat', 'wb') as f:
                pickle.dump(datos, f)
        except Exception as e:
            print(f"Error guardando datos: {e}")
    
    def cargar_datos(self):
        try:
            if os.path.exists('animalitos_data.dat'):
                with open('animalitos_data.dat', 'rb') as f:
                    datos = pickle.load(f)
                    self.frecuencias = datos['frecuencias']
                    self.total_resultados = datos['total_resultados']
                    self.historico = datos['historico']
                    self.ultima_actualizacion = datos['ultima_actualizacion']
        except:
            pass
    
    def validar_animal(self, animal):
        return animal.capitalize() in self.animales
    
    def actualizar_frecuencias(self, nuevos_resultados):
        resultados_validos = []
        for res in nuevos_resultados:
            animal = res.strip().capitalize()
            if self.validar_animal(animal):
                self.frecuencias[animal] += 1
                resultados_validos.append(animal)
                self.total_resultados += 1
                self.historico.append(animal)
        self.ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.guardar_datos()
        return resultados_validos
    
    def calcular_probabilidades(self):
        probabilidades = {}
        for animal, freq in self.frecuencias.items():
            if self.total_resultados > 0:
                probabilidades[animal] = freq / self.total_resultados
            else:
                probabilidades[animal] = 0
        return probabilidades
    
    def get_top_animales(self, n=5):
        probabilidades = self.calcular_probabilidades()
        return sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def get_estadisticas(self):
        probabilidades = self.calcular_probabilidades()
        animal_mas_frecuente, prob_max = max(probabilidades.items(), key=lambda x: x[1])
        return {
            'total_resultados': self.total_resultados,
            'animal_mas_probable': animal_mas_frecuente,
            'probabilidad_maxima': prob_max,
            'top_5': self.get_top_animales(5),
            'animales_sin_salir': [animal for animal in self.animales if self.frecuencias[animal] == 0],
            'ultima_actualizacion': self.ultima_actualizacion
        }
    
    def mostrar_estadisticas(self):
        stats = self.get_estadisticas()
        print(f"\n{'='*60}")
        print("🎰 SISTEMA DE ANÁLISIS DE LOTERÍA ANIMALITOS")
        print(f"{'='*60}")
        print(f"📊 Total de resultados: {stats['total_resultados']}")
        print(f"🕐 Última actualización: {stats['ultima_actualizacion']}")
        print(f"🏆 Animal más probable: {stats['animal_mas_probable']} ({stats['probabilidad_maxima']:.2%})")
        print(f"\n📈 TOP 5 ANIMALES:")
        for i, (animal, prob) in enumerate(stats['top_5'], 1):
            print(f"  {i}. {animal}: {prob:.2%}")
        if stats['animales_sin_salir']:
            print(f"\n❌ Animales que no han salido: {', '.join(stats['animales_sin_salir'])}")
        print(f"{'='*60}")

    def reiniciar_datos(self):
        self.frecuencias = {animal: 0 for animal in self.animales}
        self.total_resultados = 0
        self.historico = []
        self.ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.guardar_datos()
        print("✅ Todos los datos han sido reiniciados.")

def main():
    print("🎰 Iniciando sistema de análisis de Lotería Animalitos...")
    analizador = AnalizadorAnimalitos()
    
    while True:
        try:
            analizador.mostrar_estadisticas()
            print("\n💡 OPCIONES:")
            print("1. Ingresar nuevos resultados")
            print("2. Reiniciar todos los datos")
            print("3. Salir")
            opcion = input("\nSeleccione una opción (1-3): ").strip()
            
            if opcion == "1":
                entrada = input("\n🎯 Ingrese resultados separados por coma: ").strip()
                if entrada:
                    nuevos_resultados = [x.strip() for x in entrada.split(",")]
                    resultados_procesados = analizador.actualizar_frecuencias(nuevos_resultados)
                    if resultados_procesados:
                        print(f"✅ Resultados procesados: {', '.join(resultados_procesados)}")
            
            elif opcion == "2":
                confirmacion = input("¿Está seguro de reiniciar todos los datos? (s/n): ").strip().lower()
                if confirmacion == 's':
                    analizador.reiniciar_datos()
            
            elif opcion == "3":
                print("👋 Terminando sistema. ¡Buena suerte!")
                break
            
            else:
                print("⚠️  Opción no válida.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()