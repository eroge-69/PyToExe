import traceback
import asyncio
import time
import datetime
import pickle
import json
import csv
from pathlib import Path
from threading import Thread
from typing import List, Dict, Optional, Any
import sqlite3
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import hashlib
import platform
import logging

from components.CustomElevatedButton import CustomElevatedButton
from components.CustomDraftButton import CustomDraftButton
from components.CustomTextField import CustomTextField
from utils.nombre_to_chiffre import number_to_words

from flet.core import *
from flet import (
    # Références et événements
    Ref,
    ControlEvent,
    RouteChangeEvent,
    KeyboardEvent,
    # Disposition et mise en page
    Page,
    View,
    AppView,
    Row,
    Column,
    Container,
    Card,
    ResponsiveRow,
    ListView,
    # Composants UI
    Text,
    Icon,
    Icons,
    IconButton,
    Button,
    Image,
    Divider,
    # Champs de saisie
    CupertinoTextField,
    KeyboardType,
    InputFilter,
    NumbersOnlyInputFilter,
    # AutoComplete,
    AutoCompleteSuggestion,
    AutoCompleteSelectEvent,
    DatePicker,
    Dropdown,
    dropdown,
    # Tables
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    # Barres de navigation
    AppBar,
    NavigationBar,
    NavigationBarDestination,
    # Éléments interactifs
    SearchBar,
    SnackBar,
    AlertDialog,
    PopupMenuButton,
    PopupMenuItem,
    TextButton,
    # Indicateurs et effets
    ProgressRing,
    BoxShadow,
    ClipBehavior,
    # Styles et mise en forme
    BorderSide,
    RoundedRectangleBorder,
    FontWeight,
    TextAlign,
    alignment,
    padding,
    border_radius,
    border,
    Colors,
    ScrollMode,
    ControlState,
    MainAxisAlignment,
    CrossAxisAlignment,
    # Fichiers
    FilePicker,
    FilePickerResultEvent,
    Image,
    # Thèmes
    Theme,
)

from utils.impression_facture import (
    imprimer_commande_thread,
)

from utils.utils import *
from utils.speaker import Speaker
from db.db_utils import DBUtils

from utils.drafts_manager import *
from views.login_view import LoginView
from views.accounts_view import *
from views.commandes_view import *
from views.dashboard_view import *
from views.clients_view import *
from views.finaces_view import *
from views.rapports_view import *

from components.widgets import *
from components.widgets import CustomAutoComplete as AutoComplete

# logging.basicConfig(level=logging.DEBUG)

from config import DB_PATH, DRAFTS_PATH

# Chemins constants - modification du nom
CURRENT_DIR = Path(__file__).parent.resolve()
# DB_PATH.mkdir(parents=True, exist_ok=True)
DRAFTS_PATH = str(CURRENT_DIR / "assets" / "drafts" / "drafts.df")

from config import LOGO_PATH

db.migrate_database()


class ArticlePressing(DataRow):
    def __init__(
        self,
        nom,
        quantite,
        type_service,
        prix_unitaire,
        prix_total,
        date_depot,
        date_retrait_prevue,
        statut,
        article_delete=None,
        calcul_totaux=None,
        devise_initiale="FC",
        article_edit=None,
    ):
        # Stockage des données internes
        self._nom = nom
        self._quantite = quantite
        self._type_service = type_service
        self._prix_unitaire = prix_unitaire
        self._prix_total = prix_total
        self._date_depot = date_depot
        self._date_retrait_prevue = date_retrait_prevue
        self._statut = statut
        self._devise = devise_initiale

        self.article_edit = article_edit
        self.article_delete = article_delete
        self.calcul_totaux = calcul_totaux

        self.statuts_possibles = ["En attente", "En cours", "Prêt", "Livré", "Urgent"]
        self.statut_color = self._get_statut_color(statut)

        # Widgets texte réutilisables
        self.txt_prix_unitaire = Text(f"{prix_unitaire:.2f} {devise_initiale}")
        self.txt_prix_total = Text(f"{prix_total:.2f} {devise_initiale}")
        self.txt_statut = Text(statut, color=self.statut_color)

        super().__init__(
            cells=[
                DataCell(Text(nom)),
                DataCell(Text(str(quantite))),
                DataCell(Text(type_service)),
                DataCell(self.txt_prix_unitaire),
                DataCell(self.txt_prix_total),
                DataCell(Text(date_depot)),
                DataCell(Text(date_retrait_prevue)),
                DataCell(
                    Container(
                        content=self.txt_statut,
                        on_click=self._changer_statut,
                        padding=padding.symmetric(horizontal=6, vertical=4),
                        ink=True,
                    )
                ),
                DataCell(
                    Row(
                        [
                            IconButton(
                                icon=Icons.DELETE,
                                icon_color="red",
                                tooltip="Supprimer l'article",
                                on_click=self._confirmer_suppression,
                            ),
                            IconButton(
                                icon=Icons.EDIT,
                                icon_color="blue",
                                tooltip="Changer le statut",
                                # on_click=self._changer_statut
                                on_click=self._edit_article,
                            ),
                        ]
                    )
                ),
            ]
        )

    def _get_statut_color(self, statut):
        return {
            "Urgent": Colors.RED_400,
            "Livré": Colors.GREEN_400,
            "Prêt": Colors.BLUE_300,
            "En attente": Colors.GREY_500,
            "En cours": Colors.AMBER_500,
        }.get(statut, Colors.BLACK)

    def _changer_statut(self, e):
        index = (self.statuts_possibles.index(self._statut) + 1) % len(
            self.statuts_possibles
        )
        self._statut = self.statuts_possibles[index]
        self.txt_statut.value = self._statut
        self.txt_statut.color = self._get_statut_color(self._statut)
        self.txt_statut.update()

        # Notification
        e.control.page.snack_bar = SnackBar(Text(f"Nouveau statut : {self._statut}"))
        e.control.page.snack_bar.open = True
        e.control.page.update()

        # Recalcul si nécessaire
        if self.calcul_totaux:
            self.calcul_totaux()

    def _edit_article(self, e):
        if self.article_edit:
            self.article_edit(self)

    def _confirmer_suppression(self, e):
        def confirm_action(result):
            if result == "yes" and self.article_delete:
                self.article_delete(self)
            dialog.open = False
            e.page.update()

        dialog = AlertDialog(
            modal=True,
            title=Text("Confirmation"),
            content=Text("Voulez-vous vraiment supprimer cet article ?"),
            actions=[
                TextButton("Non", on_click=lambda _: confirm_action("no")),
                TextButton("Oui", on_click=lambda _: confirm_action("yes")),
            ],
        )

        # Append the dialog to the page overlay
        e.page.overlay.append(dialog)
        dialog.open = True
        e.page.update()

    def handler_devise_change(self, nouvelle_devise, taux):
        if taux <= 0:
            return  # éviter division par 0

        self._devise = nouvelle_devise
        self._prix_unitaire = round(self._prix_unitaire / taux, 2)
        self._prix_total = round(self._prix_total / taux, 2)

        self.txt_prix_unitaire.value = f"{self._prix_unitaire:.2f} {nouvelle_devise}"
        self.txt_prix_total.value = f"{self._prix_total:.2f} {nouvelle_devise}"
        self.txt_prix_unitaire.update()
        self.txt_prix_total.update()

        if self.calcul_totaux:
            self.calcul_totaux()


