# -*- coding: utf-8 -*-
import csv
import time
import win32com.client
import tkinter as tk
from tkinter import filedialog
import pymsgbox as msgbox
#import sys

# ---------------------------
# Dialogues utilisateurs (équivalent MsgBox VBScript)
# ---------------------------
def user_confirmations():
    w = msgbox.confirm(
        "As-tu téléchargé en csv l'onglet Création en masse ?",
        "BOUCLE KANBAN EN MASSE PEA",
        ["Oui", "Non"]
    )
    if w != "Oui":
        msgbox.alert(
            "Alors télécharge en csv l'onglet Création en masse S.T.P.....",
            "BOUCLE KANBAN EN MASSE PEA"
        )
        return False

    x = msgbox.confirm(
        "As-tu fermés toutes les session SAP, Sauf SAP PEA ?",
        "BOUCLE KANBAN EN MASSE PEA",
        ["Oui", "Non"]
    )
    if x != "Oui":
        msgbox.alert(
            "Alors ferme toutes les session SAP et connectes toi à SAP PEA S.T.P...",
            "BOUCLE KANBAN EN MASSE PEA"
        )
        return False

    y = msgbox.confirm(
        "Je t'informes que cette action vas créer, modifier et supprimer tous les circuits sélectionné OK tu valides les actions ?",
        "BOUCLE KANBAN EN MASSE PEA",
        ["Oui", "Non"]
    )
    if y != "Oui":
        msgbox.alert(
            "Je t'informes qu'il n'y auras pas de changement dans PEA...",
            "BOUCLE KANBAN EN MASSE PEA"
        )
        return False

    return True

# ---------------------------
# Connexion SAP (GetObject SAPGUI)
# ---------------------------
def connect_sap():
    try:
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        connection = application.Children(0)
        session = connection.Children(0)
        print("[INFO] Connexion SAP OK")
        return application, connection, session
    except Exception as e:
        print(f"[ERREUR] Connexion SAP impossible : {e}")
        return None, None, None

# ---------------------------
# Sélection du fichier CSV (fenêtre)
# ---------------------------
def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Sélectionnez le fichier CSV Boucle Kanban",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        print("[ERREUR] Aucun fichier sélectionné.")
        return None
    return file_path

