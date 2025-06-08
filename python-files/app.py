from docx.enum.text import WD_ALIGN_PARAGRAPH

from flask import Flask, request, send_file, render_template
import os
import unicodedata
import subprocess
from werkzeug.utils import secure_filename
from docx import Document
import logging
from contextlib import contextmanager
from ebooklib import epub
import zipfile
from PIL import Image
import io
import base64
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuration des formats d'image autorisés
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

# Configuration des polices disponibles
FONT_OPTIONS = {
    'text_fonts': {
        'libre_caslon': 'Libre Caslon Text',
        'eb_garamond': 'EB Garamond',
        'sabon': 'Sabon',
        'cambria': 'Cambria',
        'linux_libertine': 'Linux Libertine',  # ← NOUVEAU : remplace playfair_display
    },
    'title_fonts': {
        'libre_caslon': 'Libre Caslon Text',
        'eb_garamond': 'EB Garamond',
        'sabon': 'Sabon',
        'euphoria_script': 'Euphoria Script',
        'playfair_display': 'Playfair Display',  # ← Reste dans les polices de titre
        'century_gothic': 'Century Gothic',
        'cambria': 'Cambria',
    }
}


def validate_image_file(file):
    """Valide le format d'image"""
    if not file or not file.filename:
        return False
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def cleanup_temp_files(base_path, extensions=['.aux', '.out', '.fls', '.fdb_latexmk', '.fmt', '.log']):
    """Nettoie les fichiers temporaires de LaTeX"""
    for ext in extensions:
        temp_file = base_path + ext
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logger.info(f"Fichier temporaire LaTeX supprimé : {temp_file}")
            except OSError as e:
                logger.warning(f"Impossible de supprimer {temp_file}: {e}")


def get_font_commands(text_font_key, title_font_key):
    """Génère les commandes LaTeX pour les polices sélectionnées"""
    text_fonts = FONT_OPTIONS['text_fonts']
    title_fonts = FONT_OPTIONS['title_fonts']

    # Police de texte principal avec fallbacks
    text_font_commands = []

    if text_font_key == 'libre_caslon':
        text_font_commands = [
            r"\IfFontExistsTF{Libre Caslon Text}{",
            r"  \setmainfont{Libre Caslon Text}[Ligatures=TeX]",
            r"}{",
            r"  \setmainfont{Times New Roman}[Ligatures=TeX]",
            r"}"
        ]
    elif text_font_key == 'eb_garamond':
        text_font_commands = [
            r"\IfFontExistsTF{EB Garamond}{",
            r"  \setmainfont{EB Garamond}[Ligatures=TeX]",
            r"}{",
            r"  \setmainfont{Times New Roman}[Ligatures=TeX]",
            r"}"
        ]
    elif text_font_key == 'sabon':
        text_font_commands = [
            r"\IfFontExistsTF{Sabon}{",
            r"  \setmainfont{Sabon}[Ligatures=TeX]",
            r"}{",
            r"  \setmainfont{Times New Roman}[Ligatures=TeX]",
            r"}"
        ]
    elif text_font_key == 'cambria':
        text_font_commands = [
            r"\IfFontExistsTF{Cambria}{",
            r"  \setmainfont{Cambria}[Ligatures=TeX]",
            r"}{",
            r"  \setmainfont{Times New Roman}[Ligatures=TeX]",
            r"}"
        ]

    # Police pour les titres
    title_font_commands = []

    if title_font_key == 'libre_caslon':
        title_font_commands = [r"\newfontfamily\titlefont{Libre Caslon Text}[Scale=1.0]"]
    elif title_font_key == 'eb_garamond':
        title_font_commands = [r"\newfontfamily\titlefont{EB Garamond}[Scale=1.0]"]
    elif title_font_key == 'sabon':
        title_font_commands = [r"\newfontfamily\titlefont{Sabon}[Scale=1.0]"]
    elif title_font_key == 'euphoria_script':
        title_font_commands = [r"\newfontfamily\titlefont{Euphoria Script}[Scale=1.0]"]
    elif title_font_key == 'playfair_display':
        title_font_commands = [r"\newfontfamily\titlefont{Playfair Display}[Scale=1.0]"]
    elif title_font_key == 'century_gothic':
        title_font_commands = [r"\newfontfamily\titlefont{Century Gothic}[Scale=1.0]"]
    elif title_font_key == 'cambria':
        title_font_commands = [r"\newfontfamily\titlefont{Cambria}[Scale=1.0]"]

    return text_font_commands, title_font_commands


def is_right_aligned(para):
    """Détecte si un paragraphe est aligné à droite (pour les mises en exergue)"""
    try:
        return para.alignment == WD_ALIGN_PARAGRAPH.RIGHT
    except:
        return False


def is_center_aligned(para):  # ← MAINTENANT CORRECTEMENT ALIGNÉE
    """Détecte si un paragraphe est centré"""
    try:
        return para.alignment == WD_ALIGN_PARAGRAPH.CENTER
    except:
        return False


def get_latex_alignment_command(is_right, is_center=False):
    """Convertit l'alignement en commande LaTeX - TOUS les alignements"""
    if is_center:
        return r'{\centering ', r'\par}'
    elif is_right:
        return r'\begin{flushright}', r'\end{flushright}'
    else:
        return '', ''


def get_html_alignment_style(is_right, is_center=False):
    """Convertit l'alignement en style CSS pour EPUB - gestion de tous les alignements"""
    if is_center:
        return 'text-align: center;'
    elif is_right:
        return 'text-align: right;'
    else:
        return 'text-align: justify;'  # Tout le reste est justifié


