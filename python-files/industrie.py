


# --- Fonction d'assistance pour la traduction ---
def get_lang():
    # Cette fonction doit être définie avant d'être appelée dans st.set_page_config
    # et avant la définition de la fonction t()
    # Pour éviter l'erreur "t is not defined" au premier appel, on utilise la clé directe
    # pour le libellé du selectbox.
    lang_code = st.sidebar.selectbox(
        "Langue / Language", # Utiliser une chaîne littérale pour le premier affichage
        options=list(translations.keys()),
        index=0, # Défaut sur 'fr'
        key="lang_selector"
    )
    return lang_code

# Définir lang et t() avant st.set_page_config
lang = get_lang()
def t(key):
    return translations.get(lang, {}).get(key, f"_{key}_")


# --- Configuration & Initialisation ---
st.set_page_config(
    page_title=t("app_title") + " - " + t("Analysis and Smart Data Entry"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. STYLE & INTERFACE (CSS Pour un look premium) 🎨
# ==============================================================================
def apply_premium_style():
    st.markdown(f"""
    <style>
    /* --- General --- */
    .stApp {{
        background-color: #0F172A; /* Couleur de fond principale (Bleu nuit) */
        color: #E2E8F0; /* Couleur de texte principale (Gris clair) */
    }}
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }}

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {{
        background-color: #1E293B; /* Fond de la sidebar (Bleu-gris) */
        border-right: 1px solid #334155;
    }}
    [data-testid="stSidebar"] h2 {{
        color: #FFFFFF;
        font-weight: bold;
    }}

    /* --- Titres --- */
    h1, h2, h3 {{
        color: #FFFFFF; /* Titres en blanc pour contraster */
        font-weight: 700;
    }}
    h1 {{
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 0.1em;
    }}
    /* Sous-titre personnalisé */
    .app-subtitle {{
        text-align: center;
        color: #94A3B8; /* Gris plus doux pour le sous-titre */
        font-size: 1.1em;
        margin-bottom: 2rem;
    }}

    /* --- Boutons --- */
    .stButton>button {{
        background-color: #3B82F6; /* Bleu vif pour l'action principale */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: #2563EB; /* Bleu plus foncé au survol */
        transform: translateY(-2px);
    }}

    /* --- Selectbox / Inputs --- */
    .stSelectbox>div>div, .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: #2D3A4B; /* Fond des inputs */
        color: #E2E8F0;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 10px;
    }}
    .stSelectbox>div>div:focus, .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border-color: #3B82F6;
        box-shadow: 0 0 0 1px #3B82F6;
    }}
    .stSelectbox>div>div>span {{
        color: #E2E8F0; /* Couleur du texte sélectionné */
    }}

    /* --- Expander (Zone de déploiement) --- */
    .streamlit-expanderHeader {{
        background-color: #1E293B;
        color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #334155;
        padding: 10px 20px;
        margin-top: 15px;
    }}
    .streamlit-expanderContent {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 20px;
    }}
    /* Retirer l'arrondi du haut si l'expander est ouvert */
    .streamlit-expander[aria-expanded="true"] .streamlit-expanderHeader {{
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
    }}

    /* --- Dataframe (Pandas) --- */
    .stDataFrame {{
        background-color: #1E293B; /* Fond du tableau */
        border-radius: 8px;
        overflow: hidden;
    }}
    .stDataFrame table {{
        width: 100%;
    }}
    .stDataFrame th {{
        background-color: #334155; /* Entête de colonne */
        color: #FFFFFF;
        font-weight: bold;
        padding: 10px;
        text-align: left;
    }}
    .stDataFrame td {{
        background-color: #1E293B; /* Cellules */
        color: #E2E8F0;
        padding: 8px 10px;
        border-bottom: 1px solid #334155;
    }}
    .stDataFrame tbody tr:hover td {{
        background-color: #2D3A4B; /* Ligne au survol */
    }}

    /* --- Tabs (Onglets) --- */
    [data-baseweb="tab-list"] {{
        gap: 8px; /* Espacement entre les onglets */
        justify-content: center; /* Centrer les onglets */
    }}
    [data-baseweb="tab"] {{
        background-color: #2D3A4B; /* Couleur des onglets inactifs */
        color: #94A3B8;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        transition: all 0.2s ease-in-out;
    }}
    [data-baseweb="tab"][aria-selected="true"] {{
        background-color: #3B82F6; /* Onglet actif */
        color: white;
        font-weight: bold;
    }}
    [data-baseweb="tab"]:hover {{
        background-color: #334155;
    }}

    /* --- Statistiques / Métriques (st.metric) --- */
    [data-testid="stMetric"] {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }}
    [data-testid="stMetric"] label {{
        color: #94A3B8;
        font-size: 0.9em;
    }}
    [data-testid="stMetricValue"] {{
        color: #FFFFFF;
        font-size: 1.8em;
        font-weight: bold;
    }}

    /* --- Streamlit Infos/Warnings/Errors --- */
    .stAlert {{
        border-radius: 8px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
    .stAlert.info {{
        background-color: #2563EB; /* Bleu pour info */
        color: white;
    }}
    .stAlert.warning {{
        background-color: #FBBF24; /* Jaune pour warning */
        color: black;
    }}
    .stAlert.error {{
        background-color: #EF4444; /* Rouge pour error */
        color: white;
    }}

    /* --- Logo ErnestMind --- */
    .ernestmind-logo {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 2rem;
        max-width: 150px; /* Taille maximale du logo */
    }}

    /* --- Footer Message --- */
    .footer-message {{
        text-align: center;
        color: #94A3B8;
        font-size: 0.9em;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #334155;
    }}

    /* --- Révolution ErnestMind Section --- */
    .revolution-section {{
        background-color: #1E293B;
        border-radius: 12px;
        padding: 30px;
        margin-top: 4rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .revolution-section h2 {{
        color: #3B82F6; /* Bleu vif pour le titre de section */
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    .revolution-section h3 {{
        color: #FFFFFF;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
    }}
    .revolution-section p {{
        color: #E2E8F0;
        line-height: 1.7;
        margin-bottom: 1rem;
    }}
    .revolution-section ul {{
        list-style-type: none;
        padding-left: 0;
    }}
    .revolution-section ul li {{
        margin-bottom: 0.8rem;
        color: #E2E8F0;
    }}
    .revolution-section ul li b {{
        color: #FFFFFF;
    }}
    .revolution-section .stMarkdown p strong {{ /* Pour les strong dans les textes */
        color: #3B82F6;
    }}
    .revolution-section .confidential-note {{
        font-size: 0.8em;
        color: #64748B;
        text-align: center;
        margin-top: 2rem;
    }}

    /* Effets de carte pour les résultats d'analyse */
    .analysis-card {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    .analysis-card h3 {{
        color: #FFFFFF;
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 1.4em;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
    }}
    .analysis-card p, .analysis-card ul {{
        color: #E2E8F0;
        line-height: 1.6;
    }}
    .analysis-card ul {{
        margin-left: 20px;
    }}

    /* Style pour les petits titres dans les cartes */
    .small-title {{
        color: #94A3B8;
        font-size: 0.9em;
        margin-bottom: 5px;
    }}
    .value-text {{
        color: #FFFFFF;
        font-size: 1.1em;
        font-weight: bold;
    }}

    /* Styles pour les badges d'entités */
    .entity-badge {{
        display: inline-block;
        background-color: #3B82F6; /* Bleu */
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        margin-right: 5px;
        margin-bottom: 5px;
        font-size: 0.85em;
        font-weight: 500;
    }}
    .entity-badge.PERSON {{ background-color: #F97316; }} /* Orange */
    .entity-badge.ORG {{ background-color: #10B981; }} /* Vert */
    .entity-badge.GPE {{ background-color: #6366F1; }} /* Violet */
    .entity-badge.DATE {{ background-color: #EC4899; }} /* Rose */
    .entity-badge.MONEY {{ background-color: #EAB308; }} /* Jaune */

    /* Custom CSS pour les colonnes (si utilisé) */
    .st-emotion-cache-nahz7x {{ /* Ajuster le padding pour les colonnes */
        padding-top: 1rem;
    }}

    /* Image Upload Dropzone */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: #1E293B;
        border: 2px dashed #475569;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #94A3B8;
    }}
    [data-testid="stFileUploaderDropzone"] svg {{
        color: #94A3B8;
    }}
    [data-testid="stFileUploaderDropzone"] p {{
        color: #94A3B8;
    }}
    </style>
    """, unsafe_allow_html=True)

# Appliquer le style
apply_premium_style()

# ==============================================================================
# 3. FONCTIONS D'ANALYSE & EXTRACTION (Moteurs du V80) ⚙️
# ==============================================================================

# Logo ErnestMind (URL ou fichier local)
ERNESTMIND_LOGO_URL = "https://i.ibb.co/P9tP1yV/ernestmind-logo-vertical-white.png" # Remplacez par l'URL de votre logo

@st.cache_data
def get_ernestmind_logo_base64():
    try:
        response = requests.get(ERNESTMIND_LOGO_URL)
        response.raise_for_status() # Lève une exception pour les codes d'état HTTP d'erreur
        return base64.b64encode(response.content).decode()
    except requests.exceptions.RequestException as e:
        st.error(f"{t('Erreur lors du chargement du logo ErnestMind pour les rapports')}: {e}")
        st.warning(t('Les rapports seront générés sans logo.'))
        return None

def extract_text_from_pdf(pdf_file):
    text_content = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() or ""
    return text_content

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_xlsx(xlsx_file):
    df = pd.read_excel(xlsx_file)
    # Convert all cells to string and join them for text analysis
    return df.to_string(index=False)

def extract_text_from_txt(txt_file):
    return txt_file.read().decode('utf-8')

def extract_text_from_json(json_file):
    data = json.load(json_file)
    return json.dumps(data, indent=2)

def extract_text_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return ET.tostring(root, encoding='unicode')

def extract_text_from_eml(eml_file):
    msg = email.message_from_bytes(eml_file.read())
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # try to get plain text content
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                text_content = part.get_payload(decode=True).decode()
                break
    else:
        text_content = msg.get_payload(decode=True).decode()
    return text_content

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        # Convert to RGB to ensure compatibility with pytesseract
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return pytesseract.image_to_string(image, lang='fra+eng') # Support both French and English
    except Exception as e:
        st.warning(f"Impossible d'extraire le texte de l'image. Assurez-vous que Tesseract est installé et configuré. Erreur: {e}")
        return ""

# --- Fonction principale d'extraction ---
def extract_file_content(uploaded_file):
    file_type = uploaded_file.type
    filename = uploaded_file.name
    text_content = ""
    data_frames = [] # Pour les données tabulaires (ex: Excel)

    try:
        if 'pdf' in file_type:
            text_content = extract_text_from_pdf(uploaded_file)
        elif 'document' in file_type or 'word' in file_type: # docx
            text_content = extract_text_from_docx(uploaded_file)
        elif 'spreadsheet' in file_type or 'excel' in file_type: # xlsx
            df = pd.read_excel(uploaded_file)
            data_frames.append(df)
            text_content = df.to_string(index=False) # Convert for text analysis
        elif 'text/plain' in file_type:
            text_content = extract_text_from_txt(uploaded_file)
        elif 'application/json' in file_type:
            text_content = extract_text_from_json(uploaded_file)
        elif 'application/xml' in file_type:
            text_content = extract_text_from_xml(uploaded_file)
        elif 'message/rfc822' in file_type or '.eml' in filename: # EML files
            text_content = extract_text_from_eml(uploaded_file)
        elif 'image' in file_type:
            text_content = extract_text_from_image(uploaded_file)
        else:
            return None, None, t("unsupported_format")
        return text_content, data_frames, None
    except Exception as e:
        return None, None, f"{t('error_parsing')} {e}"

# --- Fonctions d'analyse de données (Pandas) ---
def analyze_dataframe(df):
    analysis = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "numeric_cols": df.select_dtypes(include=np.number).columns.tolist(),
        "categorical_cols": df.select_dtypes(include=['object', 'category']).columns.tolist(),
        "null_counts": df.isnull().sum().to_dict(),
        "head": df.head().to_html(), # Pour affichage dans le rapport
        "describe": df.describe(include='all').to_html() # Statistiques descriptives
    }
    return analysis

# --- Fonctions d'analyse de texte (NLP) ---
def analyze_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    unique_words = set(words)
    analysis = {
        "total_words": len(words),
        "unique_words": len(unique_words),
        "potential_titles": re.findall(r'^[A-Z][^\n.!?]*[.!?]?', text, re.MULTILINE)[:5],
        "paragraphs": [p for p in text.split('\n\n') if p.strip()][:5] # Premiers paragraphes
    }

    # Reconnaissance d'entités avec spaCy (si installé)
    try:
        import spacy
        # Charger le modèle 'fr_core_news_sm' ou 'en_core_web_sm'
        # Vous devrez exécuter : python -m spacy download fr_core_news_sm
        # Ou : python -m spacy download en_core_web_sm
        model_name = "fr_core_news_sm" if lang == "fr" else "en_core_web_sm"
        nlp = spacy.load(model_name)
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({"text": ent.text, "label": ent.label_})
        analysis["entities"] = entities
    except ImportError:
        analysis["entities"] = [{"text": t("enable_spacy_prompt"), "label": "INFO"}]
    except OSError:
        analysis["entities"] = [{"text": t("enable_spacy_prompt"), "label": "INFO"}]

    return analysis

# --- Clustering de documents ---
def perform_clustering(documents):
    if len(documents) < 2:
        return None # Pas de clustering avec moins de 2 documents

    vectorizer = TfidfVectorizer(stop_words=list(translations['fr'].values()) + list(translations['en'].values()), max_features=1000) # Utiliser les traductions comme stop words
    try:
        X = vectorizer.fit_transform(documents)
        num_clusters = min(len(documents), 5) # Max 5 clusters ou le nombre de documents
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10) # n_init pour éviter les warnings
        kmeans.fit(X)
        clusters = kmeans.labels_
        feature_names = vectorizer.get_feature_names_out()
        
        # Trouver les mots-clés distinctifs pour chaque cluster
        top_keywords_per_cluster = {}
        for i in range(num_clusters):
            # Obtenir les centroïdes du cluster
            centroid = kmeans.cluster_centers_[i]
            # Trier les mots-clés par leur score TF-IDF dans ce centroïde
            sorted_indices = centroid.argsort()[::-1]
            top_keywords = [feature_names[idx] for idx in sorted_indices[:5]] # Top 5 mots-clés
            top_keywords_per_cluster[i] = top_keywords
        
        return {"clusters": clusters.tolist(), "top_keywords": top_keywords_per_cluster}
    except Exception as e:
        return f"Erreur lors du clustering : {e}"