# ---------------------------
# Lecture et transformation proche du VBScript
# - lit tout, skip 13 premières lignes
# - split par virgule
# - conserve au moins 14 colonnes
# ---------------------------
def read_and_prepare_data(file_path):
    data_rows = []
    with open(file_path, "r", encoding="utf-8-sig", errors="replace", newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for idx, row in enumerate(reader):
            if idx < 13:
                continue
            # strip espaces en bordure sur chaque cellule
            row = [cell.strip() for cell in row]
            # garantir au moins 14 colonnes (indices 0..13)
            if len(row) < 14:
                # pad with empty strings
                row += [""] * (14 - len(row))
            data_rows.append(row)
    print(f"[INFO] {len(data_rows)} lignes lues (après skip 13 lignes).")
    return data_rows

# ---------------------------
# Helpers: check if control exists (renvoie True/False)
# ---------------------------
def control_exists(session, control_id):
    try:
        # second argument False isn't supported; we'll catch exception
        _ = session.findById(control_id)
        return True
    except Exception:
        return False

# ---------------------------
# Fonctions SAP reproduisant exactement ton VBScript
# J'utilise les même IDs que dans ton VBScript.
# ---------------------------
def Creation_boucle_KBN_PEA_FULL(session, data_row, ligne_index_for_logs):
    try:
        print(f"[INFO] Début Creation FULL - ligne {ligne_index_for_logs} - MATNR={data_row[1]}")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NPKMC"
        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.7)

        # WERKS
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subSELECTION:SAPLMPK_CCY_UI:0113/ctxtRMPKR-WERKS"
        ).Text = data_row[5]
        time.sleep(0.3)

        session.findById("wnd[0]/tbar[1]/btn[7]").press()
        time.sleep(0.5)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0130/subBIGGRIDCONTAINER:SAPLMPK_CCY_UI:0135/"
            "cntlAVAILABLE_CONTROLCYCLES/shellcont/shell"
        ).pressToolbarButton("CCY_CRE")
        time.sleep(0.5)

        session.findById("wnd[1]/usr/ctxtRMPKR-MATNR").Text = data_row[1]
        session.findById("wnd[1]/usr/ctxtRMPKR-PRVBE").Text = data_row[11]
        session.findById("wnd[1]/usr/cmbRMPKR-LCM_STATUS").Key = "3"
        session.findById("wnd[1]/usr/cmbRMPKR-LCM_STATUS").SetFocus()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        time.sleep(0.6)

        # Onglet NSTR, radio STFRD
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0801/radRMPKR-STFRD"
        ).Select()
        time.sleep(0.2)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/txtPKHD-ABLAD"
        ).Text = data_row[9]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/txtPKHD-BEHAZ"
        ).Text = "2"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/txtPKHD-BEHMG"
        ).Text = data_row[10]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0801/ctxtPKHD-PKSTF"
        ).Text = data_row[6]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/txtPKHD-ZTHEODUR"
        ).Text = data_row[3]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZTHEODURU"
        ).Text = "JRS"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/txtPKHD-ZADDREPTIM"
        ).Text = "3"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZADDREPTIMU"
        ).Text = "JRS"

        # position caret etc.
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZADDREPTIMU"
        ).SetFocus()
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZADDREPTIMU"
        ).caretPosition = 3

        session.findById("wnd[0]").sendVKey(0)
        time.sleep(0.3)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0812/ctxtPKHD-EKORG"
        ).Text = "AI01"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0812/ctxtPKHD-PKUMW"
        ).Text = data_row[5]

        # focus / caret
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0812/ctxtPKHD-PKUMW"
        ).SetFocus()
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0812/ctxtPKHD-PKUMW"
        ).caretPosition = 4

        # popu
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "cntlMENUE/shellcont/shell"
        ).pressButton("POPU")
        time.sleep(0.4)

        session.findById("wnd[1]/usr/tblSAPLMPK_CCY_UIKANBANLIST/chkPKPS-SPKKZ[0,0]").Selected = True
        session.findById("wnd[1]/usr/tblSAPLMPK_CCY_UIKANBANLIST/chkPKPS-SPKKZ[0,0]").SetFocus()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        # sauvegarder et fermer
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/tbar[0]/btn[3]").press()
        print(f"[OK] Creation FULL terminée - ligne {ligne_index_for_logs}")
        time.sleep(0.3)

    except Exception as e:
        print(f"[SAP ERROR FULL] ligne {ligne_index_for_logs} MATNR={data_row[1]} : {e}")

