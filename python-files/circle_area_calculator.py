import math
import sys

def oblicz_pole_kola(promien):
    """
    Oblicza pole koła dla podanego promienia.
    
    Args:
        promien (float): Promień koła
        
    Returns:
        float: Pole koła
    """
    if promien < 0:
        raise ValueError("Promień nie może być ujemny!")
    
    return math.pi * promien ** 2

def main():
    print("=" * 50)
    print("    KALKULATOR POLA KOŁA")
    print("=" * 50)
    
    while True:
        try:
            print("\nOpcje:")
            print("1. Oblicz pole koła")
            print("2. Wyjście")
            
            wybor = input("\nWybierz opcję (1-2): ").strip()
            
            if wybor == "1":
                promien_str = input("Podaj promień koła: ").strip()
                
                # Zamiana przecinka na kropkę dla polskich użytkowników
                promien_str = promien_str.replace(",", ".")
                
                promien = float(promien_str)
                pole = oblicz_pole_kola(promien)
                
                print(f"\n📊 WYNIKI:")
                print(f"   Promień: {promien}")
                print(f"   Pole koła: {pole:.6f}")
                print(f"   Pole koła (zaokrąglone): {pole:.2f}")
                
                # Dodatkowe informacje
                obwod = 2 * math.pi * promien
                print(f"   Obwód koła: {obwod:.2f}")
                
            elif wybor == "2":
                print("\nDo widzenia!")
                sys.exit(0)
                
            else:
                print("❌ Nieprawidłowy wybór! Wybierz 1 lub 2.")
                
        except ValueError as e:
            if "could not convert" in str(e):
                print("❌ Błąd: Podaj prawidłową liczbę!")
            else:
                print(f"❌ Błąd: {e}")
        except KeyboardInterrupt:
            print("\n\nProgram przerwany przez użytkownika.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    main()