# --- Fonctions de génération de rapport ---
def generate_pdf_report(analysis_results, ernestmind_logo_base64):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []

    # Title
    Story.append(Paragraph(f"<h1 align='center'>{t('app_title')} - {t('Analysis and Smart Data Entry')}</h1>", styles['h1']))
    Story.append(Paragraph(f"<h2 align='center'>{t('Rapport généré le')} {datetime.date.today()}</h2>", styles['h2']))
    Story.append(Spacer(1, 0.2 * inch))

    # Logo
    if ernestmind_logo_base64:
        try:
            logo_data = base64.b64decode(ernestmind_logo_base64)
            logo_image = ImageReader(io.BytesIO(logo_data))
            # Ajuster la taille de l'image
            img_width, img_height = logo_image.getSize()
            aspect_ratio = img_height / img_width
            desired_width = 1.5 * inch
            desired_height = desired_width * aspect_ratio
            img = RlImage(logo_image, width=desired_width, height=desired_height)
            img.hAlign = 'CENTER'
            Story.append(img)
            Story.append(Spacer(1, 0.2 * inch))
        except Exception as e:
            st.error(f"Erreur lors de l'intégration du logo au PDF: {e}")

    # General Summary
    Story.append(Paragraph(f"<h3>{t('results_title')}</h3>", styles['h3']))
    Story.append(Spacer(1, 0.1 * inch))

    for i, result in enumerate(analysis_results):
        Story.append(Paragraph(f"<h2>{t('card_doc_info')}: {result['filename']}</h2>", styles['h2']))
        Story.append(Spacer(1, 0.1 * inch))

        # Document Info Table
        info_data = [
            [Paragraph(f"<b>{t('info_filename')}:</b>", styles['Normal']), result['filename']],
            [Paragraph(f"<b>{t('info_size')}:</b>", styles['Normal']), f"{result['size'] / 1024:.2f} KB"],
            [Paragraph(f"<b>{t('info_type')}:</b>", styles['Normal']), result['type']],
            [Paragraph(f"<b>{t('info_pages')}:</b>", styles['Normal']), result.get('page_count', 'N/A')]
        ]
        info_table = Table(info_data, colWidths=[2 * inch, 5 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        Story.append(info_table)
        Story.append(Spacer(1, 0.2 * inch))

        # Text Analysis
        if result['text_analysis'] and result['text_analysis']['total_words'] > 0:
            Story.append(Paragraph(f"<h3>{t('card_text_analysis')}</h3>", styles['h3']))
            Story.append(Paragraph(f"<b>{t('text_total_words')}:</b> {result['text_analysis']['total_words']}", styles['Normal']))
            Story.append(Paragraph(f"<b>{t('text_unique_words')}:</b> {result['text_analysis']['unique_words']}", styles['Normal']))
            Story.append(Spacer(1, 0.1 * inch))

            Story.append(Paragraph(f"<b>{t('structure_titles')}:</b>", styles['Normal']))
            for title in result['text_analysis']['potential_titles']:
                Story.append(Paragraph(f"- {title}", styles['Normal']))
            Story.append(Spacer(1, 0.1 * inch))

            Story.append(Paragraph(f"<b>{t('structure_paragraphs')}:</b>", styles['Normal']))
            for para in result['text_analysis']['paragraphs']:
                Story.append(Paragraph(para, styles['Normal']))
            Story.append(Spacer(1, 0.2 * inch))

        # Tabular Data
        if result['data_analysis']:
            Story.append(Paragraph(f"<h3>{t('card_table_analysis')}</h3>", styles['h3']))
            Story.append(Paragraph(f"<b>{t('table_shape')}:</b> {result['data_analysis']['shape'][0]} {t('table_rows')} x {result['data_analysis']['shape'][1]} {t('table_cols')}", styles['Normal']))
            Story.append(Spacer(1, 0.1 * inch))
            
            # Display head of dataframe
            Story.append(Paragraph(f"<b>{t('Données Tabulaires (extrait)')}:</b>", styles['Normal']))
            # Use BeautifulSoup to parse the HTML table and convert to ReportLab Table
            soup = BeautifulSoup(result['data_analysis']['head'], 'html.parser')
            html_table = soup.find('table')
            if html_table:
                table_data = []
                # Headers
                headers = [th.get_text() for th in html_table.find_all('th')]
                table_data.append(headers)
                # Rows
                for row in html_table.find_all('tr'):
                    cols = [td.get_text() for td in row.find_all('td')]
                    if cols: # Avoid empty rows
                        table_data.append(cols)
                
                if table_data:
                    # Determine column widths
                    col_widths = [doc.width / len(table_data[0]) for _ in table_data[0]]
                    rl_table = Table(table_data, colWidths=col_widths)
                    rl_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1E293B')),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#E2E8F0')),
                        ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#475569')),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('LEFTPADDING', (0,0), (-1,-1), 6),
                        ('RIGHTPADDING', (0,0), (-1,-1), 6),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ]))
                    Story.append(rl_table)
                    Story.append(Spacer(1, 0.2 * inch))

        Story.append(Spacer(1, 0.5 * inch)) # Espace entre chaque document

    # Inter-document analysis (Clustering)
    if st.session_state.clustering_results and st.session_state.clustering_results != t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'):
        Story.append(Paragraph(f"<h3>{t('card_clustering')}</h3>", styles['h3']))
        Story.append(Paragraph(t('clustering_description'), styles['Normal']))
        Story.append(Spacer(1, 0.1 * inch))

        cluster_data = []
        cluster_data.append([Paragraph("<b>Cluster ID</b>", styles['Normal']), Paragraph(f"<b>{t('cluster_keywords')}</b>", styles['Normal']), Paragraph("<b>Documents</b>", styles['Normal'])])

        for cluster_id, keywords in st.session_state.clustering_results['top_keywords'].items():
            docs_in_cluster = [
                result['filename'] for idx, result in enumerate(analysis_results)
                if st.session_state.clustering_results['clusters'][idx] == cluster_id
            ]
            cluster_data.append([
                str(cluster_id + 1), # +1 pour un affichage base 1
                ", ".join(keywords),
                ", ".join(docs_in_cluster)
            ])

        cluster_table = Table(cluster_data, colWidths=[1.2 * inch, 2.5 * inch, 3.5 * inch])
        cluster_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        Story.append(cluster_table)
        Story.append(Spacer(1, 0.5 * inch))

    # Footer
    Story.append(Paragraph(f"<p align='center' style='color:#64748B;'>{t('revolution_footer_message')}</p>", styles['Normal']))
    Story.append(Paragraph(f"<p align='center' style='color:#64748B; font-size:0.8em;'>{t('revolution_confidential_note')}</p>", styles['Normal']))


    doc.build(Story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_word_report(analysis_results, ernestmind_logo_base64):
    if DocxDocument is None:
        st.error("La bibliothèque 'python-docx' n'est pas installée. Veuillez l'installer (`pip install python-docx`) pour générer des rapports Word.")
        return None

    document = DocxDocument()
    # Styles
    styles = document.styles
    styles['Normal'].font.name = 'Arial'
    styles['Normal'].font.size = Pt(11)

    # Title
    document.add_heading(f"{t('app_title')} - {t('Analysis and Smart Data Entry')}", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_heading(f"{t('Rapport généré le')} {datetime.date.today()}", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Logo
    if ernestmind_logo_base64:
        try:
            logo_data = base64.b64decode(ernestmind_logo_base64)
            image_stream = io.BytesIO(logo_data)
            document.add_picture(image_stream, width=Inches(1.5)).alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception as e:
            st.error(f"Erreur lors de l'intégration du logo au document Word: {e}")

    document.add_heading(t('results_title'), level=2)

    for i, result in enumerate(analysis_results):
        document.add_heading(f"{t('card_doc_info')}: {result['filename']}", level=3)

        # Document Info Table
        table = document.add_table(rows=1, cols=2)
        table.autofit = True
        table.rows[0].cells[0].text = t('info_filename')
        table.rows[0].cells[1].text = result['filename']

        row_cells = table.add_row().cells
        row_cells[0].text = t('info_size')
        row_cells[1].text = f"{result['size'] / 1024:.2f} KB"

        row_cells = table.add_row().cells
        row_cells[0].text = t('info_type')
        row_cells[1].text = result['type']

        row_cells = table.add_row().cells
        row_cells[0].text = t('info_pages')
        row_cells[1].text = result.get('page_count', 'N/A')

        # Style table (optional, more complex styling requires XML manipulation)
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0) # Gris clair
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Apply shading to header (requires qn for XML modification)
        try:
            tbl_pr = table._element.xpath('w:tblPr')[0]
            tbl_shd = ET.SubElement(tbl_pr, qn('w:shd'))
            tbl_shd.set(qn('w:val'), 'clear')
            tbl_shd.set(qn('w:fill'), '334155') # Couleur de fond #334155
            for cell in table.rows[0].cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) # Blanc pour le texte d'en-tête
        except Exception as e:
            # print(f"Warning: Could not apply advanced table styling: {e}")
            pass # Ignore if qn is not available or error occurs

        document.add_paragraph() # Add a new paragraph after table for spacing

        # Text Analysis
        if result['text_analysis'] and result['text_analysis']['total_words'] > 0:
            document.add_heading(t('card_text_analysis'), level=4)
            document.add_paragraph(f"{t('text_total_words')}: {result['text_analysis']['total_words']}")
            document.add_paragraph(f"{t('text_unique_words')}: {result['text_analysis']['unique_words']}")

            document.add_paragraph(f"{t('structure_titles')}:")
            for title in result['text_analysis']['potential_titles']:
                document.add_paragraph(f"- {title}", style='List Bullet')
            
            document.add_paragraph(f"{t('structure_paragraphs')}:")
            for para in result['text_analysis']['paragraphs']:
                document.add_paragraph(para)
            document.add_paragraph() # Spacing

        # Tabular Data
        if result['data_analysis']:
            document.add_heading(t('card_table_analysis'), level=4)
            document.add_paragraph(f"{t('table_shape')}: {result['data_analysis']['shape'][0]} {t('table_rows')} x {result['data_analysis']['shape'][1]} {t('table_cols')}")
            document.add_paragraph(f"{t('Données Tabulaires (extrait)')}:")
            
            # Convert HTML table (from df.head().to_html()) to Word table
            soup = BeautifulSoup(result['data_analysis']['head'], 'html.parser')
            html_table = soup.find('table')
            if html_table:
                # Create a new table in the Word document
                rows = html_table.find_all('tr')
                if rows:
                    word_table = document.add_table(rows=len(rows), cols=len(rows[0].find_all(['th', 'td'])))
                    word_table.autofit = True
                    
                    for r_idx, row in enumerate(rows):
                        cols = row.find_all(['th', 'td'])
                        for c_idx, col in enumerate(cols):
                            cell = word_table.cell(r_idx, c_idx)
                            cell.text = col.get_text()
                            # Apply basic styling
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
                            if r_idx == 0: # Header row
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.font.bold = True
                                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) # Blanc
                                # Apply shading to header cells
                                try:
                                    cell_shd = ET.SubElement(cell._tc, qn('w:tcPr'))
                                    ET.SubElement(cell_shd, qn('w:shd'), {qn('w:val'): 'clear', qn('w:fill'): '334155'}) # Couleur de fond
                                except Exception:
                                    pass # Ignore if error occurs

            document.add_paragraph() # Spacing

    # Inter-document analysis (Clustering)
    if st.session_state.clustering_results and st.session_state.clustering_results != t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'):
        document.add_heading(t('card_clustering'), level=2)
        document.add_paragraph(t('clustering_description'))

        cluster_table_data = []
        cluster_table_data.append([
            "Cluster ID",
            t('cluster_keywords'),
            "Documents"
        ])

        for cluster_id, keywords in st.session_state.clustering_results['top_keywords'].items():
            docs_in_cluster = [
                result['filename'] for idx, result in enumerate(analysis_results)
                if st.session_state.clustering_results['clusters'][idx] == cluster_id
            ]
            cluster_table_data.append([
                str(cluster_id + 1),
                ", ".join(keywords),
                ", ".join(docs_in_cluster)
            ])
        
        # Create table in Word
        num_rows = len(cluster_table_data)
        num_cols = len(cluster_table_data[0])
        cluster_word_table = document.add_table(rows=num_rows, cols=num_cols)
        cluster_word_table.autofit = True

        for r_idx, row_data in enumerate(cluster_table_data):
            for c_idx, cell_data in enumerate(row_data):
                cell = cluster_word_table.cell(r_idx, c_idx)
                cell.text = cell_data
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0) # Gris clair
                if r_idx == 0: # Header row
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) # Blanc
                    try:
                        cell_shd = ET.SubElement(cell._tc, qn('w:tcPr'))
                        ET.SubElement(cell_shd, qn('w:shd'), {qn('w:val'): 'clear', qn('w:fill'): '334155'})
                    except Exception:
                        pass
        document.add_paragraph() # Spacing

    # Footer
    footer = document.sections[0].footer
    p = footer.paragraphs[0]
    p.text = f"{t('revolution_footer_message')}\n{t('revolution_confidential_note')}"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_txt_report(analysis_results, ernestmind_logo_base64):
    report_content = []
    report_content.append(f"--- {t('app_title')} - {t('Analysis and Smart Data Entry')} ---")
    report_content.append(f"{t('Rapport généré le')} {datetime.date.today()}\n")

    report_content.append(f"{t('results_title')}\n")

    for i, result in enumerate(analysis_results):
        report_content.append(f"=== {t('card_doc_info')}: {result['filename']} ===")
        report_content.append(f"{t('info_filename')}: {result['filename']}")
        report_content.append(f"{t('info_size')}: {result['size'] / 1024:.2f} KB")
        report_content.append(f"{t('info_type')}: {result['type']}")
        report_content.append(f"{t('info_pages')}: {result.get('page_count', 'N/A')}\n")

        if result['text_analysis'] and result['text_analysis']['total_words'] > 0:
            report_content.append(f"--- {t('card_text_analysis')} ---")
            report_content.append(f"{t('text_total_words')}: {result['text_analysis']['total_words']}")
            report_content.append(f"{t('text_unique_words')}: {result['text_analysis']['unique_words']}\n")

            report_content.append(f"{t('structure_titles')}:")
            for title in result['text_analysis']['potential_titles']:
                report_content.append(f"- {title}")
            report_content.append("\n")

            report_content.append(f"{t('structure_paragraphs')}:")
            for para in result['text_analysis']['paragraphs']:
                report_content.append(para)
            report_content.append("\n")

        if result['data_analysis']:
            report_content.append(f"--- {t('card_table_analysis')} ---")
            report_content.append(f"{t('table_shape')}: {result['data_analysis']['shape'][0]} {t('table_rows')} x {result['data_analysis']['shape'][1]} {t('table_cols')}\n")
            report_content.append(f"{t('Données Tabulaires (extrait)')}:\n{result['data_analysis']['head']}\n")

        report_content.append("\n" + "="*80 + "\n\n") # Separator between documents

    # Inter-document analysis (Clustering)
    if st.session_state.clustering_results and st.session_state.clustering_results != t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'):
        report_content.append(f"--- {t('card_clustering')} ---")
        report_content.append(f"{t('clustering_description')}\n")
        
        for cluster_id, keywords in st.session_state.clustering_results['top_keywords'].items():
            docs_in_cluster = [
                result['filename'] for idx, result in enumerate(analysis_results)
                if st.session_state.clustering_results['clusters'][idx] == cluster_id
            ]
            report_content.append(f"Cluster {cluster_id + 1}:")
            report_content.append(f"  {t('cluster_keywords')}: {', '.join(keywords)}")
            report_content.append(f"  Documents: {', '.join(docs_in_cluster)}\n")
        report_content.append("\n")

    report_content.append(f"\n--- {t('revolution_footer_message')} ---")
    report_content.append(f"--- {t('revolution_confidential_note')} ---")

    return "\n".join(report_content).encode('utf-8')