def Creation_boucle_KBN_PEA_INTER(session, data_row, ligne_index_for_logs):
    try:
        print(f"[INFO] Début Creation INTER - ligne {ligne_index_for_logs} - MATNR={data_row[1]}")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NPKMC"
        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.5)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subSELECTION:SAPLMPK_CCY_UI:0113/ctxtRMPKR-WERKS"
        ).Text = data_row[5]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subSELECTION:SAPLMPK_CCY_UI:0113/ctxtRMPKR-PRVBE"
        ).Text = data_row[11]
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subSELECTION:SAPLMPK_CCY_UI:0113/ctxtRMPKR-PRVBE"
        ).SetFocus()
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subSELECTION:SAPLMPK_CCY_UI:0113/ctxtRMPKR-PRVBE"
        ).caretPosition = 10

        session.findById("wnd[0]/tbar[1]/btn[7]").press()
        time.sleep(0.4)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0130/subBIGGRIDCONTAINER:SAPLMPK_CCY_UI:0135/"
            "cntlAVAILABLE_CONTROLCYCLES/shellcont/shell"
        ).pressToolbarButton("CCY_CRE")
        time.sleep(0.4)

        session.findById("wnd[1]/usr/ctxtRMPKR-MATNR").Text = data_row[1]
        session.findById("wnd[1]/usr/cmbRMPKR-LCM_STATUS").Key = "3"
        session.findById("wnd[1]/usr/cmbRMPKR-LCM_STATUS").SetFocus()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        time.sleep(0.4)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0801/radRMPKR-STUML"
        ).Select()

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/txtPKHD-ABLAD"
        ).Text = data_row[9]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/txtPKHD-BEHAZ"
        ).Text = "2"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/txtPKHD-BEHMG"
        ).Text = data_row[10]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0801/ctxtPKHD-PKSTU"
        ).Text = data_row[6]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/txtPKHD-ZTHEODUR"
        ).Text = data_row[3]

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZTHEODURU"
        ).Text = "JRS"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/txtPKHD-ZADDREPTIM"
        ).Text = "3"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZADDREPTIMU"
        ).Text = "JRS"

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZADDREPTIMU"
        ).SetFocus()
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "ssubCUSTSCR1:SAPLXMPK:1000/ctxtPKHD-ZADDREPTIMU"
        ).caretPosition = 3

        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.3)

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0813/ctxtPKHD-UMLGO"
        ).Text = "TTTR"
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0813/ctxtPKHD-UMLGO"
        ).SetFocus()
        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "tabsTABSTRIP/tabpNSTR/ssubINCLUDE8XX:SAPLMPK_CCY_UI:0813/ctxtPKHD-UMLGO"
        ).caretPosition = 4

        session.findById(
            "wnd[0]/usr/ssubCCY_AND_SELECTION:SAPLMPK_CCY_UI:0111/"
            "subCCY:SAPLMPK_CCY_UI:0131/subCONTROL_CYCLE:SAPLMPK_CCY_UI:0201/"
            "cntlMENUE/shellcont/shell"
        ).pressButton("POPU")
        time.sleep(0.4)

        session.findById("wnd[1]/usr/tblSAPLMPK_CCY_UIKANBANLIST/chkPKPS-SPKKZ[0,0]").Selected = True
        session.findById("wnd[1]/usr/tblSAPLMPK_CCY_UIKANBANLIST/chkPKPS-SPKKZ[0,0]").SetFocus()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/tbar[0]/btn[3]").press()

        print(f"[OK] Creation INTER terminée - ligne {ligne_index_for_logs}")
        time.sleep(0.3)

    except Exception as e:
        print(f"[SAP ERROR INTER] ligne {ligne_index_for_logs} MATNR={data_row[1]} : {e}")

def Modification_boucle_KBN_PEA(session, data_row, ligne_index_for_logs):
    try:
        print(f"[INFO] Début Modification - ligne {ligne_index_for_logs} MATNR={data_row[1]}")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/NPK02"
        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.4)

        session.findById("wnd[0]/usr/ctxtRMPKR-MATNR").Text = data_row[1]
        session.findById("wnd[0]/usr/ctxtRMPKR-WERKS").Text = data_row[5]
        session.findById("wnd[0]/usr/ctxtRMPKR-PRVBE").Text = data_row[11]
        session.findById("wnd[0]/usr/ctxtRMPKR-PRVBE").SetFocus()
        session.findById("wnd[0]/usr/ctxtRMPKR-PRVBE").caretPosition = 10
        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.3)

        # debug echo
        print(f"[DEBUG] data_row[9]={data_row[9]} data_row[10]={data_row[10]}")

        if data_row[9] != "":
            session.findById("wnd[0]/usr/txtPKHD-ABLAD").Text = data_row[9]
        if data_row[10] != "":
            session.findById("wnd[0]/usr/txtPKHD-BEHMG").Text = data_row[10]
            session.findById("wnd[0]/usr/txtPKHD-BEHMG").SetFocus()
            session.findById("wnd[0]/usr/txtPKHD-BEHMG").caretPosition = 2

        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        print(f"[OK] Modification terminée - ligne {ligne_index_for_logs}")

    except Exception as e:
        print(f"[SAP ERROR MODIF] ligne {ligne_index_for_logs} MATNR={data_row[1]} : {e}")

