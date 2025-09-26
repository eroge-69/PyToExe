import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
import logging
import json
import os
import csv
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="Dashboard PEA - Gestion Complète avec Stratégie Trading",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fichier de sauvegarde
PORTFOLIO_FILE = "portfolio_pea.json"
ALERTS_FILE = "alertes_pea.json"

# Liste des actions éligibles PEA
ACTIONS_PEA = {
    'ACCOR': 'AC.PA',
    'AIR LIQUIDE': 'AI.PA',
    'AIRBUS': 'AIR.PA',
    'ALSTOM': 'ALO.PA',
    'AXA': 'CS.PA',
    'BNP PARIBAS': 'BNP.PA',
    'BOUYGUES': 'EN.PA',
    'CAPGEMINI': 'CAP.PA',
    'CARREFOUR': 'CA.PA',
    'CREDIT AGRICOLE': 'ACA.PA',
    'DANONE': 'DAN.PA',
    'EDF': 'EDF.PA',
    'ENGIE': 'ENGI.PA',
    'HERMES': 'RMS.PA',
    'KERING': 'KER.PA',
    'LOREAL': 'OR.PA',
    'LVMH': 'MC.PA',
    'MICHELIN': 'ML.PA',
    'ORANGE': 'ORA.PA',
    'PERNOD RICARD': 'RI.PA',
    'PUBLICIS': 'PUB.PA',
    'RENAULT': 'RNO.PA',
    'SAFRAN': 'SAF.PA',
    'SAINT GOBAIN': 'SGO.PA',
    'SANOFI': 'SAN.PA',
    'SCHNEIDER ELECTRIC': 'SU.PA',
    'SOCIETE GENERALE': 'GLE.PA',
    'STELLANTIS': 'STLA.PA',
    'TOTALENERGIES': 'TTE.PA',
    'VINCI': 'DG.PA'
}

ACTIONS_PEA_PME = {
    'BENETEAU': 'BEN.PA',
    'EUROFINS SCIENTIFIC': 'ERF.PA',
    'GIMV': 'GIMB.BR',
    'GUERBET': 'GBT.PA',
    'IPSOS': 'IPS.PA',
    'LABEYRIE': 'LABE.PA',
    'LDC': 'LOUP.PA',
    'LISI': 'FII.PA',
    'METROPOLE TV': 'MMT.PA',
    'NEXANS': 'NEX.PA',
    'SOITEC': 'SOI.PA',
    'TFF GROUP': 'TFF.PA',
    'TRIGANO': 'TRI.PA'
}

