#!/usr/bin/env python3
"""
Organisatie Website Analyzer - Streamlit Version (Verbeterd)
Analyseert websites en digitale kanalen van overheidsorganisaties met Bing zoekacties
FIX: Toont nu alle gevonden resultaten in plaats van 1 per domein

Vereisten:
pip install streamlit requests beautifulsoup4 pandas

Uitvoeren:
streamlit run zoeken4_fixed.py
"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import io
import json
from typing import Dict, List, Tuple

# Pagina configuratie
st.set_page_config(
    page_title="Organisatie Website Analyzer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

class WebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def check_url_exists(self, url: str) -> Tuple[bool, int, str]:
        """Controleert of een URL bestaat en toegankelijk is"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return True, response.status_code, response.url
        except requests.RequestException as e:
            try:
                # Probeer GET als HEAD faalt
                response = self.session.get(url, timeout=10, allow_redirects=True)
                return True, response.status_code, response.url
            except requests.RequestException:
                return False, 0, str(e)
    
    def search_primary(self, query: str, max_results: int = 10) -> List[Dict]:
        """Primaire zoekfunctie die Bing zoekacties uitvoert"""
        st.info(f"🔍 Zoekactie starten voor: {query}")
        return self.search_alternative(query, max_results)
    
    def search_alternative(self, query: str, max_results: int = 10) -> List[Dict]:
        """Primaire zoekmethoden - gebruikt alleen Bing Search"""
        st.info(f"🔍 Zoekactie voor: {query}")
        results = []
        
        # Bing Search (via scraping)
        try:
            bing_results = self.search_bing_scrape(query, max_results)
            if bing_results:
                results.extend(bing_results)
                st.success(f"✅ {len(bing_results)} Bing resultaten gevonden")
            else:
                st.info("ℹ️ Bing: geen resultaten")
        except Exception as e:
            st.warning(f"Bing scraping gefaald: {str(e)[:50]}...")
        
        total_found = len(results)
        if total_found == 0:
            st.error(f"❌ Geen zoekresultaten voor '{query}' - zoekmachine gefaald")
            st.info("💡 Probeer een andere organisatie of controleer internetverbinding")
        else:
            st.success(f"🎯 Totaal {total_found} resultaten gevonden voor '{query}'")
        
        return results
    

    
    def extract_real_url_from_bing(self, bing_url: str) -> str:
        """Extraheert de echte URL uit een Bing redirect URL"""
        if not bing_url or not bing_url.startswith('http'):
            return bing_url
            
        # Als het al een echte URL is, gewoon terugsturen
        if not ('bing.com' in bing_url and ('ck/a' in bing_url or 'cc=' in bing_url)):
            return bing_url
            
        try:
            # Probeer de redirect te volgen om de echte URL te krijgen
            response = self.session.head(bing_url, timeout=5, allow_redirects=True)
            if response.url and response.url != bing_url:
                return response.url
        except:
            pass
            
        # Fallback: probeer URL uit de Bing redirect te parsen
        try:
            from urllib.parse import urlparse, parse_qs
            
            # Verschillende Bing URL formaten proberen
            if 'u=' in bing_url:
                # Zoek u= parameter
                parts = bing_url.split('u=')
                if len(parts) > 1:
                    url_part = parts[1].split('&')[0]
                    from urllib.parse import unquote
                    decoded_url = unquote(url_part)
                    if decoded_url.startswith('http'):
                        return decoded_url
                        
            # Probeer andere parameters
            parsed = urlparse(bing_url)
            query_params = parse_qs(parsed.query)
            
            for param in ['url', 'u', 'target', 'dest']:
                if param in query_params and query_params[param]:
                    candidate_url = query_params[param][0]
                    if candidate_url.startswith('http'):
                        return candidate_url
                        
        except:
            pass
            
        return bing_url  # Return original if all else fails

    def search_bing_scrape(self, query: str, max_results: int = 10) -> List[Dict]:
        """Scrapet Bing zoekresultaten en extraheert echte URLs"""
        results = []
        
        try:
            search_url = "https://www.bing.com/search"
            params = {'q': query, 'count': max_results}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse Bing resultaten - probeer verschillende selectors
                search_results = soup.find_all('li', class_='b_algo')
                
                for result in search_results[:max_results]:
                    try:
                        title_elem = result.find('h2')
                        if title_elem and title_elem.find('a'):
                            title = title_elem.get_text(strip=True)
                            raw_url = title_elem.find('a').get('href')
                            
                            # Probeer eerst data-href attribuut (heeft soms de echte URL)
                            link_elem = title_elem.find('a')
                            real_url = (link_elem.get('data-href') or 
                                      link_elem.get('data-url') or 
                                      raw_url)
                            
                            # Extract echte URL uit Bing redirect
                            clean_url = self.extract_real_url_from_bing(real_url)
                            
                            # Zoek beschrijving
                            desc_elem = result.find('p')
                            description = desc_elem.get_text(strip=True) if desc_elem else ''
                            
                            # Extra check: probeer ook cite element (heeft vaak de echte URL)
                            cite_elem = result.find('cite')
                            if cite_elem and not clean_url.startswith('http'):
                                cite_url = cite_elem.get_text(strip=True)
                                if cite_url and not cite_url.startswith('www.bing.com'):
                                    if not cite_url.startswith('http'):
                                        cite_url = 'https://' + cite_url
                                    clean_url = cite_url
                            
                            # Alleen toevoegen als we een geldige URL hebben
                            if clean_url and not clean_url.startswith('https://www.bing.com/ck/'):
                                results.append({
                                    'title': title,
                                    'url': clean_url,
                                    'snippet': description[:200],
                                    'source': 'Bing Scraping'
                                })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            st.warning(f"Bing scraping issue: {str(e)[:50]}")
        
        return results
    

    
    def determine_archiving_frequency(self, url: str, title: str, regime: str = 'ons-advies') -> str:
        """Bepaalt archiveringsfrequentie gebaseerd op URL en titel"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if regime == 'officieel':
            # Officiële richtlijn: alles dagelijks behalve technisch onmogelijk
            if any(keyword in title_lower for keyword in ['technisch niet mogelijk', 'juridisch niet mogelijk']):
                return 'Niet archiveren'
            return 'Dagelijks'
        else:
            # Ons advies: praktische benadering
            
            # Niet archiveren
            if any(keyword in title_lower for keyword in [
                'formulier', 'formulieren', 'timeblockr', 'iburgerzaken',
                'meldingen', 'belastingbalie', 'fixi', 'app', 'archiefweb'
            ]):
                return 'Niet archiveren'
            
            # Wekelijks
            if any(keyword in title_lower for keyword in [
                'regionaal energieloket', 'activiteiten', 'vacatures'
            ]):
                return 'Wekelijks'
            
            # Sociale media krijgt 'best effort'
            if any(platform in url_lower for platform in [
                'facebook.com', 'instagram.com', 'linkedin.com', 
                'youtube.com', 'twitter.com', 'x.com'
            ]):
                return 'Best effort'
            
            # Alle overige: dagelijks
            return 'Dagelijks'



    def deduplicate_by_url(self, results: List[Dict]) -> List[Dict]:
        """Verwijdert alleen exacte duplicaten (zelfde URL), behoudt verschillende pagina's van hetzelfde domein"""
        seen_urls = set()
        deduplicated = []
        
        for result in results:
            url = result['url']
            
            # Behoud alles met 'Onbekend' URL (CSV data)
            if url == 'Onbekend':
                deduplicated.append(result)
                continue
                
            # Voor echte URLs: alleen toevoegen als we deze URL nog niet hebben gezien
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(result)
            # Als we de URL al hebben gezien, skip deze (exacte duplicaat)
        
        return deduplicated