def Suppression_boucle_KBN_PEA(session, data_row, ligne_index_for_logs):
    try:
        print(f"[INFO] Début Suppression - ligne {ligne_index_for_logs} MATNR={data_row[1]}")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/NPK02"
        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.4)

        session.findById("wnd[0]/usr/ctxtRMPKR-MATNR").Text = data_row[1]
        session.findById("wnd[0]/usr/ctxtRMPKR-WERKS").Text = data_row[5]
        session.findById("wnd[0]/usr/ctxtRMPKR-PRVBE").Text = data_row[11]
        session.findById("wnd[0]/usr/ctxtRMPKR-PRVBE").SetFocus()
        session.findById("wnd[0]/usr/ctxtRMPKR-PRVBE").caretPosition = 10
        session.findById("wnd[0]/tbar[0]/btn[0]").press()
        time.sleep(0.3)

        session.findById("wnd[0]/mbar/menu[0]/menu[4]").select()
        session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        print(f"[OK] Suppression terminée - ligne {ligne_index_for_logs}")

    except Exception as e:
        print(f"[SAP ERROR DELETE] ligne {ligne_index_for_logs} MATNR={data_row[1]} : {e}")

# ---------------------------
# Boucle principale: parcours des lignes et appel des routines
# ---------------------------
def main():
    if not user_confirmations():
        print("[INFO] Utilisateur a annulé.")
        return

    application, connection, session = connect_sap()
    if session is None:
        msgbox.alert("Impossible de se connecter à SAP. Vérifie que SAP est ouvert et le scripting activé.", "Erreur SAP")
        return

    file_path = select_csv_file()
    if not file_path:
        return

    data = read_and_prepare_data(file_path)

    # On parcourt les lignes comme dans ton VBScript (tab_data_2)
    for i, row in enumerate(data):
        ligne_log = i + 14  # +14 comme dans ton VBScript pour correspondre aux lignes du CSV original
        try:
            # Vérifier qu'il y a au moins 14 colonnes
            if len(row) < 14:
                print(f"[WARNING] Ligne {ligne_log} ignorée: moins de 14 colonnes.")
                continue

            # --- FILTRE : Ne traiter que les lignes dont la colonne 13 commence par "OK"
            reponse = str(row[13]).strip().upper()
            if not reponse.startswith("OK"):
                print(f"[INFO] Ligne {ligne_log} ignorée : Réponse='{row[13]}' (pas OK)")
                continue

            objet = str(row[0]).strip()
            strategie = str(row[6]).strip()

            # --- Vérifier que la colonne 12 est vide
            if str(row[12]).strip() != "":
                print(f"[INFO] Ligne {ligne_log} ignorée : colonne 12 non vide")
                continue

            # --- Dispatch selon le type d'objet et la stratégie
            if objet == "Ajout d'un Cms dans libre service":
                if strategie.startswith("T13"):
                    Creation_boucle_KBN_PEA_FULL(session, row, ligne_log)
                elif strategie.startswith("T11"):
                    Creation_boucle_KBN_PEA_INTER(session, row, ligne_log)
                else:
                    print(f"[INFO] Ligne {ligne_log} - stratégie inconnue pour Ajout: '{strategie}'")

            elif objet == "Modification d'un CMS dans libre service":
                Modification_boucle_KBN_PEA(session, row, ligne_log)

            elif objet == "Suppression d'un CMS dans libre service":
                Suppression_boucle_KBN_PEA(session, row, ligne_log)

            else:
                # autre type d'objet -> ignoré comme dans ton VB
                print(f"[INFO] Ligne {ligne_log} ignorée : Objet non reconnu '{objet}'")
                continue

        except Exception as e:
            print(f"[ERREUR] Ligne {ligne_log} : {e}")

    msgbox.alert("Je t'informes que les créations, modifications et suppressions des circuits ont bien été effectuées dans SAP PEA...", "BOUCLE KANBAN EN MASSE PEA")
    print("[INFO] Traitement terminé.")

if __name__ == "__main__":
    main()