def generate_excel_report(analysis_results):
    if openpyxl is None:
        st.error("La bibliothèque 'openpyxl' n'est pas installée. Veuillez l'installer (`pip install openpyxl`) pour générer des rapports Excel.")
        return None

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for i, result in enumerate(analysis_results):
            sheet_name = f"Doc_{i+1}"
            
            # Summary sheet for each document
            summary_data = {
                t('info_filename'): [result['filename']],
                t('info_size'): [f"{result['size'] / 1024:.2f} KB"],
                t('info_type'): [result['type']],
                t('info_pages'): [result.get('page_count', 'N/A')]
            }
            summary_df = pd.DataFrame(summary_data).T.reset_index()
            summary_df.columns = ["Propriété", "Valeur"]
            summary_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0, startcol=0)

            # Text Analysis
            if result['text_analysis'] and result['text_analysis']['total_words'] > 0:
                text_analysis_df = pd.DataFrame({
                    "Métrique": [t('text_total_words'), t('text_unique_words')],
                    "Valeur": [result['text_analysis']['total_words'], result['text_analysis']['unique_words']]
                })
                text_analysis_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(summary_df) + 2, startcol=0)

                # Potential titles
                titles_df = pd.DataFrame({"Titres Potentiels": result['text_analysis']['potential_titles']})
                titles_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(summary_df) + len(text_analysis_df) + 4, startcol=0)

                # Paragraphs
                paragraphs_df = pd.DataFrame({"Premiers Paragraphes": result['text_analysis']['paragraphs']})
                paragraphs_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(summary_df) + len(text_analysis_df) + len(titles_df) + 6, startcol=0)

            # Tabular Data
            if result['data_analysis']:
                # Write original dataframes to separate sheets if available
                for j, df in enumerate(result['original_dataframes']):
                    df.to_excel(writer, sheet_name=f"{sheet_name}_Tabular_{j+1}", index=False)
                
                # Write analysis of the first dataframe
                if result['original_dataframes']:
                    data_analysis_summary = {
                        "Dimensions": [f"{result['data_analysis']['shape'][0]} {t('table_rows')} x {result['data_analysis']['shape'][1]} {t('table_cols')}"],
                        "Colonnes": [", ".join(result['data_analysis']['columns'])],
                        "Types de Colonnes": [str(result['data_analysis']['dtypes'])],
                        "Comptes de Null": [str(result['data_analysis']['null_counts'])]
                    }
                    data_analysis_df = pd.DataFrame(data_analysis_summary).T.reset_index()
                    data_analysis_df.columns = ["Propriété Analyse Tabulaire", "Valeur"]
                    
                    start_row_tab = writer.sheets[sheet_name].max_row + 2
                    data_analysis_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row_tab, startcol=0)
                    
                    # Add df.describe
                    describe_df = pd.read_html(result['data_analysis']['describe'], header=0)[0]
                    describe_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=writer.sheets[sheet_name].max_row + 2, startcol=0)
        
        # Inter-document analysis (Clustering) - in a separate sheet
        if st.session_state.clustering_results and st.session_state.clustering_results != t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'):
            clustering_data = []
            for cluster_id, keywords in st.session_state.clustering_results['top_keywords'].items():
                docs_in_cluster = [
                    result['filename'] for idx, result in enumerate(analysis_results)
                    if st.session_state.clustering_results['clusters'][idx] == cluster_id
                ]
                clustering_data.append({
                    "Cluster ID": cluster_id + 1,
                    t('cluster_keywords'): ", ".join(keywords),
                    "Documents": ", ".join(docs_in_cluster)
                })
            clustering_df = pd.DataFrame(clustering_data)
            clustering_df.to_excel(writer, sheet_name="Clustering Summary", index=False)
        
        # Add general footer to a dedicated sheet or first sheet if needed
        # Not easily done in a structured way for Excel, usually added as a note or in a summary sheet.
        # For simplicity, will add to the first sheet as a final note.
        # This part might need adjustment based on desired Excel report structure.
        ws = writer.sheets[list(writer.sheets.keys())[0]] # Get the first worksheet
        current_row = ws.max_row + 2
        ws.cell(row=current_row, column=1, value=t('revolution_footer_message'))
        ws.cell(row=current_row + 1, column=1, value=t('revolution_confidential_note'))


    output.seek(0)
    return output.getvalue()