def extract_footnotes_from_paragraph(para):
    """
    Extrait les notes de bas de page d'un paragraphe Word
    Retourne le texte nettoyé et une liste des notes
    """
    footnotes = []
    clean_text = ""

    for run in para.runs:
        run_text = run.text

        # Vérifier s'il y a des notes de bas de page dans ce run
        if hasattr(run, '_element'):
            # Chercher les références de notes dans le XML du run
            footnote_refs = run._element.xpath('.//w:footnoteReference',
                                               namespaces={
                                                   'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})

            for ref in footnote_refs:
                footnote_id = ref.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                if footnote_id:
                    # Extraire le texte de la note de bas de page
                    footnote_text = get_footnote_text(para.part, footnote_id)
                    if footnote_text:
                        footnotes.append(footnote_text)
                        # Remplacer la référence par un marqueur temporaire
                        run_text = run_text.replace(run.text, run.text + f"[FOOTNOTE_{len(footnotes)}]")

        clean_text += run_text

    return clean_text, footnotes


def get_footnote_text(document_part, footnote_id):
    """
    Récupère le texte d'une note de bas de page par son ID
    """
    try:
        # Accéder aux notes de bas de page dans le document
        footnotes_part = document_part.footnotes_part
        if footnotes_part:
            for footnote in footnotes_part.footnotes:
                if footnote.footnote_id == footnote_id:
                    # Extraire le texte de tous les paragraphes de la note
                    footnote_text = ""
                    for para in footnote.paragraphs:
                        footnote_text += para.text + " "
                    return footnote_text.strip()
    except Exception as e:
        logger.warning(f"Erreur lors de l'extraction de la note {footnote_id}: {e}")

    return None


def process_footnotes_for_latex(text, footnotes):
    """
    Remplace les marqueurs de notes par des commandes LaTeX
    """
    for i, footnote in enumerate(footnotes, 1):
        marker = f"[FOOTNOTE_{i}]"
        if marker in text:
            footnote_latex = escape_latex(footnote)
            text = text.replace(marker, f"\\footnote{{{footnote_latex}}}")

    return text


def process_footnotes_for_html(text, footnotes):
    """
    Remplace les marqueurs de notes par des liens HTML avec notes en fin de chapitre
    """
    footnote_links = ""
    footnote_list = ""

    for i, footnote in enumerate(footnotes, 1):
        marker = f"[FOOTNOTE_{i}]"
        if marker in text:
            # Créer un lien vers la note
            link = f'<sup><a href="#footnote_{i}" id="footnote_ref_{i}">{i}</a></sup>'
            text = text.replace(marker, link)

            # Ajouter la note à la liste des notes
            footnote_list += f'<div id="footnote_{i}" style="margin-bottom: 0.5em; font-size: 0.9em;"><sup>{i}</sup> {footnote} <a href="#footnote_ref_{i}">↑</a></div>'

    if footnote_list:
        footnote_links = f'<div style="border-top: 1px solid #ccc; margin-top: 2em; padding-top: 1em;"><h4>Notes</h4>{footnote_list}</div>'

    return text, footnote_links


def process_simple_footnotes_for_html(text, footnotes_dict, global_footnote_counter, current_chapter_file):
    """
    Traite les notes simples (NOTE1), (NOTE2) pour HTML/EPUB avec compteur global
    """
    import re

    # Pattern pour détecter (NOTE1), (NOTE2), etc.
    note_pattern = r'\(NOTE(\d+)\)'
    note_matches = list(re.finditer(note_pattern, text))

    processed_notes = []

    if note_matches:
        logger.info(f"🔍 Notes simples détectées pour EPUB: {len(note_matches)}")

        for match in reversed(note_matches):
            note_num = match.group(1)

            # Incrémenter le compteur global
            global_footnote_counter[0] += 1
            global_note_id = global_footnote_counter[0]

            # Chercher la définition dans le dictionnaire
            if note_num in footnotes_dict:
                footnote_text = footnotes_dict[note_num]
                # Créer un lien vers la note de fin avec référence au chapitre courant
                footnote_html = f'<sup><a href="endnotes.xhtml#endnote_{global_note_id}" id="endnote_ref_{global_note_id}">{global_note_id}</a></sup>'
                text = text[:match.start()] + footnote_html + text[match.end():]

                # Ajouter à la liste des notes traitées avec info du chapitre
                processed_notes.append({
                    'id': global_note_id,
                    'text': footnote_text,
                    'chapter_file': current_chapter_file,
                    'ref_id': f"endnote_ref_{global_note_id}"
                })

                logger.info(f"✅ Note simple convertie pour EPUB: (NOTE{note_num}) -> endnote {global_note_id}")
            else:
                # Fallback
                footnote_html = f'<sup><a href="endnotes.xhtml#endnote_{global_note_id}" id="endnote_ref_{global_note_id}">{global_note_id}</a></sup>'
                text = text[:match.start()] + footnote_html + text[match.end():]

                processed_notes.append({
                    'id': global_note_id,
                    'text': 'Texte à définir',
                    'chapter_file': current_chapter_file,
                    'ref_id': f"endnote_ref_{global_note_id}"
                })

                logger.info(f"⚠️ Note (NOTE{note_num}) sans définition pour EPUB")

    return text, processed_notes


def create_endnotes_page(endnotes):
    """
    Crée une page HTML pour les notes de fin avec liens de retour corrects
    """
    notes_html = ""
    for note in endnotes:
        # Lien de retour vers le chapitre d'origine
        back_link = f"{note['chapter_file']}#{note['ref_id']}"

        notes_html += f'''
        <div id="endnote_{note['id']}" style="margin-bottom: 1.5em; padding: 1em; border-left: 3px solid #666; background-color: #f9f9f9;">
            <p style="margin: 0; line-height: 1.4;">
                <sup style="font-weight: bold; color: #333;">{note['id']}</sup> 
                {note['text']} 
                <a href="{back_link}" style="font-size: 0.9em; color: #0066cc; text-decoration: none; margin-left: 1em;">↑ retour au texte</a>
            </p>
        </div>
        '''

    return f'''
    <html>
        <head>
            <title>Notes</title>
            <style>
                body {{ font-family: Georgia, serif; line-height: 1.6; margin: 2em; }}
                h1 {{ text-align: center; color: #333; border-bottom: 2px solid #333; padding-bottom: 0.5em; }}
                a {{ color: #0066cc; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Notes</h1>
            {notes_html}
        </body>
    </html>
    '''


def get_luatex_config(title, author, text_font_key='libre_caslon', title_font_key='libre_caslon',
                      text_size='12', title1_size='32', title2_size='26', title3_size='22', use_script=True):
    """Configuration LaTeX optimisée pour qualité éditoriale professionnelle avec support des notes de bas de page"""
    config_lines = [
        f"\\documentclass[12pt,twoside,openright]{{book}}",

        # PACKAGES ESSENTIELS POUR LUALATEX
        r"\usepackage{fontspec}",
        r"\usepackage{luatextra}",
        r"\usepackage{microtype}",
        r"\usepackage{polyglossia}",
        r"\setmainlanguage{french}",
        r"\usepackage{silence}",
        r"\WarningFilter{latexfont}{Font shape}",
        r"\WarningFilter{latexfont}{Some font shapes were not available}",

        # PACKAGES ADDITIONNELS POUR QUALITÉ ÉDITORIALE
        r"\usepackage{impnattypo}",  # Améliore la typographie française
        r"\usepackage{lua-widow-control}",  # Contrôle avancé veuves/orphelines
        r"\usepackage{chickenize}",  # Debug des problèmes de mise en page

        # PACKAGES POUR LES NOTES DE BAS DE PAGE
        r"\usepackage[stable,bottom]{footmisc}",

        # GÉOMÉTRIE OPTIMISÉE POUR LA LECTURE
        r"\usepackage{geometry}",
        r"\geometry{paperwidth=6in, paperheight=9in, inner=0.8in, outer=0.65in, top=0.8in, bottom=1in, heightrounded}",

        # PACKAGES VISUELS
        r"\usepackage{graphicx}",
        r"\usepackage{setspace}",
        r"\usepackage{xcolor}",
        r"\usepackage[most]{tcolorbox}",
        r"\usepackage{lettrine}",

        # EN-TÊTES
        r"\usepackage{fancyhdr}",
        r"\setlength{\headheight}{15pt}",

        # CONFIGURATION DES NOTES DE BAS DE PAGE - VERSION UNIQUE ET CORRIGÉE
        r"\setlength{\footnotesep}{0.5em}",
        r"\setlength{\skip\footins}{1.2em}",
        r"\renewcommand{\footnoterule}{%",
        r"  \kern-3pt%",
        r"  \hrule width 0.4\columnwidth height 0.4pt%",
        r"  \kern 10pt%",
        r"}",
        r"\renewcommand{\footnotesize}{\fontsize{9}{11}\selectfont}",

        # MICROTYPOGRAPHIE AVANCÉE POUR LUALATEX
        r"\microtypesetup{",
        r"  activate={true,nocompatibility},",
        r"  final,",
        r"  tracking=true,",
        r"  kerning=true,",
        r"  spacing=true,",
        r"  factor=1100,",
        r"  stretch=20,",
        r"  shrink=20",
        r"}",

        # RÉGLAGES TYPOGRAPHIQUES PROFESSIONNELS
        r"\tolerance=1500",  # Augmenté pour plus de flexibilité
        r"\emergencystretch=3em",  # Plus de stretch d'urgence
        r"\hbadness=1000",  # Réduit les avertissements
        r"\vbadness=1000",
        r"\hfuzz=0.1pt",  # Plus strict
        r"\vfuzz=0.1pt",

        # CÉSURES INTELLIGENTES
        r"\lefthyphenmin=2",  # Minimum 2 lettres avant césure
        r"\righthyphenmin=3",  # Minimum 3 lettres après césure
        r"\hyphenpenalty=500",  # Réduit la pénalité de césure (favorise les césures)
        r"\exhyphenpenalty=50",  # Césures après tirets

        # CONTRÔLE AVANCÉ DES VEUVES/ORPHELINES
        r"\clubpenalty=10000",  # Orphelines
        r"\widowpenalty=10000",  # Veuves
        r"\brokenpenalty=10000",  # Césures sur plusieurs pages
        r"\interlinepenalty=0",  # Permet coupures entre lignes
        r"\predisplaypenalty=10000",  # Avant équations
        r"\postdisplaypenalty=10000",  # Après équations
        r"\displaywidowpenalty=10000",  # Veuves avec équations

        # CONTRÔLE DES RIVIÈRES ET ESPACEMENT
        r"\lineskiplimit=0pt",
        r"\lineskip=1pt",
        r"\parskip=0pt plus 0.5pt",  # Légère flexibilité entre paragraphes
        r"\parfillskip=0pt plus 1fil",

        # RÉGLAGES POUR ÉVITER LES RIVIÈRES
        r"\setlength{\parindent}{1.5em}",  # Alinéa standard
        r"\nonfrenchspacing",  # Espaces après ponctuation

        # CONFIGURATION LUA-WIDOW-CONTROL (si disponible)
        r"\lwcsetup{",
        r"  balanced=true,",
        r"  draft=false",
        r"}",

        # COULEURS
        r"\definecolor{bubblegray}{RGB}{240,240,240}",
    ]

    # AJOUT DES POLICES PERSONNALISÉES avec microtypographie
    text_font_commands, title_font_commands = get_font_commands(text_font_key, title_font_key)
    config_lines.extend(text_font_commands)
    config_lines.extend(title_font_commands)

    # Activation de la microtypographie pour les polices personnalisées
    config_lines.extend([
        r"\SetTracking{encoding={*}, shape=sc}{40}",  # Lettres capitales
        r"\SetProtrusion{encoding={*}}{",
        r"  A = {50,50},",
        r"  F = {0,50},",
        r"  J = {50,0},",
        r"  K = {0,50},",
        r"  L = {0,50},",
        r"  P = {0,50},",
        r"  R = {0,50},",
        r"  T = {50,50},",
        r"  V = {50,50},",
        r"  W = {50,50},",
        r"  X = {50,50},",
        r"  Y = {50,50},",
        r"  k = {0,50},",
        r"  r = {0,50},",
        r"  t = {0,50},",
        r"  v = {50,50},",
        r"  w = {50,50},",
        r"  x = {50,50},",
        r"  y = {50,50}",
        r"}",
    ])

    # Définir euphoria comme alias de titlefont pour la compatibilité
    config_lines.append(r"\let\euphoria\titlefont")

    config_lines.extend([
        # STYLES DE PAGE
        r"\fancypagestyle{banniere}{",
        r"  \fancyhf{}",
        r"  \fancyfoot[C]{\thepage}",
        r"  \renewcommand{\headrulewidth}{0pt}",
        r"  \fancyhead[CE]{\textcolor{gray}{\footnotesize\MakeUppercase{" + title + "}}}",
        r"  \fancyhead[CO]{\textcolor{gray}{\footnotesize\leftmark}}",
        r"}",

        r"\fancypagestyle{chapitre}{",
        r"  \fancyhf{}",
        r"  \fancyfoot[C]{\thepage}",
        r"  \renewcommand{\headrulewidth}{0pt}",
        r"}",

        r"\fancypagestyle{empty}{",
        r"  \fancyhf{}",
        r"  \renewcommand{\headrulewidth}{0pt}",
        r"}",

        r"\pagestyle{banniere}",

        # Redéfinir \cleardoublepage avec gestion des veuves/orphelines
        r"\makeatletter",
        r"\def\cleardoublepage{\clearpage\if@twoside \ifodd\c@page\else",
        r"\hbox{}\thispagestyle{empty}\newpage\if@twocolumn\hbox{}\newpage\fi\fi\fi}",

        # Améliorer la gestion des coupures de page
        r"\def\@textbottom{\vskip \z@ \@plus 1fil}",
        r"\let\@texttop\relax",
        r"\makeatother",

        # ESPACEMENT OPTIMISÉ
        r"\setstretch{1.35}",  # Légèrement réduit pour plus de texte par page

        # Redéfinir la taille normale avec microtypographie
        f"\\renewcommand{{\\normalsize}}{{\\fontsize{{{text_size}}}{{{float(text_size) * 1.2}}}\\selectfont}}",
        f"\\normalsize",

        # CONFIGURATION LETTRINE AMÉLIORÉE
        r"\setcounter{DefaultLines}{3}",
        r"\renewcommand{\LettrineFontHook}{\titlefont}",
        r"\renewcommand{\LettrineTextFont}{\normalfont\scshape}",
        r"\setlength{\DefaultFindent}{0.1em}",
        r"\setlength{\DefaultNindent}{0.5em}",

        # MÉTADONNÉES
        f"\\title{{{title}}}",
        f"\\author{{{author}}}",
        r"\date{}",

        r"\begin{document}",

        # PAGE DE TITRE
        r"\begin{titlepage}",
        r"\thispagestyle{empty}",
        r"BANNER_PLACEHOLDER",
        r"\begin{center}",
    ])

    # TITRE CONDITIONNEL SUR LA PAGE DE GARDE
    if use_script and title_font_key in ['euphoria_script', 'playfair_display']:
        config_lines.append(
            f"{{\\fontsize{{{int(title1_size) + 8}}}{{{int(title1_size) + 14}}}\\selectfont\\titlefont {title}}}\\\\[2cm]")
    else:
        config_lines.append(
            f"{{\\fontsize{{{int(title1_size) + 8}}}{{{int(title1_size) + 14}}}\\selectfont\\titlefont {title.upper()}}}\\\\[2cm]")

    config_lines.extend([
        r"{\fontsize{18}{22}\selectfont\textsc{" + author.upper() + r"}}",
        r"\end{center}",
        r"\vfill",
        r"\end{titlepage}",

        # PAGE BLANCHE
        r"\thispagestyle{empty}",
        r"\mbox{}",
        r"\cleardoublepage",
    ])

    return config_lines


def escape_latex(text):
    """Échapper les caractères spéciaux LaTeX"""
    special_chars = {
        '%': r'\%', '&': r'\&', '#': r'\#', '_': r'\_',
        '$': r'\$', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde', '^': r'\textasciicircum'
    }
    for char, latex_char in special_chars.items():
        text = text.replace(char, latex_char)
    return text


def clean_text(text):
    """Nettoie et normalise le texte"""
    text = unicodedata.normalize('NFKC', text)
    text = ''.join(c for c in text if c.isprintable())
    return text.strip()


def clean_typography_advanced(text):
    import re

    text = re.sub(r'  +', ' ', text)
    text = text.strip()

    if not text:
        return text

    # Points de suspension
    text = text.replace('...', '…')

    # Ponctuation française avec espaces insécables NORMALES (pas fines)
    text = text.replace(' !', '~!')
    text = text.replace(' ?', '~?')
    text = text.replace(' :', '~:')
    text = text.replace(' ;', '~;')
    text = text.replace('« ', '«~')
    text = text.replace(' »', '~»')

    # Tirets cadratins pour les dialogues
    text = re.sub(r'^-\s+', '—~', text, flags=re.MULTILINE)
    text = re.sub(r'\s+-\s+', ' —~', text)

    # Éviter les coupures sur des mots courts
    text = re.sub(r' (à|de|du|le|la|les|un|une|ce|et|ou|si|se|me|te|ne|en|on|il|je|tu) ', r'~\1~', text)

    # Titres de civilité
    text = re.sub(r'(M\.|Mme|Mlle|Dr|Pr)\s+', r'\1~', text)

    return text


def is_narrator_line(text, is_after_chapter=False):
    """Détecte si une ligne est un narrateur - VERSION CORRIGÉE"""
    if not text or len(text.strip()) == 0:
        return False

    text = text.strip()

    # Format classique [Narrateur]
    if text.startswith('[') and text.endswith(']') and len(text) <= 50:
        return True

    # Narrateur sans crochets juste après un chapitre
    if is_after_chapter:
        if (len(text) <= 30 and
                not text.endswith(('.', '!', '?', ':', ';')) and
                text[0].isupper() and
                len(text.split()) <= 3):
            return True

    return False


def is_epigraph_text(para):
    """Détecte si un paragraphe est une épigraphe (texte en italique avant le premier chapitre)"""
    try:
        # Vérifier si tout le paragraphe est en italique
        if not para.runs:
            return False

        text = para.text.strip()
        if not text:
            return False

        # Vérifier si tous les runs sont en italique
        all_italic = True
        for run in para.runs:
            if run.text.strip():  # Ignorer les runs vides
                try:
                    if not (run.italic is True or
                            (hasattr(run, 'font') and run.font and run.font.italic is True) or
                            (hasattr(run, '_element') and (
                                    '<w:i/>' in run._element.xml or '<w:i ' in run._element.xml))):
                        all_italic = False
                        break
                except:
                    all_italic = False
                    break

        return all_italic
    except:
        return False


def is_center_text(para):
    """Détecte si un paragraphe est centré (pour les épigraphes centrées)"""
    try:
        return para.alignment == WD_ALIGN_PARAGRAPH.CENTER
    except:
        return False

    """Détecte si une ligne est un narrateur"""
    if not text or len(text.strip()) == 0:
        return False

    text = text.strip()

    # Format classique [Narrateur]
    if text.startswith('[') and text.endswith(']') and len(text) <= 30:
        return True

    # Narrateur sans crochets juste après un chapitre
    if is_after_chapter:
        if (len(text) <= 25 and
                not text.endswith(('.', '!', '?', ':', ';')) and
                text[0].isupper() and
                len(text.split()) <= 2):
            return True

    return False


# REMPLACER la fonction process_markdown_footnotes par cette version qui cherche PARTOUT :

def process_markdown_footnotes(doc):
    """
    Système de notes adapté au format [^1]: NOTE1: texte - VERSION DEBUG
    """
    footnotes_dict = {}

    logger.info("🔍 RECHERCHE DES NOTES au format [^X]: NOTEX: texte...")

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        # Afficher TOUS les paragraphes pour debug
        if text:
            logger.info(f"Paragraphe {i}: '{text}'")

        # Pattern pour détecter [^1]: NOTE1: texte
        markdown_footnote_pattern = r'^\[\^(\d+)\]:\s*NOTE(\d+):\s*(.+)$'
        match = re.match(markdown_footnote_pattern, text)

        if match:
            ref_num = match.group(1)
            note_num = match.group(2)
            note_text = match.group(3).strip()
            footnotes_dict[note_num] = note_text
            logger.info(f"✅ Note Markdown trouvée: [^{ref_num}] -> NOTE{note_num} = '{note_text}'")

        # Aussi chercher le format simple NOTE1: texte (sans [^])
        simple_pattern = r'^NOTE(\d+):\s*(.+)$'
        simple_match = re.match(simple_pattern, text)

        if simple_match:
            note_num = simple_match.group(1)
            note_text = simple_match.group(2).strip()
            footnotes_dict[note_num] = note_text
            logger.info(f"✅ Note simple trouvée: NOTE{note_num} = '{note_text}'")

    logger.info(f"📋 RÉSULTAT FINAL: {len(footnotes_dict)} notes trouvées")

    # Debug : afficher le dictionnaire final
    for num, text in footnotes_dict.items():
        logger.info(f"  📝 DANS LE DICT -> NOTE{num}: {text}")

    return footnotes_dict


def convert_format(para):
    """Convertit le formatage Word vers LaTeX avec un système de notes simple"""
    formatted_text = ""

    # Vérifier si c'est une définition de note simple : NOTE1: texte
    text_content = para.text.strip()
    simple_footnote_pattern = r'^NOTE(\d+):\s*(.+)$'
    if re.match(simple_footnote_pattern, text_content):
        # C'est une définition de note, on l'ignore dans le texte principal
        logger.info(f"📝 Définition de note ignorée: {text_content}")
        return ""

    # Formatage du texte normal
    for run in para.runs:
        run_text = escape_latex(run.text)
        is_bold = False
        is_italic = False

        # Détection du gras
        try:
            if run.bold is True:
                is_bold = True
            if hasattr(run, 'font') and run.font and run.font.bold is True:
                is_bold = True
            if hasattr(run, '_element'):
                xml_str = run._element.xml
                if '<w:b/>' in xml_str or '<w:b ' in xml_str:
                    is_bold = True
        except:
            pass

        # Détection de l'italique
        try:
            if run.italic is True:
                is_italic = True
            if hasattr(run, 'font') and run.font and run.font.italic is True:
                is_italic = True
            if hasattr(run, '_element'):
                xml_str = run._element.xml
                if '<w:i/>' in xml_str or '<w:i ' in xml_str:
                    is_italic = True
        except:
            pass

        # Application du formatage
        if is_bold and is_italic:
            formatted_text += f"\\textbf{{\\textit{{{run_text}}}}}"
        elif is_bold:
            formatted_text += f"\\begingroup\\bfseries {run_text}\\endgroup\\ "
        elif is_italic:
            formatted_text += f"\\textit{{{run_text}}}"
        else:
            formatted_text += run_text

    # SYSTÈME DE NOTES SIMPLE : remplacer (NOTE1), (NOTE2), etc.
    note_pattern = r'\(NOTE(\d+)\)'
    note_matches = list(re.finditer(note_pattern, formatted_text))

    if note_matches:
        logger.info(f"🔍 Notes simples détectées: {len(note_matches)}")

        for match in reversed(note_matches):
            note_num = match.group(1)

            # Chercher la définition dans le dictionnaire global
            if hasattr(convert_format, 'footnotes_dict') and note_num in convert_format.footnotes_dict:
                footnote_text = convert_format.footnotes_dict[note_num]
                footnote_latex = escape_latex(footnote_text)
                footnote_cmd = f"\\footnote{{{footnote_latex}}}"
                formatted_text = formatted_text[:match.start()] + footnote_cmd + formatted_text[match.end():]
                logger.info(f"✅ Note simple convertie: (NOTE{note_num}) -> \\footnote{{{footnote_text}}}")
            else:
                footnote_cmd = f"\\footnote{{texte à définir}}"
                formatted_text = formatted_text[:match.start()] + footnote_cmd + formatted_text[match.end():]
                logger.info(f"⚠️ Note (NOTE{note_num}) sans définition")

    # Gestion de TOUS les alignements
    is_right = is_right_aligned(para)
    is_center = is_center_aligned(para)
    start_cmd, end_cmd = get_latex_alignment_command(is_right, is_center)

    if start_cmd and end_cmd:
        return f"{start_cmd}\n{formatted_text}\n{end_cmd}"
    else:
        return formatted_text


def convert_format_html_with_alignment(para):
    """Convertit le formatage Word vers HTML avec gestion de l'alignement à droite et des notes de bas de page pour EPUB"""
    formatted_text = ""
    all_footnotes = []

    for run in para.runs:
        run_text = run.text
        is_bold = False
        is_italic = False

        # Extraire les notes de bas de page de ce run
        run_footnotes = []
        if hasattr(run, '_element'):
            try:
                # Chercher les références de notes dans le XML du run
                footnote_refs = run._element.xpath('.//w:footnoteReference',
                                                   namespaces={
                                                       'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})

                for ref in footnote_refs:
                    footnote_id = ref.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                    if footnote_id:
                        # Extraire le texte de la note de bas de page
                        footnote_text = get_footnote_text(para.part, footnote_id)
                        if footnote_text:
                            run_footnotes.append(footnote_text)
                            all_footnotes.append(footnote_text)
            except Exception as e:
                logger.debug(f"Erreur lors de l'extraction des notes: {e}")

        try:
            if run.bold is True:
                is_bold = True
            if run.italic is True:
                is_italic = True
            if hasattr(run, 'font') and run.font:
                if run.font.bold is True:
                    is_bold = True
                if run.font.italic is True:
                    is_italic = True
        except:
            pass

        # Application du formatage HTML
        if is_bold and is_italic:
            formatted_text += f"<strong><em>{run_text}</em></strong>"
        elif is_bold:
            formatted_text += f"<strong>{run_text}</strong>"
        elif is_italic:
            formatted_text += f"<em>{run_text}</em>"
        else:
            formatted_text += run_text

        # Ajouter les notes de bas de page comme marqueurs temporaires
        for i, footnote in enumerate(run_footnotes):
            formatted_text += f"[FOOTNOTE_{len(all_footnotes)}]"

    # Traitement des notes manuelles au format [1], [2], etc.
    manual_footnote_pattern = r'\[(\d+)\]'
    manual_matches = list(re.finditer(manual_footnote_pattern, formatted_text))

    # Ajouter les notes manuelles à la liste
    for match in manual_matches:
        footnote_num = match.group(1)
        all_footnotes.append(f"Note {footnote_num} - À définir")

        # Détection de TOUS les alignements
    is_right = is_right_aligned(para)
    is_center = is_center_aligned(para)
    style = get_html_alignment_style(is_right, is_center)

    return formatted_text, style, all_footnotes


def get_footnote_text_complete(document_part, footnote_id):
    """
    Fonction complète pour extraire les notes de bas de page
    """
    logger.debug(f"🔍 Recherche note ID: {footnote_id}")

    try:
        # Méthode 1 : Via document principal
        if hasattr(document_part, 'document'):
            doc = document_part.document

            # Chercher dans footnotes_part
            if hasattr(doc, 'part') and hasattr(doc.part, 'rels'):
                for rel_id, rel in doc.part.rels.items():
                    if 'footnotes' in str(rel.target_ref).lower():
                        try:
                            footnotes_part = rel.target_part
                            if hasattr(footnotes_part, 'footnotes'):
                                for footnote in footnotes_part.footnotes:
                                    if str(footnote.footnote_id) == str(footnote_id):
                                        text = ""
                                        for para in footnote.paragraphs:
                                            text += para.text + " "
                                        result = text.strip()
                                        if result:
                                            logger.info(f"✅ Note trouvée (méthode 1): {result[:50]}...")
                                            return result
                        except Exception as e:
                            logger.debug(f"Erreur méthode 1: {e}")

        # Méthode 2 : Via footnotes_part direct
        if hasattr(document_part, 'footnotes_part') and document_part.footnotes_part:
            try:
                for footnote in document_part.footnotes_part.footnotes:
                    if str(footnote.footnote_id) == str(footnote_id):
                        text = ""
                        for para in footnote.paragraphs:
                            text += para.text + " "
                        result = text.strip()
                        if result:
                            logger.info(f"✅ Note trouvée (méthode 2): {result[:50]}...")
                            return result
            except Exception as e:
                logger.debug(f"Erreur méthode 2: {e}")

        # Méthode 3 : Via document.footnotes
        try:
            if hasattr(document_part, 'document') and hasattr(document_part.document, 'footnotes'):
                for footnote in document_part.document.footnotes:
                    if str(footnote.footnote_id) == str(footnote_id):
                        text = ""
                        for para in footnote.paragraphs:
                            text += para.text + " "
                        result = text.strip()
                        if result:
                            logger.info(f"✅ Note trouvée (méthode 3): {result[:50]}...")
                            return result
        except Exception as e:
            logger.debug(f"Erreur méthode 3: {e}")

        # Méthode 4 : Recherche exhaustive dans toutes les parties
        try:
            root_part = document_part
            while hasattr(root_part, 'part'):
                root_part = root_part.part

            if hasattr(root_part, 'package'):
                package = root_part.package
                for part in package.parts:
                    if 'footnotes' in str(part).lower():
                        try:
                            if hasattr(part, 'footnotes'):
                                for footnote in part.footnotes:
                                    if str(footnote.footnote_id) == str(footnote_id):
                                        text = ""
                                        for para in footnote.paragraphs:
                                            text += para.text + " "
                                        result = text.strip()
                                        if result:
                                            logger.info(f"✅ Note trouvée (méthode 4): {result[:50]}...")
                                            return result
                        except Exception as e:
                            logger.debug(f"Erreur dans partie {part}: {e}")
        except Exception as e:
            logger.debug(f"Erreur méthode 4: {e}")

    except Exception as e:
        logger.warning(f"Erreur générale extraction note {footnote_id}: {e}")

    logger.warning(f"❌ Note {footnote_id} non trouvée - retour fallback")
    return f"Note {footnote_id} - texte non trouvé"


# AJOUT D'UNE FONCTION DE DEBUG :

def debug_document_structure(doc):
    """Debug pour analyser la structure du document"""
    logger.info("🔍 ANALYSE DE LA STRUCTURE DU DOCUMENT:")

    try:
        if hasattr(doc, 'part'):
            logger.info(f"Document part: {doc.part}")
            if hasattr(doc.part, 'rels'):
                logger.info(f"Relations trouvées: {len(doc.part.rels)}")
                for rel_id, rel in doc.part.rels.items():
                    logger.info(f"  - {rel_id}: {rel.target_ref}")
    except Exception as e:
        logger.info(f"Erreur analyse structure: {e}")

    # Rechercher les footnotes
    try:
        if hasattr(doc, 'footnotes'):
            logger.info(f"Document.footnotes: {len(doc.footnotes)} notes trouvées")
    except:
        logger.info("Pas de doc.footnotes")

    # Compter les références de notes dans le texte
    footnote_refs_count = 0
    for para in doc.paragraphs:
        if hasattr(para, '_element'):
            try:
                refs = para._element.xpath('.//w:footnoteReference',
                                           namespaces={
                                               'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
                footnote_refs_count += len(refs)
            except:
                pass

    logger.info(f"📝 Références de notes trouvées dans le texte: {footnote_refs_count}")


def process_footnotes_for_latex(text, footnotes):
    """
    Remplace les marqueurs de notes par des commandes LaTeX
    """
    for i, footnote in enumerate(footnotes, 1):
        marker = f"[FOOTNOTE_{i}]"
        if marker in text:
            footnote_latex = escape_latex(footnote)
            text = text.replace(marker, f"\\footnote{{{footnote_latex}}}")

    # Traitement des références manuelles [1], [2], etc.
    manual_footnote_pattern = r'\[(\d+)\]'
    manual_matches = list(re.finditer(manual_footnote_pattern, text))

    for match in reversed(manual_matches):
        footnote_num = match.group(1)
        footnote_placeholder = f"\\footnote{{Note {footnote_num} - À définir}}"
        text = text[:match.start()] + footnote_placeholder + text[match.end():]

    return text


def process_footnotes_for_html(text, footnotes, chapter_footnote_counter):
    """
    Remplace les marqueurs de notes par des liens HTML avec notes en fin de chapitre
    """
    footnote_list = ""
    current_footnote_num = chapter_footnote_counter[0]

    for i, footnote in enumerate(footnotes, 1):
        marker = f"[FOOTNOTE_{i}]"
        if marker in text:
            current_footnote_num += 1
            # Créer un lien vers la note
            link = f'<sup><a href="#footnote_{current_footnote_num}" id="footnote_ref_{current_footnote_num}">{current_footnote_num}</a></sup>'
            text = text.replace(marker, link)

            # Ajouter la note à la liste des notes
            footnote_list += f'<div id="footnote_{current_footnote_num}" style="margin-bottom: 0.5em; font-size: 0.9em;"><sup>{current_footnote_num}</sup> {footnote} <a href="#footnote_ref_{current_footnote_num}">↑</a></div>'

    # Traitement des références manuelles [1], [2], etc.
    manual_footnote_pattern = r'\[(\d+)\]'
    manual_matches = list(re.finditer(manual_footnote_pattern, text))

    for match in reversed(manual_matches):
        footnote_num = match.group(1)
        current_footnote_num += 1
        link = f'<sup><a href="#footnote_{current_footnote_num}" id="footnote_ref_{current_footnote_num}">{current_footnote_num}</a></sup>'
        footnote_content = f"Note {footnote_num} - À définir"
        footnote_list += f'<div id="footnote_{current_footnote_num}" style="margin-bottom: 0.5em; font-size: 0.9em;"><sup>{current_footnote_num}</sup> {footnote_content} <a href="#footnote_ref_{current_footnote_num}">↑</a></div>'
        text = text[:match.start()] + link + text[match.end():]

    # Mettre à jour le compteur
    chapter_footnote_counter[0] = current_footnote_num

    footnote_section = ""
    if footnote_list:
        footnote_section = f'<div style="border-top: 1px solid #ccc; margin-top: 2em; padding-top: 1em;"><h4>Notes</h4>{footnote_list}</div>'

    return text, footnote_section


def detect_manual_footnotes(text):
    """
    Détecte les notes de bas de page manuelles dans le format [1], [2], etc.
    et les convertit en format approprié
    """
    footnotes = []

    # Pattern pour détecter les références manuelles [1], [2], etc.
    pattern = r'\[(\d+)\]'
    matches = re.finditer(pattern, text)

    for match in matches:
        footnote_num = match.group(1)
        footnotes.append(f"Note {footnote_num} - À définir")

    return text, footnotes


# =====================================
# 📸 FONCTIONS POUR SUPPORT DES IMAGES
# =====================================
# Ajoutez tout ce code AVANT la ligne @app.route('/', methods=['GET', 'POST'])

def extract_images_from_docx(docx_path, upload_folder):
    """Extrait toutes les images d'un fichier .docx et les sauvegarde"""
    images_info = {}

    try:
        logger.info(f"🔍 Extraction des images de : {docx_path}")

        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            # Lister tous les fichiers dans l'archive
            for file_info in zip_ref.filelist:
                # Chercher les images dans word/media/
                if file_info.filename.startswith('word/media/'):
                    # Extraire le nom du fichier image
                    image_name = os.path.basename(file_info.filename)

                    # Extensions d'images supportées
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
                    if any(image_name.lower().endswith(ext) for ext in valid_extensions):
                        # Extraire l'image
                        image_data = zip_ref.read(file_info.filename)

                        logger.info(f"📸 Image trouvée : {image_name} ({len(image_data)} bytes)")

                        # Sauvegarder dans le dossier uploads
                        image_path = os.path.join(upload_folder, image_name)
                        with open(image_path, 'wb') as img_file:
                            img_file.write(image_data)

                        # Stocker les informations de l'image
                        images_info[file_info.filename] = {
                            'filename': image_name,
                            'path': image_path,
                            'data': image_data  # IMPORTANT : stocker les données binaires
                        }

                        logger.info(f"💾 Image sauvegardée : {image_name}")

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des images : {e}")

    logger.info(f"📋 Total images extraites : {len(images_info)}")
    return images_info


def extract_images_from_paragraph(para, images_info):
    """Extrait les références d'images d'un paragraphe Word - VERSION CORRIGÉE"""
    images_in_para = []

    # Méthode 1: Vérifier le XML du paragraphe directement
    try:
        para_xml = para._p.xml
        if 'graphicData' in para_xml:
            logger.info(f"🖼️ GRAPHIQUE DÉTECTÉ dans paragraphe: '{para.text[:50]}...'")

            # Chercher tous les embed IDs dans le XML
            import re
            embed_matches = re.findall(r'r:embed="([^"]*)"', para_xml)

            for embed_id in embed_matches:
                logger.info(f"   📸 Embed ID trouvé: {embed_id}")

                try:
                    if embed_id in para.part.rels:
                        rel = para.part.rels[embed_id]
                        image_path_in_docx = rel.target_ref
                        full_image_path = f"word/{image_path_in_docx}"

                        logger.info(f"   🔍 Chemin image: {full_image_path}")

                        if full_image_path in images_info:
                            images_in_para.append(images_info[full_image_path])
                            logger.info(f"   ✅ Image trouvée: {images_info[full_image_path]['filename']}")
                        else:
                            logger.warning(f"   ❌ Image non trouvée dans images_info")
                            logger.info(f"   📋 Images disponibles: {list(images_info.keys())}")

                except Exception as e:
                    logger.warning(f"   ⚠️ Erreur traitement embed {embed_id}: {e}")

    except Exception as e:
        logger.debug(f"Erreur XML paragraph: {e}")

    # Méthode 2: Parcourir les runs (ancienne méthode en backup)
    try:
        for run in para.runs:
            if hasattr(run, '_element'):
                drawings = run._element.xpath('.//a:blip',
                                              namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})

                for drawing in drawings:
                    embed_id = drawing.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if embed_id and embed_id in para.part.rels:
                        rel = para.part.rels[embed_id]
                        image_path_in_docx = rel.target_ref
                        full_image_path = f"word/{image_path_in_docx}"

                        if full_image_path in images_info and images_info[full_image_path] not in images_in_para:
                            images_in_para.append(images_info[full_image_path])
                            logger.info(f"🖼️ Image trouvée (méthode 2): {images_info[full_image_path]['filename']}")

    except Exception as e:
        logger.debug(f"Erreur méthode 2: {e}")

    logger.info(f"🎯 TOTAL images dans ce paragraphe: {len(images_in_para)}")
    return images_in_para


def copy_images_to_upload_folder(images_info, upload_folder):
    """S'assure que toutes les images sont copiées dans le dossier de compilation LaTeX"""
    import shutil
    for image_path, image_info in images_info.items():
        source_path = image_info['path']
        dest_path = os.path.join(upload_folder, image_info['filename'])

        if not os.path.exists(dest_path):
            try:
                shutil.copy2(source_path, dest_path)
                logger.info(f"📸 Image copiée pour LaTeX: {image_info['filename']}")
            except Exception as e:
                logger.error(f"Erreur copie image {image_info['filename']}: {e}")


def convert_format_with_images(para, images_info):
    """Convertit le formatage Word vers LaTeX avec support des images - VERSION CORRIGÉE"""
    formatted_text = ""

    # Vérifier si c'est une définition de note simple : NOTE1: texte
    text_content = para.text.strip()
    simple_footnote_pattern = r'^NOTE(\d+):\s*(.+)$'
    if re.match(simple_footnote_pattern, text_content):
        logger.info(f"📝 Définition de note ignorée: {text_content}")
        return ""

    # CORRECTION: Extraire les images AVANT le traitement du texte
    images_in_para = extract_images_from_paragraph(para, images_info)

    # Si le paragraphe contient des images, les ajouter en premier
    if images_in_para:
        logger.info(f"🖼️ AJOUT IMMÉDIAT DE {len(images_in_para)} IMAGES")
        for image_info in images_in_para:
            image_latex = f"""
\\begin{{center}}
\\includegraphics[width=0.6\\textwidth,keepaspectratio]{{{image_info['filename']}}}
\\end{{center}}
\\vspace{{0.5cm}}
"""
            formatted_text += image_latex
            logger.info(f"✅ IMAGE AJOUTÉE AU LATEX: {image_info['filename']}")

    # Formatage du texte normal (comme la fonction convert_format originale)
    text_part = ""
    for run in para.runs:
        run_text = escape_latex(run.text)
        is_bold = False
        is_italic = False

        # Détection du gras
        try:
            if run.bold is True:
                is_bold = True
            if hasattr(run, 'font') and run.font and run.font.bold is True:
                is_bold = True
            if hasattr(run, '_element'):
                xml_str = run._element.xml
                if '<w:b/>' in xml_str or '<w:b ' in xml_str:
                    is_bold = True
        except:
            pass

        # Détection de l'italique
        try:
            if run.italic is True:
                is_italic = True
            if hasattr(run, 'font') and run.font and run.font.italic is True:
                is_italic = True
            if hasattr(run, '_element'):
                xml_str = run._element.xml
                if '<w:i/>' in xml_str or '<w:i ' in xml_str:
                    is_italic = True
        except:
            pass

        # Application du formatage
        if is_bold and is_italic:
            text_part += f"\\textbf{{\\textit{{{run_text}}}}}"
        elif is_bold:
            text_part += f"\\begingroup\\bfseries {run_text}\\endgroup\\ "
        elif is_italic:
            text_part += f"\\textit{{{run_text}}}"
        else:
            text_part += run_text

    # SYSTÈME DE NOTES SIMPLE : remplacer (NOTE1), (NOTE2), etc.
    note_pattern = r'\(NOTE(\d+)\)'
    note_matches = list(re.finditer(note_pattern, text_part))

    if note_matches:
        logger.info(f"🔍 Notes simples détectées: {len(note_matches)}")

        for match in reversed(note_matches):
            note_num = match.group(1)

            # Chercher la définition dans le dictionnaire global
            if hasattr(convert_format_with_images,
                       'footnotes_dict') and note_num in convert_format_with_images.footnotes_dict:
                footnote_text = convert_format_with_images.footnotes_dict[note_num]
                footnote_latex = escape_latex(footnote_text)
                footnote_cmd = f"\\footnote{{{footnote_latex}}}"
                text_part = text_part[:match.start()] + footnote_cmd + text_part[match.end():]
                logger.info(f"✅ Note simple convertie: (NOTE{note_num}) -> \\footnote{{{footnote_text}}}")
            else:
                footnote_cmd = f"\\footnote{{texte à définir}}"
                text_part = text_part[:match.start()] + footnote_cmd + text_part[match.end():]
                logger.info(f"⚠️ Note (NOTE{note_num}) sans définition")

    # Ajouter le texte après les images
    formatted_text += text_part

    # Gestion de TOUS les alignements
    is_right = is_right_aligned(para)
    is_center = is_center_aligned(para)
    start_cmd, end_cmd = get_latex_alignment_command(is_right, is_center)

    if start_cmd and end_cmd:
        return f"{start_cmd}\n{formatted_text}\n{end_cmd}"
    else:
        return formatted_text


# CORRECTION 1: Bug des images dans EPUB
# Remplacez la fonction convert_format_html_with_alignment_and_images par cette version corrigée :

def convert_format_html_with_alignment_and_images(para, images_info):
    """Version simple - alignement corrigé"""
    formatted_text = ""
    all_footnotes = []

    # Images
    images_in_para = extract_images_from_paragraph(para, images_info)
    if images_in_para:
        for image_info in images_in_para:
            image_html = f'<div style="text-align: center; margin: 1em 0;"><img src="images/{image_info["filename"]}" style="max-width: 60%; height: auto;" alt="Image"/></div>'
            formatted_text += image_html

    # Texte
    for run in para.runs:
        if run.bold and run.italic:
            formatted_text += f"<strong><em>{run.text}</em></strong>"
        elif run.bold:
            formatted_text += f"<strong>{run.text}</strong>"
        elif run.italic:
            formatted_text += f"<em>{run.text}</em>"
        else:
            formatted_text += run.text

    # Alignement simple
    if is_center_aligned(para):
        style = 'text-align: center;'
    elif is_right_aligned(para):
        style = 'text-align: right;'
    else:
        style = 'text-align: justify;'
    # À la fin de la fonction, avant le return
    if images_in_para:
        logger.info(f"🔥 RETOUR AVEC IMAGES: {formatted_text[:100]}...")

    return formatted_text, style, all_footnotes


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        temp_files = []
        try:
            logger.info("Début de génération PDF avec LuaLaTeX")

            # Validation du fichier
            if 'file' not in request.files:
                return "Erreur : aucun fichier fourni.", 400
            file = request.files['file']
            if file.filename == '':
                return "Erreur : fichier non sélectionné.", 400
            if not file.filename.endswith('.docx'):
                return "Erreur : format non supporté.", 400

            # Sauvegarde du fichier
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            temp_files.append(filepath)

            # Gestion de la bannière
            banner_filename = None
            if 'banner' in request.files:
                banner_file = request.files['banner']
                if banner_file and banner_file.filename:
                    if not validate_image_file(banner_file):
                        return "Erreur : format de bannière non supporté.", 400

                    banner_filename = secure_filename(banner_file.filename)
                    banner_path = os.path.join(UPLOAD_FOLDER, banner_filename)
                    banner_file.save(banner_path)
                    temp_files.append(banner_path)

            # Traitement du document
            doc = Document(filepath)

            # CORRECTION: Extraction et copie des images
            images_info = extract_images_from_docx(filepath, UPLOAD_FOLDER)
            copy_images_to_upload_folder(images_info, UPLOAD_FOLDER)
            temp_files.extend([info['path'] for info in images_info.values()])
            logger.info(f"📸 Images extraites pour PDF: {len(images_info)}")

            # Extraire les notes de bas de page Markdown
            markdown_footnotes = process_markdown_footnotes(doc)
            convert_format_with_images.footnotes_dict = markdown_footnotes

            debug_document_structure(doc)
            title = escape_latex(clean_text(request.form.get('title', 'Titre du roman')))
            author = escape_latex(clean_text(request.form.get('author', "Nom de l'auteur")))

            # Récupérer les options
            use_lettrine = request.form.get('use_lettrine') == 'on'
            use_script = request.form.get('use_script_font') == 'on'
            text_font = request.form.get('text_font', 'libre_caslon')
            title_font = request.form.get('title_font', 'libre_caslon')
            text_size = request.form.get('text_size', '12')
            title1_size = request.form.get('title1_size', '32')
            title2_size = request.form.get('title2_size', '26')
            title3_size = request.form.get('title3_size', '22')

            base_filename = os.path.splitext(filename)[0]
            tex_path = os.path.join(UPLOAD_FOLDER, base_filename + ".tex")
            pdf_path = os.path.join(UPLOAD_FOLDER, base_filename + ".pdf")
            temp_files.extend([tex_path, pdf_path])

            # Génération du LaTeX avec les polices sélectionnées
            latex_lines = get_luatex_config(title, author, text_font, title_font, text_size,
                                            title1_size, title2_size, title3_size, use_script)

            # Gestion de la bannière sur la page de garde
            for i, line in enumerate(latex_lines):
                if line == "BANNER_PLACEHOLDER":
                    if banner_filename:
                        latex_lines[
                            i] = r"\vspace*{-2.5cm}\hspace*{-3cm}\includegraphics[width=\dimexpr\paperwidth+6cm\relax,keepaspectratio]{" + banner_filename + r"}\vspace{0.5cm}"
                    else:
                        latex_lines[i] = r"\vspace*{4cm}"
                    break

            # CORRECTION: Traitement du contenu - boucle corrigée
            first_paragraph = True
            collecting_texto = False
            texto_nom = ""
            texto_contenu = []
            texto_type = ""
            just_after_chapter = False
            first_chapter_found = False
            epigraph_content = []

            # Parcourir TOUS les paragraphes
            for para in doc.paragraphs:
                text = clean_text(para.text)

                # CORRECTION: Ne pas ignorer les paragraphes qui contiennent des images même sans texte
                images_in_para = extract_images_from_paragraph(para, images_info)

                # Ignorer seulement les paragraphes complètement vides (pas de texte ET pas d'images)
                if not text and not images_in_para and not collecting_texto:
                    continue

                style = para.style.name if para.style else ''

                # CORRECTION: Utiliser la fonction corrigée pour traiter les images
                safe_text = convert_format_with_images(para, images_info)

                # NOUVEAU : Gestion des épigraphes avant le premier chapitre
                if not first_chapter_found and not collecting_texto:
                    # Vérifier si c'est un titre de chapitre
                    if (style.startswith('Heading 1') or style.startswith('Titre 1') or
                            style.startswith('Heading 2') or style.startswith('Titre 2')):

                        # On a trouvé le premier chapitre - traiter les épigraphes accumulées
                        if epigraph_content:
                            logger.info(f"📝 Traitement de {len(epigraph_content)} épigraphes avant le premier chapitre")
                            latex_lines.append(r"\cleardoublepage")
                            latex_lines.append(r"\thispagestyle{empty}")
                            latex_lines.append(r"\vspace*{\fill}")

                            for epigraph in epigraph_content:
                                latex_lines.append(epigraph)
                                latex_lines.append("")

                            latex_lines.append(r"\vspace*{\fill}")
                            latex_lines.append(r"\cleardoublepage")
                            epigraph_content = []

                        first_chapter_found = True

                    # Si pas encore de chapitre trouvé, vérifier si c'est une épigraphe
                    elif (is_epigraph_text(para) or is_center_text(para)) and (text or images_in_para):
                        logger.info(f"📖 Épigraphe détectée: '{text[:50] if text else 'Image'}...'")

                        if text:
                            if is_center_text(para):
                                epigraph_latex = f"{{\\centering\\textit{{{escape_latex(text)}}}\\par}}"
                            else:
                                epigraph_latex = f"{{\\raggedleft\\textit{{{escape_latex(text)}}}\\par}}"
                            epigraph_content.append(epigraph_latex)

                        # Ajouter les images d'épigraphe
                        if images_in_para:
                            for image_info in images_in_para:
                                image_latex = f"""\\begin{{center}}
\\includegraphics[width=0.4\\textwidth,keepaspectratio]{{{image_info['filename']}}}
\\end{{center}}
\\vspace{{0.5cm}}"""
                                epigraph_content.append(image_latex)
                        continue

                    # Si c'est un texte en italique, traiter comme épigraphe
                    elif text and not style.startswith('Heading'):
                        if safe_text and "\\textit{" in safe_text:
                            logger.info(f"📖 Épigraphe en italique détectée: '{text[:50]}...'")
                            epigraph_latex = f"{{\\raggedleft\\textit{{{escape_latex(text)}}}\\par}}"
                            epigraph_content.append(epigraph_latex)
                            continue
                        else:
                            logger.info(f"📄 Texte d'introduction ignoré: '{text[:30]}...'")
                            continue

                # Gestion des textos - début
                if text.startswith("##") and not collecting_texto:
                    if "##droite" in text and ":" in text:
                        texto_nom = text.split(":", 1)[1].strip()
                        texto_type = "right"
                    elif "##gauche" in text and ":" in text:
                        texto_nom = text.split(":", 1)[1].strip()
                        texto_type = "left"
                    else:
                        texto_nom = text[2:].strip()
                        texto_type = "left"

                    collecting_texto = True
                    texto_contenu = []
                    continue

                # Gestion des textos - fin
                if text.strip() == "##fin" and collecting_texto:
                    texte_final = "\\\\".join([escape_latex(p) for p in texto_contenu if p.strip()])
                    prenom_latex = escape_latex(texto_nom)

                    if texto_type == "right":
                        latex_lines.append(r"\begin{flushright}")
                        latex_lines.append(
                            r"\begin{tcolorbox}[colback=blue!10, colframe=blue!10, arc=6pt, boxrule=0pt, width=0.75\linewidth, left=8pt, right=8pt, top=8pt, bottom=8pt]")
                        latex_lines.append(r"\raggedleft")
                        latex_lines.append(
                            r"\textbf{\titlefont\fontsize{18}{20}\selectfont " + prenom_latex + r"}\\[0.3em]")
                        latex_lines.append(r"\fontsize{10}{12}\selectfont " + texte_final)
                        latex_lines.append(r"\end{tcolorbox}")
                        latex_lines.append(r"\end{flushright}")
                    else:
                        latex_lines.append(
                            r"\begin{tcolorbox}[colback=bubblegray, colframe=bubblegray, arc=6pt, boxrule=0pt, width=0.75\linewidth, left=8pt, right=8pt, top=8pt, bottom=8pt]")
                        latex_lines.append(
                            r"\textbf{\titlefont\fontsize{18}{20}\selectfont " + prenom_latex + r"}\\[0.3em]")
                        latex_lines.append(r"\fontsize{10}{12}\selectfont " + texte_final)
                        latex_lines.append(r"\end{tcolorbox}")

                    latex_lines.append("")
                    collecting_texto = False
                    texto_nom = ""
                    texto_contenu = []
                    texto_type = ""
                    continue

                # Collecter le contenu des textos
                if collecting_texto:
                    if not text.startswith("##"):
                        texto_contenu.append(para.text.strip())
                    continue

                # Gestion des TITRE 1 (Chapitres principaux)
                if style.startswith('Heading 1') or style.startswith('Titre 1'):
                    latex_lines.append(r"\cleardoublepage")
                    header_text = text.replace('~', ' ').replace('\\,', ' ')  # Utiliser 'text' au lieu de 'safe_text'
                    latex_lines.append(r"\markboth{" + escape_latex(header_text.upper()) + "}{" + escape_latex(
                        header_text.upper()) + "}")

                    if banner_filename:
                        latex_lines.append(r"\thispagestyle{chapitre}")
                        latex_lines.append(r"\vspace*{-4.5cm}")
                        latex_lines.append(r"\hspace*{-3cm}")
                        latex_lines.append(
                            r"\includegraphics[width=\dimexpr\paperwidth+6cm\relax,keepaspectratio]{" + banner_filename + r"}")
                        latex_lines.append(r"\vspace{-0.8cm}")
                        latex_lines.append(r"\begin{center}")
                        if use_script and title_font in ['euphoria_script', 'playfair_display']:
                            latex_lines.append(
                                f"{{\\fontsize{{{title1_size}}}{{{int(title1_size) + 4}}}\\selectfont\\titlefont {safe_text}}}")
                        else:
                            latex_lines.append(
                                f"{{\\fontsize{{{title1_size}}}{{{int(title1_size) + 4}}}\\selectfont\\titlefont {safe_text.upper()}}}")
                        latex_lines.append(r"\end{center}")
                        latex_lines.append(r"\vspace{0.3cm}")
                    else:
                        latex_lines.append(r"\thispagestyle{chapitre}")
                        latex_lines.append(r"\vspace*{0.5cm}")
                        latex_lines.append(r"\begin{center}")
                        if use_script and title_font in ['euphoria_script', 'playfair_display']:
                            latex_lines.append(
                                f"{{\\fontsize{{{int(title1_size) + 8}}}{{{int(title1_size) + 14}}}\\selectfont\\titlefont {safe_text}}}")
                        else:
                            latex_lines.append(
                                f"{{\\fontsize{{{title1_size}}}{{{int(title1_size) + 4}}}\\selectfont\\titlefont {safe_text.upper()}}}")
                        latex_lines.append(r"\end{center}")
                        latex_lines.append(r"\vspace{0.3cm}")

                    first_paragraph = True
                    just_after_chapter = True
                    continue

                # Gestion des TITRE 2 (Sous-titres)
                elif style.startswith('Heading 2') or style.startswith('Titre 2'):
                    latex_lines.append(r"\vspace{0.5cm}")
                    if use_script and title_font in ['euphoria_script', 'playfair_display']:
                        latex_lines.append(
                            f"{{\\centering\\fontsize{{{title2_size}}}{{30}}\\selectfont\\titlefont {escape_latex(text)}\\par}}")
                    else:
                        latex_lines.append(
                            f"{{\\centering\\fontsize{{{title2_size}}}{{30}}\\selectfont\\titlefont {escape_latex(text).upper()}\\par}}")
                    latex_lines.append(r"\vspace{0.3cm}")
                    first_paragraph = True
                    just_after_chapter = True
                    continue

                # Gestion des TITRE 3 (Sous-sous-titres)
                elif style.startswith('Heading 3') or style.startswith('Titre 3'):
                    latex_lines.append(r"\vspace{0.4cm}")
                    if use_script and title_font in ['euphoria_script', 'playfair_display']:
                        latex_lines.append(
                            f"{{\\centering\\fontsize{{{title3_size}}}{{{int(title3_size) + 2}}}\\selectfont\\titlefont {escape_latex(text)}\\par}}")
                    else:
                        latex_lines.append(
                            f"{{\\centering\\fontsize{{{title3_size}}}{{{int(title3_size) + 2}}}\\selectfont\\titlefont {escape_latex(text).upper()}\\par}}")
                    latex_lines.append(r"\vspace{0.2cm}")
                    first_paragraph = True
                    just_after_chapter = True
                    continue

                # Gestion des narrateurs
                if is_narrator_line(text, just_after_chapter):
                    narrator = escape_latex(text[1:-1] if text.startswith('[') and text.endswith(']') else text)

                    if just_after_chapter and banner_filename:
                        latex_lines.append(r"\vspace{0.5cm}")
                    elif just_after_chapter:
                        latex_lines.append(r"\vspace{0.8cm}")
                    else:
                        latex_lines.append(r"\vspace{1.2cm}")

                    latex_lines.append(r"\begin{center}")
                    latex_lines.append(r"{\fontsize{16}{18}\selectfont\textit{" + narrator + "}}")
                    latex_lines.append(r"\end{center}")
                    latex_lines.append(r"\vspace{0.8cm}")
                    just_after_chapter = False
                    continue

                # Gestion des paragraphes normaux avec lettrine optionnelle ET notes de bas de page
                if first_paragraph and len(safe_text) > 20 and use_lettrine:
                    if len(safe_text) >= 2 and safe_text[0].isalpha():
                        try:
                            first_char = escape_latex(safe_text[0])
                            words = safe_text.split()
                            if len(words) > 0:
                                first_word_rest = escape_latex(words[0][1:])
                                rest_of_text = escape_latex(' '.join(words[1:]))
                                latex_lines.append(
                                    f"\\lettrine[lines=3,loversize=0.15,lraise=0.1,findent=2pt,nindent=0pt]{{{first_char}}}{{{first_word_rest}}} {rest_of_text}")
                            else:
                                rest_text = escape_latex(safe_text[1:])
                                latex_lines.append(
                                    f"\\lettrine[lines=3,loversize=0.15,lraise=0.1,findent=2pt,nindent=0pt]{{{first_char}}}{{{rest_text}}}")
                        except Exception:
                            latex_lines.append(safe_text)
                    else:
                        latex_lines.append(safe_text)
                    first_paragraph = False
                elif first_paragraph and len(safe_text) > 20 and not use_lettrine:
                    latex_lines.append(r"\hspace{1.5em}" + safe_text)
                    first_paragraph = False
                else:
                    # CORRECTION: S'assurer que safe_text est ajouté même s'il ne contient que des images
                    if safe_text.strip() or images_in_para:
                        latex_lines.append(safe_text)

                just_after_chapter = False
                latex_lines.append("")

            # CORRECTION: Fermer le document LaTeX APRÈS la boucle
            latex_lines.append(r"\end{document}")

            # Écriture du fichier .tex
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write("\n".join(latex_lines))

            # COMPILATION AVEC LUALATEX
            lualatex_path = r"C:\Users\sabif\AppData\Local\Programs\MiKTeX\miktex\bin\x64\lualatex.exe"

            logger.info("Début compilation LuaLaTeX...")

            try:
                # Première compilation
                result = subprocess.run(
                    [lualatex_path, "-interaction=nonstopmode", "-file-line-error", base_filename + ".tex"],
                    cwd=UPLOAD_FOLDER,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                logger.info("Première compilation LuaLaTeX réussie")

                # Deuxième compilation
                result2 = subprocess.run(
                    [lualatex_path, "-interaction=nonstopmode", "-file-line-error", base_filename + ".tex"],
                    cwd=UPLOAD_FOLDER,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                logger.info("Deuxième compilation LuaLaTeX réussie")

            except subprocess.CalledProcessError as e:
                # Vérifier si le PDF a quand même été généré malgré les avertissements
                if os.path.exists(pdf_path):
                    logger.warning(f"PDF généré malgré les avertissements LaTeX (code {e.returncode})")
                else:
                    logger.error(f"Vraie erreur LaTeX - Code de retour: {e.returncode}")
                    return f"Erreur lors de la compilation PDF (LuaLaTeX - Code {e.returncode}).", 500

            return send_file(pdf_path, as_attachment=True, download_name=base_filename + ".pdf")

        except Exception as e:
            logger.error(f"Erreur lors de la génération PDF : {str(e)}")
            return f"Erreur lors de la génération PDF : {str(e)}", 500

    # Retourner le template pour les requêtes GET
    return render_template('index.html')

def debug_images_extraction(doc, images_info):
    """Debug pour comprendre pourquoi les images ne sont pas détectées"""
    logger.info("🔍 === DEBUG EXTRACTION IMAGES ===")
    logger.info(f"Images extraites du ZIP: {len(images_info)}")

    for path, info in images_info.items():
        logger.info(f"  📸 {path} -> {info['filename']}")

    # Compter les paragraphes avec graphicData
    graphic_paras = 0
    for i, para in enumerate(doc.paragraphs):
        try:
            if hasattr(para, '_p') and 'graphicData' in para._p.xml:
                graphic_paras += 1
                logger.info(f"  🖼️ Paragraphe {i} contient graphicData: '{para.text[:30]}...'")
        except:
            pass

    logger.info(f"📊 Total paragraphes avec graphicData: {graphic_paras}")
    logger.info("🔍 === FIN DEBUG IMAGES ===")
    
def generate_epub(file, title, author, banner_file, cover_file):
    """Génère un fichier EPUB à partir d'un document Word - VERSION COMPLÈTEMENT CORRIGÉE"""
    temp_files = []
    epub_path = None

    try:
        logger.info(f"Début de génération EPUB : {title} par {author}")

        # Sauvegarder le fichier temporairement
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        temp_files.append(filepath)

        # Charger le document Word
        doc = Document(filepath)

        # Extraire les images du document Word
        images_info = extract_images_from_docx(filepath, UPLOAD_FOLDER)
        temp_files.extend([info['path'] for info in images_info.values()])
        logger.info(f"📸 Images extraites pour EPUB: {len(images_info)}")

        # Créer le livre EPUB
        book = epub.EpubBook()
        book.set_identifier('id123456')
        book.set_title(title)
        book.set_language('fr')
        book.add_author(author)

        if images_info:
            logger.info(f"🔧 FORÇAGE IMMÉDIAT: Ajout de {len(images_info)} images à l'EPUB")
            images_added = add_images_to_epub(book, images_info)
            logger.info(f"📸 RÉSULTAT: {images_added} images ajoutées immédiatement")
        else:
            logger.info("⚠️ Aucune image trouvée dans le document")

        # Gestion de la couverture
        if cover_file and cover_file.filename:
            if validate_image_file(cover_file):
                cover_filename = secure_filename(cover_file.filename)
                cover_path = os.path.join(UPLOAD_FOLDER, cover_filename)
                cover_file.save(cover_path)
                temp_files.append(cover_path)

                with open(cover_path, 'rb') as f:
                    book.set_cover("cover.jpg", f.read())
                    logger.info("Couverture ajoutée à l'EPUB")

        # Gestion de la bannière
        banner_html = ""
        if banner_file and banner_file.filename:
            if validate_image_file(banner_file):
                banner_filename = secure_filename(banner_file.filename)
                banner_path = os.path.join(UPLOAD_FOLDER, banner_filename)
                banner_file.save(banner_path)
                temp_files.append(banner_path)

                with open(banner_path, 'rb') as f:
                    banner_item = epub.EpubItem(
                        uid="banner",
                        file_name=f"images/{banner_filename}",
                        media_type="image/jpeg" if banner_filename.lower().endswith(('.jpg', '.jpeg')) else "image/png",
                        content=f.read()
                    )
                    book.add_item(banner_item)
                    banner_html = f'<img src="images/{banner_filename}" style="width: 100%; margin-bottom: 2em;" alt="Bannière"/>'
                    logger.info("Bannière ajoutée à l'EPUB")

        # Extraire les notes Markdown
        markdown_footnotes = process_markdown_footnotes(doc)
        logger.info(f"📋 Notes Markdown extraites: {len(markdown_footnotes)}")

        # Variables globales
        global_footnote_counter = [0]
        all_endnotes = []

        # Page d'introduction (page de garde)
        intro_html = f"""
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 1em; 
                    font-family: Georgia, serif; 
                    text-align: center; 
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    min-height: 90vh;
                }}
                h1, h2 {{ text-align: center; }}
                .title-container {{
                    text-align: center;
                    margin: auto;
                }}
            </style>
        </head>
        <body>
            <div class="title-container">
                {banner_html if banner_html else ''}
                <h1 style='font-size: 2.5em; margin-bottom: 0.5em; text-align: center;'>{title}</h1>
                <h2 style='font-size: 1.2em; font-weight: normal; text-align: center;'>{author.upper()}</h2>
            </div>
        </body>
        </html>
        """

        intro_page = epub.EpubHtml(title='Page de garde', file_name='intro.xhtml', lang='fr')
        intro_page.content = intro_html
        book.add_item(intro_page)

        chapters = []
        toc_structure = []
        current_chapter = None
        chap_id = 1
        epigraph_content = []  # POUR STOCKER LES ÉPIGRAPHES
        first_chapter_found = False

        # Variables pour textos
        collecting_texto = False
        texto_nom = ""
        texto_contenu = []
        texto_type = ""

        for para in doc.paragraphs:
            text = clean_text(para.text)

            # Ignorer les définitions de notes
            simple_footnote_pattern = r'^NOTE(\d+):\s*(.+)$'
            if re.match(simple_footnote_pattern, text):
                logger.info(f"📝 Définition de note ignorée: {text}")
                continue

            images_in_para = extract_images_from_paragraph(para, images_info)

            # Ignorer les paragraphes complètement vides
            if not text and not images_in_para and not collecting_texto:
                continue

            style = para.style.name if para.style else ''

            # === GESTION DES ÉPIGRAPHES AVANT LE PREMIER CHAPITRE ===
            # ÉTAPE 3 : REMPLACEMENT EXACT POUR LES ÉPIGRAPHES
            #
            # Dans votre fichier app.py, cherchez la ligne 1842 qui dit :
            # # === GESTION DES ÉPIGRAPHES AVANT LE PREMIER CHAPITRE ===
            #
            # SUPPRIMEZ tout depuis la ligne 1842 jusqu'à la ligne 1875 (qui dit "continue")
            #
            # REMPLACEZ par ce bloc exact :

            # === GESTION DES ÉPIGRAPHES AVANT LE PREMIER CHAPITRE - VERSION CORRIGÉE ===
            if not first_chapter_found and not collecting_texto:
                # Vérifier si c'est un titre de chapitre
                if (style.startswith('Heading 1') or style.startswith('Titre 1') or
                        style.startswith('Heading 2') or style.startswith('Titre 2') or
                        style.startswith('Heading 3') or style.startswith('Titre 3')):

                    # On a trouvé le premier chapitre - traiter les épigraphes accumulées
                    if epigraph_content:
                        logger.info(f"📝 Création du chapitre d'épigraphes : {len(epigraph_content)} épigraphes")

                        # Créer le chapitre d'épigraphes avec CSS amélioré
                        epigraph_chapter = epub.EpubHtml(title='Introduction', file_name='epigraphs.xhtml', lang='fr')

                        epigraph_html = f"""
                                    <html>
                                    <head>
                                        <title>Introduction</title>
                                        <style>
                                            body {{ 
                                                margin: 0; 
                                                padding: 2em; 
                                                font-family: Georgia, serif; 
                                                text-align: center; 
                                                line-height: 1.8;
                                                display: flex;
                                                flex-direction: column;
                                                justify-content: center;
                                                min-height: 80vh;
                                            }}
                                            .epigraph {{ 
                                                font-style: italic; 
                                                margin: 2em auto; 
                                                max-width: 80%; 
                                                text-align: center;
                                                font-size: 1.1em;
                                            }}
                                            .center {{ text-align: center; }}
                                            .right {{ text-align: right; }}
                                            img {{ 
                                                max-width: 100%; 
                                                height: auto; 
                                                display: block; 
                                                margin: 1em auto; 
                                            }}
                                        </style>
                                    </head>
                                    <body>
                                        {''.join(epigraph_content)}
                                    </body>
                                    </html>
                                    """

                        epigraph_chapter.content = epigraph_html
                        book.add_item(epigraph_chapter)
                        chapters.append(epigraph_chapter)
                        toc_structure.append({
                            'level': 1,
                            'title': 'Introduction',
                            'chapter': epigraph_chapter,
                            'is_subsection': False
                        })

                        epigraph_content = []

                    first_chapter_found = True
                    # Continuer avec le traitement normal du chapitre

                # Si pas encore de chapitre trouvé, traiter comme épigraphe potentielle
                elif text or images_in_para:
                    logger.info(f"📖 Contenu d'épigraphe détecté: '{text[:50] if text else 'Image seulement'}...'")

                    # Traiter avec la nouvelle fonction
                    if process_epigraph_with_images(para, images_info, epigraph_content):
                        continue


            # === GESTION DES TEXTOS ===
            if text.startswith("##") and not collecting_texto:
                if "##droite" in text and ":" in text:
                    texto_nom = text.split(":", 1)[1].strip()
                    texto_type = "right"
                elif "##gauche" in text and ":" in text:
                    texto_nom = text.split(":", 1)[1].strip()
                    texto_type = "left"
                else:
                    texto_nom = text[2:].strip()
                    texto_type = "left"

                collecting_texto = True
                texto_contenu = []
                continue

            if text.strip() == "##fin" and collecting_texto:
                if texto_type == "right":
                    texto_html = f"""
                    <div style="background-color: #e3f2fd; border-radius: 6px; padding: 12px; margin: 1em 5% 1em 25%; width: 70%; max-width: 70%;">
                        <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 8px; text-align: right;">{texto_nom}</div>
                        <div style="font-size: 0.9em; line-height: 1.2; text-align: right; word-wrap: break-word;">
                            {'<br>'.join([t.strip() for t in texto_contenu if t.strip()])}
                        </div>
                    </div>
                    """
                else:
                    texto_html = f"""
                    <div style="background-color: #f0f0f0; border-radius: 6px; padding: 12px; margin: 1em 5%; width: 70%; max-width: 70%;">
                        <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 8px;">{texto_nom}</div>
                        <div style="font-size: 0.9em; line-height: 1.2; word-wrap: break-word;">
                            {'<br>'.join([t.strip() for t in texto_contenu if t.strip()])}
                        </div>
                    </div>
                    """

                if current_chapter:
                    add_content_to_chapter(current_chapter, texto_html)

                collecting_texto = False
                texto_nom = ""
                texto_contenu = []
                texto_type = ""
                continue

            if collecting_texto:
                if not text.startswith("##"):
                    texto_contenu.append(para.text.strip())
                continue

            # === GESTION DES TITRES - VERSION CORRIGÉE ===
            title_level = None
            if style.startswith('Heading 1') or style.startswith('Titre 1'):
                title_level = 1
            elif style.startswith('Heading 2') or style.startswith('Titre 2'):
                title_level = 2
            elif style.startswith('Heading 3') or style.startswith('Titre 3'):
                title_level = 3

            if title_level:  # TRAITER TOUS LES NIVEAUX DE TITRES
                logger.info(f"📖 TITRE NIVEAU {title_level} DÉTECTÉ: {text}")

                # Créer le nouveau chapitre pour les titres 1 et 2
                if title_level <= 2:
                    current_chapter = epub.EpubHtml(title=text, file_name=f'chap_{chap_id}.xhtml', lang='fr')

                    banner_chapter_html = ""
                    if banner_html and title_level == 1:
                        banner_chapter_html = f'<div style="text-align: center; margin-bottom: 1em;">{banner_html}</div>'

                    title_size = "2.5em" if title_level == 1 else "2em"
                    title_tag = "h1" if title_level == 1 else "h2"

                    current_chapter.content = f"""
                    <html><head><title>{text}</title>
                    <style>
                        body {{ margin: 0; padding: 0 1em; font-family: Georgia, serif; text-align: justify; line-height: 1.6; }}
                        h1, h2, h3 {{ text-align: center; margin: 2em 0 1em 0; }}
                        .narrator {{ text-align: center !important; font-style: italic; font-size: 1.1em; margin: 1.5em 0; display: block; width: 100%; clear: both; }}
                        p {{ margin-bottom: 1em; text-align: justify; }}
                        img {{ max-width: 100%; height: auto; display: block; margin: 1em auto; }}
                        div[style*="text-align: center"] {{ text-align: center !important; }}
                    </style>
                    </head>
                    <body>
                    {banner_chapter_html}
                    <div style="text-align: center;"><{title_tag} style="font-size: {title_size};">{text}</{title_tag}></div>
                    </body></html>
                    """

                    book.add_item(current_chapter)
                    chapters.append(current_chapter)
                    toc_structure.append({
                        'level': title_level,
                        'title': text,
                        'chapter': current_chapter,
                        'is_subsection': False
                    })
                    chap_id += 1
                    continue

                # Pour les titres 3, les ajouter au chapitre courant
                elif title_level == 3 and current_chapter:
                    logger.info(f"📖 AJOUT TITRE 3 AU CHAPITRE: {text}")
                    title3_html = f'<div style="text-align: center;"><h3 style="font-size: 1.5em; margin: 1.5em 0 1em 0;">{text}</h3></div>'
                    add_content_to_chapter(current_chapter, title3_html)
                    continue

            # === GESTION DES NARRATEURS ===
            if is_narrator_line(text):
                narrator = text[1:-1] if text.startswith('[') and text.endswith(']') else text
                narrator_html = f'<div style="text-align: center !important; font-style: italic; font-size: 1.1em; margin: 1.5em 0; display: block; width: 100%; clear: both;">{narrator}</div>'

                if current_chapter:
                    add_content_to_chapter(current_chapter, narrator_html)
                    logger.info(f"📝 Narrateur ajouté (centré): {narrator}")
                continue

            # === TRAITEMENT DU CONTENU NORMAL ===
            if text or images_in_para:
                try:
                    # Force l'extraction d'images pour chaque paragraphe
                    images_in_para = extract_images_from_paragraph(para, images_info)
                    if images_in_para:
                        logger.info(f"🚨 IMAGES FORCÉES: {[img['filename'] for img in images_in_para]}")

                    formatted_text, align_style, footnotes = convert_format_html_with_alignment_and_images(para, images_info)

                    # Force l'ajout d'images si elles existent
                    if images_in_para and '<img' not in formatted_text:
                        for image_info in images_in_para:
                            image_html = f'<div style="text-align: center; margin: 1em 0;"><img src="images/{image_info["filename"]}" style="max-width: 60%; height: auto;" alt="Image"/></div>'
                            formatted_text = image_html + formatted_text
                            logger.info(f"🔥 IMAGE FORCÉE: {image_info['filename']}")

                except Exception as e:
                    logger.error(f"Erreur traitement contenu: {e}")
                    formatted_text = text if text else ""
                    align_style = 'text-align: justify;'
                    footnotes = []

                # Traiter les notes
                chapter_file = current_chapter.file_name if current_chapter else 'intro_content.xhtml'
                formatted_text, chapter_endnotes = process_simple_footnotes_for_html(
                    formatted_text, markdown_footnotes, global_footnote_counter, chapter_file
                )
                all_endnotes.extend(chapter_endnotes)

                text_with_footnotes, _ = process_footnotes_for_html(formatted_text, footnotes, [0])

                if text_with_footnotes.strip() or images_in_para:
                    if images_in_para and '<img' in formatted_text:
                        # Si c'est juste une image, pas besoin de balise <p>
                        content_html = formatted_text
                    elif text_with_footnotes.strip():
                        content_html = f'<p style="{align_style} margin-bottom: 1em;">{text_with_footnotes}</p>'
                    else:
                        content_html = ""

                    if current_chapter and content_html:
                        add_content_to_chapter(current_chapter, content_html)

        # Créer la page de notes si nécessaire
        if all_endnotes:
            endnotes_html = create_endnotes_page(all_endnotes)
            endnotes_chapter = epub.EpubHtml(title='Notes', file_name='endnotes.xhtml', lang='fr')
            endnotes_chapter.content = endnotes_html
            book.add_item(endnotes_chapter)
            chapters.append(endnotes_chapter)
            toc_structure.append({
                'level': 1,
                'title': 'Notes',
                'chapter': endnotes_chapter,
                'is_subsection': False
            })

        # Créer la table des matières
        toc = []
        spine = [intro_page, 'nav']
        for item in toc_structure:
            if item['level'] == 1:
                toc.append(item['chapter'])
                spine.append(item['chapter'])
            elif item['level'] == 2:
                spine.append(item['chapter'])

        # Finaliser l'EPUB
        book.toc = toc
        book.spine = spine
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Écrire le fichier EPUB
        base_filename = os.path.splitext(filename)[0]
        epub_path = os.path.join(UPLOAD_FOLDER, base_filename + ".epub")
        epub.write_epub(epub_path, book, {})
        temp_files.append(epub_path)

        logger.info(f"EPUB généré avec succès : {epub_path}")
        return epub_path

    except Exception as e:
        logger.error(f"Erreur lors de la génération EPUB : {str(e)}")
        raise e

    finally:
        # Nettoyage des fichiers temporaires (sauf l'EPUB final)
        for temp_file in temp_files:
            if temp_file != epub_path and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass


def process_epigraph_with_images(para, images_info, epigraph_content):
    """Traite les épigraphes avec gestion correcte des images"""
    text = clean_text(para.text)
    images_in_para = extract_images_from_paragraph(para, images_info)

    # Si le paragraphe contient des images
    if images_in_para:
        logger.info(f"🖼️ Image trouvée dans épigraphe: {[img['filename'] for img in images_in_para]}")
        for image_info in images_in_para:
            image_html = f'''
            <div style="text-align: center; margin: 2em auto; max-width: 70%;">
                <img src="images/{image_info['filename']}" style="max-width: 100%; height: auto;" alt="Image épigraphe"/>
            </div>
            '''
            epigraph_content.append(image_html)
            logger.info(f"✅ Image ajoutée à l'épigraphe: {image_info['filename']}")

    # Si le paragraphe contient aussi du texte
    if text:
        if is_center_text(para):
            epigraph_html = f'<div style="font-style: italic; text-align: center; margin: 2em auto; max-width: 80%; font-size: 1.1em;">{text}</div>'
        elif is_right_aligned(para):
            epigraph_html = f'<div style="font-style: italic; text-align: right; margin: 2em auto; max-width: 80%; font-size: 1.1em;">{text}</div>'
        else:
            epigraph_html = f'<div style="font-style: italic; text-align: center; margin: 2em auto; max-width: 80%; font-size: 1.1em;">{text}</div>'
        epigraph_content.append(epigraph_html)

    return len(images_in_para) > 0 or bool(text)

@app.route('/epub', methods=['POST'])
def generate_epub_route():
    """Route pour la génération d'EPUB"""
    try:
        logger.info("Début de génération EPUB")

        # Validation du fichier
        if 'file' not in request.files:
            return "Erreur : aucun fichier fourni.", 400
        file = request.files['file']
        if file.filename == '':
            return "Erreur : fichier non sélectionné.", 400
        if not file.filename.endswith('.docx'):
            return "Erreur : format non supporté.", 400

        # Récupération des paramètres
        title = clean_text(request.form.get('title', 'Titre du roman'))
        author = clean_text(request.form.get('author', "Nom de l'auteur"))

        # Gestion des fichiers optionnels
        banner_file = request.files.get('banner')
        cover_file = request.files.get('cover')

        # Génération de l'EPUB
        epub_path = generate_epub(file, title, author, banner_file, cover_file)

        if epub_path and os.path.exists(epub_path):
            return send_file(epub_path, as_attachment=True,
                             download_name=os.path.basename(epub_path))
        else:
            return "Erreur : fichier EPUB non généré.", 500

    except Exception as e:
        logger.error(f"Erreur lors de la génération EPUB : {str(e)}")
        return f"Erreur lors de la génération EPUB : {str(e)}", 500


@contextmanager
def temp_file_cleanup(*file_paths):
    """Gestionnaire de contexte pour nettoyer les fichiers temporaires"""
    try:
        yield
    finally:
        for filepath in file_paths:
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info(f"Fichier temporaire nettoyé : {filepath}")
                except OSError as e:
                    logger.warning(f"Impossible de supprimer {filepath}: {e}")


# AJOUTEZ CES FONCTIONS À LA FIN DE VOTRE FICHIER app.py (avant le if __name__ == '__main__':)

def add_content_to_chapter(chapter, content_html):
    """Ajoute du contenu à un chapitre existant"""
    current_content = chapter.content
    if isinstance(current_content, bytes):
        current_content = current_content.decode('utf-8')

    updated_content = current_content.replace(
        '</body></html>',
        f'{content_html}</body></html>'
    )
    chapter.content = updated_content


def create_intro_chapter(book, chapters, toc_structure):
    """Crée le chapitre d'introduction une seule fois"""
    logger.info("✅ Création unique du chapitre d'introduction")

    intro_content_chapter = epub.EpubHtml(
        title='Introduction',
        file_name='intro_content.xhtml',
        lang='fr'
    )
    intro_content_chapter.content = """
    <html><head><title>Introduction</title>
    <style>
        body { margin: 0; padding: 0 1em; font-family: Georgia, serif; text-align: justify; }
    </style>
    </head>
    <body>
    </body></html>
    """

    book.add_item(intro_content_chapter)
    chapters.insert(1, intro_content_chapter)  # Après la page de garde

    toc_structure.insert(0, {
        'level': 1,
        'title': 'Introduction',
        'chapter': intro_content_chapter,
        'is_subsection': False
    })

    return intro_content_chapter


# REMPLACEZ AUSSI votre fonction add_images_to_epub existante par cette version corrigée :

def add_images_to_epub(book, images_info):
    """Ajoute toutes les images extraites à l'EPUB - VERSION CORRIGÉE FINALE"""
    logger.info(f"🔄 Ajout de {len(images_info)} images à l'EPUB...")

    added_images = []

    for image_path, image_info in images_info.items():
        try:
            # Vérifier que l'image existe
            if not os.path.exists(image_info['path']):
                logger.warning(f"❌ Image manquante: {image_info['path']}")
                continue

            # Déterminer le type MIME
            filename = image_info['filename'].lower()
            if filename.endswith(('.jpg', '.jpeg')):
                media_type = "image/jpeg"
            elif filename.endswith('.png'):
                media_type = "image/png"
            elif filename.endswith('.gif'):
                media_type = "image/gif"
            elif filename.endswith('.bmp'):
                media_type = "image/bmp"
            else:
                media_type = "image/jpeg"

            # Lire les données de l'image depuis le fichier
            with open(image_info['path'], 'rb') as f:
                image_data = f.read()

            if not image_data:
                logger.warning(f"❌ Image vide: {image_info['filename']}")
                continue

            logger.info(f"📸 Ajout image: {image_info['filename']} ({len(image_data)} bytes)")

            # Créer l'item EPUB pour l'image avec un nom nettoyé
            clean_filename = image_info['filename'].replace('.', '_').replace(' ', '_').replace('-', '_')
            image_item = epub.EpubItem(
                uid=f"image_{clean_filename}",
                file_name=f"images/{image_info['filename']}",
                media_type=media_type,
                content=image_data
            )

            book.add_item(image_item)
            added_images.append(image_info['filename'])
            logger.info(f"✅ Image ajoutée à l'EPUB : {image_info['filename']}")

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout de l'image {image_info['filename']} : {e}")

    logger.info(f"📋 TOTAL IMAGES AJOUTÉES À L'EPUB: {len(added_images)}")
    for img_name in added_images:
        logger.info(f"   ✅ {img_name}")

    # Remplacez la fin de votre fichier app.py (après la fonction add_images_to_epub) par :

    return len(added_images)


# FIN DES FONCTIONS - AJOUTEZ UNE LIGNE VIDE ICI

if __name__ == '__main__':
    # Nettoyage initial du dossier uploads
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                os.remove(filepath)
                logger.info(f"Fichier de démarrage supprimé : {filepath}")
            except OSError:
                pass

    logger.info("🚀 Serveur Flask démarré - Générateur PDF/EPUB avec support des notes de bas de page")
    app.run(debug=True, host='0.0.0.0', port=5000)