class AccueilPressing(Container):
    def __init__(self, page: Page):
        print("🚀 Initialisation OPTIMISÉE de AccueilPressing...")
        super().__init__()
        self.page = page
        self.page.accueil_pressing = self

        self.expand = True
        self._vues_chargees = {}  # Dictionnaire pour suivre les vues chargées
        self._last_alert_count = 0

        # État / services
        print("🔌 Connexion à la base de données...")
        self.db = db

        self.menu_buttons: dict[str, CustomElevatedButton] = {}
        self.drafts_list_ref = Ref[ListView]()
        self.drafts_listview: ListView | None = None

        # Taux dollar
        print("💱 Chargement du taux du dollar...")
        # self._taux_dollar = self._get_taux()
        self._taux_dollar = TauxDollarWrapper(self._get_taux())

        # Vues - initialisées à None (chargement paresseux)
        self.__principal_view = None
        self.__commandes_view = None
        self.__clients_view = None
        self.__tableau_bord_view = None
        self.__finances_view = None
        self.__alertes_view = None
        self.__parametres_view = None
        self.__profil_view = None
        self.__rapports_view = None

        # Vue courante
        self.current_view_name = "Accueil"
        self.current_view = Container(expand=True)

        # Interface minimale au départ
        print("📦 Création de l'interface minimale...")
        self.content = self._create_minimal_ui()
        self.badge_container = None

        # Charger uniquement la vue principale + brouillons
        print("🔄 Chargement de la vue principale uniquement...")
        self._load_principal_view()
        # self._load_drafts_light()  # Version légère des brouillons
        self._load_drafts()

        print("🎯 INIT AccueilPressing OPTIMISÉ - Terminé")

    def _create_minimal_ui(self):
        """Interface minimale qui se charge rapidement"""
        return Container(
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    self._create_header_light(),
                    Row(
                        expand=True,
                        controls=[
                            self._create_menu_light(),
                            Container(expand=True, content=self.current_view),
                        ],
                    ),
                ],
            ),
        )

    def _create_header_light(self):
        """Header stylisé et fonctionnel avec logo, notifications, paramètres, profil."""
        try:
            logo_widget = Text(
                "B", color=Colors.BLUE_700, weight=FontWeight.BOLD
            )  # Fallback

            # ✅ Chemin intelligent du logo
            logo_path = (
                None  # LOGO_PATH if LOGO_PATH and Path(LOGO_PATH).exists() else None
            )

            # 🔄 Essai sur d'autres chemins si le logo n'existe pas
            if not logo_path or not Path(logo_path).exists():
                alt_paths = [
                    Path(".") / "assets" / "images" / "logo_la_benediction.png",
                    Path(".") / "logo_la_benediction.png",
                    Path("assets") / "images" / "logo_la_benediction.png",
                ]
                for path in alt_paths:
                    if path.exists():
                        logo_path = path
                        break
            logo_path = None

            if logo_path and Path(logo_path).exists():
                logo_widget = Image(
                    src=f"file:///{Path(logo_path).as_posix()}",
                    width=40,
                    height=40,
                    fit="contain",
                )
            else:
                print(f"[⚠️] Logo introuvable dans les chemins définis")

        except Exception as e:
            print(f"[ERREUR] Chargement du logo : {e}")

        # ✅ Fonction de changement de vue
        def go_to(view_name: str):
            return lambda e: self.__change_view(view_name)

        return Container(
            height=60,
            bgcolor=Colors.BLUE_700,
            padding=padding.symmetric(horizontal=20),
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    # ⬅️ Logo + Nom entreprise
                    Row(
                        spacing=10,
                        controls=[
                            Container(
                                width=40,
                                height=40,
                                bgcolor=Colors.WHITE,
                                border_radius=5,
                                alignment=alignment.center,
                                content=logo_widget,
                            ),
                            Text(
                                "Pressing Bénédiction",
                                color="white",
                                size=18,
                                weight=FontWeight.BOLD,
                            ),
                        ],
                    ),
                    # ➡️ Icônes : alertes, paramètres, profil
                    Row(
                        spacing=10,
                        controls=[
                            IconButton(
                                icon=Icons.NOTIFICATIONS,
                                icon_color="white",
                                tooltip="Alertes",
                                on_click=go_to("Alertes"),
                            ),
                            IconButton(
                                icon=Icons.SETTINGS,
                                icon_color="white",
                                tooltip="Paramètres",
                                on_click=go_to("Parametres"),
                            ),
                            IconButton(
                                icon=Icons.PERSON,
                                icon_color="white",
                                tooltip="Profil",
                                on_click=go_to("Profil"),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _create_menu_light(self):
        """Menu simplifié sans brouillons au début."""

        def menu_button(label, icon, view_name):
            btn = CustomElevatedButton(
                text=label,
                icon=icon,
                selected=(self.current_view_name == view_name),
                on_click=lambda e: self.__change_view_lazy(view_name),
                # minimal=True  # Optionnel : version légère du bouton
            )
            self.menu_buttons[view_name] = btn
            return btn

        # ✅ On stocke la colonne dans une variable accessible globalement
        self.menu_column_light = Column(
            spacing=5,
            controls=[
                menu_button("Accueil", Icons.HOME, "Accueil"),
                menu_button("Commandes", Icons.LIST_ALT, "Commandes"),
                menu_button("Clients", Icons.PEOPLE, "Clients"),
                menu_button("Tableau de bord", Icons.BAR_CHART, "TableauBord"),
                menu_button("Finances", Icons.ACCOUNT_BALANCE, "Finances"),
                menu_button("Rapports", Icons.ANALYTICS, "Rapports"),
                # Les brouillons seront ajoutés ici dynamiquement
            ],
        )

        return Container(
            width=200,  # Plus étroit
            bgcolor=Colors.GREY_50,
            padding=padding.all(10),
            content=self.menu_column_light,
        )

    def _load_principal_view(self):
        """Charge uniquement la vue principale"""
        try:
            self.__principal_view = PressingPrincipalView(
                self.page,
                draft_handler=self._add_draft,
                taux_dollar=self._get_taux(),
            )
            self.current_view.content = self.__principal_view
            self._vues_chargees["Accueil"] = True
            print("✅ Vue principale chargée")
        except Exception as e:
            print(f"❌ Erreur chargement vue principale: {e}")
            traceback.print_exc()

    def _load_drafts_light(self):
        """Charge seulement les 20 derniers brouillons et les affiche dans la ListView."""
        try:
            if not self.drafts_listview:
                self.drafts_listview = ListView(
                    expand=True, spacing=2, auto_scroll=False
                )

            brouillons = self.db.charger_brouillons_recentes(limit=20)

            self.drafts_listview.controls.clear()

            for b in brouillons:
                # 🔎 Récupération et formatage lisible de la date
                raw_date = b.get("created_at") or b.get("date_depot") or ""
                try:
                    dt = datetime.datetime.fromisoformat(raw_date)
                    date_str = dt.strftime("%d/%m/%Y %H:%M")  # Ex: 28/09/2025 23:42
                except Exception:
                    date_str = raw_date  # fallback brut si parsing échoue

                # 🧾 Construction d'une ligne courte et utile à afficher
                nom_client = b.get("client_nom", "Client")
                identifiant = b.get("id")
                ligne_info = f"{nom_client} • {date_str}"

                # ✅ Création du bouton avec info condensée
                btn = CustomDraftButton(
                    page=self.page,
                    brouillon_data={"id": identifiant},
                    nom_client=ligne_info,
                    date="",  # Date déjà incluse dans le nom affiché
                    delete_callback=self.__delete_draft,
                    load_callback=self.__load_draft,
                    # minimal=True  # Décommenter si design compact
                )

                self.drafts_listview.controls.append(btn)

            if brouillons and not hasattr(self, "_drafts_section_added"):
                self._add_drafts_section_to_menu()
                self._drafts_section_added = (
                    True  # Marque comme ajouté pour éviter doublons
                )

            self.drafts_listview.update()  # Forcer le rafraîchissement de la ListView

        except Exception as e:
            print(f"⚠️ Erreur chargement brouillons légers: {e}")

    def _add_drafts_section_to_menu(self):
        """Ajoute les brouillons récents dans le menu light (sans entête)."""
        try:
            if hasattr(self, "_drafts_section_added") and self._drafts_section_added:
                return  # Ne rien faire si déjà ajouté

            if self.menu_column_light:
                self.menu_column_light.controls.append(self.drafts_listview)
                self.menu_column_light.update()
                self._drafts_section_added = True
                print("✅ Brouillons ajoutés au menu light.")
            else:
                print("⚠️ menu_column_light non défini.")
        except Exception as e:
            print(f"❌ Erreur ajout brouillons menu light : {e}")

    def __change_view_lazy(self, view_name: str):
        """Navigation avec chargement paresseux"""
        try:
            if self.current_view_name == view_name:
                print(f"[DEBUG] Vue {view_name} déjà active")
                return

            self.current_view_name = view_name
            self._update_menu_selection(view_name)

            # Afficher une vue de chargement
            self._show_loading_view(view_name)

            # Charger la vue en tâche de fond
            self.page.run_task(self._run_view_loader, view_name)

        except Exception as ex:
            print(f"❌ Erreur changement vue: {ex}")
            self._show_error_view(view_name)
            traceback.print_exc()

    async def _run_view_loader(self, view_name: str):
        await self._load_view_async(view_name)

    async def _load_view_async(self, view_name: str):
        """Charge une vue de manière asynchrone"""
        try:
            view = None

            if view_name == "Accueil" and self.__principal_view:
                view = self.__principal_view

            elif view_name == "Commandes":
                if not self.__commandes_view:
                    print("📦 Chargement paresseux de CommandesView...")
                    self.__commandes_view = CommandesView(
                        self.page,
                        handler_nouvelle_commande=self.__nouvelle_commande,
                        accueil_reference=self,
                    )
                view = self.__commandes_view

            elif view_name == "Clients":
                if not self.__clients_view:
                    print("📦 Chargement paresseux de ClientsView...")
                    self.__clients_view = ClientsView(self.page)
                view = self.__clients_view

            elif view_name == "TableauBord":
                if not self.__tableau_bord_view:
                    print("📦 Chargement paresseux de TableauBordPressingView...")
                    self.__tableau_bord_view = TableauBordPressingView(self.page)
                view = self.__tableau_bord_view

            elif view_name == "Finances":
                if not self.__finances_view:
                    print("📦 Chargement paresseux de FinancesView...")
                    self.__finances_view = FinancesView(self.page)
                view = self.__finances_view

            elif view_name == "Alertes":
                if not self.__alertes_view:
                    print("📦 Chargement paresseux de AlertesPressingView...")
                    self.__alertes_view = AlertesPressingView(self.page)
                view = self.__alertes_view

            elif view_name == "Parametres":
                if not self.__parametres_view:
                    print("📦 Chargement paresseux de ParametresView...")
                    self.__parametres_view = ParametresView(self.page)
                view = self.__parametres_view

            elif view_name == "Profil":
                if not self.__profil_view:
                    print("📦 Chargement paresseux de ProfilView...")
                    self.__profil_view = ProfilView(self.page)
                view = self.__profil_view

            elif view_name == "Rapports":
                if not self.__rapports_view:
                    print("📦 Chargement paresseux de RapportsView...")
                    self.__rapports_view = RapportsView(self.page)
                view = self.__rapports_view

            else:
                print(f"[WARN] Vue inconnue demandée : {view_name}")

            if view:
                self.current_view.content = view
                self._vues_chargees[view_name] = True

                if self.page:
                    self.page.update()

        except Exception as e:
            print(f"❌ Erreur chargement vue {view_name}: {e}")
            self._show_error_view(view_name)
            traceback.print_exc()

    def _show_loading_view(self, view_name: str):
        """Affiche un loader pendant le chargement"""
        self.current_view.content = Container(
            content=Column(
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    ProgressRing(width=16, height=16),
                    Container(height=8),
                    Text(f"Chargement {view_name}...", size=12),
                ],
            ),
            alignment=alignment.center,
        )
        if self.page:
            self.page.update()

    def _show_error_view(self, view_name: str):
        """Affiche une erreur de chargement"""
        self.current_view.content = Container(
            content=Column(
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Icon(Icons.ERROR_OUTLINE, color=Colors.RED_400, size=24),
                    Container(height=8),
                    Text(
                        f"Erreur chargement {view_name}", size=12, color=Colors.RED_400
                    ),
                    TextButton(
                        "Réessayer",
                        on_click=lambda e: self.__change_view_lazy(view_name),
                    ),
                ],
            ),
            alignment=alignment.center,
        )
        if self.page:
            self.page.update()

    def did_mount(self):
        """Appelé lorsque le contrôle est ajouté à la page."""
        print("🎯 AccueilPressing monté sur la page")
        # Charger les brouillons après montage
        # self._load_drafts()
        self._load_principal_view()
        self._load_drafts_light()

    @property
    def taux_dollar(self):
        return float(self._taux_dollar)

    def _get_taux(self) -> TauxDollarWrapper:
        print("🔍 Récupération du taux dollar...")
        try:
            taux = self.db.get_taux_dollar()
            if taux is None:
                print("⚠️ Aucun taux trouvé, retour à la valeur par défaut: 1.0")
                return TauxDollarWrapper(1.0)
            print(f"✅ Taux récupéré: {taux}")
            return TauxDollarWrapper(taux)
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du taux: {e}")
            return TauxDollarWrapper(1.0)

    def _init_views_sync(self):
        """Initialisation SYNCHRONE de toutes les vues"""
        try:
            print("📦 Chargement de PressingPrincipalView...")
            self.__principal_view = PressingPrincipalView(
                self.page,
                draft_handler=self._add_draft,
                taux_dollar=self._get_taux(),
            )
            print("✅ PressingPrincipalView chargé")

            print("📦 Chargement de CommandesView...")
            self.__commandes_view = CommandesView(
                self.page,
                handler_nouvelle_commande=self.__nouvelle_commande,
                accueil_reference=self,
            )
            print("✅ CommandesView chargé")

            print("📦 Chargement de ClientsView...")
            self.__clients_view = ClientsView(self.page)
            print("✅ ClientsView chargé")

            print("📦 Chargement de TableauBordPressingView...")
            self.__tableau_bord_view = TableauBordPressingView(self.page)
            print("✅ TableauBordPressingView chargé")

            print("📦 Chargement de FinancesView...")
            self.__finances_view = FinancesView(self.page)
            print("✅ FinancesView chargé")

            print("📦 Chargement de AlertesPressingView...")
            self.__alertes_view = AlertesPressingView(self.page)
            print("✅ AlertesPressingView chargé")

            print("📦 Chargement de ParametresView...")
            self.__parametres_view = ParametresView(self.page)
            print("✅ ParametresView chargé")

            print("📦 Chargement de ProfilView...")
            self.__profil_view = ProfilView(self.page)
            print("✅ ProfilView chargé")

            print("📦 Chargement de RapportsView...")
            self.__rapports_view = RapportsView(self.page)
            print("✅ RapportsView chargé")

            self._vues_initialisees = True
            print("✅ Toutes les vues ont été initialisées")

            # Placer la vue principale
            self.current_view.content = self.__principal_view
            print("✅ Vue principale attachée")

        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation des vues : {e}")
            traceback.print_exc()

    def _create_full_ui(self):
        """Interface complète"""
        # Menu latéral
        menu = Container(
            width=250,
            bgcolor="white",
            content=self._create_menu(),
            padding=padding.only(bottom=10),
        )

        # Zone de contenu principal (scrollable)
        main_area = Container(
            expand=True,
            content=Column(
                scroll=ScrollMode.AUTO,
                expand=True,
                controls=[self.current_view],
            ),
        )

        return Container(
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    self._create_header(),
                    Row(
                        expand=True,
                        controls=[menu, main_area],
                    ),
                ],
            ),
        )

    def _create_header(self):
        """Barre supérieure avec logo, badge d'alertes, paramètres, profil."""
        # Badge alertes
        self.badge_container = Container(
            width=18,
            height=18,
            bgcolor="red",
            border_radius=9,
            alignment=alignment.center,
            right=0,
            top=0,
            visible=False,
            content=Text("0", size=10, color="white"),
        )
        self.alert_badge = Stack(
            controls=[
                IconButton(
                    Icons.NOTIFICATIONS,
                    icon_color="white",
                    on_click=lambda e: self.__change_view_lazy("Alertes"),
                ),
                self.badge_container,
            ]
        )

        return Container(
            height=60,
            bgcolor=Colors.BLUE_700,
            padding=padding.symmetric(horizontal=20),
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Row(
                        controls=[
                            Image(
                                src=str(
                                    CURRENT_DIR
                                    / "assets"
                                    / "images"
                                    / "logo_la_benediction.png"
                                ),
                                height=40,
                                width=40,
                            ),
                            Text(
                                "Pressing Bénédiction",
                                color="white",
                                size=16,
                                weight=FontWeight.BOLD,
                            ),
                        ],
                        alignment=MainAxisAlignment.START,
                    ),
                    Container(expand=True),
                    Row(
                        controls=[
                            self.alert_badge,
                            IconButton(
                                Icons.SETTINGS,
                                icon_color="white",
                                on_click=lambda e: self.__change_view_lazy(
                                    "Parametres"
                                ),
                            ),
                            IconButton(
                                Icons.PERSON,
                                icon_color="white",
                                on_click=lambda e: self.__change_view_lazy("Profil"),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
            ),
        )

    def _create_menu(self):
        """Crée les boutons du menu latéral + la ListView des brouillons"""

        def menu_button(label, icon, view_name):
            btn = CustomElevatedButton(
                text=label,
                icon=icon,
                selected=(self.current_view_name == view_name),
                on_click=lambda e: self.__change_view(view_name),
            )
            self.menu_buttons[view_name] = btn
            return btn

        if not self.drafts_listview:
            self.drafts_listview = ListView(
                ref=self.drafts_list_ref,
                auto_scroll=True,
                expand=True,
                spacing=5,
            )

        return Column(
            scroll=ScrollMode.AUTO,
            spacing=0,
            expand=True,
            controls=[
                Container(height=10),
                Container(
                    padding=padding.symmetric(horizontal=15),
                    expand=True,
                    content=Column(
                        controls=[
                            menu_button("Accueil", Icons.HOME, "Accueil"),
                            menu_button("Commandes", Icons.LIST_ALT, "Commandes"),
                            menu_button("Clients", Icons.PEOPLE, "Clients"),
                            menu_button(
                                "Tableau de bord", Icons.BAR_CHART, "TableauBord"
                            ),
                            menu_button("Finances", Icons.ACCOUNT_BALANCE, "Finances"),
                            menu_button("Rapports", Icons.ANALYTICS, "Rapports"),
                            Container(height=20),
                            Text(
                                "COMMANDES ENREGISTRÉES",
                                color="black",
                                size=12,
                                weight=FontWeight.BOLD,
                            ),
                            self.drafts_listview,
                        ]
                    ),
                ),
            ],
        )

    def __change_view(self, view_name: str):
        try:
            self.current_view_name = view_name

            # Gestion spéciale pour mode édition (reste pareil)
            if view_name in ("Accueil", "NouvelleCommande") and hasattr(
                self.page, "commande_a_modifier"
            ):
                print("🔄 Création de la vue en mode ÉDITION")
                self.__principal_view = PressingPrincipalView(
                    self.page,
                    draft_handler=self._add_draft,
                    taux_dollar=float(self.taux_dollar),
                    commande_a_modifier=self.page.commande_a_modifier,
                )
                delattr(self.page, "commande_a_modifier")
            elif view_name in ("Accueil", "NouvelleCommande"):
                print("🔄 Création de la vue en mode NORMAL")
                self.__principal_view = PressingPrincipalView(
                    self.page,
                    draft_handler=self._add_draft,
                    taux_dollar=float(self.taux_dollar),
                )

            # Vérifier / instancier les vues paresseuses ici si nécessaire
            if view_name == "Commandes" and not self.__commandes_view:
                print("📦 Chargement direct paresseux de CommandesView")
                self.__commandes_view = CommandesView(
                    self.page,
                    handler_nouvelle_commande=self.__nouvelle_commande,
                    accueil_reference=self,
                )
            elif view_name == "Clients" and not self.__clients_view:
                print("📦 Chargement direct paresseux de ClientsView")
                self.__clients_view = ClientsView(self.page)
            elif view_name == "TableauBord" and not self.__tableau_bord_view:
                print("📦 Chargement direct paresseux de TableauBordPressingView")
                self.__tableau_bord_view = TableauBordPressingView(self.page)
            elif view_name == "Finances" and not self.__finances_view:
                print("📦 Chargement direct paresseux de FinancesView")
                self.__finances_view = FinancesView(self.page)
            elif view_name == "Alertes" and not self.__alertes_view:
                print("📦 Chargement direct paresseux de AlertesPressingView")
                self.__alertes_view = AlertesPressingView(self.page)
            elif view_name == "Parametres" and not self.__parametres_view:
                print("📦 Chargement direct paresseux de ParametresView")
                self.__parametres_view = ParametresView(self.page)
            elif view_name == "Profil" and not self.__profil_view:
                print("📦 Chargement direct paresseux de ProfilView")
                self.__profil_view = ProfilView(self.page)
            elif view_name == "Rapports" and not self.__rapports_view:
                print("📦 Chargement direct paresseux de RapportsView")
                self.__rapports_view = RapportsView(self.page)

            # Map des vues (après s'être assuré qu'elles sont instanciées)
            view_map = {
                "Accueil": self.__principal_view,
                "NouvelleCommande": self.__principal_view,
                "Commandes": self.__commandes_view,
                "Clients": self.__clients_view,
                "TableauBord": self.__tableau_bord_view,
                "Finances": self.__finances_view,
                "Alertes": self.__alertes_view,
                "Parametres": self.__parametres_view,
                "Profil": self.__profil_view,
                "Rapports": self.__rapports_view,
            }

            new_view = view_map.get(view_name)
            if not new_view:
                print(f"❌ Aucune vue associée au nom : {view_name}")
                return

            print(f"📱 Chargement de la vue: {view_name}")
            self.current_view.content = new_view

            # Appel des méthodes on_mount spécifiques
            mount_map = {
                "Commandes": self.__commandes_view,
                "Clients": self.__clients_view,
                "Rapports": self.__rapports_view,
                "TableauBord": self.__tableau_bord_view,
                "Finances": self.__finances_view,
                "Alertes": self.__alertes_view,
                "Parametres": self.__parametres_view,
                "Profil": self.__profil_view,
            }
            if view_name in mount_map:
                self.page.run_task(mount_map[view_name].on_mount)
            elif view_name in ("Accueil", "NouvelleCommande"):
                self.page.run_task(self._ensure_principal_view_loaded)

            self._update_menu_selection(view_name)

            if (
                view_name == "Alertes"
                and self.badge_container
                and self.badge_container.visible
            ):
                self.badge_container.visible = False
                self.badge_container.update()

            print("🔄 Mise à jour de la page...")
            self.page.update()

        except Exception as ex:
            print(f"❌ Erreur dans __change_view: {ex}")
            import traceback

            traceback.print_exc()

    def _update_menu_selection(self, selected_view: str):
        """Met à jour la sélection dans le menu"""
        for view_name, button in self.menu_buttons.items():
            button.selected = view_name == selected_view
            button.update()

    def _show_loading_view(self, view_name: str):
        """Affiche un loader pour une vue demandée"""
        self.current_view.content = Column(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            controls=[
                ProgressRing(),
                Container(height=10),
                Text(f"Chargement de « {view_name} »...", size=12),
            ],
        )
        if self.page:
            self.page.update()

    def verifier_accessibilite(self):
        """Vérifie comment CommandesView peut accéder à AccueilPressing"""
        print("🔍 Diagnostic d'accessibilité:")
        print(f"self.page: {self.page}")
        print(
            f"self.page.controls: {len(self.page.controls) if hasattr(self.page, 'controls') else 'N/A'}"
        )

        # Vérifier si cette instance est stockée quelque part accessible
        if hasattr(self.page, "accueil_pressing"):
            print("✅ AccueilPressing accessible via page.accueil_pressing")
        else:
            print("❌ AccueilPressing NON accessible via page.accueil_pressing")

        # Vérifier la structure des contrôles
        for i, control in enumerate(getattr(self.page, "controls", [])):
            print(f"Control {i}: {type(control)}")
            if hasattr(control, "content"):
                print(f"  Content: {type(control.content)}")

    def test_modification_commande(self):
        """Méthode de test pour vérifier la fonctionnalité de modification"""
        try:
            # Simuler une commande à modifier
            commande_test = {
                "id": 1,
                "numero_commande": "CMD-TEST-001",
                "client_nom": "Client Test",
                "telephone": "123456789",
                "date_depot": "2024-01-01",
                "date_retrait_prevue": "2024-01-05",
                "statut": "En attente",
                "montant_total": 10000,
                "montant_paye": 5000,
                "reste_a_payer": 5000,
            }

            self.page.commande_a_modifier = commande_test
            self.__change_view("Accueil")
            print("🧪 Test de modification lancé")

        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")

    def ouvrir_modification_commande(self, commande_data):
        """Méthode publique dédiée pour ouvrir une commande en modification"""
        try:
            print(f"🎯 Ouvrir modification commande appelé {commande_data}")
            self.page.commande_a_modifier = commande_data
            self.__change_view("Accueil")
        except Exception as e:
            print(f"❌ Erreur ouvrir_modification_commande: {e}")

    async def _delayed_load_drafts(self):
        """Charger les brouillons après un délai pour assurer l'init complète"""
        await asyncio.sleep(0.5)
        self._load_drafts()

    async def initialize_views(self):
        """Initialise les vues de manière asynchrone après l'ajout à la page"""
        try:
            print("🔄 Initialisation des vues...")

            # Création des vues principales pour le pressing
            self.__principal_view = PressingPrincipalView(
                self.page,
                draft_handler=self._add_draft,
                taux_dollar=float(self.taux_dollar),
            )

            self.__commandes_view = CommandesView(
                self.page,
                handler_nouvelle_commande=self.__nouvelle_commande,
                accueil_reference=self,
            )

            self.__clients_view = ClientsView(self.page)
            self.__tableau_bord_view = TableauBordPressingView(self.page)
            self.__finances_view = FinancesView(self.page)
            self.__alertes_view = AlertesPressingView(self.page)
            self.__parametres_view = ParametresView(self.page)
            self.__profil_view = ProfilView(self.page)
            self.__rapports_view = RapportsView(self.page)

            # Mettre à jour la vue courante si nécessaire
            if (
                hasattr(self, "current_view_name")
                and self.current_view_name == "Accueil"
            ):
                self.current_view.content = self.__principal_view
                if (
                    self.page
                    and hasattr(self.page, "update")
                    and callable(self.page.update)
                ):
                    self.page.update()

            print("✅ Vues initialisées avec succès")

        except Exception as e:
            print(f"❌ Erreur initialisation vues: {e}")
            traceback.print_exc()

    async def _safe_initialize(self):
        await self.initialize_views()
        self._load_drafts()

    async def _ensure_principal_view_loaded(self):
        """S'assure que la vue principale est complètement chargée"""
        await asyncio.sleep(0.1)  # Petit délai pour laisser l'UI se mettre à jour
        if hasattr(self.__principal_view, "update"):
            self.__principal_view.update()

    def _update_menu_selection(self, selected_view):
        """Met à jour l'état de sélection de tous les boutons du menu"""
        for view_name, button in self.menu_buttons.items():
            button.selected = view_name == selected_view
            button.update()

    def _load_drafts(self):
        """Charge les brouillons et les affiche dans la liste."""
        try:
            if not self.drafts_listview:
                return
            brouillons = self.db.charger_brouillons()

            self.drafts_listview.controls.clear()
            for b in brouillons:
                if not b or not b.get("id"):
                    continue

                nom = (
                    b.get("client", {}).get("nom")
                    or b.get("client_nom")
                    or "Client inconnu"
                )
                date = b.get("created_at", "") or b.get("date_depot", "")
                if "T" in date:
                    date = date.split("T")[0]

                btn = CustomDraftButton(
                    page=self.page,
                    brouillon_data={"id": b["id"]},
                    nom_client=nom,
                    date=date,
                    delete_callback=self.__delete_draft,
                    load_callback=self.__load_draft,
                )
                self.drafts_listview.controls.append(btn)

            self.drafts_listview.update()
        except Exception as e:
            print(f"Erreur chargement brouillons: {e}")
            if self.drafts_listview:
                self.drafts_listview.controls.clear()
                self.drafts_listview.update()

    def __load_draft(self, draft_button):
        """Charge un brouillon de commande depuis un bouton personnalisé."""
        try:
            brouillon_id = getattr(draft_button, "brouillon_data", {}).get("id")
            if brouillon_id is None and isinstance(draft_button, dict):
                brouillon_id = draft_button.get("id")
            if not brouillon_id:
                raise ValueError(f"Brouillon invalide (id absent) : {draft_button}")

            brouillon = self.db.get_brouillon_by_id(brouillon_id)
            if not brouillon:
                raise ValueError("Brouillon non trouvé en base")

            # Aller sur Accueil et injecter le brouillon
            self.__change_view("Accueil")
            if hasattr(self.__principal_view, "load_draft"):
                self.__principal_view.load_draft(brouillon)
                self._show_snackbar("Brouillon chargé avec succès", success=True)
                # Supprimer le brouillon une fois chargé
                self.db.supprimer_brouillon(brouillon_id)
                self._load_drafts()
            else:
                raise AttributeError("La vue principale ne supporte pas load_draft()")
        except Exception as e:
            print(f"[Erreur] Chargement du brouillon : {e}")
            self._show_snackbar("Erreur lors du chargement du brouillon", error=True)

    def __delete_draft(self, draft_button):
        """Supprime un brouillon et recharge la liste."""
        try:
            brouillon = getattr(draft_button, "brouillon_data", None)
            brouillon_id = (brouillon or {}).get("id")
            if brouillon_id is None and isinstance(draft_button, dict):
                brouillon_id = draft_button.get("id")

            if brouillon_id is not None:
                self.db.supprimer_brouillon(brouillon_id)
            elif brouillon:
                self.db.supprimer_brouillon_par_contenu(brouillon)
            else:
                raise ValueError("Brouillon invalide ou manquant")

            self._load_drafts()
            self._show_snackbar("Brouillon supprimé avec succès", success=True)
        except Exception as e:
            print(f"Erreur suppression brouillon: {e}")
            self._show_snackbar(
                "Erreur lors de la suppression du brouillon", error=True
            )

    def _add_draft(self, brouillon: dict):
        """Callback depuis la vue principale : enregistre un brouillon et rafraîchit la liste."""
        try:
            self.db.enregistrer_brouillon(brouillon)
            self._load_drafts()
            self._show_snackbar("Brouillon sauvegardé avec succès", success=True)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du brouillon: {e}")
            self._show_snackbar("Erreur lors de la sauvegarde du brouillon", error=True)

    def __nouvelle_commande(self, e=None):
        self.__change_view("Accueil")

    def _show_snackbar(
        self,
        message: str,
        *,
        success=False,
        color=None,
        error=False,
        bgcolor=None,
        duration=3,
    ):
        """Affiche un message Snackbar personnalisé sur la page."""
        if self.page is None:
            return

        if success:
            color = Colors.GREEN
        elif error:
            color = Colors.RED
        elif bgcolor is not None:
            color = bgcolor
        else:
            color = Colors.BLUE_700

        self.page.snack_bar = SnackBar(
            content=Text(message, color="white"),
            bgcolor=color,
            duration=duration * 1000,
            behavior=SnackBarBehavior.FLOATING,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _add_draft(self, brouillon):
        """
        Reçoit un brouillon (dict) depuis PressingPrincipalView et l'enregistre dans la base.
        """
        try:
            self.db.enregistrer_brouillon(brouillon)
            self._load_drafts()
            self._show_snackbar("Brouillon sauvegardé avec succès", success=True)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du brouillon: {e}")
            self._show_snackbar("Erreur lors de la sauvegarde du brouillon", error=True)

    def __delete_draft(self, draft_button):
        """
        Supprime un brouillon de la base de données et recharge la liste.
        """
        try:
            # Récupérer l'identifiant ou les données du brouillon à supprimer
            brouillon = getattr(draft_button, "brouillon_data", None)
            brouillon_id = getattr(draft_button, "brouillon_data", {}).get("id")
            if brouillon_id is None:
                brouillon_id = draft_button["id"]

            if not brouillon_id and not brouillon:
                raise ValueError("Brouillon invalide ou manquant")

            # Suppression via DBUtils (adapte selon ta structure, ex: utiliser un id ou hash)
            # Exemple si tu as un champ 'id' dans le brouillon :
            if brouillon_id is not None:
                self.db.supprimer_brouillon(brouillon_id)
            else:
                # Sinon, supprime par hash ou autre identifiant unique
                self.db.supprimer_brouillon_par_contenu(brouillon)

            # Recharge la liste des brouillons
            self._load_drafts()
            self._show_snackbar("Brouillon supprimé avec succès", success=True)
        except Exception as e:
            print(f"Erreur suppression brouillon: {e}")
            self._show_snackbar(
                "Erreur lors de la suppression du brouillon", error=True
            )

    def _get_alert_count(self):
        # Implémenter la logique de récupération des alertes
        try:
            return 0  # À remplacer par la vraie logique
        except Exception:
            return 0

    def _update_alert_badge(self, count):
        if count > 0:
            self.badge_container.visible = True
            self.badge_container.content.value = str(count)
        else:
            self.badge_container.visible = False

        self.badge_container.update()

    def _show_snackbar(
        self,
        message: str,
        *,
        success=False,
        color=None,
        error=False,
        bgcolor=None,
        duration=3,
    ):
        """
        Affiche un message Snackbar personnalisé sur la page.

        Paramètres :
            - message (str) : texte à afficher
            - success (bool) : message de succès (vert)
            - error (bool) : message d'erreur (rouge)
            - bgcolor (str) : couleur personnalisée (ex: Colors.BLUE_700)
            - duration (int) : durée en secondes (par défaut 3)
        """
        if self.page is None:  # ✅ Éviter l'erreur si la page n'est pas disponible
            return
        # Priorité des couleurs : success > error > couleur personnalisée > bleu par défaut
        if success:
            color = Colors.GREEN
        elif error:
            color = Colors.RED
        elif bgcolor is not None:
            color = bgcolor
        else:
            color = Colors.BLUE_700  # couleur par défaut

        self.page.snack_bar = SnackBar(
            content=Text(message, color="white"),
            bgcolor=color,
            duration=duration * 1000,  # convertir secondes en ms si besoin
            behavior=SnackBarBehavior.FLOATING,
        )
        self.page.snack_bar.open = True
        self.page.update()


class PressingPrincipalView(Column):
    def __init__(
        self, page: Page, draft_handler=None, taux_dollar=None, commande_a_modifier=None
    ):
        print("🚀 Initialisation SYNC de PressingPrincipalView...")
        super().__init__()

        self.page = page
        self.draft_handler = draft_handler
        self.commande_a_modifier = commande_a_modifier
        self.mode_edition = commande_a_modifier is not None
        print(f"📝 Mode édition : {'Oui' if self.mode_edition else 'Non'}")

        # Flags de contrôle
        self._data_loaded = False
        self._ui_controls_ready = False
        self._deja_charge = False

        self._article_has_focus = None
        self.expand = True
        self.scroll = ScrollMode.AUTO
        self.spacing = 15
        self.horizontal_alignment = CrossAxisAlignment.STRETCH

        self._active_date_field = None
        self.client_id = None
        self.commande_id = None
        self.taux_dollar = taux_dollar or 2900
        print(f"💱 Taux dollar utilisé : {self.taux_dollar}")

        self.charges_connexes_fc = 0.0
        self.reduction_accordee_fc = 0.0
        self.montant_paye_fc = 0.0
        self.article_saisie_en_cours = ""

        # Initialisation du sélecteur de date
        print("📅 Initialisation du sélecteur de date...")
        self.date_picker = DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=self._on_date_selected,
        )
        self.article_en_modification = None
        self.page.overlay.append(self.date_picker)
        print("✅ Sélecteur de date ajouté à la page")

        # Initialisation de la table de panier
        print("📊 Création de la table panier...")
        self.table_panier = DataTable(
            columns=[
                DataColumn(
                    label=Text("Article"), tooltip="Nom de l'article", numeric=False
                ),
                DataColumn(label=Text("Qté"), numeric=True),
                DataColumn(label=Text("Type")),
                DataColumn(label=Text("Prix Unit.")),
                DataColumn(label=Text("Prix Total")),
                DataColumn(label=Text("Dépôt")),
                DataColumn(label=Text("Retrait prévu")),
                DataColumn(label=Text("Statut")),
                DataColumn(label=Text("Actions")),
            ],
            rows=[],
            heading_row_color=Colors.BLUE_100,
            border=border.all(1, Colors.GREY_300),
            column_spacing=10,
        )
        print("✅ Table panier initialisée")

        # Types et statuts
        self.types_services = [
            "Lavage",
            "Repassage",
            "Nettoyage à sec",
            "Teinture",
            "Rénovation",
        ]
        self.statuts_articles = ["En attente", "En cours", "Prêt", "Livré", "Urgent"]
        print(f"📦 Types de services : {self.types_services}")
        print(f"📦 Statuts articles : {self.statuts_articles}")

        # Initialisation SYNCHRONE
        print("🔄 Initialisation SYNCHRONE des contrôles...")
        self._init_ui_controls()
        self._init_db_sync()

        # Construction de l'interface
        print("🧱 Construction de l'interface...")
        self.controls = self._create_initial_interface()

        # Si mode édition, charger la commande
        if self.mode_edition and not self._deja_charge:
            print("🔄 Chargement de la commande en mode édition...")
            self._charger_commande_existante()
            self._deja_charge = True

        self._data_loaded = True
        self._ui_controls_ready = True

        print("🎯 INIT PressingPrincipalView SYNC - Terminé")

    def did_mount(self):
        """Appelé lorsque le contrôle est ajouté à la page"""
        print("🎯 PressingPrincipalView montée sur la page")

        # Si en mode édition et pas encore chargé, charger maintenant
        if self.mode_edition and not self._deja_charge:
            print("🔄 Chargement différé des données de commande...")
            self._charger_commande_existante()
            self._deja_charge = True

    def _init_db_sync(self):
        """Initialisation SYNCHRONE de la base de données"""
        try:
            print("📦 Initialisation de la base de données...")
            self.db = db
            print("✅ Base de données initialisée")
        except Exception as e:
            print(f"❌ Erreur initialisation DB: {e}")
            self.db = None

    def _create_initial_interface(self):
        """Crée l'interface complète"""
        return [
            self._create_header_section(),
            self._create_client_section(),
            self._create_service_section(),
            self._create_article_input_section(),
            self._create_panier_section(),
            self._create_footer_section(),
        ]

    def _init_ui_controls(self):
        """Initialise tous les contrôles UI"""
        # Champs client
        self.nom_client = CustomTextField(
            label="Nom du client",
            prefix_icon=Icon(Icons.PERSON),
            width=250,
            on_change=self._rechercher_client,
        )
        self.telephone_client = CustomTextField(label="Téléphone", width=180)

        # Champs dates
        self.date_depot = self._create_date_field("Date de dépôt")
        self.date_retrait_prevue = self._create_date_field("Date de retrait prévue")

        # Sélecteurs
        self.type_service = Dropdown(
            options=[dropdown.Option(service) for service in self.types_services],
            width=180,
            value=self.types_services[0],
            on_change=self._actualiser_prix,
        )

        self.statut = Dropdown(
            options=[dropdown.Option(statut) for statut in self.statuts_articles],
            width=150,
            value=self.statuts_articles[0],
        )

        # Contrôles financiers
        self.devises = self._create_devise_dropdown()
        self.totaux = Text("0 FC", color="white", weight=FontWeight.BOLD)
        self.net_a_payer = Text(
            "Net à payer : 0 FC", weight=FontWeight.BOLD, color=Colors.BLUE_700
        )
        self.reste_a_payer = Text("0 FC", color="white", weight=FontWeight.BOLD)
        self.montant_chiffre = Text("Zéro franc congolais", size=12, expand=True)
        self.switch_speaker = Switch(value=False)

        self.mode_paiement = Dropdown(
            options=[
                dropdown.Option("Cash"),
                dropdown.Option("Mobile Money"),
                dropdown.Option("Virement"),
                dropdown.Option("Partiel"),  # Nouvelle option
            ],
            value="Cash",
            width=150,
            on_change=self._on_mode_paiement_change,
        )

        # Dans _init_ui_controls, modifiez les champs financiers
        self.charges_connexes = CustomTextField(
            label="Charges connexes",
            suffix=Text(self.devises.value),
            value="0",
            read_only=False,
            width=150,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self._calcul_totaux(),
        )

        self.reduction_accordee = CustomTextField(
            label="Réduction accordée",
            suffix=Text(self.devises.value),
            value="0",
            read_only=False,
            width=150,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self._calcul_totaux(),
        )

        self.montant_paye = CustomTextField(
            label="Paiement Cash",
            suffix=Text(self.devises.value),
            value="0",
            read_only=False,
            width=150,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self._calcul_totaux(),
        )

        # Champs de saisie d'article avec surveillance des événements clavier
        self.champ_article = AutoComplete(
            suggestions=self._get_article_suggestions(),
            on_select=self._select_article_from_suggestion,
        )

        # Ajouter un gestionnaire d'événements clavier personnalisé
        self.champ_article.on_focus = self._on_article_focus
        self.champ_article.on_blur = self._on_article_blur

        self.quantite = self._create_quantity_field()

        self.champ_prix = CustomTextField(
            label="Prix unitaire",
            value="0",
            width=120,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=self._update_total_price,
            on_submit=lambda e: self.add_article_panier(None),
        )

        self.prix_total = Text("0", size=14, weight=FontWeight.BOLD)

        # Surveiller les événements clavier au niveau de la page
        self.page.on_keyboard_event = self._handle_global_key_event

    def _create_header_section(self):
        # MODIFIÉ: Afficher "Modifier Commande" si en mode édition
        titre = "Modifier Commande" if self.mode_edition else "Nouvelle Commande"
        icon = Icons.EDIT if self.mode_edition else Icons.ADD_TASK

        return Container(
            bgcolor=Colors.with_opacity(0.05, Colors.BLUE),
            border=border.all(1, Colors.with_opacity(0.2, Colors.BLUE)),
            border_radius=border_radius.all(8),
            padding=padding.symmetric(horizontal=20, vertical=15),
            margin=padding.only(bottom=10),
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Row(
                        spacing=10,
                        controls=[
                            Icon(icon, size=26, color=Colors.BLUE_700),
                            Text(
                                titre,
                                size=22,
                                weight=FontWeight.BOLD,
                                color=Colors.BLUE_700,
                            ),
                        ],
                    ),
                    # Afficher le numéro de commande si en mode édition
                    (
                        Text(
                            (
                                f"Commande: {self.commande_a_modifier['numero_commande']}"
                                if self.mode_edition
                                else ""
                            ),
                            size=14,
                            color=Colors.GREY_600,
                        )
                        if self.mode_edition
                        else Container()
                    ),
                ],
            ),
        )

    def _verifier_etat_chargement(self):
        """Vérifie l'état du chargement des données"""
        print("\n🔍 ÉTAT DU CHARGEMENT:")
        print(f"Mode édition: {self.mode_edition}")
        print(f"Commande ID: {self.commande_id}")
        print(f"Nom client: {getattr(self.nom_client, 'value', 'N/A')}")
        print(f"Téléphone: {getattr(self.telephone_client, 'value', 'N/A')}")
        print(f"Date dépôt: {getattr(self.date_depot, 'value', 'N/A')}")
        print(f"Date retrait: {getattr(self.date_retrait_prevue, 'value', 'N/A')}")
        print(f"Nombre d'articles: {len(self.table_panier.rows)}")
        print("---\n")

    def _charger_commande_existante(self):
        """Charge les données d'une commande existante pour modification"""
        try:
            # ✅ Empêcher le double chargement
            if hasattr(self, "_deja_charge") and self._deja_charge:
                print("⚠️ Commande déjà chargée, éviter le double chargement")
                return

            print("🔄 Chargement des données de la commande existante...")

            if not self.commande_a_modifier:
                print("❌ Aucune commande à modifier")
                return

            # ✅ Stocker l'ID de la commande
            self.commande_id = self.commande_a_modifier["id"]
            print(f"🔢 ID de la commande: {self.commande_id}")

            # ✅ Vérifier que les contrôles sont bien sur la page
            if not self._controles_sur_la_page():
                print("⏳ Contrôles pas encore sur la page, report du chargement...")

                # ➕ Planifier un nouveau chargement plus tard
                import asyncio

                async def retry_later():
                    await asyncio.sleep(0.5)
                    self._charger_commande_existante()

                if self.page:
                    self.page.run_task(retry_later)
                return

            # ✅ Remplir les infos client
            if self.commande_a_modifier.get("client_id"):
                client = db.get_client(self.commande_a_modifier["client_id"])
                if client:
                    self.client_id = client["id"]
                    self.nom_client.value = client.get("nom", "")
                    self.telephone_client.value = client.get("telephone", "")
                else:
                    # Données partielles
                    self.nom_client.value = self.commande_a_modifier.get(
                        "client_nom", ""
                    )
                    self.telephone_client.value = self.commande_a_modifier.get(
                        "telephone", ""
                    )
            else:
                self.nom_client.value = self.commande_a_modifier.get("client_nom", "")
                self.telephone_client.value = self.commande_a_modifier.get(
                    "telephone", ""
                )

            # ✅ Convertir et remplir les dates
            self._convertir_et_remplir_dates()

            # ✅ Remplir les autres champs
            self.statut.value = self.commande_a_modifier.get("statut", "En attente")
            self.montant_paye.value = str(
                self.commande_a_modifier.get("montant_paye", 0)
            )
            self.mode_paiement.value = self.commande_a_modifier.get(
                "mode_paiement", "Cash"
            )
            self.charges_connexes.value = str(
                self.commande_a_modifier.get("charges_connexes", 0)
            )
            self.reduction_accordee.value = str(
                self.commande_a_modifier.get("reduction_accordee", 0)
            )

            # ✅ Charger les articles de la commande
            self._charger_articles_commande()

            # ✅ Calculer les totaux
            self._calcul_totaux()

            # ✅ Mettre à jour les champs UI
            self._update_ui_controls_safe()

            # ✅ Log de succès
            print("✅ Données de la commande chargées avec succès")

            # ✅ Mettre à jour l'état global de chargement
            self._verifier_etat_chargement()

            # ✅ Marquer comme chargé pour éviter un second chargement
            self._deja_charge = True

        except Exception as e:
            print(f"❌ Erreur lors du chargement de la commande: {e}")
            traceback.print_exc()

    def _controles_sur_la_page(self):
        """Vérifie si les contrôles principaux sont sur la page"""
        try:
            # Vérifier quelques contrôles clés
            controles_a_verifier = [
                self.nom_client,
                self.telephone_client,
                self.date_depot,
                self.date_retrait_prevue,
                self.statut,
            ]

            for controle in controles_a_verifier:
                if hasattr(controle, "page") and controle.page is None:
                    return False
            return True
        except:
            return False

    def _convertir_et_remplir_dates(self):
        """Convertit et remplit les dates dans le bon format"""
        try:
            date_depot = self.commande_a_modifier.get("date_depot", "")
            date_retrait = self.commande_a_modifier.get("date_retrait_prevue", "")

            # Fonction de conversion
            def convertir_date(date_str):
                if not date_str:
                    return ""
                try:
                    # Essayer différents formats
                    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]

                    for fmt in formats:
                        try:
                            date_obj = datetime.datetime.strptime(date_str, fmt)
                            return date_obj.strftime("%d/%m/%Y")
                        except ValueError:
                            continue

                    # Si aucun format ne fonctionne, retourner la chaîne originale
                    return date_str
                except:
                    return date_str

            self.date_depot.value = convertir_date(date_depot)
            self.date_retrait_prevue.value = convertir_date(date_retrait)

        except Exception as e:
            print(f"❌ Erreur conversion dates: {e}")
            self.date_depot.value = self.commande_a_modifier.get("date_depot", "")
            self.date_retrait_prevue.value = self.commande_a_modifier.get(
                "date_retrait_prevue", ""
            )

    def _charger_articles_commande(self):
        """Charge les articles de la commande en évitant les doublons"""
        try:
            # Vider le panier avant de charger pour éviter les doublons
            self.table_panier.rows.clear()

            articles = self.db.get_articles_commande(self.commande_id)
            print(f"📦 Nombre d'articles à charger: {len(articles)}")

            if not articles:
                print("⚠️ Aucun article trouvé pour cette commande")
                self._verifier_articles_alternatif()
                return

            for article in articles:
                try:
                    nom_article = (
                        article.get("type_article")
                        or article.get("nom")
                        or "Article inconnu"
                    )
                    quantite = article.get("quantite", 1)
                    type_service = (
                        article.get("service_nom")
                        or article.get("type_service")
                        or "Lavage"
                    )
                    prix_unitaire = float(article.get("prix_unitaire", 0))
                    prix_total = float(
                        article.get("prix_total", prix_unitaire * quantite)
                    )
                    statut_article = article.get("statut", "En attente")

                    # Vérifier si l'article n'existe pas déjà (éviter les doublons)
                    article_existe = False
                    for row in self.table_panier.rows:
                        if (
                            row._nom == nom_article
                            and row._type_service == type_service
                            and row._quantite == quantite
                        ):
                            article_existe = True
                            break

                    if not article_existe:
                        article_row = ArticlePressing(
                            nom=nom_article,
                            quantite=quantite,
                            type_service=type_service,
                            prix_unitaire=prix_unitaire,
                            prix_total=prix_total,
                            date_depot=self.date_depot.value,
                            date_retrait_prevue=self.date_retrait_prevue.value,
                            statut=statut_article,
                            article_delete=self._delete_article,
                            article_edit=self.charger_article_a_modifier,
                            calcul_totaux=self._calcul_totaux,
                            devise_initiale=self.devises.value,
                        )
                        self.table_panier.rows.append(article_row)
                        print(f"✅ Article ajouté: {nom_article} (Qty: {quantite})")
                    else:
                        print(f"⚠️ Article déjà présent: {nom_article}")

                except Exception as e:
                    print(f"❌ Erreur lors de l'ajout de l'article: {e}")
                    print(f"   Données article: {article}")

        except Exception as e:
            print(f"❌ Erreur lors du chargement des articles: {e}")

    def _verifier_articles_alternatif(self):
        """Vérifie les articles avec une méthode alternative"""
        try:
            print("🔍 Recherche alternative des articles...")

            # Méthode 1: Vérifier directement dans la table
            query_direct = "SELECT * FROM articles_commandes WHERE commande_id = ?"
            result_direct = self.db.execute_query(query_direct, (self.commande_id,))
            print(f"📋 Articles trouvés (méthode directe): {len(result_direct)}")

            # Méthode 2: Vérifier les jointures
            query_jointure = """
            SELECT ac.*, ta.nom as type_article, s.nom as service 
            FROM articles_commandes ac
            LEFT JOIN types_articles ta ON ac.type_article_id = ta.id
            LEFT JOIN services s ON ac.service_id = s.id
            WHERE ac.commande_id = ?
            """
            result_jointure = self.db.execute_query(query_jointure, (self.commande_id,))
            print(f"📋 Articles trouvés (avec jointures): {len(result_jointure)}")

            if result_direct or result_jointure:
                print("ℹ️  Articles trouvés avec méthodes alternatives")
                # Charger avec les données brutes
                for article in result_direct + result_jointure:
                    try:
                        nom_article = article.get("type_article") or "Article"
                        quantite = article.get("quantite", 1)
                        type_service = article.get("service") or "Lavage"
                        prix_unitaire = float(article.get("prix_unitaire", 0))

                        article_row = ArticlePressing(
                            nom=nom_article,
                            quantite=quantite,
                            type_service=type_service,
                            prix_unitaire=prix_unitaire,
                            prix_total=prix_unitaire * quantite,
                            date_depot=self.date_depot.value,
                            date_retrait_prevue=self.date_retrait_prevue.value,
                            statut=article.get("statut", "En attente"),
                            article_delete=self._delete_article,
                            article_edit=self.charger_article_a_modifier,
                            calcul_totaux=self._calcul_totaux,
                            devise_initiale=self.devises.value,
                        )
                        self.table_panier.rows.append(article_row)
                        print(f"✅ Article ajouté (alternatif): {nom_article}")
                    except Exception as e:
                        print(f"❌ Erreur ajout article alternatif: {e}")

        except Exception as e:
            print(f"❌ Erreur vérification alternative: {e}")

    def _update_ui_controls_safe(self):
        """Mise à jour sécurisée des contrôles UI"""
        try:
            print("🔄 Mise à jour sécurisée des contrôles UI...")

            # Attendre que les contrôles soient sur la page
            if not self._controles_sur_la_page():
                print("⏳ Contrôles pas prêts, report de la mise à jour...")
                return

            # Liste des contrôles à mettre à jour
            controls_to_update = [
                ("Nom client", self.nom_client),
                ("Téléphone client", self.telephone_client),
                ("Date dépôt", self.date_depot),
                ("Date retrait prévue", self.date_retrait_prevue),
                ("Statut", self.statut),
                ("Charges connexes", self.charges_connexes),
                ("Réduction accordée", self.reduction_accordee),
                ("Montant payé", self.montant_paye),
                ("Mode de paiement", self.mode_paiement),
            ]

            for nom, control in controls_to_update:
                try:
                    if (
                        control
                        and hasattr(control, "update")
                        and control.page is not None
                    ):
                        control.update()
                        print(f"✅ {nom} mis à jour")
                    else:
                        print(f"⚠️ {nom} non disponible pour mise à jour")
                except Exception as e:
                    print(f"❌ Erreur mise à jour {nom}: {e}")

            # Mettre à jour le tableau
            try:
                if self.table_panier and self.table_panier.page is not None:
                    self.table_panier.update()
                    print("✅ Tableau du panier mis à jour")
            except Exception as e:
                print(f"❌ Erreur mise à jour tableau: {e}")

            print("✅ Mise à jour sécurisée terminée")

        except Exception as e:
            print(f"❌ Erreur générale dans _update_ui_controls_safe: {e}")

    def _update_ui_controls(self):
        """Met à jour tous les contrôles UI après le chargement"""

        def _safe_update(control, label=""):
            """Met à jour un contrôle s’il possède une méthode update()"""
            try:
                if hasattr(control, "update") and callable(control.update):
                    control.update()
                    if label:
                        print(f"✅ {label} mis à jour")
            except Exception as e:
                print(f"❌ Erreur mise à jour {label or type(control).__name__}: {e}")

        print("🔄 Mise à jour des contrôles UI...")

        try:
            # Contrôles à mettre à jour (libellés facultatifs pour logs plus clairs)
            controls_map = {
                "Nom client": getattr(self, "nom_client", None),
                "Téléphone client": getattr(self, "telephone_client", None),
                "Date dépôt": getattr(self, "date_depot", None),
                "Date retrait prévue": getattr(self, "date_retrait_prevue", None),
                "Statut": getattr(self, "statut", None),
                "Charges connexes": getattr(self, "charges_connexes", None),
                "Réduction accordée": getattr(self, "reduction_accordee", None),
                "Montant payé": getattr(self, "montant_paye", None),
                "Mode de paiement": getattr(self, "mode_paiement", None),
            }

            for label, control in controls_map.items():
                if control:
                    _safe_update(control, label)

            # Mise à jour du tableau du panier
            table_panier = getattr(self, "table_panier", None)
            if table_panier:
                _safe_update(table_panier, "Tableau du panier")

            # Recalcul des totaux
            if hasattr(self, "_calcul_totaux") and callable(self._calcul_totaux):
                try:
                    self._calcul_totaux()
                    print("✅ Totaux recalculés")
                except Exception as e:
                    print(f"❌ Erreur lors du calcul des totaux: {e}")

            print("✅ Mise à jour des contrôles UI terminée")

        except Exception as e:
            print(f"❌ Erreur générale dans _update_ui_controls: {e}")

    def _create_footer_section(self):
        # MODIFIÉ: Changer le texte du bouton en mode édition
        texte_bouton_principal = (
            "Mettre à jour la commande" if self.mode_edition else "Terminer la commande"
        )

        return Card(
            elevation=2,
            content=Container(
                padding=padding.all(15),
                content=Column(
                    controls=[
                        Text("Récapitulatif", size=16, weight=FontWeight.BOLD),
                        Divider(height=10),
                        ResponsiveRow(
                            spacing=10,
                            controls=[
                                Container(
                                    col=6,
                                    content=Container(
                                        bgcolor=Colors.GREY_100,
                                        padding=padding.all(10),
                                        border_radius=10,
                                        content=Row(
                                            alignment=MainAxisAlignment.START,
                                            spacing=0,
                                            controls=[
                                                Container(
                                                    bgcolor=Colors.GREY_600,
                                                    padding=padding.symmetric(
                                                        horizontal=10, vertical=5
                                                    ),
                                                    border_radius=border_radius.only(
                                                        top_left=5, bottom_left=5
                                                    ),
                                                    content=Text(
                                                        "RESTE A PAYER",
                                                        color=Colors.WHITE,
                                                        weight=FontWeight.BOLD,
                                                    ),
                                                ),
                                                Container(
                                                    bgcolor=Colors.BLUE,
                                                    padding=padding.symmetric(
                                                        horizontal=15, vertical=5
                                                    ),
                                                    border_radius=border_radius.only(
                                                        top_right=5, bottom_right=5
                                                    ),
                                                    content=self.reste_a_payer,
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                                Container(
                                    col=6,
                                    content=Row(
                                        spacing=10,
                                        controls=[
                                            Container(
                                                content=self.montant_paye, expand=True
                                            ),
                                            Container(
                                                content=self.charges_connexes,
                                                expand=True,
                                            ),
                                            Container(
                                                content=self.reduction_accordee,
                                                expand=True,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        Divider(height=20),
                        ResponsiveRow(
                            spacing=10,
                            controls=[
                                Container(
                                    col=6,
                                    content=Row(
                                        spacing=10,
                                        controls=[
                                            ElevatedButton(
                                                "Réinitialiser",
                                                on_click=self._reset_cart,
                                                height=40,
                                                style=ButtonStyle(
                                                    shape=RoundedRectangleBorder(
                                                        radius=5
                                                    ),
                                                    color=Colors.WHITE,
                                                    bgcolor=Colors.GREY_600,
                                                ),
                                            ),
                                            (
                                                ElevatedButton(
                                                    "Sauvegarder brouillon",
                                                    on_click=self._add_draft,
                                                    height=40,
                                                    style=ButtonStyle(
                                                        shape=RoundedRectangleBorder(
                                                            radius=5
                                                        ),
                                                        color=Colors.WHITE,
                                                        bgcolor=Colors.GREEN,
                                                    ),
                                                )
                                                if not self.mode_edition
                                                else Container()
                                            ),  # Cacher en mode édition
                                        ],
                                    ),
                                ),
                                Container(
                                    col=6,
                                    alignment=alignment.center_right,
                                    content=ElevatedButton(
                                        texte_bouton_principal,
                                        on_click=self._finalize_commande,
                                        height=40,
                                        width=200,
                                        style=ButtonStyle(
                                            shape=RoundedRectangleBorder(radius=5),
                                            color=Colors.WHITE,
                                            bgcolor=(
                                                Colors.ORANGE
                                                if self.mode_edition
                                                else Colors.BLUE
                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ]
                ),
            ),
        )

    def _finalize_commande(self, e=None):
        """Finalise la commande (création ou modification)"""
        if self.mode_edition:
            self._mettre_a_jour_commande()
        else:
            self._creer_nouvelle_commande()

    def _mettre_a_jour_commande(self):
        """Met à jour une commande existante dans la base de données"""
        try:
            if not self.commande_id:
                self._show_snackbar("Erreur: ID de commande manquant", error=True)
                return

            # 1. Gestion du client
            telephone_client = (
                self.telephone_client.value.strip()
                if self.telephone_client.value
                else ""
            )

            if telephone_client:
                # Chercher un client existant
                client = db.get_client_by_phone(telephone_client)

                if client is None:
                    # Créer un nouveau client
                    client = self.db.creer_client(
                        nom=self.nom_client.value, telephone=telephone_client
                    )
                    if client:
                        self.client_id = client["id"]
                    else:
                        self._show_snackbar(
                            "Erreur lors de la création du client", error=True
                        )
                        return
                else:
                    self.client_id = client["id"]
            else:
                self.client_id = None

            # 2. Calculs des montants
            total_articles = sum(
                article._prix_total for article in self.table_panier.rows
            )
            charges = float(self.charges_connexes.value or 0.0)
            reduction = float(self.reduction_accordee.value or 0.0)
            montant_paye = float(self.montant_paye.value or 0.0)

            net_a_payer = total_articles + charges - reduction
            reste_a_payer = max(0.0, net_a_payer - montant_paye)
            type_paiement = "Partiel" if reste_a_payer > 0 else "Complet"

            # 3. Mettre à jour la commande principale
            db.mettre_a_jour_commande_complete(
                commande_id=self.commande_id,
                client_id=self.client_id,
                date_retrait_prevue=self.date_retrait_prevue.value,
                montant_total=net_a_payer,
                montant_paye=montant_paye,
                reste_a_payer=reste_a_payer,
                type_paiement=type_paiement,
                mode_paiement=self.mode_paiement.value,
                statut=self.statut.value,
            )

            # 4. Mettre à jour les articles
            # Supprimer les anciens articles
            self.db.supprimer_articles_commande(self.commande_id)

            # Ajouter les nouveaux articles
            for article in self.table_panier.rows:
                type_article_id = self._get_type_article_id(article._nom)
                service_id = self._get_service_id(article._type_service)

                if type_article_id and service_id:
                    self.db.ajouter_article_commande(
                        commande_id=self.commande_id,
                        type_article_id=type_article_id,
                        service_id=service_id,
                        quantite=int(article._quantite),
                        prix_unitaire=float(article._prix_unitaire),
                        notes="",
                        statut=article._statut,
                    )

            # 5. Mettre à jour la dette si nécessaire
            if reste_a_payer > 0:
                # Vérifier si une dette existe déjà
                dettes_existantes = self.db.get_dettes_par_commande(self.commande_id)

                if dettes_existantes:
                    # Mettre à jour la dette existante
                    self.db.mettre_a_jour_dette(
                        dette_id=dettes_existantes[0]["id"],
                        montant_initial=reste_a_payer,
                        date_echeance=self.date_retrait_prevue.value,
                    )
                else:
                    # Créer une nouvelle dette
                    self.db.creer_dette_client(
                        client_id=self.client_id,
                        commande_id=self.commande_id,
                        montant_initial=reste_a_payer,
                        date_echeance=self.date_retrait_prevue.value,
                    )
            else:
                # Supprimer la dette si elle existe
                self.db.supprimer_dette_par_commande(self.commande_id)

            self._show_snackbar(
                f"Commande #{self.commande_id} mise à jour avec succès ✅", success=True
            )

            # Générer le bon de commande mis à jour
            self._generer_bon_commande()

            # Rediriger vers la vue des commandes après un délai
            import asyncio

            async def rediriger():
                await asyncio.sleep(2)
                self._retour_vers_commandes()

            asyncio.create_task(rediriger())

        except Exception as e:
            self._show_snackbar(f"Erreur lors de la mise à jour: {str(e)}", error=True)

    def _retour_vers_commandes(self):
        """Retourne à la vue des commandes"""
        # Cette méthode dépend de votre architecture de navigation
        if hasattr(self.page, "parent") and hasattr(self.page.parent, "__change_view"):
            self.page.parent.__change_view("Commandes")

    def _generer_bon_commande(self):
        """Génère le bon de commande mis à jour"""
        try:
            articles_data = []
            for article in self.table_panier.rows:
                articles_data.append(
                    [
                        article._nom,
                        article._quantite,
                        article._type_service,
                        article._prix_unitaire,
                        article._prix_total,
                    ]
                )

            total_articles = sum(
                article._prix_total for article in self.table_panier.rows
            )
            charges = float(self.charges_connexes.value or 0.0)
            reduction = float(self.reduction_accordee.value or 0.0)
            montant_paye = float(self.montant_paye.value or 0.0)
            net_a_payer = total_articles + charges - reduction

            imprimer_commande_thread(
                list_articles=articles_data,
                prix_total=net_a_payer,
                reduction=reduction,
                charges_connexes=charges,
                montant_paye=montant_paye,
                reste_a_payer=max(0.0, net_a_payer - montant_paye),
                montant_final=net_a_payer,
                montant_en_lettres=number_to_words(net_a_payer),
                date=self.date_depot.value,
                date_retrait_prevue=self.date_retrait_prevue.value,
                nom_client=self.nom_client.value,
                telephone_client=self.telephone_client.value,
                num_commande=self.commande_a_modifier["numero_commande"],
                statut=self.statut.value,
                mode_paiement=self.mode_paiement.value,
                devise=self.devises.value,
            )
        except Exception as e:
            print(f"Erreur génération bon de commande: {e}")

    def charger_commande_pour_modification(self, commande_data):
        """Méthode pour charger une commande depuis CommandesView"""
        self.commande_a_modifier = commande_data
        self.mode_edition = True
        self._charger_commande_existante()

    def _on_mode_paiement_change(self, e):
        if self.mode_paiement.value == "Partiel":
            self.montant_paye.read_only = False
            self.montant_paye.value = "0"
        else:
            self.montant_paye.read_only = True
            # Si mode complet, montant payé = total
            total = sum(article._prix_total for article in self.table_panier.rows)
            self.montant_paye.value = str(total)
        self.montant_paye.update()
        self._calcul_totaux()

    def charger_article_a_modifier(self, article: ArticlePressing):
        # Ne surtout pas retirer l'article de la table ici

        # Mettre à jour la variable autocomplete bricolée
        self.article_saisie_en_cours = article._nom

        # Charger les valeurs dans les champs d'entrée
        self.champ_article.value = article._nom
        self.type_service.value = article._type_service
        self.quantite.value = str(article._quantite)
        self.champ_prix.value = str(article._prix_unitaire)
        self.prix_total.value = f"{article._prix_total:.2f} {self.devises.value}"

        # Mettre l'article en mode modification
        self.article_en_modification = article

        # Forcer la mise à jour des contrôles UI
        self.champ_article.update()
        self.type_service.update()
        self.quantite.update()
        self.champ_prix.update()
        self.prix_total.update()

    def _on_charges_change(self, e):
        try:
            valeur = float(e.control.value) if e.control.value else 0.0
            # Convertir en FC si nécessaire
            if self.devises.value == "$":
                self.charges_connexes_fc = valeur * self.taux_dollar
            else:
                self.charges_connexes_fc = valeur
        except ValueError:
            self.charges_connexes_fc = 0.0
        self._calcul_totaux()

    def _on_reduction_change(self, e):
        try:
            valeur = float(e.control.value) if e.control.value else 0.0
            # Convertir en FC si nécessaire
            if self.devises.value == "$":
                self.reduction_accordee_fc = valeur * self.taux_dollar
            else:
                self.reduction_accordee_fc = valeur
        except ValueError:
            self.reduction_accordee_fc = 0.0
        self._calcul_totaux()

    def _on_montant_paye_change(self, e):
        try:
            valeur = float(e.control.value) if e.control.value else 0.0
            # Convertir en FC si nécessaire
            if self.devises.value == "$":
                self.montant_paye_fc = valeur * self.taux_dollar
            else:
                self.montant_paye_fc = valeur
        except ValueError:
            self.montant_paye_fc = 0.0
        self._calcul_totaux()

    def _get_type_article_id(self, nom_article: str) -> int:
        query = "SELECT id FROM types_articles WHERE nom = ?"
        result = db.execute_select(query, (nom_article,))
        if result:
            return result[0]["id"]  # Ajuste selon ta méthode execute_select
        else:
            # Optionnel: insérer un nouveau type article si non trouvé
            insert_query = "INSERT INTO types_articles (nom, prix_base) VALUES (?, ?)"
            prix_base = 0  # Ou un prix par défaut, ou un paramètre
            db.execute_update(insert_query, (nom_article, prix_base))
            # Récupérer l'id inséré
            new_id = db.cursor.lastrowid
            return new_id

    def _get_service_id(self, nom_service: str) -> int:
        query = "SELECT id FROM services WHERE nom = ?"
        result = db.execute_select(query, (nom_service,))
        if result:
            return result[0]["id"]
        else:
            # Optionnel: insérer un nouveau service si non trouvé
            insert_query = "INSERT INTO services (nom, prix_unitaire) VALUES (?, ?)"
            prix_unitaire = 0  # Valeur par défaut
            db.execute_update(insert_query, (nom_service, prix_unitaire))
            new_id = db.cursor.lastrowid
            return new_id

    def _on_article_focus(self, e):
        """Quand le champ article prend le focus"""
        self._article_has_focus = True
        self.page.update()

    def _on_article_blur(self, e):
        """Quand le champ article perd le focus"""
        self._article_has_focus = False
        # Sauvegarder la valeur actuelle
        if hasattr(e.control, "value"):
            self.article_saisie_en_cours = e.control.value
        self.page.update()

    def _handle_global_key_event(self, e: KeyboardEvent):
        """Gestionnaire global des événements clavier"""
        # Si le champ article a le focus, capturer la saisie
        if self._article_has_focus and e.key:
            # Mettre à jour la saisie en cours
            if e.key == "Backspace":
                self.article_saisie_en_cours = self.article_saisie_en_cours[:-1]
            elif len(e.key) == 1:  # Caractère normal
                self.article_saisie_en_cours += e.key

            # Mettre à jour la valeur du champ (pour l'affichage)
            self.champ_article.value = self.article_saisie_en_cours
            self.champ_article.update()

            # Filtrer les suggestions en fonction de la saisie
            self._update_suggestions_based_on_input()

        # Gestion des touches spéciales
        if e.key == "Escape":
            self._reset_entry_fields()
        elif e.key == "Enter" and self._article_has_focus:
            # Si on appuye sur Entrée dans le champ article, on ajoute l'article
            self.add_article_panier(None)

    def _update_suggestions_based_on_input(self):
        """Met à jour les suggestions en fonction de la saisie"""
        if not self.article_saisie_en_cours:
            # Si la saisie est vide, afficher toutes les suggestions
            self.champ_article.suggestions = self._get_article_suggestions()
        else:
            # Filtrer les suggestions en fonction de la saisie
            filtered_suggestions = [
                s
                for s in self._get_article_suggestions()
                if self.article_saisie_en_cours.lower() in s.value.lower()
            ]
            self.champ_article.suggestions = filtered_suggestions

        self.champ_article.update()

    def _create_date_field(self, label):
        current_date = datetime.datetime.now()
        return CustomTextField(
            label=label,
            width=160,
            value=format_date(current_date),
            prefix_icon=Icon(Icons.CALENDAR_TODAY, color="black"),
            read_only=True,
            on_click=lambda e: self._open_date_picker(e.control),
        )

    def _open_date_picker(self, text_field):
        try:
            current_date = parse_date(text_field.value) or datetime.datetime.now()
            self.date_picker.current_date = current_date
            self._active_date_field = text_field
            self.date_picker.open = True
            self.page.update()
        except Exception as ex:
            print(f"Erreur dans _open_date_picker: {ex}")

    def _on_date_selected(self, e):
        try:
            selected_date = e.control.value
            if selected_date and self._active_date_field:
                self._active_date_field.value = selected_date.strftime("%d/%m/%Y")
                self._active_date_field.update()
        except Exception as ex:
            print(f"Erreur dans _on_date_selected: {ex}")

    def _create_devise_dropdown(self):
        return Dropdown(
            options=[dropdown.Option("FC"), dropdown.Option("$")],
            width=80,
            border_radius=10,
            bgcolor="white",
            content_padding=padding.symmetric(vertical=0, horizontal=10),
            value="FC",
            on_change=self._change_devise,
        )

    def _create_quantity_field(self):
        return CustomTextField(
            value="1",
            width=80,
            input_filter=NumbersOnlyInputFilter(),
            on_change=self._update_total_price,
            on_submit=lambda e: self.add_article_panier(None),
            suffix=Column(
                controls=[
                    IconButton(
                        Icons.ARROW_DROP_UP,
                        icon_size=16,
                        padding=0,
                        height=12,
                        width=16,
                        on_click=lambda e: self._adjust_quantity(1),
                    ),
                    IconButton(
                        Icons.ARROW_DROP_DOWN,
                        icon_size=16,
                        padding=0,
                        height=12,
                        width=16,
                        on_click=lambda e: self._adjust_quantity(-1),
                    ),
                ],
                spacing=0,
                tight=True,
            ),
        )

    def _create_client_section(self):
        return Card(
            elevation=2,
            content=Container(
                padding=padding.all(15),
                content=Column(
                    controls=[
                        Text("Informations Client", size=16, weight=FontWeight.BOLD),
                        Divider(height=10),
                        ResponsiveRow(
                            controls=[
                                Container(content=self.nom_client, col=4),
                                Container(content=self.telephone_client, col=3),
                                Container(content=self.date_depot, col=2),
                                Container(content=self.date_retrait_prevue, col=3),
                            ],
                            spacing=10,
                        ),
                    ],
                ),
            ),
        )

    def _create_service_section(self):
        return Card(
            elevation=2,
            content=Container(
                padding=padding.all(15),
                content=Column(
                    controls=[
                        Text("Détails du Service", size=16, weight=FontWeight.BOLD),
                        Divider(height=10),
                        ResponsiveRow(
                            spacing=10,
                            controls=[
                                Container(content=self.statut, col=3),
                                Container(content=self.devises, col=2),
                                Container(
                                    col=7,
                                    content=Column(
                                        spacing=5,
                                        controls=[
                                            self.net_a_payer,
                                            Row(
                                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                                                vertical_alignment=CrossAxisAlignment.CENTER,
                                                controls=[
                                                    Container(
                                                        content=self.montant_chiffre,
                                                        expand=True,
                                                    ),
                                                    IconButton(
                                                        icon=Icons.RECORD_VOICE_OVER,
                                                        icon_size=20,
                                                        on_click=lambda e: self._speak_amount(),
                                                    ),
                                                    self.switch_speaker,
                                                ],
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )

    def _create_article_input_section(self):
        return Card(
            elevation=2,
            content=Container(
                padding=padding.all(15),
                content=Column(
                    controls=[
                        Text("Ajouter un Article", size=16, weight=FontWeight.BOLD),
                        Divider(height=10),
                        ResponsiveRow(
                            controls=[
                                Container(content=Text("Article"), col=3),
                                Container(content=Text("Type"), col=2),
                                Container(content=Text("Quantité"), col=1),
                                Container(content=Text("Prix Unitaire"), col=2),
                                Container(content=Text("Prix Total"), col=2),
                                Container(content=Text("Action"), col=2),
                            ],
                            spacing=5,
                        ),
                        ResponsiveRow(
                            controls=[
                                Container(
                                    content=Container(
                                        padding=padding.symmetric(horizontal=5),
                                        bgcolor=Colors.WHITE,
                                        border_radius=5,
                                        content=self.champ_article,
                                    ),
                                    col=3,
                                ),
                                Container(content=self.type_service, col=2),
                                Container(content=self.quantite, col=1),
                                Container(content=self.champ_prix, col=2),
                                Container(
                                    content=Row(
                                        controls=[
                                            self.prix_total,
                                            Text(self.devises.value),
                                        ],
                                    ),
                                    col=2,
                                ),
                                Container(
                                    content=ElevatedButton(
                                        "+ Ajouter",
                                        on_click=self.add_article_panier,
                                        height=40,
                                        style=ButtonStyle(
                                            shape=RoundedRectangleBorder(radius=5),
                                            color=Colors.WHITE,
                                            bgcolor=Colors.BLUE,
                                        ),
                                    ),
                                    col=2,
                                ),
                            ],
                            spacing=5,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ],
                ),
            ),
        )

    def _create_panier_section(self):
        return Card(
            elevation=2,
            content=Container(
                padding=padding.all(10),
                content=Column(
                    controls=[
                        Text("Panier d'Articles", size=16, weight=FontWeight.BOLD),
                        Divider(height=6),
                        Container(
                            height=300,
                            content=Column(
                                expand=True, scroll="auto", controls=[self.table_panier]
                            ),
                        ),
                    ],
                ),
            ),
        )

    def _create_footer_section(self):
        return Card(
            elevation=2,
            content=Container(
                padding=padding.all(15),
                content=Column(
                    controls=[
                        Text("Récapitulatif", size=16, weight=FontWeight.BOLD),
                        Divider(height=10),
                        ResponsiveRow(
                            spacing=10,
                            controls=[
                                Container(
                                    col=6,
                                    content=Container(
                                        bgcolor=Colors.GREY_100,
                                        padding=padding.all(10),
                                        border_radius=10,
                                        content=Row(
                                            alignment=MainAxisAlignment.START,
                                            spacing=0,
                                            controls=[
                                                Container(
                                                    bgcolor=Colors.GREY_600,
                                                    padding=padding.symmetric(
                                                        horizontal=10, vertical=5
                                                    ),
                                                    border_radius=border_radius.only(
                                                        top_left=5, bottom_left=5
                                                    ),
                                                    content=Text(
                                                        "RESTE A PAYER",
                                                        color=Colors.WHITE,
                                                        weight=FontWeight.BOLD,
                                                    ),
                                                ),
                                                Container(
                                                    bgcolor=Colors.BLUE,
                                                    padding=padding.symmetric(
                                                        horizontal=15, vertical=5
                                                    ),
                                                    border_radius=border_radius.only(
                                                        top_right=5, bottom_right=5
                                                    ),
                                                    content=self.reste_a_payer,
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                                Container(
                                    col=6,
                                    content=Row(
                                        spacing=10,
                                        controls=[
                                            Container(
                                                content=self.montant_paye, expand=True
                                            ),
                                            Container(
                                                content=self.charges_connexes,
                                                expand=True,
                                            ),
                                            Container(
                                                content=self.reduction_accordee,
                                                expand=True,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        Divider(height=20),
                        ResponsiveRow(
                            spacing=10,
                            controls=[
                                Container(
                                    col=6,
                                    content=Row(
                                        spacing=10,
                                        controls=[
                                            ElevatedButton(
                                                "Réinitialiser",
                                                on_click=self._reset_cart,
                                                height=40,
                                                style=ButtonStyle(
                                                    shape=RoundedRectangleBorder(
                                                        radius=5
                                                    ),
                                                    color=Colors.WHITE,
                                                    bgcolor=Colors.GREY_600,
                                                ),
                                            ),
                                            ElevatedButton(
                                                "Sauvegarder brouillon",
                                                on_click=self._add_draft,
                                                height=40,
                                                style=ButtonStyle(
                                                    shape=RoundedRectangleBorder(
                                                        radius=5
                                                    ),
                                                    color=Colors.WHITE,
                                                    bgcolor=Colors.GREEN,
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                                Container(
                                    col=6,
                                    alignment=alignment.center_right,
                                    content=ElevatedButton(
                                        "Terminer la commande",
                                        on_click=self._finalize_commande,
                                        height=40,
                                        width=200,
                                        style=ButtonStyle(
                                            shape=RoundedRectangleBorder(radius=5),
                                            color=Colors.WHITE,
                                            bgcolor=Colors.BLUE,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ]
                ),
            ),
        )

    def _get_article_suggestions(self):
        # Cette méthode doit être implémentée selon votre base de données
        articles = [
            {"nom": "Chemise"},
            {"nom": "Pantalon"},
            {"nom": "Robe"},
            {"nom": "Veste"},
        ]
        return [AutoCompleteSuggestion(key=a["nom"], value=a["nom"]) for a in articles]

    def _select_article_from_suggestion(self, e: AutoCompleteSelectEvent):
        prix_par_defaut = {
            "Chemise": 1500,
            "Pantalon": 2000,
            "Robe": 2500,
            "Veste": 3000,
        }

        # Mettre à jour la saisie en cours
        self.article_saisie_en_cours = e.selection.value

        # Déterminer le prix
        prix = prix_par_defaut.get(e.selection.value, 0)
        if self.devises.value == "$":
            prix = prix / self.taux_dollar

        # Mettre à jour les champs de prix
        self.champ_prix.value = f"{prix:.2f}"
        self.champ_prix.update()

        self._update_total_price(None)

    def _ajouter_article_table(
        self,
        nom,
        quantite,
        type_service,
        prix_unitaire,
        prix_total,
        statut,
        date_depot,
        date_retrait,
    ):
        # Création d'une nouvelle ligne de données (DataRow)
        row = DataRow(
            cells=[
                DataCell(Text(nom)),
                DataCell(Text(str(quantite))),
                DataCell(Text(type_service)),
                DataCell(Text(f"{prix_unitaire} ")),
                DataCell(Text(f"{prix_total} ")),
                DataCell(Text(date_depot)),
                DataCell(Text(date_retrait)),
                DataCell(Text(statut)),
                DataCell(
                    Row(
                        controls=[
                            IconButton(
                                icon=Icons.DELETE,
                                icon_color=Colors.RED,
                                tooltip="Supprimer",
                                on_click=lambda e: self._supprimer_article(nom),
                            ),
                            IconButton(
                                icon=Icons.EDIT,
                                tooltip="Modifier",
                                on_click=lambda e: self._modifier_article(nom),
                            ),
                        ]
                    )
                ),
            ]
        )

        # Ajout de la ligne au tableau
        self.table_panier.rows.append(row)
        self.table_panier.update()

        # Recalcul des totaux (si applicable)
        self._calcul_totaux()

    def _supprimer_article(self, nom_article):
        nouvelle_liste = []
        for row in self.table_panier.rows:
            nom = row.cells[0].content.value
            if nom != nom_article:
                nouvelle_liste.append(row)

        self.table_panier.rows = nouvelle_liste
        self.table_panier.update()
        self._calcul_totaux()
        self._show_snackbar(f"Article '{nom_article}' supprimé.")

    def _modifier_article(self, nom_article):
        for row in self.table_panier.rows:
            if row.cells[0].content.value == nom_article:
                self.champ_article.value = nom_article
                self.quantite.value = int(row.cells[1].content.value)
                self.type_service.value = row.cells[2].content.value
                self.champ_prix.value = row.cells[3].content.value.replace(" FC", "")
                self.date_depot.value = row.cells[5].content.value
                self.date_retrait_prevue.value = row.cells[6].content.value

                # Marque qu'on est en train de modifier cet article
                self.article_en_modification = nom_article
                self._update_total_price(None)
                self.champ_article.update()
                self.quantite.update()
                self.type_service.update()
                self.champ_prix.update()
                self.date_depot.update()
                self.date_retrait_prevue.update()

                self._show_snackbar(f"Modification de '{nom_article}' en cours...")
                break

    def _adjust_quantity(self, delta: int):
        current = int(self.quantite.value or 0)
        new_value = max(0, current + delta)
        self.quantite.value = str(new_value)
        self.quantite.update()
        self._update_total_price(None)

    def _update_total_price(self, e):
        try:
            qty = int(self.quantite.value or 0)
            prix = float(self.champ_prix.value.split(" ")[0] or 0)
            self.prix_total.value = f"{qty * prix:.2f}"
            self.prix_total.update()
        except:
            pass

    def _rechercher_client(self, e):
        # Implémentation simplifiée - à adapter selon votre base de données
        nom_client = self.nom_client.value
        if nom_client:
            # Simulation de recherche client
            clients = {
                "Dupont": {"telephone": "0123456789", "dette": 5000},
                "Martin": {"telephone": "0987654321", "dette": 0},
            }

            if nom_client in clients:
                client_info = clients[nom_client]
                self.telephone_client.value = client_info["telephone"]
                if client_info["dette"] > 0:
                    self._show_snackbar(
                        f"Client a une dette de {client_info['dette']} FC"
                    )

    def _actualiser_prix(self, e):
        # Implémentation simplifiée - à adapter selon votre base de données
        prix_par_service = {
            "Lavage": 1000,
            "Repassage": 800,
            "Nettoyage à sec": 1500,
            "Teinture": 2000,
            "Rénovation": 2500,
        }

        type_service = self.type_service.value
        prix = prix_par_service.get(type_service, 0)
        if self.devises.value == "$":
            prix = prix / self.taux_dollar

        self.champ_prix.value = f"{prix:.2f}"
        self.champ_prix.update()
        self._update_total_price(None)

    def _find_article_index(self, article_to_find):
        for i, article in enumerate(self.table_panier.rows):
            if (
                article._nom == article_to_find._nom
                and article._type_service == article_to_find._type_service
                and article._quantite == article_to_find._quantite
                and article._prix_unitaire == article_to_find._prix_unitaire
            ):
                return i
        return None

    def add_article_panier(self, e):
        try:
            # 1. Récupérer le nom de l'article
            nom = (
                self.article_saisie_en_cours.strip()
                if self.article_saisie_en_cours
                else (
                    self.champ_article.value.strip()
                    if hasattr(self.champ_article, "value")
                    else ""
                )
            )

            if not nom:
                self._show_snackbar("❌ Veuillez saisir ou sélectionner un article.")
                return

            # 2. Autres données saisies
            type_service = self.type_service.value
            statut = self.statut.value

            try:
                qty = int(self.quantite.value)
            except ValueError:
                self._show_snackbar("❌ Quantité invalide.")
                return

            try:
                prix = float(self.champ_prix.value.split(" ")[0].replace(",", "."))
            except ValueError:
                self._show_snackbar("❌ Prix unitaire invalide.")
                return

            if qty <= 0:
                self._show_snackbar("❌ La quantité doit être supérieure à zéro.")
                return

            # 3. Empêcher les doublons (par nom + type_service)
            for row in self.table_panier.rows:
                cell0 = row.cells[0].content
                cell2 = row.cells[2].content

                if hasattr(cell0, "value"):
                    nom_row = cell0.value.strip().lower()
                elif hasattr(cell0, "content") and hasattr(cell0.content, "value"):
                    nom_row = cell0.content.value.strip().lower()
                else:
                    nom_row = ""

                if hasattr(cell2, "value"):
                    type_row = cell2.value.strip().lower()
                elif hasattr(cell2, "content") and hasattr(cell2.content, "value"):
                    type_row = cell2.content.value.strip().lower()
                else:
                    type_row = ""

                if nom_row == nom.lower() and type_row == type_service.lower():
                    self._show_snackbar(
                        "⚠️ Cet article existe déjà dans le panier avec ce type de service."
                    )
                    pass  # Tu peux gérer ici la mise à jour ou autre comportement

            if self.article_en_modification:
                # Modification : remplacer à la place exacte dans la table
                index = self._find_article_index(self.article_en_modification)

                # Création nouvelle instance pour éviter l'erreur "Text Control must be added..."
                article_modifie = ArticlePressing(
                    nom=nom,
                    quantite=qty,
                    type_service=type_service,
                    prix_unitaire=prix,
                    prix_total=qty * prix,
                    date_depot=self.date_depot.value,
                    date_retrait_prevue=self.date_retrait_prevue.value,
                    statut=statut,
                    article_edit=self.charger_article_a_modifier,
                    article_delete=self._delete_article,
                    calcul_totaux=self._calcul_totaux,
                    devise_initiale=self.devises.value,
                )

                if index is not None:
                    self.table_panier.rows[index] = article_modifie
                else:
                    # Si l'article en modification n'est pas dans la liste, on l'ajoute en fin
                    self.table_panier.rows.append(article_modifie)

                self.table_panier.update()
                self.article_en_modification = None

            else:
                # Ajout d'un nouvel article
                article_row = ArticlePressing(
                    nom=nom,
                    quantite=qty,
                    type_service=type_service,
                    prix_unitaire=prix,
                    prix_total=qty * prix,
                    date_depot=self.date_depot.value,
                    date_retrait_prevue=self.date_retrait_prevue.value,
                    statut=statut,
                    article_edit=self.charger_article_a_modifier,
                    article_delete=self._delete_article,
                    calcul_totaux=self._calcul_totaux,
                    devise_initiale=self.devises.value,
                )

                self.table_panier.rows.append(article_row)
                self.table_panier.update()

                self._show_snackbar("✅ Article ajouté au panier.", bgcolor="green")

            # Réinitialiser les champs et recalculer les totaux dans tous les cas
            self._reset_entry_fields()
            self._calcul_totaux()

        except Exception as ex:
            print(f"[Erreur] add_article_panier: {ex}")
            self._show_snackbar(f"❌ Une erreur s'est produite : {ex}")

    def _edit_article(self, article):
        # Remplir les champs avec les valeurs de l'article sélectionné
        self.champ_article.value = article._nom
        self.quantite.value = str(article._quantite)
        self.type_service.value = article._type_service
        self.champ_prix.value = str(article._prix_unitaire)
        self.date_depot.value = article._date_depot
        self.date_retrait_prevue.value = article._date_retrait_prevue
        self.statut.value = article._statut
        self.devises.value = article._devise
        self.article_en_modification = article
        self.champ_article.update()
        self.quantite.update()
        self.type_service.update()
        self.champ_prix.update()
        self.date_depot.update()
        self.date_retrait_prevue.update()
        self.statut.update()
        self.devises.update()
        self._show_snackbar(f"Modification de '{article._nom}' en cours...")

    def _delete_article(self, article):
        try:
            self.table_panier.rows.remove(article)
            self.table_panier.update()
            self._calcul_totaux()
        except Exception as ex:
            print(f"[Erreur] _delete_article: {ex}")
            self._show_snackbar("❌ Impossible de supprimer l'article.")

    def _reset_entry_fields(self):
        # Réinitialiser la variable de saisie autocomplete bricolé
        self.article_saisie_en_cours = ""

        # Réinitialiser le champ article (texte + suggestions)
        self.champ_article.value = ""
        self.champ_article.suggestions = self._get_article_suggestions()

        # Gérer le focus pour que l'utilisateur puisse saisir directement
        self.champ_article.focus = False
        self.page.update()  # Appliquer la perte de focus avant de remettre
        self.champ_article.focus = True
        self.champ_article.update()

        # Réinitialiser les autres champs
        self.type_service.value = ""  # À adapter si tu as une valeur par défaut
        self.type_service.update()

        self.quantite.value = "1"
        self.quantite.update()

        self.champ_prix.value = "0"
        self.champ_prix.update()

        self.prix_total.value = (
            f"0 {self.devises.value}"  # Toujours cohérent avec la devise affichée
        )
        self.prix_total.update()

        # S'assurer qu'on n'est plus en mode modification
        self.article_en_modification = None

    def _reset_cart(self, e):
        self.table_panier.rows = []
        self.nom_client.value = ""
        self.telephone_client.value = ""
        self._reset_entry_fields()
        self.table_panier.update()
        self._calcul_totaux()

    def _add_draft(self, e):
        """
        Construit un brouillon à partir du panier d'articles et des informations client,
        puis le transmet au draft_handler si disponible.
        """

        # Vérifie s'il y a des articles dans le panier
        if not self.table_panier.rows:
            self._show_snackbar("Aucun article à enregistrer", error=True)
            return

        # Initialisation des articles
        draft_articles = []
        for article in self.table_panier.rows:
            draft_articles.append(
                {
                    "nom": article._nom,
                    "quantite": article._quantite,
                    "type_service": article._type_service,
                    "prix_unitaire": article._prix_unitaire,
                    "prix_total": article._prix_total,
                    "statut": getattr(
                        article, "_statut", "En attente"
                    ),  # valeur par défaut
                    "date_depot": self.date_depot.value,
                    "date_retrait_prevue": self.date_retrait_prevue.value,
                }
            )

        # Valeurs client avec défauts
        nom_client = self.nom_client.value or "Sans nom"
        telephone_client = self.telephone_client.value or ""
        date_depot = self.date_depot.value or datetime.datetime.now().strftime(
            "%d-%m-%Y"
        )
        date_retrait_prevue = self.date_retrait_prevue.value or ""

        # Montants connexes
        charges = float(self.charges_connexes.value or 0.0)
        reduction = float(self.reduction_accordee.value or 0.0)
        total_articles = sum(a["prix_total"] for a in draft_articles)
        net_a_payer = total_articles + charges - reduction

        # Paiement
        montant_paye = float(self.montant_paye.value or 0.0)
        type_paiement = "Partiel" if montant_paye < net_a_payer else "Complet"

        # Construction du brouillon
        brouillon = {
            "client": {
                "nom": nom_client,
                "telephone": telephone_client,
                "date_depot": date_depot,
                "date_retrait_prevue": date_retrait_prevue,
            },
            "service": {
                "statut": self.statut.value,
                "devise": self.devises.value,
                "net_a_payer": net_a_payer,
                "montant_lettres": number_to_words(net_a_payer),
            },
            "paiement": {
                "mode": self.mode_paiement.value,
                "montant_paye": montant_paye,
                "type": type_paiement,
            },
            "charges": charges,
            "reduction": reduction,
            "totaux": total_articles,
            "articles": draft_articles,
        }

        # Envoie du brouillon via le handler
        if self.draft_handler:
            self.draft_handler(brouillon)
            self._show_snackbar("Brouillon sauvegardé avec succès")
            self._reset_cart(None)
        else:
            self._show_snackbar(
                "Impossible de sauvegarder le brouillon (draft_handler manquant)",
                error=True,
            )

    def load_draft(self, brouillon_data):
        """Charge un brouillon depuis la base de données"""
        try:
            # Réinitialiser le panier
            self.table_panier.rows.clear()

            # Récupérer les données du brouillon
            articles = brouillon_data.get("articles", [])
            client = brouillon_data.get("client", {})
            service = brouillon_data.get("service", {})

            # Réinsérer chaque article du brouillon dans le panier
            for article in articles:
                article_row = ArticlePressing(
                    nom=article.get("nom", ""),
                    quantite=article.get("quantite", 1),
                    type_service=article.get("type_service", ""),
                    prix_unitaire=article.get("prix_unitaire", 0),
                    prix_total=article.get("prix_total", 0),
                    date_depot=article.get("date_depot", ""),
                    date_retrait_prevue=article.get("date_retrait_prevue", ""),
                    statut=article.get("statut", "En attente"),
                    article_delete=self._delete_article,
                    article_edit=self.charger_article_a_modifier,
                    calcul_totaux=self._calcul_totaux,
                    devise_initiale=article.get("devise", "FC"),
                )
                self.table_panier.rows.append(article_row)

            # Mettre à jour les champs client
            self.nom_client.value = client.get("nom", "")
            self.telephone_client.value = client.get("telephone", "")
            self.date_depot.value = client.get("date_depot", "")
            self.date_retrait_prevue.value = client.get("date_retrait_prevue", "")
            self.statut.value = service.get("statut", "En attente")
            self.devises.value = service.get("devise", "FC")

            # Mettre à jour les totaux
            self._calcul_totaux()

            # Mettre à jour l'interface
            self.nom_client.update()
            self.telephone_client.update()
            self.date_depot.update()
            self.date_retrait_prevue.update()
            self.statut.update()
            self.devises.update()
            self.table_panier.update()

            self._show_snackbar("Brouillon chargé", success=True)

        except Exception as e:
            print(f"Erreur lors du chargement du brouillon: {e}")
            self._show_snackbar("Erreur lors du chargement du brouillon", error=True)

    def _change_devise(self, e: ControlEvent):
        # Déterminer le taux de conversion
        if self.devises.value == "$":
            taux = 1 / self.taux_dollar
        else:
            taux = self.taux_dollar

        devise_actuelle = self.devises.value

        # ✅ Mettre à jour les articles dans le panier
        for article in self.table_panier.rows:
            try:
                ancien_prix = float(article.txt_prix_unitaire.value.split(" ")[0])
                nouveau_prix = ancien_prix * taux
                article.txt_prix_unitaire.value = (
                    f"{nouveau_prix:.2f} {devise_actuelle}"
                )

                quantite = float(article._quantite)
                article.txt_prix_total.value = (
                    f"{nouveau_prix * quantite:.2f} {devise_actuelle}"
                )

                # Mettre à jour la devise interne si nécessaire
                article._devise = devise_actuelle
            except Exception as ex:
                print(f"[Erreur de conversion article] {ex}")

        # ✅ Mettre à jour les champs financiers (charges, réductions, paiement)
        self._update_financial_fields(taux)
        self._update_financial_fields(taux)

        # Seul le champ montant_paye est converti uniquement si en mode partiel
        if self.mode_paiement.value == "Partiel":
            self._update_financial_fields(taux)

        # ✅ Mettre à jour le champ de saisie prix unitaire (si non vide)
        if self.champ_prix.value and self.champ_prix.value.strip() != "0":
            try:
                ancien = float(self.champ_prix.value.strip())
                nouveau = ancien * taux
                self.champ_prix.value = f"{nouveau:.2f}"
                self.champ_prix.update()
                self._update_total_price(None)
            except:
                pass

        # ✅ Rafraîchir les éléments visuels
        self.table_panier.update()
        self._calcul_totaux()

    def _update_totals_with_devise(self, taux):
        # Convertir les valeurs stockées en FC vers la nouvelle devise
        devise = self.devises.value

        # Mettre à jour les champs avec la nouvelle devise
        self.charges_connexes.suffix = Text(devise)
        self.reduction_accordee.suffix = Text(devise)
        self.montant_paye.suffix = Text(devise)

        # Convertir les valeurs affichées
        if self.charges_connexes.value and self.charges_connexes.value != "0":
            charges_actuelles = (
                float(self.charges_connexes.value.split(" ")[0])
                if " " in self.charges_connexes.value
                else float(self.charges_connexes.value)
            )
            self.charges_connexes.value = f"{charges_actuelles * taux:.2f}"

        if self.reduction_accordee.value and self.reduction_accordee.value != "0":
            reduction_actuelle = (
                float(self.reduction_accordee.value.split(" ")[0])
                if " " in self.reduction_accordee.value
                else float(self.reduction_accordee.value)
            )
            self.reduction_accordee.value = f"{reduction_actuelle * taux:.2f}"

        if self.montant_paye.value and self.montant_paye.value != "0":
            montant_actuel = (
                float(self.montant_paye.value.split(" ")[0])
                if " " in self.montant_paye.value
                else float(self.montant_paye.value)
            )
            self.montant_paye.value = f"{montant_actuel * taux:.2f}"

        # Mettre à jour l'affichage
        self.charges_connexes.update()
        self.reduction_accordee.update()
        self.montant_paye.update()

    def _update_financial_fields(self, taux):
        # Mettre à jour les champs financiers avec la nouvelle devise
        devise = self.devises.value

        # Convertir et mettre à jour les valeurs
        for field_name in ["charges_connexes", "reduction_accordee", "montant_paye"]:
            field = getattr(self, field_name)
            if field.value and field.value != "0":
                try:
                    # Extraire la valeur numérique (en ignorant la devise)
                    value_str = field.value
                    if " " in value_str:
                        value_str = value_str.split(" ")[0]

                    current_value = float(value_str)
                    new_value = current_value * taux
                    field.value = f"{new_value:.2f}"
                    field.update()
                except ValueError:
                    pass

        # Mettre à jour les suffixes pour afficher la bonne devise
        self.charges_connexes.suffix = Text(devise)
        self.reduction_accordee.suffix = Text(devise)
        self.montant_paye.suffix = Text(devise)

        # Mettre à jour l'affichage
        self.charges_connexes.update()
        self.reduction_accordee.update()
        self.montant_paye.update()

    def _calcul_totaux(self):
        total = 0
        for article in self.table_panier.rows:
            total += parse_montant(article.txt_prix_total.value)

        # Récupérer les valeurs des champs financiers
        try:
            charges = (
                float(self.charges_connexes.value.split(" ")[0])
                if " " in self.charges_connexes.value
                else float(self.charges_connexes.value or 0)
            )
        except ValueError:
            charges = 0

        try:
            reduction = (
                float(self.reduction_accordee.value.split(" ")[0])
                if " " in self.reduction_accordee.value
                else float(self.reduction_accordee.value or 0)
            )
        except ValueError:
            reduction = 0

        try:
            montant_paye = (
                float(self.montant_paye.value.split(" ")[0])
                if " " in self.montant_paye.value
                else float(self.montant_paye.value or 0)
            )
        except ValueError:
            montant_paye = 0

        net_a_payer = total + charges - reduction
        devise = self.devises.value

        self.totaux.value = f"{net_a_payer:.2f} {devise}"
        self.net_a_payer.value = f"Net à payer : {net_a_payer:.2f} {devise}"
        self.reste_a_payer.value = max(0.0, net_a_payer - montant_paye)
        self.montant_chiffre.value = number_to_words(net_a_payer) + f" {devise}"

        # ✅ Ne faire update QUE si les contrôles sont affichés
        for ctrl in [
            self.totaux,
            self.reste_a_payer,
            self.net_a_payer,
            self.montant_chiffre,
        ]:
            if ctrl.page:
                ctrl.update()

    def _speak_amount(self):
        if self.switch_speaker.value:
            speaker = Speaker()
            speaker.say(self.montant_chiffre.value)

    def handler_keyboard_key(self, e: KeyboardEvent):
        if e.key == "Escape":
            # Vider le champ actif selon le focus
            if hasattr(self, "_active_field") and self._active_field:
                self._active_field.value = ""
                self._active_field.update()
            elif self._article_has_focus:
                self.article_saisie_en_cours = ""
                self.champ_article.value = ""
                self.champ_article.update()
        elif e.key == "Enter" and self._article_has_focus:
            self.add_article_panier(None)

    def _show_snackbar(
        self,
        message: str,
        *,
        success=False,
        color=None,
        error=False,
        bgcolor=None,
        duration=3,
    ):
        """
        Affiche un message Snackbar personnalisé sur la page.

        Paramètres :
            - message (str) : texte à afficher
            - success (bool) : message de succès (vert)
            - error (bool) : message d'erreur (rouge)
            - bgcolor (str) : couleur personnalisée (ex: Colors.BLUE_700)
            - duration (int) : durée en secondes (par défaut 3)
        """
        if self.page is None:  # ✅ Éviter l'erreur si la page n'est pas disponible
            return
        # Priorité des couleurs : success > error > couleur personnalisée > bleu par défaut
        if success:
            color = Colors.GREEN
        elif error:
            color = Colors.RED
        elif bgcolor is not None:
            color = bgcolor
        else:
            color = Colors.BLUE_700  # couleur par défaut

        self.page.snack_bar = SnackBar(
            content=Text(message, color="white"),
            bgcolor=color,
            duration=duration * 1000,  # convertir secondes en ms si besoin
            behavior=SnackBarBehavior.FLOATING,
        )
        self.page.snack_bar.open = True
        self.page.update()


def main(page: Page):
    page.title = "Pressing La Bénédiction - Système de Gestion"
    page.favicon = str(CURRENT_DIR / "assets" / "images" / "logo_la_benediction.png")
    page.padding = 0
    page.fonts = {
        "Poppins": str(
            CURRENT_DIR / "assets" / "fonts" / "Poppins" / "Poppins-Regular.ttf"
        ),
        "Poppins-Bold": str(
            CURRENT_DIR / "assets" / "fonts" / "Poppins" / "Poppins-Bold.ttf"
        ),
    }

    # Configuration du thème avec une apparence professionnelle
    page.theme = Theme(
        font_family="Poppins", color_scheme_seed="blue", use_material3=True
    )

    page.window_maximized = True
    page.window.min_width = 1200
    page.window.min_height = 700

    page.dialog = AlertDialog(
        modal=True,
        title=Text("Veuillez patienter..."),
        content=ProgressRing(),
        actions=[],
        actions_alignment=MainAxisAlignment.CENTER,
    )

    # Gestionnaire de session utilisateur
    user_session = {
        "logged_in": False,
        "username": None,
        "role": None,
        "permissions": [],
    }

    # Gestionnaire de sauvegarde automatique
    autosave_interval = 300  # 5 minutes
    last_autosave = time.time()

    def check_autosave():
        nonlocal last_autosave
        current_time = time.time()
        if (
            current_time - last_autosave >= autosave_interval
            and user_session["logged_in"]
        ):
            # Sauvegarde automatique des brouillons
            drafts = init_load_drafts()
            save_drafts(drafts)
            last_autosave = current_time
            page.snack_bar = SnackBar(
                Text("Sauvegarde automatique effectuée"), duration=2000
            )
            page.snack_bar.open = True
            page.update()

    # Vérification périodique de sauvegarde automatique
    def autosave_task():
        while True:
            time.sleep(60)  # Vérifier toutes les minutes
            check_autosave()

    # Démarrer le thread de sauvegarde automatique
    page.run_thread(autosave_task)

    last_route_before_login = "/home"  # Par défaut

    def on_route_change(event):
        global last_route_before_login
        page.views.clear()

        routes = {
            "/": lambda: View(
                "/", [LoginView(page, on_login_success=on_login_success)]
            ),
            "/login": lambda: View(
                "/login", [LoginView(page, on_login_success=on_login_success)]
            ),
            "/home": lambda: View("/home", [AccueilPressing(page)]),
            "/orders": lambda: View("/orders", [CommandesView(page)]),
            "/clients": lambda: View("/clients", [ClientsView(page)]),
            "/stats": lambda: View("/stats", [StatistiquesView(page)]),
            "/settings": lambda: View("/settings", [ParametresView(page)]),
            "/profil": lambda: View("/profil", [ProfilView(page)]),
        }

        current_route = event.route

        # Si non connecté et page protégée, mémoriser et forcer login
        if not user_session.get("logged_in", False) and current_route not in [
            "/",
            "/login",
        ]:
            last_route_before_login = current_route  # mémoriser la route
            page.views.append(routes["/login"]())
        elif current_route in routes:
            page.views.append(routes[current_route]())
        else:
            # Page 404
            page.views.append(
                View(
                    "/404",
                    [
                        Container(
                            content=Column(
                                controls=[
                                    Text(
                                        "Page non trouvée",
                                        size=24,
                                        weight=FontWeight.BOLD,
                                    ),
                                    Text("La page que vous recherchez n'existe pas."),
                                    ElevatedButton(
                                        "Retour à l'accueil",
                                        on_click=lambda e: page.go("/home"),
                                    ),
                                ],
                                alignment=MainAxisAlignment.CENTER,
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                            ),
                            alignment=alignment.center,
                            expand=True,
                        )
                    ],
                )
            )

        page.update()

    def on_login_success(username, role):
        user_session["logged_in"] = True
        user_session["username"] = username
        user_session["role"] = role

        # Définir les permissions en fonction du rôle
        if role == "admin":
            user_session["permissions"] = ["all"]
        elif role == "gestionnaire":
            user_session["permissions"] = ["orders", "clients", "stats"]
        elif role == "employe":
            user_session["permissions"] = ["orders"]

        page.go("/home")

    def on_logout(e):
        user_session["logged_in"] = False
        user_session["username"] = None
        user_session["role"] = None
        user_session["permissions"] = []

        # Sauvegarder les brouillons avant de se déconnecter
        drafts = init_load_drafts()
        save_drafts(drafts)

        page.go("/")

    def navigate_to(index):
        routes = ["/home", "/orders", "/clients", "/stats", "/settings"]
        if 0 <= index < len(routes):
            page.go(routes[index])

    # Gestion des erreurs globales
    def on_error(e):
        error_msg = f"Une erreur s'est produite: {e.data if hasattr(e, 'data') else 'Erreur inconnue'}"
        page.snack_bar = SnackBar(Text(error_msg), duration=4000)
        page.snack_bar.open = True
        page.update()

    # Gestion des événements clavier globaux
    def on_keyboard(e: KeyboardEvent):
        if e.key == "F1":
            page.go("/home")
        elif e.key == "F2" and user_session["logged_in"]:
            page.go("/orders")
        elif e.key == "F5":
            page.update()
        elif e.key == "F12" and user_session.get("role") == "admin":
            page.go("/settings")

    # Configuration des gestionnaires d'événements
    page.on_route_change = on_route_change
    page.on_view_pop = lambda view: page.views.pop() if len(page.views) > 1 else None
    page.on_error = on_error
    page.on_keyboard_event = on_keyboard

    # Vérifier si l'utilisateur est déjà connecté (session persistante)
    saved_user = page.client_storage.get("user")
    if saved_user:
        user_session["logged_in"] = True
        user_session["username"] = saved_user.get("username")
        user_session["role"] = saved_user.get("role")
        page.go("/home")
    else:
        page.go("/")

    # Mettre à jour la page après initialisation
    page.update()


app(main, assets_dir=str(CURRENT_DIR / "assets"))  # view=WEB_BROWSER,