def generate_master_report(analysis_results, export_format):
    ernestmind_logo_base64 = get_ernestmind_logo_base64()

    if export_format == "Excel":
        return generate_excel_report(analysis_results)
    elif export_format == "Word":
        return generate_word_report(analysis_results, ernestmind_logo_base64)
    elif export_format == "Texte (.txt)":
        return generate_txt_report(analysis_results, ernestmind_logo_base64)
    elif export_format == "PDF":
        return generate_pdf_report(analysis_results, ernestmind_logo_base64)
    return None


# ==============================================================================
# 4. INTERFACE UTILISATEUR STREAMLIT 🖥️
# ==============================================================================

# Logo en haut de la page
st.image(ERNESTMIND_LOGO_URL, use_column_width=False, width=200, output_format="PNG", caption="ErnestMind.ai Logo")
st.markdown(f"<h1 class='app-title'>{t('app_title')}</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='app-subtitle'>{t('app_subtitle')}</p>", unsafe_allow_html=True)

# Initialisation de session_state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'clustering_results' not in st.session_state:
    st.session_state.clustering_results = None

# Sidebar pour le téléversement et les options
with st.sidebar:
    st.markdown(f"## {t('sidebar_title')}")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        f"**{t('upload_label')}**",
        type=["pdf", "docx", "xlsx", "txt", "json", "xml", "eml", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help=t("supported_formats")
    )

    if st.button(t('analyze_button')):
        if uploaded_files:
            st.session_state.analysis_results = [] # Reset previous results
            all_text_content_for_clustering = []
            filenames_for_clustering = []

            progress_bar = st.progress(0, text=f"{t('analysis_in_progress')} 0/{len(uploaded_files)} {t('files')}...")

            for i, uploaded_file in enumerate(uploaded_files):
                file_size = uploaded_file.size
                file_type = uploaded_file.type
                filename = uploaded_file.name

                st.write(f"**{t('Processing')} {filename}...**")
                
                text_content, data_frames, error = extract_file_content(uploaded_file)
                
                if error:
                    st.error(f"Error processing {filename}: {error}")
                    continue

                if text_content:
                    text_analysis = analyze_text(text_content)
                    all_text_content_for_clustering.append(text_content)
                    filenames_for_clustering.append(filename)
                else:
                    text_analysis = {}

                data_analysis = None
                if data_frames:
                    # For simplicity, analyze only the first dataframe if multiple exist in an Excel file
                    data_analysis = analyze_dataframe(data_frames[0])

                st.session_state.analysis_results.append({
                    "filename": filename,
                    "size": file_size,
                    "type": file_type,
                    "text_content": text_content, # Keep raw text for display if needed
                    "text_analysis": text_analysis,
                    "original_dataframes": data_frames, # Store original DFs for Excel export
                    "data_analysis": data_analysis,
                    "page_count": len(pdfplumber.open(uploaded_file).pages) if 'pdf' in file_type else 'N/A' # Specific for PDF
                })
                progress_bar.progress((i + 1) / len(uploaded_files), text=f"{t('analysis_in_progress')} {i+1}/{len(uploaded_files)} {t('files')}...")
            
            # Perform clustering if multiple files with text content were analyzed
            if len(all_text_content_for_clustering) > 1:
                st.session_state.clustering_results = perform_clustering(all_text_content_for_clustering)
                if isinstance(st.session_state.clustering_results, str): # Error message from clustering
                    st.warning(f"Clustering Warning: {st.session_state.clustering_results}")
                    st.session_state.clustering_results = t('Pas assez de contenu textuel distinct pour un regroupement pertinent.') # Set a specific message
            else:
                st.session_state.clustering_results = t('Pas assez de contenu textuel distinct pour un regroupement pertinent.')
            
            progress_bar.empty() # Clear progress bar after completion
            st.success("Analyse terminée ! ✨")

        else:
            st.info(t('no_files_uploaded'))

