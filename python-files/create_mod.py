import os
from pathlib import Path

def create_mod_files(mod_dir: str = "SupplyBasedArsenal"):
    """
    Crée la structure de dossiers et les fichiers pour le mod Arma Reforger "SupplyBasedArsenal".
    Exécutez ce script Python pour générer le mod prêt à être importé dans Arma Reforger Workbench.
    """
    base_path = Path(mod_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    # Dossier addons
    addons_path = base_path / "addons"
    addons_path.mkdir(parents=True, exist_ok=True)

    # Fichier config.conf
    config_content = """
modName = "SupplyBasedArsenal";
author = "VotreNom";
version = "1.0";
dependencies = {};
"""
    with open(addons_path / "config.conf", "w", encoding="utf-8") as f:
        f.write(config_content.strip())

    # Dossiers scripts
    scripts_path = addons_path / "scripts" / "Game"
    scripts_path.mkdir(parents=True, exist_ok=True)

    # Components
    components_path = scripts_path / "Components"
    components_path.mkdir(parents=True, exist_ok=True)

    player_supply_content = """
// PlayerSupplyComponent.es
class PlayerSupplyComponent : ScriptComponent
{
    [Attribute("0", UIWidgets.EditBox, "Solde initial de supplies")]
    protected int m_iInitialBalance;

    replicated int m_iSupplyBalance;  // Répliqué pour synchro client-serveur

    void PlayerSupplyComponent(IEntity owner)
    {
        m_iSupplyBalance = m_iInitialBalance;
    }

    void AddSupplies(int amount)
    {
        if (GetGame().InPlayMode() && Replication.IsServer())
        {
            m_iSupplyBalance += amount;
            Replication.BumpMe();  // Force la réplication
        }
    }

    bool DeductSupplies(int amount)
    {
        if (GetGame().InPlayMode() && Replication.IsServer())
        {
            if (m_iSupplyBalance >= amount)
            {
                m_iSupplyBalance -= amount;
                Replication.BumpMe();
                return true;
            }
        }
        return false;
    }

    int GetBalance()
    {
        return m_iSupplyBalance;
    }

    // Exemple d'événement pour contribution : Ajouter 100 supplies sur kill (à attacher via GameMode)
    void OnPlayerKilled(int playerId, IEntity victim, IEntity killer)
    {
        if (killer)
        {
            PlayerSupplyComponent supplyComp = PlayerSupplyComponent.Cast(killer.FindComponent(PlayerSupplyComponent));
            if (supplyComp)
                supplyComp.AddSupplies(100);  // Contribution : +100 pour tuer un ennemi
        }
    }
}
"""
    with open(components_path / "PlayerSupplyComponent.es", "w", encoding="utf-8") as f:
        f.write(player_supply_content.strip())

    supply_deposit_content = """
// SupplyDepositComponent.es
class SupplyDepositComponent : ScriptComponent
{
    void OnInteract(IEntity player, IEntity supplyCrate)  // Appel via interaction UI
    {
        SCR_ResourceComponent resource = SCR_ResourceComponent.Cast(supplyCrate.FindComponent(SCR_ResourceComponent));  // Assume supplies ont ce composant
        if (resource)
        {
            int amount = resource.GetResourceAmount();  // Quantité de supplies dans la caisse

            // Ajouter à l'équipe (faction)
            SCR_Faction faction = SCR_Faction.Cast(GetGame().GetFactionManager().GetFactionByKey(player.GetFactionKey()));
            if (faction)
                faction.AddSupplies(amount);  // Méthode hypothétique ; adaptez à SCR_FactionManager.AddSupplies()

            // Ajouter au personnel
            PlayerSupplyComponent supplyComp = PlayerSupplyComponent.Cast(player.FindComponent(PlayerSupplyComponent));
            if (supplyComp)
                supplyComp.AddSupplies(amount);

            // Détruire la caisse après dépôt
            GetGame().GetWorld().DeleteEntity(supplyCrate);
        }
    }
}
"""
    with open(components_path / "SupplyDepositComponent.es", "w", encoding="utf-8") as f:
        f.write(supply_deposit_content.strip())

    # Modded
    modded_path = scripts_path / "Modded"
    modded_path.mkdir(parents=True, exist_ok=True)

    game_mode_content = """
// Dans modded SCR_GameModeConflict.es
modded class SCR_GameModeConflict
{
    override void OnPlayerSpawned(int playerId, IEntity entity)
    {
        super.OnPlayerSpawned(playerId, entity);
        entity.InsertComponent(PlayerSupplyComponent);  // Ajoute le composant
    }
}
"""
    with open(modded_path / "SCR_GameModeConflict.es", "w", encoding="utf-8") as f:
        f.write(game_mode_content.strip())

    arsenal_item_content = """
// SCR_ArsenalItem.es
modded class SCR_ArsenalItem
{
    [Attribute("0", UIWidgets.EditBox, "Coût en supplies pour cet item", "0 1000")]
    protected int m_iSupplyCost;

    int GetSupplyCost()
    {
        return m_iSupplyCost;
    }
}
"""
    with open(modded_path / "SCR_ArsenalItem.es", "w", encoding="utf-8") as f:
        f.write(arsenal_item_content.strip())

    vehicle_spawn_content = """
// SCR_VehicleSpawnPointComponent.es (pour usines de véhicules)
modded class SCR_VehicleSpawnPointComponent
{
    override void SpawnVehicle()
    {
        // Calculer coût (ex. fixe par véhicule, ou via attribute)
        int vehicleCost = 300;  // Ex. 300 pour un jeep, configurez par prefab

        IEntity player = GetGame().GetPlayerController().GetControlledEntity();
        PlayerSupplyComponent supplyComp = PlayerSupplyComponent.Cast(player.FindComponent(PlayerSupplyComponent));

        if (supplyComp && supplyComp.DeductSupplies(vehicleCost))
        {
            super.SpawnVehicle();
        }
        else
        {
            GetGame().GetMenuManager().OpenDialog("Supplies insuffisantes pour spawn véhicule !");
        }
    }
}
"""
    with open(modded_path / "SCR_VehicleSpawnPointComponent.es", "w", encoding="utf-8") as f:
        f.write(vehicle_spawn_content.strip())

    # Menus
    menus_path = scripts_path / "Menus"
    menus_path.mkdir(parents=True, exist_ok=True)

    arsenal_menu_content = """
// SCR_ArsenalMenu.es
modded class SCR_ArsenalMenu : ChimeraMenuBase
{
    // Override la méthode d'application du loadout
    override void ApplyLoadout()
    {
        // Calculer coût total du loadout
        int totalCost = 0;
        array<SCR_ArsenalItem> loadoutItems = GetCurrentLoadoutItems();  // Méthode hypothétique ; adaptez à GetLoadoutItems() ou similaire via SCR_LoadoutManager
        foreach (SCR_ArsenalItem item : loadoutItems)
        {
            totalCost += item.GetSupplyCost();
        }

        // Récupérer le joueur et son composant
        IEntity player = GetGame().GetPlayerController().GetControlledEntity();
        PlayerSupplyComponent supplyComp = PlayerSupplyComponent.Cast(player.FindComponent(PlayerSupplyComponent));

        if (supplyComp && supplyComp.DeductSupplies(totalCost))
        {
            super.ApplyLoadout();  // Appliquer si OK
            Print("Loadout appliqué pour " + totalCost + " supplies.");
        }
        else
        {
            // Notification si insuffisant
            GetGame().GetMenuManager().OpenDialog("Supplies insuffisantes ! Solde actuel : " + supplyComp.GetBalance());
        }
    }

    // Ajoutez une UI pour montrer les coûts (optionnel) : Dans le layout de l'arsenal, ajoutez un TextWidget pour afficher totalCost en temps réel.
}
"""
    with open(menus_path / "SCR_ArsenalMenu.es", "w", encoding="utf-8") as f:
        f.write(arsenal_menu_content.strip())

    map_menu_content = """
// SCR_MapMenu.es
modded class SCR_MapMenu : ChimeraMenuBase
{
    protected TextWidget m_wSupplyBalanceText;  // Widget pour afficher

    override void OnMenuOpen()
    {
        super.OnMenuOpen();

        // Créer le widget dynamiquement si pas dans layout
        Widget root = GetRootWidget();
        m_wSupplyBalanceText = TextWidget.Cast(root.FindAnyWidget("SupplyBalanceText"));  // Si dans layout ; sinon :
        if (!m_wSupplyBalanceText)
        {
            m_wSupplyBalanceText = TextWidget.Cast(GetGame().GetWorkspace().CreateWidgets("{YourLayoutPath}/SupplyText.layout", root));  // Créez un layout simple avec TextWidget
            m_wSupplyBalanceText.SetPos(0.05, 0.05);  // Position en haut-gauche
        }

        UpdateBalanceDisplay();
    }

    void UpdateBalanceDisplay()
    {
        IEntity player = GetGame().GetPlayerController().GetControlledEntity();
        PlayerSupplyComponent supplyComp = PlayerSupplyComponent.Cast(player.FindComponent(PlayerSupplyComponent));
        if (supplyComp && m_wSupplyBalanceText)
        {
            m_wSupplyBalanceText.SetText("Supplies Personnelles : " + supplyComp.GetBalance());
        }
    }

    // Mettre à jour périodiquement (ex. via timer)
    override void OnMenuUpdate(float tDelta)
    {
        super.OnMenuUpdate(tDelta);
        UpdateBalanceDisplay();  // Rafraîchit à chaque frame
    }
}
"""
    with open(menus_path / "SCR_MapMenu.es", "w", encoding="utf-8") as f:
        f.write(map_menu_content.strip())

    # Layouts
    layouts_path = addons_path / "layouts"
    layouts_path.mkdir(parents=True, exist_ok=True)

    supply_text_layout = """
<root>
    <controls>
        <TextWidget name="SupplyBalanceText" text="" font="Default" color="#FFFFFFFF" size="20" />
    </controls>
</root>
"""
    with open(layouts_path / "SupplyText.layout", "w", encoding="utf-8") as f:
        f.write(supply_text_layout.strip())

    print(f"Mod créé avec succès dans le dossier : {base_path.resolve()}")
    print("Ouvrez Arma Reforger Workbench, ajoutez ce projet, et testez !")
    print("Note : Ajustez les chemins dans les scripts si nécessaire (ex. {YourLayoutPath} -> layouts).")

if __name__ == "__main__":
    create_mod_files()