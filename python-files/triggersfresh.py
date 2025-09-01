import tkinter as tk
from tkinter import messagebox

import threading

# Seznam fake triggerů
fake_triggery = {
    "consumables:server:addThirst",
    "consumables:server:addHunger",
    "esx_ambulancejob:syncDeadBody",
    "nb_community:server:workServices",
    "QBCore:Server:AddItem",
    "rs_fishing:server:caughtFish",
    "nb_community:server:workService",
    "rs_farms:server:handle",
    "redst0nia:checking",
    "esx_mafiajob:confiscatePlayerItem",
    "lscustoms:payGarage",
    "vrp_slotmachine:server:2",
    "esx_fueldelivery:pay",
    "esx_carthief:pay",
    "esx_godirtyjob:pay",
    "esx_pizza:pay",
    "esx_ranger:pay",
    "esx_truckerjob:pay",
    "AdminMenu:giveBank",
    "AdminMenu:giveCash",
    "esx_gopostaljob:pay",
    "esx_banksecurity:pay",
    "esx_slotmachine:sv:2",
    "esx_billing:sendBill",
    "esx_jail:sendToJail",
    "esx_jailer:sendToJail",
    "NB:recruterplayer",
    "js:jailuser",
    "esx-qalle-jail:jailPlayer",
    "OG_cuffs:cuffCheckNearest",
    "cuffServer",
    "cuffGranted",
    "esx:giveInventoryItem",
    "esx:removeInventoryItem",
    "esx_mechanicjob:startCraft",
    "esx_drugs:startHarvestWeed",
    "esx_drugs:startTransformWeed",
    "esx_drugs:startSellWeed",
    "esx_drugs:startHarvestCoke",
    "esx_drugs:startTransformCoke",
    "esx_drugs:startSellCoke",
    "esx_drugs:startHarvestMeth",
    "esx_drugs:startTransformMeth",
    "esx_drugs:startSellMeth",
    "esx_drugs:startHarvestOpium",
    "esx_drugs:startSellOpium",
    "esx_drugs:startTransformOpium",
    "esx_blanchisseur:startWhitening",
    "esx_drugs:stopHarvestCoke",
    "esx_drugs:stopTransformCoke",
    "esx_drugs:stopSellCoke",
    "esx_drugs:stopHarvestMeth",
    "esx_drugs:stopTransformMeth",
    "esx_drugs:stopSellMeth",
    "esx_drugs:stopHarvestWeed",
    "esx_drugs:stopTransformWeed",
    "esx_drugs:stopSellWeed",
    "esx_drugs:stopHarvestOpium",
    "esx_drugs:stopTransformOpium",
    "esx_drugs:stopSellOpium",
    "esx_tankerjob:pay",
    "esx_vehicletrunk:giveDirty",
    "gambling:spend",
    "AdminMenu:giveDirtyMoney",
    "mission:completed",
    "truckerJob:success",
    "99kr-burglary:addMoney",
    "esx_jailer:unjailTime",
    "esx_ambulancejob:revive",
    "DiscordBot:playerDied",
    "hentailover:xdlol",
    "antilynx8:anticheat",
    "antilynx8:crashuser",
    "antilynxr6:detection",
    "antilynx8r4a:anticheat",
    "antilynxr4:detect",
    "antilynxr4:crashuser1",
    "ynx8:anticheat",
    "lynx8:anticheat",
    "shilling=yet7",
    "adminmenu:allowall",
    "h:xd",
    "esx_skin:responseSaveSkin",
    "ljail:jailplayer",
    "adminmenu:setsalary",
    "adminmenu:cashoutall",
    "HCheat:TempDisableDetection",
    "esx_drugs:pickedUpCannabis",
    "esx_drugs:processCannabis",
    "esx-qalle-hunting:reward",
    "esx-qalle-hunting:sell",
    "esx_mecanojob:onNPCJobCompleted",
    "BsCuff:Cuff696999",
    "veh_SR:CheckMoneyForVeh",
    "mellotrainer:adminTempBan",
    "mellotrainer:adminKick",
    "d0pamine_xyz:getFuckedNigger",
    "esx_communityservice:sendToCommunityService",
    "InteractSound_SV:PlayOnAll",
    "InteractSound_SV:PlayWithinDistance",
    "crown_xyz:getFuckedNigger",
    "esx:clientLog",
    "kashactersS:DeleteCharacter",
    "lscustoms:UpdateVeh",
    "NB:destituerplayer",
    "esx_vangelico_robbery:robberycomplete",
    "esx_vangelico_robbery:gioielli",
    "esx_policejob:requestarrest",
    "ems:revive",
    "whoapd:revive",
    "paramedic:revive",
}

# Funkce pro kontrolu triggeru
def zkontroluj_trigger():
    zadany = entry.get().strip()
    if zadany in fake_triggery:
        messagebox.showerror("Výsledek", "⚠️ TRIGGER JE FAKE")
    else:
        messagebox.showinfo("Výsledek", "✅ TRIGGER NENÍ FAKE")

# Zavře okno po 30 sekundách
def automaticke_zavreni():
    root.after(30000, root.destroy)  # 30 000 ms = 30 sekund

# GUI
root = tk.Tk()
root.title("Kontrola Triggeru")
root.geometry("300x150")
root.resizable(False, False)

# Vstupní pole a tlačítko
label = tk.Label(root, text="Zadej název triggeru:")
label.pack(pady=10)

entry = tk.Entry(root, width=40)
entry.pack()

button = tk.Button(root, text="Zkontrolovat", command=zkontroluj_trigger)
button.pack(pady=10)

# Spustí automatické zavření
automaticke_zavreni()

# Spuštění GUI
root.mainloop()