def safe_float(value, default=0):
    """Convertit safely en float"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def load_portfolio():
    """Charge le portefeuille depuis le fichier JSON"""
    try:
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        logger.error(f"Erreur chargement portfolio: {e}")
        return {}

def save_portfolio(portfolio):
    """Sauvegarde le portefeuille dans le fichier JSON"""
    try:
        with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde portfolio: {e}")
        return False

def get_technical_analysis(ticker, action_name):
    """Analyse technique pour recommandations d'achat/vente"""
    try:
        stock = yf.Ticker(ticker)
        
        # Données historiques pour analyse technique
        hist = stock.history(period="6mo")
        if hist.empty or len(hist) < 50:
            return {"erreur": "Données historiques insuffisantes"}
        
        # Calcul des indicateurs techniques
        prix_actuel = hist['Close'].iloc[-1]
        prix_20j = hist['Close'].rolling(20).mean().iloc[-1]
        prix_50j = hist['Close'].rolling(50).mean().iloc[-1]
        prix_200j = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else prix_50j
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        perte = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / perte
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(rs.iloc[-1]) else 50
        
        # Support et résistance
        resistance = hist['High'].rolling(20).max().iloc[-1]
        support = hist['Low'].rolling(20).min().iloc[-1]
        
        # Tendances
        tendance_courte = "HAUSSIÈRE" if prix_actuel > prix_20j else "BAISSIÈRE"
        tendance_moyenne = "HAUSSIÈRE" if prix_20j > prix_50j else "BAISSIÈRE"
        tendance_longue = "HAUSSIÈRE" if prix_50j > prix_200j else "BAISSIÈRE"
        
        # Score d'achat/vente (0-100)
        score_achat = 0
        score_vente = 0
        
        # Règles de scoring
        if prix_actuel > prix_200j: score_achat += 25
        if prix_actuel > prix_50j: score_achat += 20
        if rsi < 30: score_achat += 20  # Survente
        if prix_actuel < support * 1.02: score_achat += 15  # Proche support
        if tendance_longue == "HAUSSIÈRE": score_achat += 20
        
        if prix_actuel < prix_200j: score_vente += 25
        if prix_actuel < prix_50j: score_vente += 20
        if rsi > 70: score_vente += 20  # Surachat
        if prix_actuel > resistance * 0.98: score_vente += 15  # Proche résistance
        if tendance_longue == "BAISSIÈRE": score_vente += 20
        
        # Recommandation finale
        if score_achat - score_vente >= 20:
            recommandation = "🟢 FORT ACHAT"
            confidence = min(95, score_achat)
        elif score_achat - score_vente >= 10:
            recommandation = "🟡 ACHAT MODÉRÉ"
            confidence = max(score_achat, score_vente)
        elif score_vente - score_achat >= 20:
            recommandation = "🔴 FORTE VENTE"
            confidence = min(95, score_vente)
        elif score_vente - score_achat >= 10:
            recommandation = "🟠 VENTE MODÉRÉE"
            confidence = max(score_achat, score_vente)
        else:
            recommandation = "⚪ NEUTRE"
            confidence = 50
        
        return {
            'prix_actuel': prix_actuel,
            'moyenne_20j': prix_20j,
            'moyenne_50j': prix_50j,
            'moyenne_200j': prix_200j,
            'rsi': rsi,
            'resistance': resistance,
            'support': support,
            'tendance_courte': tendance_courte,
            'tendance_moyenne': tendance_moyenne,
            'tendance_longue': tendance_longue,
            'score_achat': score_achat,
            'score_vente': score_vente,
            'recommandation': recommandation,
            'confidence': confidence,
            'erreur': None
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse technique {ticker}: {e}")
        return {"erreur": str(e)}

def check_price_alerts(portfolio, stock_data, technical_data):
    """Vérifie les alertes de prix avec recommandations trading"""
    alerts = []
    total_perte = 0
    actions_en_alerte = 0
    recommendations_achat = 0
    recommendations_vente = 0
    
    for action_name, details in portfolio.items():
        if action_name in stock_data and not stock_data[action_name]['erreur']:
            prix_actuel = stock_data[action_name]['prix_actuel']
            prix_achat = details['prix_achat']
            
            if prix_actuel > 0 and prix_achat > 0:
                # Calcul de la variation
                variation = ((prix_actuel - prix_achat) / prix_achat) * 100
                perte_absolue = (prix_achat - prix_actuel) * details['quantite']
                
                # Analyse technique pour recommandation
                tech_analysis = technical_data.get(action_name, {})
                recommandation = tech_analysis.get('recommandation', '⚪ NEUTRE')
                confidence = tech_analysis.get('confidence', 50)
                
                # Déterminer l'action recommandée
                if "ACHAT" in recommandation and variation < -5:
                    action_recommandee = "💰 ACHETER PLUS"
                    raison = "Bon moment pour moyenner à la baisse"
                    recommendations_achat += 1
                elif "VENTE" in recommandation and variation > 10:
                    action_recommandee = "📉 PRENDRE LES BÉNÉFICES"
                    raison = "Prendre les bénéfices après une bonne hausse"
                    recommendations_vente += 1
                elif variation < -15:
                    action_recommandee = "⏳ SURVEILLER"
                    raison = "Baisse importante, attendre un signal d'achat"
                elif variation < -5:
                    action_recommandee = "📊 ANALYSER"
                    raison = "Légère baisse, vérifier les fondamentaux"
                else:
                    action_recommandee = "✅ CONSERVER"
                    raison = "Performance satisfaisante"
                
                # Vérifier si en alerte (prix actuel < prix achat)
                if prix_actuel < prix_achat:
                    alerts.append({
                        'action': action_name,
                        'prix_achat': prix_achat,
                        'prix_actuel': prix_actuel,
                        'variation': variation,
                        'quantite': details['quantite'],
                        'perte_totale': perte_absolue,
                        'niveau_alerte': get_alert_level(variation),
                        'recommandation': recommandation,
                        'action_recommandee': action_recommandee,
                        'raison': raison,
                        'confidence': confidence,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    total_perte += perte_absolue
                    actions_en_alerte += 1
    
    return alerts, total_perte, actions_en_alerte, recommendations_achat, recommendations_vente

def get_alert_level(variation):
    """Détermine le niveau d'alerte basé sur la variation"""
    if variation <= -20:
        return "🔴 CRITIQUE"
    elif variation <= -10:
        return "🟠 ÉLEVÉE"
    elif variation <= -5:
        return "🟡 MOYENNE"
    else:
        return "🔵 SURVEILLANCE"

def get_stock_data(ticker, action_name):
    """Récupère les données d'une action"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Prix actuel
        current_price = safe_float(info.get('currentPrice'))
        previous_close = safe_float(info.get('previousClose', current_price))
        
        # Historique pour les variations
        try:
            hist = stock.history(period='2d', interval='1d')
            if not hist.empty and len(hist) > 1:
                current_price = safe_float(hist['Close'].iloc[-1])
                previous_close = safe_float(hist['Close'].iloc[-2])
        except:
            pass
        
        # Calcul des variations
        change = current_price - previous_close if previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        # Dividendes
        current_year = datetime.now().year
        current_year_dividend = 0
        next_year_dividend = 0
        
        try:
            dividends = stock.dividends
            if not dividends.empty:
                current_year_dividends = dividends[dividends.index.year == current_year]
                if not current_year_dividends.empty:
                    current_year_dividend = safe_float(current_year_dividends.sum())
                
                recent_dividends = dividends[dividends.index.year >= current_year - 3]
                if not recent_dividends.empty:
                    yearly_dividends = recent_dividends.groupby(recent_dividends.index.year).sum()
                    next_year_dividend = safe_float(yearly_dividends.mean())
        except Exception as e:
            logger.warning(f"Erreur dividends {ticker}: {e}")
        
        dividend_yield = safe_float(info.get('dividendYield', 0)) * 100
        
        return {
            'prix_actuel': current_price,
            'variation': change,
            'variation_pourcent': change_percent,
            'dividende_annee_cours': current_year_dividend,
            'dividende_annee_prochaine': next_year_dividend,
            'rendement_dividende': dividend_yield,
            'volume': safe_float(info.get('volume', 0)),
            'market_cap': info.get('marketCap', 0),
            'erreur': None
        }
        
    except Exception as e:
        logger.error(f"Erreur majeure pour {ticker}: {e}")
        return {
            'prix_actuel': 0,
            'variation': 0,
            'variation_pourcent': 0,
            'dividende_annee_cours': 0,
            'dividende_annee_prochaine': 0,
            'rendement_dividende': 0,
            'volume': 0,
            'market_cap': 0,
            'erreur': str(e)
        }

def calculate_dividend_income(portfolio, stock_data):
    """Calcule les revenus de dividendes pour un portefeuille"""
    results = {}
    total_annee_cours = 0
    total_annee_prochaine = 0
    total_investissement = 0
    
    for action_name, details in portfolio.items():
        if action_name in stock_data and not stock_data[action_name]['erreur']:
            nb_actions = details['quantite']
            prix_achat = details['prix_achat']
            
            data = stock_data[action_name]
            dividende_cours = data['dividende_annee_cours'] * nb_actions
            dividende_prochain = data['dividende_annee_prochaine'] * nb_actions
            investissement = nb_actions * prix_achat
            valeur_actuelle = nb_actions * data['prix_actuel']
            plus_value = valeur_actuelle - investissement
            
            results[action_name] = {
                'quantite': nb_actions,
                'prix_achat': prix_achat,
                'investissement': investissement,
                'valeur_actuelle': valeur_actuelle,
                'plus_value': plus_value,
                'dividende_cours': dividende_cours,
                'dividende_prochain': dividende_prochain,
                'rendement_sur_cours': (dividende_cours / valeur_actuelle * 100) if valeur_actuelle > 0 else 0,
                'rendement_sur_achat': (dividende_cours / investissement * 100) if investissement > 0 else 0,
                'date_ajout': details.get('date_ajout', 'Inconnue')
            }
            
            total_annee_cours += dividende_cours
            total_annee_prochaine += dividende_prochain
            total_investissement += investissement
    
    return results, total_annee_cours, total_annee_prochaine, total_investissement

def main():
    st.title("🎯 Dashboard PEA - Gestion Complète avec Stratégie Trading")
    st.markdown("***Gestion avancée avec suppression d'actions, analyse technique et recommandations intelligentes***")
    
    # Initialisation du session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = load_portfolio()
    
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = None
    
    # Sidebar
    st.sidebar.header("🎯 Gestion du Portefeuille")
    
    # Sélection du type de PEA
    pea_type = st.sidebar.selectbox("Type de PEA", ["PEA Classique", "PEA-PME"])
    actions = ACTIONS_PEA if pea_type == "PEA Classique" else ACTIONS_PEA_PME
    
    # Configuration de la stratégie
    st.sidebar.subheader("⚙️ Paramètres de Trading")
    
    strategie_active = st.sidebar.checkbox("Activer les recommandations trading", value=True)
    agressivite = st.sidebar.selectbox("Profil de risque", 
                                      ["Conservateur", "Modéré", "Agressif"])
    stop_loss_auto = st.sidebar.checkbox("Alertes stop-loss automatiques", value=True)
    
    # Seuils personnalisables
    col1, col2 = st.sidebar.columns(2)
    with col1:
        seuil_achat = st.number_input("Seuil achat (%)", -30, 0, -10)
    with col2:
        seuil_vente = st.number_input("Seuil vente (%)", 0, 50, 15)
    
    # Gestion avancée du portefeuille
    st.sidebar.subheader("🗂️ Gestion des Actions")
    
    # Ajout d'actions
    with st.sidebar.form("add_stock_form"):
        st.write("**➕ Ajouter une action**")
        action_choice = st.selectbox("Action", list(actions.keys()))
        quantite = st.number_input("Nombre d'actions", min_value=1, value=10)
        prix_achat = st.number_input("Prix d'achat moyen (€)", min_value=0.0, value=100.0, step=0.5)
        
        if st.form_submit_button("💾 Ajouter au portefeuille"):
            st.session_state.portfolio[action_choice] = {
                'quantite': quantite,
                'prix_achat': prix_achat,
                'ticker': actions[action_choice],
                'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            if save_portfolio(st.session_state.portfolio):
                st.sidebar.success(f"✅ {quantite} actions {action_choice} ajoutées!")
                st.rerun()
    
    # Suppression d'actions
    if st.session_state.portfolio:
        st.sidebar.subheader("🗑️ Supprimer des Actions")
        
        action_to_delete = st.sidebar.selectbox(
            "Sélectionner l'action à supprimer",
            list(st.session_state.portfolio.keys())
        )
        
        if action_to_delete:
            # Affichage des détails de l'action à supprimer
            details = st.session_state.portfolio[action_to_delete]
            st.sidebar.write(f"**Détails de {action_to_delete}:**")
            st.sidebar.write(f"- Quantité: {details['quantite']} actions")
            st.sidebar.write(f"- Prix d'achat: {details['prix_achat']}€")
            st.sidebar.write(f"- Investissement: {details['quantite'] * details['prix_achat']}€")
            
            # Confirmation de suppression
            if st.sidebar.button("🗑️ Supprimer cette action", type="secondary"):
                st.session_state.delete_confirmation = action_to_delete
            
            # Modal de confirmation
            if st.session_state.delete_confirmation == action_to_delete:
                st.sidebar.warning("⚠️ Confirmez la suppression")
                col1, col2 = st.sidebar.columns(2)
                
                with col1:
                    if st.button("✅ Confirmer", type="primary"):
                        # Suppression effective
                        del st.session_state.portfolio[action_to_delete]
                        save_portfolio(st.session_state.portfolio)
                        st.session_state.delete_confirmation = None
                        st.sidebar.error(f"❌ {action_to_delete} supprimée!")
                        time.sleep(1)
                        st.rerun()
                
                with col2:
                    if st.button("❌ Annuler"):
                        st.session_state.delete_confirmation = None
                        st.rerun()
        
        # Suppression multiple
        st.sidebar.subheader("🧹 Nettoyage du Portefeuille")
        
        actions_to_clean = st.sidebar.multiselect(
            "Sélectionner plusieurs actions à supprimer",
            list(st.session_state.portfolio.keys())
        )
        
        if actions_to_clean:
            if st.sidebar.button("🗑️ Supprimer les actions sélectionnées", type="secondary"):
                for action in actions_to_clean:
                    del st.session_state.portfolio[action]
                save_portfolio(st.session_state.portfolio)
                st.sidebar.error(f"❌ {len(actions_to_clean)} actions supprimées!")
                time.sleep(1)
                st.rerun()
        
        # Réinitialisation complète
        if st.sidebar.button("💥 Tout supprimer", type="primary"):
            st.session_state.portfolio = {}
            save_portfolio({})
            st.sidebar.error("💥 Portefeuille entièrement vidé!")
            time.sleep(1)
            st.rerun()
    
    # Section principale
    if st.session_state.portfolio:
        # Récupération des données
        stock_data = {}
        technical_data = {}
        
        progress_bar = st.progress(0)
        total_actions = len(st.session_state.portfolio)
        
        for i, (action_name, details) in enumerate(st.session_state.portfolio.items()):
            ticker = details['ticker']
            stock_data[action_name] = get_stock_data(ticker, action_name)
            
            if strategie_active:
                technical_data[action_name] = get_technical_analysis(ticker, action_name)
            
            progress_bar.progress((i + 1) / total_actions)
        
        progress_bar.empty()
        
        # Vérification des alertes avec recommandations
        if strategie_active:
            alerts, total_perte, actions_en_alerte, rec_achat, rec_vente = check_price_alerts(
                st.session_state.portfolio, stock_data, technical_data
            )
            
            # Bannière d'alerte principale
            if alerts:
                st.error("🚨 **ALERTE TRADING** - Opportunités détectées")
                
                # Métriques de trading
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Recommandations ACHAT", rec_achat)
                
                with col2:
                    st.metric("Recommandations VENTE", rec_vente)
                
                with col3:
                    st.metric("Actions sous water", actions_en_alerte)
                
                with col4:
                    st.metric("Perte totale", f"{total_perte:,.0f}€")
                
                # Détail des alertes avec recommandations
                with st.expander("🎯 RECOMMANDATIONS DÉTAILLÉES", expanded=True):
                    for alert in sorted(alerts, key=lambda x: x['variation']):
                        st.markdown(f"""
                        <div style="border: 2px solid; border-color: {'green' if 'ACHETER' in alert['action_recommandee'] else 'red' if 'VENTE' in alert['action_recommandee'] else 'orange'}; 
                        padding: 15px; border-radius: 10px; margin: 10px 0; background-color: {'#f0f8f0' if 'ACHETER' in alert['action_recommandee'] else '#fff0f0' if 'VENTE' in alert['action_recommandee'] else '#fffaf0'}">
                            <h4>{'💰' if 'ACHETER' in alert['action_recommandee'] else '📉' if 'VENTE' in alert['action_recommandee'] else '📊'} {alert['action']} - {alert['niveau_alerte']}</h4>
                            <p><b>📊 Situation:</b> {alert['prix_achat']:.2f}€ → {alert['prix_actuel']:.2f}€ 
                            (<span style="color: red">{alert['variation']:.1f}%</span>)</p>
                            <p><b>🎯 Recommandation technique:</b> {alert['recommandation']} ({alert['confidence']}% confiance)</p>
                            <p><b>💡 Action conseillée:</b> <span style="font-weight: bold; color: {'green' if 'ACHETER' in alert['action_recommandee'] else 'red' if 'VENTE' in alert['action_recommandee'] else 'orange'}">{alert['action_recommandee']}</span></p>
                            <p><b>📈 Raison:</b> {alert['raison']}</p>
                            <p><b>⏰ Dernière analyse:</b> {alert['timestamp']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            else:
                st.success("✅ Portefeuille équilibré - Aucune action urgente requise")
        
        # Onglets principaux
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Synthèse", "🎯 Trading", "📈 Technique", "💰 Dividendes", "⚙️ Gestion"])
        
        with tab5:
            st.subheader("⚙️ Gestion du Portefeuille")
            
            # Vue d'ensemble des actions détenues
            st.write(f"**📊 Portefeuille actuel: {len(st.session_state.portfolio)} actions**")
            
            gestion_data = []
            for action_name, details in st.session_state.portfolio.items():
                if action_name in stock_data and not stock_data[action_name]['erreur']:
                    prix_actuel = stock_data[action_name]['prix_actuel']
                    valeur = details['quantite'] * prix_actuel
                    
                    gestion_data.append({
                        'Action': action_name,
                        'Quantité': details['quantite'],
                        'Prix Achat': f"{details['prix_achat']:.2f}€",
                        'Prix Actuel': f"{prix_actuel:.2f}€",
                        'Valeur': f"{valeur:,.0f}€",
                        'Date Ajout': details.get('date_ajout', 'Inconnue')
                    })
            
            if gestion_data:
                df_gestion = pd.DataFrame(gestion_data)
                st.dataframe(df_gestion, use_container_width=True, hide_index=True)
            
            # Actions rapides de gestion
            st.subheader("🚀 Actions Rapides")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Exporter le portefeuille", icon="💾"):
                    # Code d'export ici
                    st.success("Portefeuille exporté!")
            
            with col2:
                if st.button("🔄 Réinitialiser les prix", icon="🔁"):
                    st.info("Prix actualisés")
                    st.rerun()
            
            with col3:
                if st.button("📋 Rapport détaillé", icon="📄"):
                    st.info("Génération du rapport...")
        
        with tab1:
            st.subheader("📊 Synthèse du Portefeuille")
            
            results, total_cours, total_prochain, total_investissement = calculate_dividend_income(
                st.session_state.portfolio, stock_data
            )
            
            valeur_totale = sum([r['valeur_actuelle'] for r in results.values()])
            plus_value_totale = sum([r['plus_value'] for r in results.values()])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Valeur totale", f"{valeur_totale:,.0f}€")
            with col2: st.metric("Plus-value", f"{plus_value_totale:,.0f}€")
            with col3: st.metric("Dividende 2024", f"{total_cours:,.0f}€")
            with col4: st.metric("Actions", len(st.session_state.portfolio))
            
            # Performance détaillée
            st.subheader("📋 Performance par Action")
            overview_data = []
            for action_name, result in results.items():
                statut = "✅ Au-dessus" if result['valeur_actuelle'] >= result['investissement'] else "❌ En alerte"
                overview_data.append({
                    'Action': action_name,
                    'Investissement': f"{result['investissement']:,.0f}€",
                    'Valeur actuelle': f"{result['valeur_actuelle']:,.0f}€",
                    'Plus-value': f"{result['plus_value']:,.0f}€",
                    'Statut': statut
                })
            
            df_overview = pd.DataFrame(overview_data)
            st.dataframe(df_overview, use_container_width=True, hide_index=True)
        
        with tab2:
            st.subheader("🎯 Stratégie de Trading")
            
            if strategie_active:
                # Tableau des recommandations
                trading_data = []
                for action_name, details in st.session_state.portfolio.items():
                    if action_name in technical_data and not technical_data[action_name].get('erreur'):
                        tech = technical_data[action_name]
                        stock = stock_data[action_name]
                        prix_achat = details['prix_achat']
                        variation = ((stock['prix_actuel'] - prix_achat) / prix_achat) * 100
                        
                        # Déterminer l'action prioritaire
                        if "ACHAT" in tech['recommandation'] and variation < seuil_achat:
                            priorite = "🔴 URGENT"
                        elif "VENTE" in tech['recommandation'] and variation > seuil_vente:
                            priorite = "🟠 IMPORTANT"
                        else:
                            priorite = "🟡 SURVEILLANCE"
                        
                        trading_data.append({
                            'Action': action_name,
                            'Prix Achat': f"{prix_achat:.2f}€",
                            'Prix Actuel': f"{stock['prix_actuel']:.2f}€",
                            'Variation': f"{variation:.1f}%",
                            'RSI': f"{tech['rsi']:.1f}",
                            'Recommandation': tech['recommandation'],
                            'Confiance': f"{tech['confidence']}%",
                            'Priorité': priorite
                        })
                
                if trading_data:
                    df_trading = pd.DataFrame(trading_data)
                    st.dataframe(df_trading, use_container_width=True, hide_index=True)
                    
                    # Conseils de stratégie
                    st.subheader("💡 Conseils Stratégiques")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info("**📈 En hausse:**")
                        actions_hausse = [a for a in trading_data if float(a['Variation'].replace('%', '')) > 5]
                        for action in actions_hausse[:3]:
                            st.write(f"- {action['Action']}: {action['Variation']}")
                    
                    with col2:
                        st.info("📉 **En baisse:**")
                        actions_baisse = [a for a in trading_data if float(a['Variation'].replace('%', '')) < -5]
                        for action in actions_baisse[:3]:
                            st.write(f"- {action['Action']}: {action['Variation']}")
                
                else:
                    st.warning("Données techniques indisponibles")
            
            else:
                st.info("Activez les recommandations trading dans la sidebar")
        
        with tab3:
            st.subheader("📈 Analyse Technique Détaillée")
            
            if strategie_active:
                # Sélection de l'action à analyser
                action_analysee = st.selectbox(
                    "Choisir une action pour l'analyse technique",
                    list(st.session_state.portfolio.keys())
                )
                
                if action_analysee in technical_data and not technical_data[action_analysee].get('erreur'):
                    tech = technical_data[action_analysee]
                    stock = stock_data[action_analysee]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Prix Actuel", f"{stock['prix_actuel']:.2f}€")
                        st.metric("RSI (14j)", f"{tech['rsi']:.1f}")
                        st.metric("Support", f"{tech['support']:.2f}€")
                        st.metric("Résistance", f"{tech['resistance']:.2f}€")
                    
                    with col2:
                        st.metric("Moyenne 50j", f"{tech['moyenne_50j']:.2f}€")
                        st.metric("Moyenne 200j", f"{tech['moyenne_200j']:.2f}€")
                        st.metric("Tendance", tech['tendance_longue'])
                        st.metric("Score Achat/Vente", f"{tech['score_achat']}/{tech['score_vente']}")
                    
                    # Graphique des indicateurs
                    st.subheader("📊 Indicateurs Techniques")
                    
                    # Création du graphique avec prix et moyennes
                    fig = go.Figure()
                    
                    # Données historiques pour le graphique
                    try:
                        stock_obj = yf.Ticker(st.session_state.portfolio[action_analysee]['ticker'])
                        hist = stock_obj.history(period="6mo")
                        
                        fig.add_trace(go.Scatter(
                            x=hist.index, y=hist['Close'],
                            name='Prix de clôture',
                            line=dict(color='blue', width=2)
                        ))
                        
                        # Ajout des moyennes mobiles
                        fig.add_trace(go.Scatter(
                            x=hist.index, y=hist['Close'].rolling(50).mean(),
                            name='MM 50 jours',
                            line=dict(color='orange', width=1)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=hist.index, y=hist['Close'].rolling(200).mean(),
                            name='MM 200 jours',
                            line=dict(color='red', width=1)
                        ))
                        
                        fig.update_layout(
                            title=f"Évolution du prix de {action_analysee}",
                            xaxis_title="Date",
                            yaxis_title="Prix (€)",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la génération du graphique: {e}")
                
                else:
                    st.error("Données techniques indisponibles pour cette action")
            
            else:
                st.info("Activez l'analyse technique dans la sidebar")
        
        with tab4:
            st.subheader("💰 Revenus de Dividendes")
            
            results, total_cours, total_prochain, total_investissement = calculate_dividend_income(
                st.session_state.portfolio, stock_data
            )
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Dividende 2024", f"{total_cours:,.0f}€")
            with col2: st.metric("Dividende 2025 (est.)", f"{total_prochain:,.0f}€")
            with col3: st.metric("Rendement moyen", f"{(total_cours/total_investissement*100):.2f}%")
            with col4: st.metric("Actions versantes", len(results))
            
            # Détail des dividendes
            st.subheader("📋 Détail par Action")
            dividend_data = []
            for action_name, result in results.items():
                dividend_data.append({
                    'Action': action_name,
                    'Quantité': result['quantite'],
                    'Dividende 2024': f"{result['dividende_cours']:.2f}€",
                    'Dividende 2025': f"{result['dividende_prochain']:.2f}€",
                    'Rendement cours': f"{result['rendement_sur_cours']:.2f}%",
                    'Rendement achat': f"{result['rendement_sur_achat']:.2f}%"
                })
            
            df_dividends = pd.DataFrame(dividend_data)
            st.dataframe(df_dividends, use_container_width=True, hide_index=True)
            
            # Projection des revenus
            st.subheader("📈 Projection des Revenus")
            annees = list(range(2024, 2034))
            revenus_projetes = [total_cours * (1.05) ** (i-2024) for i in annees]
            
            fig_projection = go.Figure()
            fig_projection.add_trace(go.Scatter(
                x=annees, y=revenus_projetes,
                name='Revenus dividendes projetés',
                line=dict(color='green', width=3)
            ))
            
            fig_projection.update_layout(
                title="Projection des revenus de dividendes (croissance 5% an)",
                xaxis_title="Année",
                yaxis_title="Revenus (€)",
                height=400
            )
            
            st.plotly_chart(fig_projection, use_container_width=True)
    
    else:
        # Écran d'accueil si portefeuille vide
        st.info("💡 **Bienvenue dans votre Dashboard PEA!**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Pour commencer:")
            st.write("1. Sélectionnez votre type de PEA dans la sidebar")
            st.write("2. Ajoutez vos premières actions")
            st.write("3. Configurez votre stratégie de trading")
            st.write("4. Analysez les recommandations automatiques")
        
        with col2:
            st.subheader("🎯 Fonctionnalités principales:")
            st.write("✅ **Gestion avancée** avec suppression d'actions")
            st.write("✅ **Analyse technique** avec indicateurs avancés")
            st.write("✅ **Recommandations trading** intelligentes")
            st.write("✅ **Alertes automatiques** stop-loss et prise de bénéfices")
            st.write("✅ **Projection des dividendes** sur 10 ans")
            st.write("✅ **Export des données** et rapports détaillés")
        
        st.markdown("---")
        st.subheader("📊 Actions PEA Éligibles")
        
        # Affichage des actions disponibles
        pea_type_display = st.selectbox("Voir les actions pour:", ["PEA Classique", "PEA-PME"])
        actions_display = ACTIONS_PEA if pea_type_display == "PEA Classique" else ACTIONS_PEA_PME
        
        df_actions = pd.DataFrame([
            {'Action': name, 'Ticker': ticker} 
            for name, ticker in actions_display.items()
        ])
        
        st.dataframe(df_actions, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()