# Initialiseer analyzer
@st.cache_resource
def get_analyzer():
    return WebsiteAnalyzer()

def main():
    st.title("🌐 Organisatie Website Analyzer")
    st.markdown("Analyseert websites en digitale kanalen van overheidsorganisaties met **Bing zoekacties**")
    
    analyzer = get_analyzer()
    
    # Sidebar configuratie
    with st.sidebar:
        st.header("⚙️ Configuratie")
        
        archiving_regime = st.selectbox(
            "Archiveringsrichtlijn:",
            ["ons-advies", "officieel"],
            format_func=lambda x: "Ons praktische advies" if x == "ons-advies" else "Officiële richtlijn Nationaal Archief"
        )
        
        if archiving_regime == "officieel":
            st.info("📋 **Officiële richtlijn**: Alles dagelijks, behalve technisch/juridisch onmogelijk")
        else:
            st.info("💡 **Ons advies**: Sociale media best effort, formulieren niet archiveren, rest dagelijks")
        
        st.header("🔍 Zoekinstellingen")
        

        
        st.warning("⚠️ **Timeout Protection**: Zoekacties stoppen automatisch na 10 seconden per opdracht")
        st.info("💡 **Tip**: Tool is volledig afhankelijk van zoekresultaten")
        
        verify_urls = st.checkbox("URLs verifiëren (langzamer)", value=False)
        max_search_results = st.slider("Max zoekresultaten per zoekopdracht", 3, 15, 8)
    
    # Hoofdinterface
    tab1, tab2 = st.tabs(["📊 Analyse", "📁 CSV Upload"])
    
    with tab1:
        st.header("Organisatie Selectie")
        
        # Demo data
        demo_data = [
            {"naam": "Gemeente Hilversum", "type": "Site", "status": "Actief"},
            {"naam": "Gemeente Amsterdam", "type": "Site", "status": "Actief"},
            {"naam": "Gemeente Rotterdam", "type": "Site", "status": "Actief"},
            {"naam": "Waterschap Rivierenland", "type": "Site", "status": "Actief"},
            {"naam": "Waterschap Aa en Maas", "type": "Site", "status": "Actief"},
            {"naam": "Provincie Utrecht", "type": "Site", "status": "Actief"},
            {"naam": "Ministerie van Algemene Zaken", "type": "Site", "status": "Actief"},
        ]
        
        # Organisatie input
        col1, col2 = st.columns([2, 1])
        with col1:
            organisatie_naam = st.text_input(
                "Organisatie naam:",
                placeholder="Bijv. Gemeente Hilversum, Waterschap Rivierenland",
                help="Typ de volledige naam van de organisatie"
            )
        with col2:
            if st.button("🎯 Start Analyse", type="primary", disabled=not organisatie_naam):
                start_analysis(organisatie_naam, analyzer, archiving_regime, verify_urls, max_search_results)
        
        # Demo organisaties
        st.subheader("Of kies een demo organisatie:")
        demo_cols = st.columns(3)
        for i, org in enumerate(demo_data[:6]):
            with demo_cols[i % 3]:
                if st.button(f"📍 {org['naam']}", key=f"demo_{i}"):
                    start_analysis(org['naam'], analyzer, archiving_regime, verify_urls, max_search_results)
    
    with tab2:
        st.header("📁 CSV Bestand Upload")
        st.markdown("Upload het `digitoegankelijk_data_volledig.csv` bestand voor bulk analyse")
        
        uploaded_file = st.file_uploader(
            "Kies CSV bestand:",
            type=['csv'],
            help="CSV bestand met kolommen: naam, organisatie, type, status"
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ CSV geladen: {len(df)} records")
                
                if 'organisatie' in df.columns:
                    unique_orgs = df['organisatie'].dropna().unique()
                    st.subheader(f"Gevonden organisaties ({len(unique_orgs)}):")
                    
                    selected_org = st.selectbox("Selecteer organisatie voor analyse:", unique_orgs)
                    
                    if st.button("🎯 Analyseer Geselecteerde Organisatie", type="primary"):
                        start_analysis(selected_org, analyzer, archiving_regime, verify_urls, max_search_results, df)
                else:
                    st.error("❌ CSV bestand mist 'organisatie' kolom")
                    
            except Exception as e:
                st.error(f"❌ Fout bij laden CSV: {str(e)}")

def start_analysis(organisatie_naam: str, analyzer: WebsiteAnalyzer, archiving_regime: str, 
                   verify_urls: bool, max_search_results: int,
                   csv_data: pd.DataFrame = None):
    """Start de analyse voor een organisatie"""
    
    st.header(f"🔍 Analyse Resultaten: {organisatie_naam}")
    
    # Progress tracking
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    
    all_results = []
    
    # Stap 1: CSV data verwerken
    if csv_data is not None:
        status_text.text("📊 CSV data verwerken...")
        progress_bar.progress(0.1)
        
        org_data = csv_data[csv_data['organisatie'].str.contains(organisatie_naam, case=False, na=False)]
        for _, row in org_data.iterrows():
            result = {
                'title': row.get('naam', ''),
                'url': 'Onbekend',
                'description': f"Type: {row.get('type', '')}, Status: {row.get('status', '')}",
                'category': 'csv_data',
                'source': 'CSV Data',
                'verified': False,
                'status_code': None
            }
            result['archiving_frequency'] = analyzer.determine_archiving_frequency(
                result['url'], result['title'], archiving_regime
            )
            all_results.append(result)
    
    # Stap 2: Zoekopdrachten
    st.info("🔍 Internetzoekacties starten...")
    st.warning("⚠️ Als zoekacties te lang duren (>30 sec), zijn er mogelijk netwerk problemen")
    
    search_queries = [
        f"{organisatie_naam} officiële website",
        f"{organisatie_naam} social media Facebook Instagram LinkedIn",
        f"{organisatie_naam} digitaal loket mijn",
        f"{organisatie_naam} YouTube Twitter",
        f"{organisatie_naam} contact informatie",
    ]
    
    search_success_count = 0
    
    for i, query in enumerate(search_queries):
        status_text.text(f"🔍 Zoekopdracht ({i+1}/{len(search_queries)}): {query[:50]}...")
        progress_bar.progress(0.2 + (i * 0.15))
        
        # Rate limiting tussen zoekopdrachten
        if i > 0:
            status_text.text(f"⏳ Rate limiting - wachten 5 seconden...")
            time.sleep(5)
        
        try:
            # Timeout wrapper voor zoekacties
            search_start_time = time.time()
            search_results = analyzer.search_primary(query, max_search_results)
            search_duration = time.time() - search_start_time
            
            if search_results:
                search_success_count += 1
                st.success(f"✅ Zoekopdracht {i+1} succesvol in {search_duration:.1f} seconden")
            else:
                st.warning(f"⚠️ Zoekopdracht {i+1} gaf geen resultaten")
            
            for res in search_results:
                # Categoriseer zoekresultaten
                url_lower = res['url'].lower()
                if any(platform in url_lower for platform in ['facebook.com', 'instagram.com', 'linkedin.com', 'youtube.com', 'twitter.com', 'x.com']):
                    category = 'social'
                elif 'bibliotheek' in url_lower or 'bibliotheek' in res['title'].lower():
                    category = 'related'
                else:
                    category = 'official'
                
                result = {
                    'title': res['title'],
                    'url': res['url'],
                    'description': res['snippet'][:200] + '...' if len(res['snippet']) > 200 else res['snippet'],
                    'category': category,
                    'source': res['source'],
                    'verified': False,
                    'status_code': None
                }
                result['archiving_frequency'] = analyzer.determine_archiving_frequency(
                    result['url'], result['title'], archiving_regime
                )
                all_results.append(result)
                
        except Exception as e:
            st.error(f"❌ Zoekopdracht {i+1} gefaald: {str(e)[:100]}...")
            
            # Als alle zoekopdrachten falen, stop vroeg
            if i == 0 and search_success_count == 0:
                st.warning("🚫 Eerste zoekopdracht gefaald - mogelijk netwerk problemen.")
                break
    
    # Samenvatting van zoekresultaten
    if search_success_count > 0:
        st.success(f"✅ {search_success_count}/{len(search_queries)} zoekopdrachten succesvol")
    else:
        st.error("❌ Alle internetzoekacties gefaald - geen resultaten gevonden")
        st.info("💡 Mogelijke oorzaken: netwerk problemen, rate limiting, of organisatie heeft weinig online aanwezigheid")
    
    # Stap 3: URL verificatie
    if verify_urls and all_results:
        status_text.text("✅ URLs verifiëren...")
        progress_bar.progress(0.85)
        
        for i, result in enumerate(all_results):
            if result['url'] != 'Onbekend':
                exists, status_code, final_url = analyzer.check_url_exists(result['url'])
                result['verified'] = exists
                result['status_code'] = status_code
                result['final_url'] = final_url
                
                if i % 5 == 0 and len(all_results) > 0:
                    verification_progress = min(0.95, 0.85 + (i / len(all_results)) * 0.1)
                    progress_bar.progress(verification_progress)
    
    # Stap 4: Exacte duplicaten verwijderen (behoud verschillende pagina's van zelfde domein)
    status_text.text("🔄 Exacte duplicaten verwijderen...")
    progress_bar.progress(0.95)
    
    processed_results = analyzer.deduplicate_by_url(all_results)
    
    status_text.text("✅ Analyse voltooid!")
    progress_bar.progress(1.0)
    
    # Toon statistieken
    st.info(f"📊 **Resultaten verwerking**: {len(all_results)} → {len(processed_results)} (na verwijderen exacte duplicaten)")
    
    # Resultaten weergeven
    if processed_results:
        display_results(organisatie_naam, processed_results, archiving_regime)
    else:
        st.error("❌ Geen resultaten gevonden!")
        st.info("💡 Probeer een andere organisatie of controleer internetverbinding")

def display_results(organisatie_naam: str, results: List[Dict], archiving_regime: str):
    """Toont de analyseresultaten in bredere layout zonder dropdowns"""
    
    st.success(f"✅ Analyse voltooid voor **{organisatie_naam}** (exacte duplicaten verwijderd)")
    
    # Statistieken in volledige breedte
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Totaal gevonden", len(results))
    
    with col2:
        csv_count = len([r for r in results if r['source'] == 'CSV Data'])
        st.metric("CSV Data", csv_count)
    
    with col3:
        search_count = len([r for r in results if r['source'] == 'Bing Scraping'])
        st.metric("Zoekresultaten", search_count)
    
    with col4:
        unique_domains = len(set([urlparse(r['url']).netloc for r in results if r['url'] != 'Onbekend']))
        st.metric("Unieke Domeinen", unique_domains)
    
    with col5:
        verified_count = len([r for r in results if r.get('verified', False)])
        st.metric("URLs geverifieerd", verified_count if verified_count > 0 else "0")
    
    # Archiveringsfrequentie samenvatting
    freq_counts = {}
    for result in results:
        freq = result.get('archiving_frequency', 'Onbekend')
        freq_counts[freq] = freq_counts.get(freq, 0) + 1
    
    st.subheader("📅 Archiveringsfrequentie Overzicht")
    freq_cols = st.columns(len(freq_counts))
    for i, (freq, count) in enumerate(freq_counts.items()):
        with freq_cols[i]:
            color = {
                'Dagelijks': '🟢',
                'Wekelijks': '🔵', 
                'Best effort': '🟡',
                'Niet archiveren': '🔴'
            }.get(freq, '⚪')
            st.metric(f"{color} {freq}", count)
    
    # Gedetailleerde resultaten in volledige breedte
    st.subheader("🌐 Alle Gevonden Websites & Sociale Media")
    
    # Filter opties
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        category_filter = st.selectbox(
            "Filter op categorie:",
            ["Alle"] + list(set([r['category'] for r in results]))
        )
    with filter_col2:
        source_filter = st.selectbox(
            "Filter op bron:",
            ["Alle"] + list(set([r['source'] for r in results]))
        )
    with filter_col3:
        freq_filter = st.selectbox(
            "Filter op archiveringsfrequentie:",
            ["Alle"] + list(set([r.get('archiving_frequency', 'Onbekend') for r in results]))
        )
    
    # Filter toepassen
    filtered_results = results
    if category_filter != "Alle":
        filtered_results = [r for r in filtered_results if r['category'] == category_filter]
    if source_filter != "Alle":
        filtered_results = [r for r in filtered_results if r['source'] == source_filter]
    if freq_filter != "Alle":
        filtered_results = [r for r in filtered_results if r.get('archiving_frequency', 'Onbekend') == freq_filter]
    
    # Resultaten weergeven in kaart-style zonder dropdowns
    for i, result in enumerate(filtered_results):
        # Archiving frequency kleur
        freq = result.get('archiving_frequency', 'Onbekend')
        freq_color = {
            'Dagelijks': '🟢',
            'Wekelijks': '🔵',
            'Best effort': '🟡', 
            'Niet archiveren': '🔴'
        }.get(freq, '⚪')
        
        # Category icon
        category_icon = {
            'official': '🏛️',
            'social': '📱',
            'related': '📚',
            'csv_data': '📊'
        }.get(result['category'], '🌐')
        
        # Maak een container voor elke resultaat
        with st.container():
            # Boven container met titel en frequentie
            title_col, freq_col = st.columns([4, 1])
            
            with title_col:
                st.markdown(f"### {i+1}. {category_icon} {result['title']}")
            
            with freq_col:
                st.markdown(f"### {freq_color} {freq}")
            
            # Details in drie kolommen
            detail_col1, detail_col2, detail_col3 = st.columns([2, 2, 1])
            
            with detail_col1:
                st.markdown(f"**🔗 URL:** {result['url']}")
                st.markdown(f"**📄 Beschrijving:** {result['description']}")
            
            with detail_col2:
                st.markdown(f"**📡 Bron:** {result['source']}")
                st.markdown(f"**🏷️ Categorie:** {result['category'].title()}")
                
                if result.get('verified'):
                    status_color = "🟢" if result.get('status_code', 0) == 200 else "🟡"
                    st.markdown(f"**✅ Status:** {status_color} {result.get('status_code', 'Onbekend')}")
            
            with detail_col3:
                # Snelle actie knoppen (optioneel)
                if result['url'] != 'Onbekend':
                    if st.button(f"🔗 Open", key=f"open_{i}"):
                        st.markdown(f"[Open website]({result['url']})")
            
            # Scheiding tussen resultaten
            st.divider()
    
    # Export opties in volledige breedte
    st.subheader("📊 Export Resultaten")
    
    # Bereid alle export data vooraf voor om pagina refresh te voorkomen
    df_export = pd.DataFrame(results)
    csv_buffer = io.StringIO()
    df_export.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    json_data = {
        'organisatie': organisatie_naam,
        'datum_analyse': datetime.now().isoformat(),
        'archiverings_regime': archiving_regime,
        'deduplicatie': 'exacte_duplicaten_verwijderd',
        'totaal_resultaten': len(results),
        'resultaten': results
    }
    json_export = json.dumps(json_data, indent=2, ensure_ascii=False)
    
    report_summary = f"""ANALYSE SAMENVATTING - {organisatie_naam}
Datum: {datetime.now().strftime('%d-%m-%Y %H:%M')}
Deduplicatie: Exacte duplicaten verwijderd
        
Totaal: {len(results)} websites
Unieke domeinen: {len(set([urlparse(r['url']).netloc for r in results if r['url'] != 'Onbekend']))}

Archiveringsfrequenties:
{chr(10).join([f'• {freq}: {count}' for freq, count in freq_counts.items()])}
"""
    
    # Detailleerde .txt export met alle resultaten
    detailed_txt_report = f"""WEBSITE & SOCIALE MEDIA ANALYSE - {organisatie_naam}
Gegenereerd: {datetime.now().strftime('%d-%m-%Y %H:%M')}
Archiveringsrichtlijn: {'Officiële Richtlijn Nationaal Archief' if archiving_regime == 'officieel' else 'Ons Praktische Advies'}
Deduplicatie: Exacte duplicaten verwijderd (verschillende pagina's van zelfde domein behouden)

SAMENVATTING:
• Totaal gevonden: {len(results)}
• CSV Data: {len([r for r in results if r['source'] == 'CSV Data'])}
• Zoekresultaten: {len([r for r in results if r['source'] == 'Bing Scraping'])}
• Unieke domeinen: {len(set([urlparse(r['url']).netloc for r in results if r['url'] != 'Onbekend']))}

ARCHIVERINGSFREQUENTIES:
{chr(10).join([f'• {freq}: {count} websites' for freq, count in freq_counts.items()])}

GEDETAILLEERDE RESULTATEN:
{'='*80}
"""
    
    for i, result in enumerate(results):
        detailed_txt_report += f"""
{i+1}. {result['title']}
URL: {result['url']}
Beschrijving: {result['description']}
Categorie: {result['category'].title()}
Bron: {result['source']}
Archiveringsfrequentie: {result.get('archiving_frequency', 'Onbekend')}
{'='*80}"""
    
    detailed_txt_report += f"""

METHODIEK:
✅ Internetzoekacties via Bing
✅ Intelligente categorisering en archiveringsfrequentie  
✅ URL verificatie met status codes
✅ Exacte duplicaten verwijderd (verschillende pagina's van zelfde domein behouden)
✅ Rate limiting bescherming

Einde rapport.
"""

    
    export_col1, export_col2, export_col3, export_col4 = st.columns(4)
    
    with export_col1:
        # CSV Export
        st.download_button(
            label="📁 Download als CSV",
            data=csv_data,
            file_name=f"website_analyse_{organisatie_naam.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="csv_download",
            help="Download resultaten als CSV spreadsheet"
        )
    
    with export_col2:
        # JSON Export        
        st.download_button(
            label="📋 Download als JSON",
            data=json_export,
            file_name=f"website_analyse_{organisatie_naam.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            key="json_download",
            help="Download resultaten als JSON data"
        )
    
    with export_col3:
        # Samenvatting TXT
        st.download_button(
            label="📄 Download Samenvatting",
            data=report_summary,
            file_name=f"samenvatting_{organisatie_naam.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            key="summary_download",
            help="Download korte samenvatting als tekstbestand"
        )
    
    with export_col4:
        # Uitgebreide .txt export
        st.download_button(
            label="📝 Download Volledig TXT",
            data=detailed_txt_report,
            file_name=f"volledig_rapport_{organisatie_naam.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            key="detailed_txt_download",
            help="Download compleet rapport met alle details als tekstbestand"
        )
    
    export_col1, export_col2, export_col3, export_col4 = st.columns(4)

if __name__ == "__main__":
    # Controleer of we in een Streamlit context draaien
    try:
        # Test of Streamlit beschikbaar is
        import streamlit as st
        # Test of we in Streamlit context zijn
        if hasattr(st, 'session_state'):
            main()
        else:
            print("❌ Dit script moet worden uitgevoerd met Streamlit!")
            print("\n🚀 Juiste manier:")
            print("   streamlit run zoeken4_fixed.py")
            print("\n📦 Streamlit niet geïnstalleerd?")
            print("   pip install streamlit")
            print("\n💡 Of voer uit in je terminal:")
            print("   python -m streamlit run zoeken4_fixed.py")
    except ImportError:
        print("❌ Streamlit is niet geïnstalleerd!")
        print("\n📦 Installeer eerst Streamlit:")
        print("   pip install streamlit")
        print("\n🚀 Dan uitvoeren met:")
        print("   streamlit run zoeken4_fixed.py")