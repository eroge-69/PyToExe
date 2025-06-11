import pygame
import sys
import webbrowser

pygame.init()

# Constants
WIDTH, HEIGHT = 900, 600
BG_COLOR_LIGHT = (245, 245, 245)
BG_COLOR_DARK = (30, 30, 30)
TEXT_COLOR_LIGHT = (50, 50, 50)
TEXT_COLOR_DARK = (220, 220, 220)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 60)
BLUE = (30, 144, 255)
HOVER_BLUE = (65, 105, 225)
FONT_NAME = pygame.font.get_default_font()
FONT_SIZE = 22
CATEGORY_HEIGHT = 60
SEARCH_BAR_HEIGHT = 50
PADDING = 20
BURGER_SIZE = 30
MENU_WIDTH = 220

# Data: Categories and AI tools with real URLs
AI_DATA = {
    "Image Generators": [
        {"name": "DALL·E 2", "url": "https://openai.com/dall-e-2/"},
        {"name": "Midjourney", "url": "https://www.midjourney.com/"},
        {"name": "Stable Diffusion", "url": "https://stability.ai/blog/stable-diffusion-public-release"},
        {"name": "Deep Dream Generator", "url": "https://deepdreamgenerator.com/"},
        {"name": "Runway ML", "url": "https://runwayml.com/"},
        {"name": "Artbreeder", "url": "https://www.artbreeder.com/"},
        {"name": "NightCafe Studio", "url": "https://creator.nightcafe.studio/"},
        {"name": "PaintsChainer", "url": "https://paintschainer.preferred.tech/index_en.html"},
        {"name": "This Person Does Not Exist", "url": "https://thispersondoesnotexist.com/"},
        {"name": "AI Painter", "url": "https://aipainter.ai/"},
    ],
    "Video Generators": [
        {"name": "Runway ML", "url": "https://runwayml.com/"},
        {"name": "Synthesia", "url": "https://www.synthesia.io/"},
        {"name": "Pictory", "url": "https://pictory.ai/"},
        {"name": "Lumen5", "url": "https://lumen5.com/"},
        {"name": "Animoto", "url": "https://animoto.com/"},
        {"name": "Magisto", "url": "https://www.magisto.com/"},
        {"name": "InVideo", "url": "https://invideo.io/"},
        {"name": "Veed.io", "url": "https://www.veed.io/"},
        {"name": "FlexClip", "url": "https://www.flexclip.com/"},
        {"name": "Clipchamp", "url": "https://clipchamp.com/"},
    ],
    "Text Generators": [
        {"name": "ChatGPT", "url": "https://chat.openai.com/"},
        {"name": "Copy.ai", "url": "https://www.copy.ai/"},
        {"name": "Jasper", "url": "https://www.jasper.ai/"},
        {"name": "Writesonic", "url": "https://writesonic.com/"},
        {"name": "Rytr", "url": "https://rytr.me/"},
        {"name": "Peppertype.ai", "url": "https://www.peppertype.ai/"},
        {"name": "AI Writer", "url": "https://ai-writer.com/"},
        {"name": "Text Blaze", "url": "https://blaze.today/"},
        {"name": "ShortlyAI", "url": "https://www.shortlyai.com/"},
        {"name": "CopySmith", "url": "https://copysmith.ai/"},
    ],
    "Chatbots": [
        {"name": "Replika", "url": "https://replika.ai/"},
        {"name": "Mitsuku", "url": "https://www.pandorabots.com/mitsuku/"},
        {"name": "Cleverbot", "url": "https://www.cleverbot.com/"},
        {"name": "Woebot", "url": "https://woebot.io/"},
        {"name": "ChatBot.com", "url": "https://www.chatbot.com/"},
        {"name": "Tidio", "url": "https://www.tidio.com/"},
        {"name": "ManyChat", "url": "https://manychat.com/"},
        {"name": "MobileMonkey", "url": "https://mobilemonkey.com/"},
        {"name": "Botsify", "url": "https://botsify.com/"},
        {"name": "Flow XO", "url": "https://flowxo.com/"},
    ],
    "Speech Recognition": [
        {"name": "Google Speech-to-Text", "url": "https://cloud.google.com/speech-to-text"},
        {"name": "IBM Watson Speech to Text", "url": "https://www.ibm.com/cloud/watson-speech-to-text"},
        {"name": "Microsoft Azure Speech", "url": "https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/"},
        {"name": "Amazon Transcribe", "url": "https://aws.amazon.com/transcribe/"},
        {"name": "Speechmatics", "url": "https://www.speechmatics.com/"},
        {"name": "Rev.ai", "url": "https://www.rev.ai/"},
        {"name": "Kaldi", "url": "https://kaldi-asr.org/"},
        {"name": "Deepgram", "url": "https://deepgram.com/"},
        {"name": "Wit.ai", "url": "https://wit.ai/"},
        {"name": "AssemblyAI", "url": "https://www.assemblyai.com/"},
    ],
    "Translation": [
        {"name": "Google Translate", "url": "https://translate.google.com/"},
        {"name": "DeepL", "url": "https://www.deepl.com/translator"},
        {"name": "Microsoft Translator", "url": "https://www.microsoft.com/en-us/translator/"},
        {"name": "Amazon Translate", "url": "https://aws.amazon.com/translate/"},
        {"name": "Yandex Translate", "url": "https://translate.yandex.com/"},
        {"name": "Reverso", "url": "https://www.reverso.net/"},
        {"name": "Linguee", "url": "https://www.linguee.com/"},
        {"name": "PROMT", "url": "https://www.promt.com/"},
        {"name": "Papago", "url": "https://papago.naver.com/"},
        {"name": "iTranslate", "url": "https://www.itranslate.com/"},
    ],
    "Recommendation Systems": [
        {"name": "Amazon Personalize", "url": "https://aws.amazon.com/personalize/"},
        {"name": "Google Recommendations AI", "url": "https://cloud.google.com/recommendations"},
        {"name": "Microsoft Azure Personalizer", "url": "https://azure.microsoft.com/en-us/services/cognitive-services/personalizer/"},
        {"name": "IBM Watson Discovery", "url": "https://www.ibm.com/cloud/watson-discovery"},
        {"name": "Salesforce Einstein", "url": "https://www.salesforce.com/products/einstein/overview/"},
        {"name": "Algolia Recommend", "url": "https://www.algolia.com/products/recommend/"},
        {"name": "Dynamic Yield", "url": "https://www.dynamicyield.com/"},
        {"name": "Qubit", "url": "https://www.qubit.com/"},
        {"name": "Kibo Personalization", "url": "https://kibocommerce.com/"},
        {"name": "Bloomreach", "url": "https://www.bloomreach.com/"},
    ],
    "Face Recognition": [
        {"name": "Face++", "url": "https://www.faceplusplus.com/"},
        {"name": "Microsoft Face API", "url": "https://azure.microsoft.com/en-us/services/cognitive-services/face/"},
        {"name": "Amazon Rekognition", "url": "https://aws.amazon.com/rekognition/"},
        {"name": "Kairos", "url": "https://www.kairos.com/"},
        {"name": "OpenCV Face Recognition", "url": "https://opencv.org/"},
        {"name": "Luxand", "url": "https://luxand.com/"},
        {"name": "Sightcorp", "url": "https://sightcorp.com/"},
        {"name": "Trueface", "url": "https://www.trueface.ai/"},
        {"name": "FaceFirst", "url": "https://www.facefirst.com/"},
        {"name": "Cognitec", "url": "https://www.cognitec.com/"},
    ],
    "Sentiment Analysis": [
        {"name": "MonkeyLearn", "url": "https://monkeylearn.com/sentiment-analysis/"},
        {"name": "Lexalytics", "url": "https://www.lexalytics.com/"},
        {"name": "IBM Watson Natural Language Understanding", "url": "https://www.ibm.com/cloud/watson-natural-language-understanding"},
        {"name": "Google Cloud Natural Language", "url": "https://cloud.google.com/natural-language"},
        {"name": "Amazon Comprehend", "url": "https://aws.amazon.com/comprehend/"},
        {"name": "Semantria", "url": "https://semantria.com/"},
        {"name": "MeaningCloud", "url": "https://www.meaningcloud.com/"},
        {"name": "Repustate", "url": "https://www.repustate.com/"},
        {"name": "Aylien", "url": "https://aylien.com/"},
        {"name": "TextBlob", "url": "https://textblob.readthedocs.io/en/dev/"},
    ],
    "AI Assistants": [
        {"name": "Google Assistant", "url": "https://assistant.google.com/"},
        {"name": "Amazon Alexa", "url": "https://developer.amazon.com/en-US/alexa"},
        {"name": "Apple Siri", "url": "https://www.apple.com/siri/"},
        {"name": "Microsoft Cortana", "url": "https://www.microsoft.com/en-us/cortana"},
        {"name": "Samsung Bixby", "url": "https://www.samsung.com/global/galaxy/apps/bixby/"},
        {"name": "Hound", "url": "https://www.soundhound.com/hound"},
        {"name": "Mycroft", "url": "https://mycroft.ai/"},
        {"name": "Snips", "url": "https://snips.ai/"},
        {"name": "Jibo", "url": "https://www.jibo.com/"},
        {"name": "Viv", "url": "https://viv.ai/"},
    ],
    "Code Generators": [
        {"name": "GitHub Copilot", "url": "https://copilot.github.com/"},
        {"name": "TabNine", "url": "https://www.tabnine.com/"},
        {"name": "Kite", "url": "https://www.kite.com/"},
        {"name": "Codex", "url": "https://openai.com/blog/openai-codex/"},
        {"name": "DeepCode", "url": "https://www.deepcode.ai/"},
        {"name": "CodeT5", "url": "https://github.com/salesforce/CodeT5"},
        {"name": "PolyCoder", "url": "https://polycoder.ai/"},
        {"name": "CodeGuru", "url": "https://aws.amazon.com/codeguru/"},
        {"name": "Sourcery", "url": "https://sourcery.ai/"},
        {"name": "Codota", "url": "https://www.codota.com/"},
    ],
    "AI in Healthcare": [
        {"name": "IBM Watson Health", "url": "https://www.ibm.com/watson-health"},
        {"name": "PathAI", "url": "https://www.pathai.com/"},
        {"name": "Tempus", "url": "https://www.tempus.com/"},
        {"name": "Butterfly Network", "url": "https://www.butterflynetwork.com/"},
        {"name": "Zebra Medical Vision", "url": "https://www.zebra-med.com/"},
        {"name": "Aidoc", "url": "https://www.aidoc.com/"},
        {"name": "Viz.ai", "url": "https://www.viz.ai/"},
        {"name": "Caption Health", "url": "https://captionhealth.com/"},
        {"name": "Freenome", "url": "https://www.freenome.com/"},
        {"name": "Insilico Medicine", "url": "https://insilico.com/"},
    ],
    "AI in Finance": [
        {"name": "Kensho", "url": "https://www.kensho.com/"},
        {"name": "Zest AI", "url": "https://www.zest.ai/"},
        {"name": "Upstart", "url": "https://www.upstart.com/"},
        {"name": "Numerai", "url": "https://numer.ai/"},
        {"name": "Alphasense", "url": "https://www.alpha-sense.com/"},
        {"name": "Ayasdi", "url": "https://www.ayasdi.com/"},
        {"name": "DataRobot", "url": "https://www.datarobot.com/"},
        {"name": "Kabbage", "url": "https://www.kabbage.com/"},
        {"name": "Sentifi", "url": "https://www.sentifi.com/"},
        {"name": "Behavox", "url": "https://www.behavox.com/"},
    ],
    "AI in Education": [
        {"name": "Carnegie Learning", "url": "https://www.carnegielearning.com/"},
        {"name": "Knewton", "url": "https://www.knewton.com/"},
        {"name": "Squirrel AI", "url": "https://www.squirrelai.com/"},
        {"name": "Querium", "url": "https://www.querium.com/"},
        {"name": "DreamBox Learning", "url": "https://www.dreambox.com/"},
        {"name": "Smart Sparrow", "url": "https://www.smartsparrow.com/"},
        {"name": "Cognii", "url": "https://www.cognii.com/"},
        {"name": "Content Technologies", "url": "https://contenttechnologiesinc.com/"},
        {"name": "ALEKS", "url": "https://www.aleks.com/"},
        {"name": "Knowre", "url": "https://www.knowre.com/"},
    ],
}

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Hub")

