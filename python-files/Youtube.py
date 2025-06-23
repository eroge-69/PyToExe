import os
import json
from pytube import YouTube
from pytube.exceptions import VideoPrivate, MembersOnly, VideoUnavailable
import browser_cookie3

def download_members_only_video(url, output_path='./'):
    """Descarga videos exclusivos para miembros usando cookies de autenticación"""
    try:
        # Obtener cookies del navegador
        cookies = browser_cookie3.load(domain_name='youtube.com')
        cookie_dict = {c.name: c.value for c in cookies}
        
        # Configurar YouTube con cookies
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True,
            cookies=cookie_dict
        )
        
        # Seleccionar mejor stream disponible
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            print("TEAM GTX: No se encontró stream compatible")
            return False
        
        print(f"\nTEAM GTX: Video exclusivo para miembros")
        print(f"🔒 Título: {yt.title}")
        print(f"👤 Canal: {yt.author}")
        print(f"⏱ Duración: {yt.length//60}:{yt.length%60:02d}")
        print(f"💾 Tamaño estimado: {stream.filesize_mb:.2f} MB")
        print("\n⬇️ Descargando contenido privado...")
        
        # Descargar video
        output_file = stream.download(output_path)
        print(f"\n✅ TEAM GTX: Descarga completada - {os.path.basename(output_file)}")
        return True
        
    except (VideoPrivate, MembersOnly):
        print("\n❌ TEAM GTX: Error - Acceso denegado a contenido para miembros")
        print("Solución: Exporta cookies de sesión válidas desde tu navegador")
        return False
    except VideoUnavailable:
        print("\n❌ TEAM GTX: Video no disponible o eliminado")
        return False
    except Exception as e:
        print(f"\n💥 TEAM GTX: Error crítico - {str(e)}")
        return False

def main():
    print("\n" + "="*50)
    print("🔥 TEAM GTX - MEMBERS VIDEO DOWNLOADER 🔥")
    print("="*50 + "\n")
    
    while True:
        url = input("Ingresa la URL del video para miembros: ").strip()
        if url.lower() in ['exit', 'salir', 'q']:
            break
            
        if 'youtube.com' not in url and 'youtu.be' not in url:
            print("❌ URL de YouTube inválida")
            continue
            
        download_members_only_video(url)
        
        continuar = input("\n¿Descargar otro video? (s/n): ").lower()
        if continuar != 's':
            break

if __name__ == "__main__":
    main()
    print("\n👋 Programa finalizado por TEAM GTX")