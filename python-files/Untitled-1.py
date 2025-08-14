def calculer_marges():
    print("=== SYSTÈME DE MARGE INVESTISSEUR ===\n")

    # Entrée des investissements
    investissement_lowis = float(input("Montant investi par Lowis (€) : "))
    investissement_paolo = float(input("Montant investi par Paolo (€) : "))

    # Entrée des revenus
    revenus_tiktok = float(input("Revenus TikTok (€) : "))
    revenus_paypal = float(input("Revenus PayPal (€) : "))

    # Total des revenus
    revenus_total = revenus_tiktok + revenus_paypal
    print(f"\n💰 Revenus totaux : {revenus_total:.2f} €")

    # Calcul des remboursements avec intérêts (20%)
    remboursement_lowis = investissement_lowis * 1.2
    remboursement_paolo = investissement_paolo * 1.2

    total_remboursements = remboursement_lowis + remboursement_paolo

    # Vérification : assez d'argent pour rembourser ?
    if total_remboursements > revenus_total:
        print("\n⚠️ Les revenus ne suffisent pas à rembourser les investisseurs.")
        if remboursement_lowis > 0:
            part_lowis = revenus_total * (remboursement_lowis / total_remboursements)
        else:
            part_lowis = 0
        if remboursement_paolo > 0:
            part_paolo = revenus_total * (remboursement_paolo / total_remboursements)
        else:
            part_paolo = 0
    else:
        # Reste après remboursement
        reste = revenus_total - total_remboursements

        # Partage du reste à 50/50
        part_lowis = remboursement_lowis + (reste / 2)
        part_paolo = remboursement_paolo + (reste / 2)

    # Affichage des résultats
    print(f"\n📊 Gains finaux :")
    print(f"  - Lowis : {part_lowis:.2f} €")
    print(f"  - Paolo : {part_paolo:.2f} €")

    input("\nAppuie sur Entrée pour quitter...")

# Lancer le programme
calculer_marges()
