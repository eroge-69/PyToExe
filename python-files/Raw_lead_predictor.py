#!/usr/bin/env python
# coding: utf-8

import numpy as np

# Richiesta input all'utente
days = int(input("Giorni trascorsi a partire da Sabato: "))
leads = int(input("Numero leads attuali: "))
leads_wow = int(input("Numero leads settimana precedente: "))
advanced = int(input("Numero leads in fase avanzata attuali: "))
advanced_wow = int(input("Numero leads in fase avanzata settimana precedente: "))

# Calcoli
optleads = 7 * leads / days
con_leads = 7 * leads / (days + 0.5)

opt_advanced = 7 * advanced / days
con_advanced = 7 * advanced / (days + 0.5)

# Output
print(f"""
Ciao @Gino Sgroi,
Al momento su Zoho vedo {leads} leads, pertanto:

optimistic_estimate = {leads}/{days}*7 = {int(optleads)} leads ({100*np.round(optleads/leads_wow-1,2)}% WoW)
conservative_estimate = {leads}/{days+0.5}*7 = {int(con_leads)} leads ({100*np.round(con_leads/leads_wow-1,2)}% WoW)

Al momento su Zoho vedo {advanced} leads in fase avanzate, pertanto:

optimistic_estimate = {advanced}/{days}*7 = {int(opt_advanced)} leads ({100*np.round(opt_advanced/advanced_wow-1,2)}% WoW)
conservative_estimate = {advanced}/{days+0.5}*7 = {int(con_advanced)} leads ({100*np.round(con_advanced/advanced_wow-1,2)}% WoW)
""")

# Mantieni aperta la finestra
input("\nPremi INVIO per chiudere...")