font = pygame.font.Font(FONT_NAME, FONT_SIZE)
small_font = pygame.font.Font(FONT_NAME, 18)

# Search bar state
search_text = ""
search_active = False

# Scroll state
scroll_offset = 0
max_scroll = 0

# App states
STATE_CATEGORIES = "categories"
STATE_AI_LIST = "ai_list"
STATE_ABOUT = "about"
current_state = STATE_CATEGORIES
current_category = None

# Donation button
donation_rect = pygame.Rect(WIDTH - 150, HEIGHT - 60, 130, 40)
donation_hover = False

# Burger menu state
burger_rect = pygame.Rect(PADDING, PADDING, BURGER_SIZE, BURGER_SIZE)
burger_open = False

# Theme state
theme_dark = False

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    surface.blit(textobj, (x, y))

def filter_items(items, text):
    return [item for item in items if text.lower() in item["name"].lower()]

def draw_search_bar():
    bar_x = PADDING + BURGER_SIZE + 10
    bar_width = WIDTH - bar_x - PADDING - 150
    bar_y = PADDING if not burger_open else PADDING - SEARCH_BAR_HEIGHT - 10
    bg_color = WHITE if not theme_dark else DARK_GRAY
    text_color = DARK_GRAY if not theme_dark else LIGHT_GRAY
    pygame.draw.rect(screen, bg_color, (bar_x, bar_y + 10, bar_width, SEARCH_BAR_HEIGHT - 20), border_radius=15)
    icon_center = (bar_x + 20, bar_y + SEARCH_BAR_HEIGHT // 2)
    pygame.draw.circle(screen, text_color, icon_center, 8, 2)
    pygame.draw.line(screen, text_color, (icon_center[0] + 5, icon_center[1] + 5), (icon_center[0] + 12, icon_center[1] + 12), 2)
    if search_text == "" and not search_active:
        placeholder = font.render("Search AI categories or tools", True, LIGHT_GRAY if not theme_dark else DARK_GRAY)
        screen.blit(placeholder, (bar_x + 40, bar_y + 15))
    else:
        txt_surface = font.render(search_text, True, text_color)
        screen.blit(txt_surface, (bar_x + 40, bar_y + 15))
    pygame.draw.rect(screen, text_color, (bar_x, bar_y + 10, bar_width, SEARCH_BAR_HEIGHT - 20), 2, border_radius=15)

def draw_list(items, offset, mouse_pos):
    y = SEARCH_BAR_HEIGHT + 2 * PADDING - offset
    if burger_open:
        y += SEARCH_BAR_HEIGHT + 10
    bg_color = WHITE if not theme_dark else DARK_GRAY
    border_color = LIGHT_GRAY if not theme_dark else (70, 70, 70)
    text_color = DARK_GRAY if not theme_dark else LIGHT_GRAY
    for i, item in enumerate(items):
        rect = pygame.Rect(PADDING + (MENU_WIDTH if burger_open else 0), y, WIDTH - 2 * PADDING - (MENU_WIDTH if burger_open else 0), CATEGORY_HEIGHT)
        if rect.collidepoint(mouse_pos) and not burger_open:
            pygame.draw.rect(screen, HOVER_BLUE, rect, border_radius=10)
        else:
            pygame.draw.rect(screen, bg_color, rect, border_radius=10)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)
        draw_text(item["name"], font, text_color, screen, rect.x + 20, rect.y + (CATEGORY_HEIGHT - FONT_SIZE) // 2)
        y += CATEGORY_HEIGHT + PADDING

def draw_donation_button(mouse_pos):
    global donation_hover
    color = HOVER_BLUE if donation_rect.collidepoint(mouse_pos) else BLUE
    pygame.draw.rect(screen, color, donation_rect, border_radius=10)
    draw_text("Donate", font, WHITE, screen, donation_rect.x + 30, donation_rect.y + 8)

def draw_burger_menu(mouse_pos):
    color = HOVER_BLUE if burger_rect.collidepoint(mouse_pos) else BLUE
    pygame.draw.rect(screen, color, burger_rect, border_radius=5)
    line_y = burger_rect.y + 7
    for _ in range(3):
        pygame.draw.rect(screen, WHITE, (burger_rect.x + 7, line_y, BURGER_SIZE - 14, 4), border_radius=2)
        line_y += 8
    if burger_open:
        menu_rect = pygame.Rect(0, 0, MENU_WIDTH, HEIGHT)
        bg_color = WHITE if not theme_dark else DARK_GRAY
        text_color = DARK_GRAY if not theme_dark else LIGHT_GRAY
        pygame.draw.rect(screen, bg_color, menu_rect)
        options = ["Home", "Settings", "About"]
        option_y = 50
        for option in options:
            draw_text(option, font, text_color, screen, 20, option_y)
            option_y += 40

def draw_about_text():
    lines = [
        "AI Hub Application",
        "Created with pygame",
        "Browse various AI tools and categories",
        "Click on an AI to open its website",
        "Settings allow toggling dark/light mode",
        "Burger menu disables AI selection when open",
        "Donate button opens donation page",
    ]
    y = 100
    text_color = DARK_GRAY if not theme_dark else LIGHT_GRAY
    for line in lines:
        draw_text(line, font, text_color, screen, PADDING + MENU_WIDTH + 20, y)
        y += 30

def main():
    global search_text, search_active, scroll_offset, current_state, current_category, burger_open, theme_dark

    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        bg_color = BG_COLOR_DARK if theme_dark else BG_COLOR_LIGHT
        screen.fill(bg_color)

        if current_state == STATE_CATEGORIES:
            items = [{"name": k} for k in AI_DATA.keys()]
        elif current_state == STATE_AI_LIST and current_category:
            items = AI_DATA.get(current_category, [])
        elif current_state == STATE_ABOUT:
            items = []
        else:
            items = []

        max_scroll = max(0, len(items) * (CATEGORY_HEIGHT + PADDING) - (HEIGHT - SEARCH_BAR_HEIGHT - 3 * PADDING - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if current_state in [STATE_CATEGORIES, STATE_AI_LIST]:
                    if search_active:
                        if event.key == pygame.K_BACKSPACE:
                            search_text = search_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            search_active = False
                        else:
                            if len(search_text) < 30 and event.unicode.isprintable():
                                search_text += event.unicode
                    else:
                        if event.key == pygame.K_s:
                            search_active = True
                if event.key == pygame.K_ESCAPE:
                    if burger_open:
                        burger_open = False
                    elif current_state == STATE_AI_LIST:
                        current_state = STATE_CATEGORIES
                        current_category = None
                    elif current_state == STATE_ABOUT:
                        current_state = STATE_CATEGORIES
                elif event.key == pygame.K_b:
                    # Additional key to toggle burger menu for easier escape
                    burger_open = not burger_open

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if burger_rect.collidepoint(event.pos):
                        burger_open = not burger_open
                    elif donation_rect.collidepoint(event.pos):
                        webbrowser.open("https://coff.ee/voyagerplat")
                    else:
                        if burger_open:
                            # Disable AI selection when burger menu is open
                            pass
                        else:
                            mx, my = event.pos
                            if PADDING + (MENU_WIDTH if burger_open else 0) <= mx <= WIDTH - PADDING and (SEARCH_BAR_HEIGHT + 2 * PADDING if not burger_open else SEARCH_BAR_HEIGHT + 2 * PADDING - SEARCH_BAR_HEIGHT - 10) <= my <= HEIGHT - 70:
                                y = SEARCH_BAR_HEIGHT + 2 * PADDING - scroll_offset
                                if burger_open:
                                    y += SEARCH_BAR_HEIGHT + 10
                                filtered_items = filter_items(items, search_text)
                                for item in filtered_items:
                                    rect = pygame.Rect(PADDING + (MENU_WIDTH if burger_open else 0), y, WIDTH - 2 * PADDING - (MENU_WIDTH if burger_open else 0), CATEGORY_HEIGHT)
                                    if rect.collidepoint(mx, my):
                                        if current_state == STATE_CATEGORIES:
                                            current_category = item["name"]
                                            current_state = STATE_AI_LIST
                                            search_text = ""
                                            scroll_offset = 0
                                        elif current_state == STATE_AI_LIST:
                                            webbrowser.open(item["url"])
                                        elif current_state == STATE_ABOUT:
                                            pass
                                        break
                                    y += CATEGORY_HEIGHT + PADDING
                            # Check burger menu options click
                            if burger_open:
                                menu_rect = pygame.Rect(0, 0, MENU_WIDTH, HEIGHT)
                                options = ["Home", "Settings", "About"]
                                option_y = 50
                                for option in options:
                                    option_rect = pygame.Rect(0, option_y, MENU_WIDTH, 40)
                                    if option_rect.collidepoint(event.pos):
                                        if option == "Home":
                                            current_state = STATE_CATEGORIES
                                            current_category = None
                                        elif option == "Settings":
                                            theme_dark = not theme_dark
                                        elif option == "About":
                                            current_state = STATE_ABOUT
                                        burger_open = False
                                        search_text = ""
                                        scroll_offset = 0
                                        break
                                    option_y += 40

                elif event.button == 4:  # Scroll up
                    scroll_offset = max(scroll_offset - 20, 0)
                elif event.button == 5:  # Scroll down
                    scroll_offset = min(scroll_offset + 20, max_scroll)

        if current_state in [STATE_CATEGORIES, STATE_AI_LIST]:
            draw_search_bar()
            filtered_items = filter_items(items, search_text)
            draw_list(filtered_items, scroll_offset, mouse_pos)
            draw_donation_button(mouse_pos)
            draw_burger_menu(mouse_pos)
        elif current_state == STATE_ABOUT:
            draw_burger_menu(mouse_pos)
            draw_about_text()
            draw_donation_button(mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