# Affichage des résultats
if st.session_state.analysis_results:
    st.markdown("---")
    st.markdown(f"## {t('results_title')}")

    # Onglets pour chaque fichier analysé
    for i, result in enumerate(st.session_state.analysis_results):
        with st.expander(f"**📄 {result['filename']}** ({result['type']})"):
            tab1, tab2, tab3, tab4 = st.tabs([t('tab_summary'), t('tab_data'), t('tab_text'), t('tab_viz')])

            with tab1: # Synthèse
                st.markdown(f"### {t('card_doc_info')}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label=t('info_filename'), value=result['filename'])
                with col2:
                    st.metric(label=t('info_size'), value=f"{result['size'] / 1024:.2f} KB")
                with col3:
                    st.metric(label=t('info_type'), value=result['type'].split('/')[-1].upper())
                with col4:
                    st.metric(label=t('info_pages'), value=result.get('page_count', 'N/A'))

                if result['text_analysis']:
                    st.markdown(f"### {t('card_doc_structure')}")
                    st.markdown(f"<p class='small-title'>{t('structure_titles')}:</p>", unsafe_allow_html=True)
                    for title in result['text_analysis']['potential_titles']:
                        st.write(f"- {title}")
                    
                    st.markdown(f"<p class='small-title'>{t('structure_paragraphs')}:</p>", unsafe_allow_html=True)
                    for para in result['text_analysis']['paragraphs']:
                        st.write(f"» {para[:150]}...") # Afficher un extrait

                if result['data_analysis']:
                    st.markdown(f"### {t('card_table_analysis')}")
                    st.metric(label=t('table_shape'), value=f"{result['data_analysis']['shape'][0]} {t('table_rows')} x {result['data_analysis']['shape'][1]} {t('table_cols')}")
                    
                    st.markdown(f"<p class='small-title'>{t('column_types_title')}:</p>", unsafe_allow_html=True)
                    for col, dtype in result['data_analysis']['dtypes'].items():
                        st.write(f"- **{col}**: {dtype}")
                    
                    st.markdown(f"<p class='small-title'>{t('column_suggestions_title')}:</p>", unsafe_allow_html=True)
                    for col, dtype in result['data_analysis']['dtypes'].items():
                        if 'int' in dtype or 'float' in dtype:
                            st.write(f"- **{col}** ({dtype}): {t('Normalisation, détection d\'outliers')}")
                        elif 'object' in dtype or 'category' in dtype:
                            st.write(f"- **{col}** ({dtype}): {t('Encodage One-Hot, regroupement')}")
                        elif 'datetime' in dtype:
                            st.write(f"- **{col}** ({dtype}): {t('Extraction de composantes (jour, mois)')}")

            with tab2: # Données Tabulaires
                st.markdown(f"### {t('tab_data')}")
                if result['original_dataframes']:
                    for j, df in enumerate(result['original_dataframes']):
                        st.markdown(f"#### Table {j+1}")
                        st.dataframe(df)
                else:
                    st.info(t('Aucune donnée tabulaire structurée n\'a été extraite de ce fichier.'))
            
            with tab3: # Analyse de Texte
                st.markdown(f"### {t('tab_text')}")
                if result['text_analysis']:
                    st.markdown(f"**{t('text_total_words')}:** {result['text_analysis'].get('total_words', 'N/A')}")
                    st.markdown(f"**{t('text_unique_words')}:** {result['text_analysis'].get('unique_words', 'N/A')}")
                    st.markdown(f"**{t('text_sentiment')}:** {result['text_analysis'].get('sentiment', 'N/A')} (Bientôt disponible)")
                    
                    st.markdown(f"#### {t('text_entities')}")
                    if result['text_analysis'].get('entities'):
                        entity_html = ""
                        for ent in result['text_analysis']['entities']:
                            if ent['label'] == "INFO": # Special case for spacy prompt
                                st.info(ent['text'])
                            else:
                                entity_html += f"<span class='entity-badge {ent['label']}'>{ent['text']} ({ent['label']})</span>"
                        st.markdown(entity_html, unsafe_allow_html=True)
                    else:
                        st.info(t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'))
                    
                    if st.checkbox(t('Voir le texte brut extrait'), key=f"raw_text_{i}"):
                        st.text_area("Texte Brut", result['text_content'], height=300)
                else:
                    st.info(t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'))

            with tab4: # Visualisations
                st.markdown(f"### {t('tab_viz')}")
                if result['data_analysis'] and result['original_dataframes']:
                    df_for_viz = result['original_dataframes'][0] # Use the first dataframe for viz
                    
                    numeric_cols = result['data_analysis']['numeric_cols']
                    categorical_cols = result['data_analysis']['categorical_cols']

                    if numeric_cols:
                        st.markdown(f"#### {t('Distribution des variables numériques')}")
                        selected_numeric = st.selectbox(t('Choisir une variable numérique'), numeric_cols, key=f"numeric_viz_{i}")
                        if selected_numeric:
                            fig_hist = px.histogram(df_for_viz, x=selected_numeric, title=f"Distribution de {selected_numeric}")
                            st.plotly_chart(fig_hist, use_container_width=True)
                        
                        if len(numeric_cols) > 1:
                            st.markdown(f"#### {t('Corrélation entre variables numériques')}")
                            fig_corr = px.imshow(df_for_viz[numeric_cols].corr(), text_auto=True, aspect="auto",
                                                title=t('Matrice de Corrélation'))
                            st.plotly_chart(fig_corr, use_container_width=True)

                    if categorical_cols:
                        st.markdown(f"#### {t('Distribution des variables catégorielles')}")
                        selected_categorical = st.selectbox(t('Choisir une variable catégorielle'), categorical_cols, key=f"cat_viz_{i}")
                        if selected_categorical:
                            fig_bar = px.bar(df_for_viz, x=selected_categorical, title=f"{t('Distribution de')} {selected_categorical}")
                            st.plotly_chart(fig_bar, use_container_width=True)
                    
                    if not numeric_cols and not categorical_cols:
                        st.info(t('Pas de colonnes numériques ou catégorielles pour générer des graphiques.'))

                else:
                    st.info(t('Aucune donnée tabulaire pour générer des visualisations.'))
    
    # Inter-document Analysis Section
    st.markdown("---")
    st.markdown(f"## {t('card_clustering')}")
    if st.session_state.clustering_results:
        if isinstance(st.session_state.clustering_results, str):
            st.info(st.session_state.clustering_results)
        else:
            st.write(t('clustering_description'))
            clustering_df_data = []
            for cluster_id, keywords in st.session_state.clustering_results['top_keywords'].items():
                docs_in_cluster = [
                    f"{st.session_state.analysis_results[idx]['filename']} (Cluster {cluster_id + 1})"
                    for idx, cluster_label in enumerate(st.session_state.clustering_results['clusters'])
                    if cluster_label == cluster_id
                ]
                clustering_df_data.append({
                    "Cluster ID": cluster_id + 1,
                    t('cluster_keywords'): ", ".join(keywords),
                    "Documents": ", ".join(docs_in_cluster)
                })
            clustering_df = pd.DataFrame(clustering_df_data)
            st.dataframe(clustering_df)
    else:
        st.info(t('Pas assez de contenu textuel distinct pour un regroupement pertinent.'))


    # --- Smart Data Entry Section ---
    st.markdown("---")
    st.markdown(f"## {t('data_entry_section_title')}")
    st.info(t('simulation_message'))
    st.markdown(f"<p>{t('data_entry_intro')}</p>", unsafe_allow_html=True)

    business_module = st.selectbox(
        t('select_business_module'),
        [
            t('module_finance'),
            t('module_hr'),
            t('module_logistics'),
            t('module_sales_marketing'),
            t('module_customer_service')
        ]
    )

    # Option to pre-fill from an analyzed document
    analyzed_filenames = [res['filename'] for res in st.session_state.analysis_results if res['text_content']]
    prefill_doc = None
    if analyzed_filenames:
        st.markdown(f"**{t('prefill_from_doc')}**")
        prefill_doc_name = st.selectbox(
            t('select_doc_for_prefill'),
            ["-- Sélectionner --"] + analyzed_filenames
        )
        if prefill_doc_name != "-- Sélectionner --":
            prefill_doc = next((res for res in st.session_state.analysis_results if res['filename'] == prefill_doc_name), None)
            st.info(f"Pré-remplissage activé pour : {prefill_doc_name}")
    else:
        st.info(t('no_doc_for_prefill'))


    # Simulated Data Entry Forms
    with st.form(key='data_entry_form'):
        if business_module == t('module_finance'):
            st.markdown(f"### {t('form_title_finance')}")
            st.write(t('finance_intro'))
            st.markdown(f"<i>{t('prefill_info_finance')}</i>", unsafe_allow_html=True)
            invoice_num = st.text_input(t('label_invoice_num'), value="INV-2023-001" if prefill_doc else "")
            amount = st.number_input(t('label_amount'), value=123.45 if prefill_doc else 0.0, format="%.2f")
            date = st.date_input(t('label_date'), value=datetime.date.today() if prefill_doc else None)
            vendor = st.text_input(t('label_vendor'), value="Fournisseur ABC" if prefill_doc else "")
            description = st.text_area(t('label_description'), value="Achat de fournitures de bureau" if prefill_doc else "")

        elif business_module == t('module_hr'):
            st.markdown(f"### {t('form_title_hr')}")
            st.write(t('hr_intro'))
            st.markdown(f"<i>{t('prefill_info_hr')}</i>", unsafe_allow_html=True)
            employee_name = st.text_input(t('label_employee_name'), value="Jean Dupont" if prefill_doc else "")
            employee_id = st.text_input(t('label_employee_id'), value="EMP001" if prefill_doc else "")
            contract_type = st.selectbox(t('label_contract_type'), ["CDI", "CDD", "Intérim", "Stage"], index=0 if not prefill_doc else 0)
            start_date = st.date_input(t('label_start_date'), value=datetime.date.today() if prefill_doc else None)

        elif business_module == t('module_logistics'):
            st.markdown(f"### {t('form_title_logistics')}")
            st.write(t('logistics_intro'))
            st.markdown(f"<i>{t('prefill_info_logistics')}</i>", unsafe_allow_html=True)
            order_id = st.text_input(t('label_order_id'), value="ORD-456" if prefill_doc else "")
            product = st.text_input(t('label_product'), value="Ordinateurs Portables" if prefill_doc else "")
            quantity = st.number_input(t('label_quantity'), value=10 if prefill_doc else 0, min_value=0)
            delivery_date = st.date_input(t('label_delivery_date'), value=datetime.date.today() + datetime.timedelta(days=7) if prefill_doc else None)

        elif business_module == t('module_sales_marketing'):
            st.markdown(f"### {t('form_title_sales')}")
            st.write(t('sales_marketing_intro'))
            st.markdown(f"<i>{t('prefill_info_sales')}</i>", unsafe_allow_html=True)
            lead_name = st.text_input(t('label_lead_name'), value="Sophie Martin" if prefill_doc else "")
            company = st.text_input(t('label_company'), value="Tech Innovations Inc." if prefill_doc else "")
            status = st.selectbox(t('label_status'), ["Nouveau", "Qualifié", "Contacté", "Opportunité", "Gagné", "Perdu"], index=0 if not prefill_doc else 0)
            next_action = st.text_area(t('label_next_action'), value="Suivi par email la semaine prochaine" if prefill_doc else "")

        elif business_module == t('module_customer_service'):
            st.markdown(f"### {t('form_title_customer_service')}")
            st.write(t('customer_service_intro'))
            st.markdown(f"<i>{t('prefill_info_customer_service')}</i>", unsafe_allow_html=True)
            ticket_id = st.text_input(t('label_ticket_id'), value="T-7890" if prefill_doc else "")
            customer_name = st.text_input(t('label_customer_name'), value="Pierre Dubois" if prefill_doc else "")
            issue = st.text_area(t('label_issue'), value="Problème de connexion au service cloud" if prefill_doc else "")
            priority = st.selectbox(t('label_priority'), ["Faible", "Moyenne", "Haute", "Urgent"], index=1 if not prefill_doc else 1)
        
        submit_button = st.form_submit_button(label=f"Soumettre Données {business_module.split(' ')[0]}") # Dynamic button label
        if submit_button:
            if business_module == t('module_finance'):
                st.success(f"{t('finance_success')}: Numéro de Facture: {invoice_num}, Montant: {amount}€")
            elif business_module == t('module_hr'):
                st.success(f"{t('hr_success')}: Employé: {employee_name}, ID: {employee_id}")
            elif business_module == t('module_logistics'):
                st.success(f"{t('logistics_success')}: Commande: {order_id}, Produit: {product}, Quantité: {quantity}")
            elif business_module == t('module_sales_marketing'):
                st.success(f"{t('sales_success')}: Lead: {lead_name}, Entreprise: {company}")
            elif business_module == t('module_customer_service'):
                st.success(f"{t('customer_service_success')}: Ticket: {ticket_id}, Client: {customer_name}")


    # --- ErnestMind Revolution Section ---
    st.markdown("---")
    st.markdown(f"""
    <div class="revolution-section">
        <h2>{t('revolution_section_title')}</h2>
        <p>{t('revolution_intro')}</p>
        <p><b>{t('revolution_mission')}</b></p>

        <h3>{t('revolution_numbers_title')}</h3>
        <ul>
            <li>{t('revolution_numbers_200_models')}</li>
            <li>{t('revolution_numbers_25_industries')}</li>
            <li>{t('revolution_numbers_20_languages')}</li>
            <li>{t('revolution_numbers_100_local')}</li>
            <li>{t('revolution_numbers_0_leaks')}</li>
            <li>{t('revolution_numbers_3_free_models')}</li>
        </ul>

        <h3>{t('revolution_why_unique_title')}</h3>
        <ul>
            <li>{t('revolution_why_unique_sovereignty')}</li>
            <li>{t('revolution_why_unique_patented')}</li>
            <li>{t('revolution_why_unique_multilingualism')}</li>
            <li>{t('revolution_why_unique_sector_adaptation')}</li>
            <li>{t('revolution_why_unique_instant_deployment')}</li>
            <li>{t('revolution_why_unique_ethics')}</li>
        </ul>

        <h3>{t('revolution_strategic_features_title')}</h3>
        <ul>
            <li>{t('revolution_strategic_features_confidentiality')}</li>
            <li>{t('revolution_strategic_features_customization')}</li>
            <li>{t('revolution_strategic_features_interface')}</li>
            <li>{t('revolution_strategic_features_support')}</li>
            <li>{t('revolution_strategic_features_interoperability')}</li>
        </ul>
        <p class="confidential-note">{t('revolution_confidential_note')}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Export Section (existing functionality) ---
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"## {t('export_section_title')}")
        export_format = st.selectbox(t('export_format'), ["Excel", "Word", "Texte (.txt)", "PDF"])
        
        report_data = generate_master_report(st.session_state.analysis_results, export_format)
        
        file_extension = {"Excel": ".xlsx", "Word": ".docx", "Texte (.txt)": ".txt", "PDF": ".pdf"}
        mime_type = {"Excel": "application/vnd.ms-excel", "Word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Texte (.txt)": "text/plain", "PDF": "application/pdf"}

        st.download_button(
            label=t('export_button'),
            data=report_data,
            file_name=f"Rapport_ErnestMind_{datetime.date.today()}{file_extension[export_format]}",
            mime=mime_type[export_format]
        )
        
else:
    st.info(t('no_files_uploaded'))

# Footer for the revolution message
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #94A3B8; font-size: 0.9em; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #334155;">
    {t('revolution_footer_message')}
</div>
""", unsafe_allow_html=True)

