import os
import subprocess
import time
from pathlib import Path

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
                                                                                      
                       ,--.                                  ,-.----.                 
    ,---,            ,--.'|                           ,---,. \    /  \     .--.--.    
  .'  .' `\      ,--,:  : |         ,---,           ,'  .' | |   :    \   /  /    '.  
,---.'     \  ,`--.'`|  ' :        /_ ./|         ,---.'   | |   |  .\ : |  :  /`. /  
|   |  .`\  | |   :  :  | |  ,---, |  ' :         |   |   .' .   :  |: | ;  |  |--`   
:   : |  '  | :   |   \ | : /___/ \.  : |         :   :  :   |   |   \ : |  :  ;_     
|   ' '  ;  : |   : '  '; |  .  \  \ ,' '         :   |  |-, |   : .   /  \  \    `.  
'   | ;  .  | '   ' ;.    ;   \  ;  `  ,'         |   :  ;/| ;   | |`-'    `----.   \ 
|   | :  |  ' |   | | \   |    \  \    '          |   |   .' |   | ;       __ \  \  | 
'   : | /  ;  '   : |  ; .'     '  \   |          '   :  '   :   ' |      /  /`--'  / 
|   | '` ,/   |   | '`--'        \  ;  ;          |   |  |   :   : :     '--'.     /  
;   :  .'     '   : |             :  \  \         |   :  \   |   | :       `--'---'   
|   ,.'       ;   |.'              \  ' ;         |   | ,'   `---'.|                  
'---'         '---'                 `--`          `----'       `---`                  
                                                                                      

    ▶ DNY'S FPS BOOSTER FOR FIVEM - v1.0
    ----------------------------------------------------------
    """
    print(banner)

def create_autoexec():
    fivem_path = Path(os.getenv('LOCALAPPDATA')) / 'FiveM' / 'FiveM.app'
    cfg_path = fivem_path / 'autoexec.cfg'
    cfg_content = """
cl_drawfps true
r_drawmodeldecals 0
r_drawtracers 0
r_decal_cullsize 100
r_lightshafts 0
r_mipbias 1.0
r_shadows 0
r_sunshafts 0
r_aaLevel 0
r_anisotropicFiltering 0
r_lodscale 0.25
r_maxmodeldecal 0
r_maxlodscale 1.0
r_motionblur 0
r_postProcess 0
r_useDepthOfField 0
r_waterRefractions 0
r_waterReflections 0
r_skipPresent 1
r_exposureGain 0.2
r_exposureValue 0.2
r_textureStreaming 0
r_shadowblur 0
r_reflectionquality 0
r_particlequality 0
r_scale 0.25
cl_lodscale 0.25
cl_detaildist 1.0
cl_detailfade 1.0
profile_mp_lod 0.0
profile_singleplayer_lod 0.0
ui_streamingDistance 100.0
cl_gta_loading_screen false
cl_loadingScreenTips false
fps_max 0
setr audio_enable3D false
    """
    cfg_path.write_text(cfg_content)
    print(f"[✔] autoexec.cfg created at: {cfg_path}")

def create_cache_cleaner():
    bat_path = Path.home() / 'Desktop' / 'DNY_Cache_Cleaner.bat'
    bat_content = (
        "@echo off
"
        "echo Cleaning FiveM Cache...
"
        "cd %localappdata%\FiveM\FiveM.app\cache
"
        "del /s /q *
"
        "cd %localappdata%\FiveM\FiveM.app\crashometry
"
        "del /s /q *
"
        "cd %localappdata%\FiveM\FiveM.app\logs
"
        "del /s /q *
"
        "echo Done! Launch FiveM now for clean performance.
"
        "pause
"
    )
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    print(f"[✔] Cache Cleaner created on Desktop.")

def optimize_windows():
    try:
        subprocess.call('powercfg -setactive SCHEME_MIN', shell=True)
        subprocess.call('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f', shell=True)
        subprocess.call('reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f', shell=True)
        print("[✔] Windows settings optimized (Power plan, Xbox Game Bar).")
    except Exception as e:
        print(f"[!] Error optimizing Windows: {e}")

def main():
    print_banner()
    time.sleep(1)
    create_autoexec()
    create_cache_cleaner()
    optimize_windows()
    print("\nAll done! Launch FiveM and enjoy boosted FPS!\n")
    input("Press ENTER to exit...")

if __name__ == '__main__':
    main()
