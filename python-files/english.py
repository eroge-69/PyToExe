import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import random
import math
import pygame
import sys
import textwrap # Added for text wrapping

# --- Constants ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2 # Can be used for end-of-questions state

# Pygame Screen Setup
pygame.init()
try:
    screen_info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
except pygame.error:
    print("Falling back to fixed size window (Fullscreen/Hardware Acceleration failed)")
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)

pygame.display.set_caption("Unit 5 English Game - Hand Tracking")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
SKY_BLUE = (135, 206, 235)
CURSOR_COLOR = (255, 100, 0) # Orange for hand cursor
MENU_TEXT_COLOR = (40, 40, 40)
MENU_HIGHLIGHT_COLOR = (0, 150, 255)
QUESTION_BG_COLOR = (0, 0, 0, 180) # Semi-transparent black
FEEDBACK_CORRECT_COLOR = (0, 200, 0)
FEEDBACK_INCORRECT_COLOR = (200, 0, 0)
BALLOON_TEXT_COLOR = (0, 0, 0) # Black text on balloons
BALLOON_COLORS = [
    (255, 182, 193), # LightPink
    (173, 216, 230), # LightBlue
    (144, 238, 144), # LightGreen
    (255, 255, 224), # LightYellow
    (221, 160, 221), # Plum
    (240, 230, 140), # Khaki
    (176, 224, 230)  # PowderBlue
]

# Game Variables
BALLOON_RADIUS_MIN = 55
BALLOON_RADIUS_MAX = 85
BALLOON_ASPECT_RATIO = 0.8
BALLOON_SPEED_MIN = 1.0
BALLOON_SPEED_MAX = 3.5
BALLOON_SPAWN_DELAY = 0.4
NUM_ANSWER_BALLOONS = 3
CURSOR_RADIUS = 12
POP_ANIMATION_FRAMES = 8
POP_PARTICLE_COUNT = 15
POP_PARTICLE_SPEED = 5
POP_PARTICLE_LIFE = 20
FEEDBACK_DISPLAY_TIME = 2.0

# Fonts
try:
    menu_font = pygame.font.SysFont('Arial', 72)
    score_font = pygame.font.SysFont('Arial', 36)
    button_font = pygame.font.SysFont('Arial', 50)
    question_font = pygame.font.SysFont('Arial', 38)
    balloon_font = pygame.font.SysFont('Arial', 22)
    feedback_font = pygame.font.SysFont('Arial', 48)
except pygame.error:
    menu_font = pygame.font.Font(None, 80)
    score_font = pygame.font.Font(None, 45)
    button_font = pygame.font.Font(None, 60)
    question_font = pygame.font.Font(None, 48)
    balloon_font = pygame.font.Font(None, 28)
    feedback_font = pygame.font.Font(None, 55)


# --- Educational Content - Based on Provided Unit 5 Images ---
questions = [
    # === Vocabulary (60 Questions - From Images 1, 2, 3, 4, 5) ===
    # Image 1: Environment
    {"question": "To influence or change something.", "options": ["affect", "contribute", "engage"], "correct_answer": "affect", "type": "Vocabulary"},
    {"question": "People's knowledge or understanding of a situation or fact.", "options": ["awareness", "influence", "livelihood"], "correct_answer": "awareness", "type": "Vocabulary"},
    {"question": "The act of deciding that an organized event will not happen.", "options": ["cancellation", "emission", "policy"], "correct_answer": "cancellation", "type": "Vocabulary"},
    {"question": "The building containing the local government offices.", "options": ["city hall", "facilities", "mosque"], "correct_answer": "city hall", "type": "Vocabulary"},
    {"question": "To make something impure by adding a dangerous or poisonous substance.", "options": ["contaminate", "purify", "maintain"], "correct_answer": "contaminate", "type": "Vocabulary"},
    {"question": "To give something, especially money, in order to help achieve something.", "options": ["contribute", "demand", "submit"], "correct_answer": "contribute", "type": "Vocabulary"},
    {"question": "The production and discharge of something, especially gas or radiation.", "options": ["emission", "sewage", "waste"], "correct_answer": "emission", "type": "Vocabulary"},
    {"question": "To occupy, attract, or involve someone's interest or attention.", "options": ["engage (in)", "bother", "reassure"], "correct_answer": "engage (in)", "type": "Vocabulary"},
    {"question": "Places or means for doing something (e.g., toilets, showers).", "options": ["facilities", "authorities", "sources"], "correct_answer": "facilities", "type": "Vocabulary"},
    {"question": "Potentially dangerous or risky.", "options": ["hazardous", "impartial", "secular"], "correct_answer": "hazardous", "type": "Vocabulary"},
    {"question": "The capacity to have an effect on the character or behaviour of someone.", "options": ["influence", "coverage", "scrutiny"], "correct_answer": "influence", "type": "Vocabulary"},
    {"question": "Being involved in something.", "options": ["involvement", "enlightenment", "atonement"], "correct_answer": "involvement", "type": "Vocabulary"},
    {"question": "To drop rubbish in a public place.", "options": ["litter", "recycle", "endure"], "correct_answer": "litter", "type": "Vocabulary"},
    {"question": "A means of securing the necessities of life.", "options": ["livelihood", "well-being", "scripture"], "correct_answer": "livelihood", "type": "Vocabulary"},
    {"question": "To keep something at the same level or rate.", "options": ["maintain", "cease", "decrease"], "correct_answer": "maintain", "type": "Vocabulary"},
    {"question": "To kill with a toxic substance.", "options": ["poison", "sacrifice", "threaten"], "correct_answer": "poison", "type": "Vocabulary"},
    {"question": "A course or principle of action adopted or proposed by a government or individual.", "options": ["policy", "campaign", "issue"], "correct_answer": "policy", "type": "Vocabulary"},
    {"question": "To remove contaminants from something.", "options": ["purify", "contaminate", "litter"], "correct_answer": "purify", "type": "Vocabulary"},
    {"question": "Waste water and excrement conveyed in sewers.", "options": ["sewage", "soil", "waste"], "correct_answer": "sewage", "type": "Vocabulary"},
    {"question": "The upper layer of earth in which plants grow.", "options": ["soil", "sand", "clay"], "correct_answer": "soil", "type": "Vocabulary"},
    # Image 2: Media / Reading
    {"question": "To make something known publicly.", "options": ["announce", "claim", "cite"], "correct_answer": "announce", "type": "Vocabulary"},
    {"question": "Showing an unfair preference for one side.", "options": ["biased", "impartial", "reliable"], "correct_answer": "biased", "type": "Vocabulary"},
    {"question": "To stop doing something.", "options": ["cease", "endure", "maintain"], "correct_answer": "cease", "type": "Vocabulary"},
    {"question": "To disagree with something.", "options": ["contradict", "reflect", "compare"], "correct_answer": "contradict", "type": "Vocabulary"},
    {"question": "The reporting of news and sport in newspapers and on radio and television.", "options": ["coverage", "readership", "front page"], "correct_answer": "coverage", "type": "Vocabulary"},
    {"question": "Ability to be believed; trustworthiness.", "options": ["credibility", "reality", "exaggeration"], "correct_answer": "credibility", "type": "Vocabulary"},
    {"question": "To damage the reputation of someone.", "options": ["discredit", "encourage", "reassure"], "correct_answer": "discredit", "type": "Vocabulary"},
    {"question": "To destroy something completely.", "options": ["eradicate", "maintain", "require"], "correct_answer": "eradicate", "type": "Vocabulary"},
    {"question": "Representing something as larger or more important than it really is.", "options": ["exaggeration", "scrutiny", "pilgrimage"], "correct_answer": "exaggeration", "type": "Vocabulary"},
    # Image 3: Well-being
    {"question": "Something that prevents someone from concentrating.", "options": ["distraction", "treatment", "recovery"], "correct_answer": "distraction", "type": "Vocabulary"},
    {"question": "To suffer something difficult or painful patiently.", "options": ["endure", "require", "relieve"], "correct_answer": "endure", "type": "Vocabulary"},
    {"question": "To bend forward and down.", "options": ["hunch over", "cope with", "stem from"], "correct_answer": "hunch over", "type": "Vocabulary"},
    {"question": "Very tired.", "options": ["knackered", "relieved", "satisfied"], "correct_answer": "knackered", "type": "Vocabulary"},
    {"question": "A return to a normal state of health, mind, or strength.", "options": ["recovery", "treatment", "belief"], "correct_answer": "recovery", "type": "Vocabulary"},
    {"question": "To lessen or remove pain or distress.", "options": ["relieve", "bother", "threaten"], "correct_answer": "relieve", "type": "Vocabulary"},
    {"question": "To need something for a particular purpose.", "options": ["require", "demand", "submit"], "correct_answer": "require", "type": "Vocabulary"},
    {"question": "Demanding great physical or mental effort.", "options": ["rigorous", "emotional", "mental"], "correct_answer": "rigorous", "type": "Vocabulary"},
    {"question": "To originate in or be caused by.", "options": ["stem from", "cope with", "care for"], "correct_answer": "stem from", "type": "Vocabulary"},
    {"question": "The state of being comfortable, healthy, or happy.", "options": ["well-being", "strength", "faith"], "correct_answer": "well-being", "type": "Vocabulary"},
    {"question": "Medical care given to a patient for an illness or injury.", "options": ["treatment", "handling", "atonement"], "correct_answer": "treatment", "type": "Vocabulary"},
    {"question": "To annoy or disturb someone.", "options": ["bother", "reassure", "relieve"], "correct_answer": "bother", "type": "Vocabulary"},
    {"question": "Relating to feelings.", "options": ["emotional", "physical", "mental"], "correct_answer": "emotional", "type": "Vocabulary"},
    {"question": "Relating to the body.", "options": ["physical", "mental", "spiritual"], "correct_answer": "physical", "type": "Vocabulary"},
    {"question": "Relating to the mind.", "options": ["mental", "physical", "emotional"], "correct_answer": "mental", "type": "Vocabulary"},
    {"question": "Feeling annoyed and unable to change or achieve something.", "options": ["frustrated", "satisfied", "relieved"], "correct_answer": "frustrated", "type": "Vocabulary"},
    {"question": "To say or do something to remove the doubts or fears of someone.", "options": ["reassure", "bother", "shock"], "correct_answer": "reassure", "type": "Vocabulary"},
    {"question": "Feeling surprised and upset by something unexpected.", "options": ["shocked", "at ease", "worried"], "correct_answer": "shocked", "type": "Vocabulary"},
    {"question": "The quality or state of being physically strong.", "options": ["strength", "weakness", "stress"], "correct_answer": "strength", "type": "Vocabulary"},
    {"question": "To deal effectively with something difficult.", "options": ["cope with", "hunch over", "stem from"], "correct_answer": "cope with", "type": "Vocabulary"},
    {"question": "Worried or uneasy.", "options": ["worried", "relieved", "satisfied"], "correct_answer": "worried", "type": "Vocabulary"},
    {"question": "Comfortable; not worried or embarrassed.", "options": ["at ease", "frustrated", "guilty"], "correct_answer": "at ease", "type": "Vocabulary"},
    {"question": "Feeling happy because something unpleasant has not happened or has ended.", "options": ["relieved", "worried", "embarrassed"], "correct_answer": "relieved", "type": "Vocabulary"},
    {"question": "Contented; pleased.", "options": ["satisfied", "frustrated", "guilty"], "correct_answer": "satisfied", "type": "Vocabulary"},
    {"question": "Feeling awkward or self-conscious.", "options": ["embarrassed", "satisfied", "at ease"], "correct_answer": "embarrassed", "type": "Vocabulary"},
    {"question": "Having done something wrong.", "options": ["guilty", "innocent", "relieved"], "correct_answer": "guilty", "type": "Vocabulary"},
    {"question": "To look after someone.", "options": ["care for", "cope with", "believe in"], "correct_answer": "care for", "type": "Vocabulary"},
    # Image 4: Religion/Spirituality
    {"question": "Related to a god; supremely good or beautiful.", "options": ["divine", "secular", "holy"], "correct_answer": "divine", "type": "Vocabulary"},
    {"question": "The state of gaining spiritual knowledge or insight.", "options": ["enlightenment", "atonement", "salvation"], "correct_answer": "enlightenment", "type": "Vocabulary"},
    {"question": "To notice or perceive something; to follow a rule or custom.", "options": ["observe", "sacrifice", "worship"], "correct_answer": "observe", "type": "Vocabulary"},
    {"question": "Making amends for a wrong or injury.", "options": ["atonement", "pilgrimage", "reincarnation"], "correct_answer": "atonement", "type": "Vocabulary"},
    {"question": "A journey to a place associated with someone or something well known or holy.", "options": ["pilgrimage", "funeral", "deed"], "correct_answer": "pilgrimage", "type": "Vocabulary"},
    {"question": "To give up something valuable for the sake of other considerations.", "options": ["sacrifice", "pray", "fast"], "correct_answer": "sacrifice", "type": "Vocabulary"},
    {"question": "Deliverance from sin and its consequences.", "options": ["salvation", "scripture", "vow"], "correct_answer": "salvation", "type": "Vocabulary"},
    {"question": "The sacred writings of Christianity or another religion.", "options": ["scripture", "belief", "soul"], "correct_answer": "scripture", "type": "Vocabulary"},
    # Found enough Vocab (60+) - can stop adding more here if desired.

    # === Expressions (30 Questions - From Image 3 'Expressing Concern' and idiomatic uses in examples) ===
    {"question": "Phrase meaning 'You seem sad or unhappy.'", "options": ["You look a bit down in the dumps", "You seem to have the weight of the world on your shoulders", "Tell me, what's the matter with you?"], "correct_answer": "You look a bit down in the dumps", "type": "Expressions"},
    {"question": "Phrase asking 'What is wrong?'", "options": ["Tell me, what's the matter with you?", "I'm sorry to hear you're feeling frazzled", "It might be a good idea to try yoga"], "correct_answer": "Tell me, what's the matter with you?", "type": "Expressions"},
    {"question": "Phrase expressing sympathy for someone feeling stressed/confused.", "options": ["I'm sorry to hear you're feeling frazzled", "I'm really concerned about how stressed you are", "You look a bit down in the dumps"], "correct_answer": "I'm sorry to hear you're feeling frazzled", "type": "Expressions"},
    {"question": "Phrase meaning 'You appear to be carrying many burdens or worries.'", "options": ["You seem to have the weight of the world on your shoulders", "Tell me, what's the matter with you?", "It might be a good idea to try yoga"], "correct_answer": "You seem to have the weight of the world on your shoulders", "type": "Expressions"},
    {"question": "Phrase showing you are worried about someone's stress level.", "options": ["I'm really concerned about how stressed you are", "You look a bit down in the dumps", "I'm sorry to hear you're feeling frazzled"], "correct_answer": "I'm really concerned about how stressed you are", "type": "Expressions"},
    {"question": "Phrase suggesting yoga or meditation might help stress.", "options": ["It might be a good idea to try yoga and meditation", "You seem to have the weight of the world on your shoulders", "Tell me, what's the matter with you?"], "correct_answer": "It might be a good idea to try yoga and meditation", "type": "Expressions"},
    {"question": "To 'take something for granted' means to...", "options": ["Fail to appreciate it", "Understand it completely", "Accept a gift"], "correct_answer": "Fail to appreciate it", "type": "Expressions"}, # From Image 1 example
    {"question": "To 'cope with' something means to...", "options": ["Deal effectively with difficulties", "Avoid a situation", "Complain about problems"], "correct_answer": "Deal effectively with difficulties", "type": "Expressions"}, # From Image 3 Vocab
    {"question": "To feel 'at ease' means to feel...", "options": ["Comfortable and relaxed", "Anxious and nervous", "Slightly ill"], "correct_answer": "Comfortable and relaxed", "type": "Expressions"}, # From Image 3 Vocab
    {"question": "To 'stem from' means to...", "options": ["Originate from or be caused by", "Stop something from growing", "Support a plant"], "correct_answer": "Originate from or be caused by", "type": "Expressions"}, # From Image 3 Vocab
    {"question": "To 'hunch over' means to...", "options": ["Bend forward and down", "Stand up straight", "Look over your shoulder"], "correct_answer": "Bend forward and down", "type": "Expressions"}, # From Image 3 Vocab
    {"question": "'Knackered' is informal British English for...", "options": ["Very tired", "Very happy", "Very angry"], "correct_answer": "Very tired", "type": "Expressions"}, # From Image 3 Vocab
    {"question": "A 'pep talk' is intended to...", "options": ["Make someone feel more courageous or enthusiastic", "Calm someone down", "Explain a complex topic"], "correct_answer": "Make someone feel more courageous or enthusiastic", "type": "Expressions"}, # From Image 3 Example
    {"question": "To 'believe in' yourself means to...", "options": ["Have confidence in your own abilities", "Follow a religion", "Trust other people"], "correct_answer": "Have confidence in your own abilities", "type": "Expressions"}, # From Image 3 Example
    {"question": "A 'breath of fresh air' refers to something that is...", "options": ["New, refreshing, and different", "Polluted air", "A type of exercise"], "correct_answer": "New, refreshing, and different", "type": "Expressions"}, # From Image 2 Example (Reading text)
    {"question": "If 'it feels like a huge weight's been lifted', you feel...", "options": ["Greatly relieved", "Physically heavier", "Disappointed"], "correct_answer": "Greatly relieved", "type": "Expressions"}, # From Image 2 Example (Reading text)
    {"question": "If something 'is such a relief to hear', you feel...", "options": ["Happy because worry is removed", "Sad about the news", "Confused by information"], "correct_answer": "Happy because worry is removed", "type": "Expressions"}, # From Image 2 Example (Reading text)
    {"question": "If someone says 'you're on the up', they mean you are...", "options": ["Improving or recovering", "Going upstairs", "Feeling sad"], "correct_answer": "Improving or recovering", "type": "Expressions"}, # From Image 2 Example (Reading text)
    {"question": "If you 'got off very lucky', it means...", "options": ["You avoided a worse outcome", "You won the lottery", "You were punished lightly"], "correct_answer": "You avoided a worse outcome", "type": "Expressions"}, # From Image 2 Example (Reading text)
    {"question": "If a situation 'could have ended very badly', it was potentially...", "options": ["Dangerous or disastrous", "Slightly inconvenient", "Very boring"], "correct_answer": "Dangerous or disastrous", "type": "Expressions"}, # From Image 2 Example (Reading text)
    {"question": "To 'engage in' debate means to...", "options": ["Take part in it", "Avoid it", "Listen to it passively"], "correct_answer": "Take part in it", "type": "Expressions"}, # From Image 1 Example
    {"question": "Public 'involvement' means that the public is...", "options": ["Participating or included", "Excluded or ignored", "Only watching"], "correct_answer": "Participating or included", "type": "Expressions"}, # From Image 1 Example
    {"question": "If a decision is 'available due to a cancellation', it means...", "options": ["It became free because someone else cancelled", "It was never available", "It is available for a short time"], "correct_answer": "It became free because someone else cancelled", "type": "Expressions"}, # From Image 1 Example
    {"question": "To 'issue a statement' means to...", "options": ["Make an official announcement", "Ask a question", "Write a private note"], "correct_answer": "Make an official announcement", "type": "Expressions"}, # From Image 5 Example
    {"question": "A 'scoop' in journalism is...", "options": ["An exclusive news story", "An ice cream tool", "A type of camera lens"], "correct_answer": "An exclusive news story", "type": "Expressions"}, # From Image 5 Example
    {"question": "To 'fact-check' a story means to...", "options": ["Verify the information is accurate", "Add more opinions", "Make the story longer"], "correct_answer": "Verify the information is accurate", "type": "Expressions"}, # From Image 5 Example
    {"question": "To 'compare' the shows means to...", "options": ["Look for similarities and differences", "Watch them all", "Choose the best one"], "correct_answer": "Look for similarities and differences", "type": "Expressions"}, # From Image 5 Example
    {"question": "To 'state' the news means to...", "options": ["Report or declare it", "Hide it", "Question it"], "correct_answer": "Report or declare it", "type": "Expressions"}, # From Image 5 Example
    {"question": "A 'tabloid' often focuses on...", "options": ["Celebrity gossip and sensationalism", "Serious political analysis", "Academic research"], "correct_answer": "Celebrity gossip and sensationalism", "type": "Expressions"}, # From Image 5 Vocab
    {"question": "If news is 'widespread', it is...", "options": ["Known by many people over a large area", "A secret", "Only known locally"], "correct_answer": "Known by many people over a large area", "type": "Expressions"}, # From Image 5 Example

    # === Grammar: Gerund vs Infinitive (15 Questions - From Image 7) ===
    {"question": "Swimming ___ (be) my greatest hobby.", "options": ["is", "to be", "being"], "correct_answer": "is", "type": "Gerund/Infinitive"}, # Gerund as subject
    {"question": "I love ___ (talk) to my greatest hobby.", "options": ["talking", "to talk", "talk"], "correct_answer": "talking", "type": "Gerund/Infinitive"}, # After 'love' (often gerund)
    {"question": "Jane started ___ (take) lessons as soon as she came in.", "options": ["taking", "to take", "take"], "correct_answer": "taking", "type": "Gerund/Infinitive"}, # After 'start' (gerund common)
    {"question": "Please take off your shoes before ___ (enter) the room.", "options": ["entering", "to enter", "enter"], "correct_answer": "entering", "type": "Gerund/Infinitive"}, # After preposition 'before'
    {"question": "It's no use ___ (try) to convince him.", "options": ["trying", "to try", "try"], "correct_answer": "trying", "type": "Gerund/Infinitive"}, # After 'It's no use'
    {"question": "We decided ___ (learn) to manage the project.", "options": ["to learn", "learning", "learn"], "correct_answer": "to learn", "type": "Gerund/Infinitive"}, # After 'decide'
    {"question": "I would love ___ (help) you, but I can't.", "options": ["to help", "helping", "help"], "correct_answer": "to help", "type": "Gerund/Infinitive"}, # After 'would love'
    {"question": "Do you remember ___ (close) the door when you leave?", "options": ["to close", "closing", "close"], "correct_answer": "to close", "type": "Gerund/Infinitive"}, # Remember + task/future
    {"question": "They don't remember ___ (meet) you.", "options": ["meeting", "to meet", "meet"], "correct_answer": "meeting", "type": "Gerund/Infinitive"}, # Remember + past action/memory
    {"question": "I stopped ___ (smoke) last year.", "options": ["smoking", "to smoke", "smoke"], "correct_answer": "smoking", "type": "Gerund/Infinitive"}, # Stop an activity
    {"question": "He stopped ___ (ask) for directions.", "options": ["to ask", "asking", "ask"], "correct_answer": "to ask", "type": "Gerund/Infinitive"}, # Stop in order to do something else
    {"question": "Try ___ (press) the red button.", "options": ["pressing", "to press", "press"], "correct_answer": "pressing", "type": "Gerund/Infinitive"}, # Try as an experiment
    {"question": "He tried ___ (open) the window, but it was stuck.", "options": ["to open", "opening", "open"], "correct_answer": "to open", "type": "Gerund/Infinitive"}, # Try as an attempt/effort
    {"question": "She avoids ___ (speak) about her past.", "options": ["speaking", "to speak", "speak"], "correct_answer": "speaking", "type": "Gerund/Infinitive"}, # After 'avoid'
    {"question": "He promised ___ (finish) the report by Friday.", "options": ["to finish", "finishing", "finish"], "correct_answer": "to finish", "type": "Gerund/Infinitive"}, # After 'promise'

    # === Grammar: Let, Allow, Have, Make (15 Questions - From Image 6) ===
    {"question": "We're going to let the dove ___ (go).", "options": ["go", "to go", "going"], "correct_answer": "go", "type": "Let/Allow/Have/Make"}, # Let + infinitive
    {"question": "Let me ___ (try) to fix your bike for you.", "options": ["try", "to try", "trying"], "correct_answer": "try", "type": "Let/Allow/Have/Make"}, # Let + infinitive
    {"question": "OK, I will allow you ___ (go) to the cinema.", "options": ["to go", "go", "going"], "correct_answer": "to go", "type": "Let/Allow/Have/Make"}, # Allow + to infinitive
    {"question": "My parents finally allowed me ___ (stay) out later.", "options": ["to stay", "stay", "staying"], "correct_answer": "to stay", "type": "Let/Allow/Have/Make"}, # Allow + to infinitive
    {"question": "Have John ___ (fix) your bike for you.", "options": ["fix", "to fix", "fixing"], "correct_answer": "fix", "type": "Let/Allow/Have/Make"}, # Have (causative) + infinitive
    {"question": "He has Brenda ___ (cook) his dinners for him.", "options": ["cook", "to cook", "cooking"], "correct_answer": "cook", "type": "Let/Allow/Have/Make"}, # Have (causative) + infinitive
    {"question": "Don't make me ___ (walk) all the way back!", "options": ["walk", "to walk", "walking"], "correct_answer": "walk", "type": "Let/Allow/Have/Make"}, # Make + infinitive
    {"question": "The coach always makes us ___ (do) fifty push-ups.", "options": ["do", "to do", "doing"], "correct_answer": "do", "type": "Let/Allow/Have/Make"}, # Make + infinitive
    {"question": "Are we ___ to park here?", "options": ["allowed", "let", "made"], "correct_answer": "allowed", "type": "Let/Allow/Have/Make"}, # Passive allow
    {"question": "They won't ___ us use the front entrance.", "options": ["let", "allow", "make"], "correct_answer": "let", "type": "Let/Allow/Have/Make"}, # Let for permission
    {"question": "The manager ___ the team work overtime.", "options": ["made", "let", "had"], "correct_answer": "made", "type": "Let/Allow/Have/Make"}, # Make for compel/force
    {"question": "Can you ___ the technician check the wiring?", "options": ["have", "make", "allow"], "correct_answer": "have", "type": "Let/Allow/Have/Make"}, # Have for arrange/causative
    {"question": "My teacher doesn't ___ us chew gum in class.", "options": ["allow", "make", "let"], "correct_answer": "allow", "type": "Let/Allow/Have/Make"}, # Allow (formal) + to infinitive (implied)
    {"question": "I was ___ to choose my own project topic.", "options": ["allowed", "let", "made"], "correct_answer": "allowed", "type": "Let/Allow/Have/Make"}, # Passive allow
    {"question": "They ___ him repeat the whole story.", "options": ["made", "let", "had"], "correct_answer": "made", "type": "Let/Allow/Have/Make"}, # Make for compel/force

    # === Grammar: Present Tenses (15 Questions - From Image 8) ===
    {"question": "The sun ___ (set) in the west.", "options": ["sets", "is setting", "has set"], "correct_answer": "sets", "type": "Present Tenses"}, # Simple: Fact
    {"question": "We usually ___ (watch) the news at nine.", "options": ["watch", "are watching", "have watched"], "correct_answer": "watch", "type": "Present Tenses"}, # Simple: Habit/Routine
    {"question": "___ you ___ (watch) this programme now?", "options": ["Are...watching", "Do...watch", "Have...watched"], "correct_answer": "Are...watching", "type": "Present Tenses"}, # Continuous: Happening now
    {"question": "Jack is always ___ (shout) at me.", "options": ["shouting", "shouts", "has shouted"], "correct_answer": "shouting", "type": "Present Tenses"}, # Continuous: Annoyance with 'always'
    {"question": "Sheila ___ (want) to be a pop star.", "options": ["wants", "is wanting", "has wanted"], "correct_answer": "wants", "type": "Present Tenses"}, # Simple: Stative verb 'want'
    {"question": "I ___ (not feel) good. Can I go home?", "options": ["don't feel", "am not feeling", "haven't felt"], "correct_answer": "don't feel", "type": "Present Tenses"}, # Simple: Stative verb 'feel' (state)
    {"question": "I ___ (see / hear) things.", "options": ["am seeing / hearing", "see / hear", "have seen / heard"], "correct_answer": "am seeing / hearing", "type": "Present Tenses"}, # Continuous: Sensory verbs used actively (implies hallucination/imagination)
    {"question": "The dog ___ (smell) the tree.", "options": ["is smelling", "smells", "has smelled"], "correct_answer": "is smelling", "type": "Present Tenses"}, # Continuous: Action in progress
    {"question": "He ___ (work) here for five years.", "options": ["has worked", "works", "is working"], "correct_answer": "has worked", "type": "Present Tenses"}, # Perfect: Started in past, continues now
    {"question": "They ___ (just / arrive) from their trip.", "options": ["have just arrived", "just arrive", "are just arriving"], "correct_answer": "have just arrived", "type": "Present Tenses"}, # Perfect: Recently completed action
    {"question": "I ___ (never / visit) Paris.", "options": ["have never visited", "never visit", "am never visiting"], "correct_answer": "have never visited", "type": "Present Tenses"}, # Perfect: Life experience
    {"question": "Look! That man ___ (try) to open your car door.", "options": ["is trying", "tries", "has tried"], "correct_answer": "is trying", "type": "Present Tenses"}, # Continuous: Happening now
    {"question": "Water ___ (freeze) at 0 degrees Celsius.", "options": ["freezes", "is freezing", "has frozen"], "correct_answer": "freezes", "type": "Present Tenses"}, # Simple: Fact
    {"question": "She often ___ (go) to the gym in the mornings.", "options": ["goes", "is going", "has gone"], "correct_answer": "goes", "type": "Present Tenses"}, # Simple: Habit/Routine
    {"question": "What ___ (you / read) at the moment?", "options": ["are you reading", "do you read", "have you read"], "correct_answer": "are you reading", "type": "Present Tenses"}, # Continuous: Happening now (at the moment)
]

# Shuffle the questions initially
random.shuffle(questions)

# --- Mediapipe Hand Tracking Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    model_complexity=1 # Use 1 for better performance balance
)
mp_drawing = mp.solutions.drawing_utils # To draw landmarks (optional)

# --- Webcam Setup ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open webcam.")
    pygame.quit()
    sys.exit()

ret, test_frame = cap.read()
if not ret:
    print("Error: Cannot read from webcam.")
    cap.release()
    pygame.quit()
    sys.exit()
cam_frame_height, cam_frame_width, _ = test_frame.shape

# --- Helper Functions ---
def get_landmark_distance(landmark1, landmark2):
    # Check if landmarks are valid
    if landmark1 is None or landmark2 is None or not hasattr(landmark1, 'x') or not hasattr(landmark2, 'x'):
        return float('inf') # Return a large distance if invalid
    x1, y1 = landmark1.x, landmark1.y
    x2, y2 = landmark2.x, landmark2.y
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def draw_text(text, font, color, surface, x, y, center=True, max_width=None):
    if max_width:
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            # Check width with the word added
            test_line_obj = font.render(current_line + word + " ", True, color)
            if test_line_obj.get_width() <= max_width:
                current_line += word + " "
            # If adding the word makes it too long
            else:
                 # Add the previous line (if not empty)
                if current_line:
                    lines.append(current_line.strip())
                # Start new line with the current word. Handle very long words.
                word_obj = font.render(word + " ", True, color)
                if word_obj.get_width() > max_width:
                     # Simple wrap for extremely long words (split crudely)
                     can_fit = ""
                     remaining = word
                     while font.render(remaining + " ", True, color).get_width() > max_width and len(remaining) > 1:
                         found_split = False
                         for i in range(len(remaining)-1, 0, -1):
                              if font.render(remaining[:i] + " ", True, color).get_width() <= max_width:
                                   lines.append(remaining[:i])
                                   remaining = remaining[i:]
                                   found_split = True
                                   break
                         if not found_split: # Word is just too long, force break
                             lines.append(remaining[0])
                             remaining=remaining[1:]

                     current_line = remaining + " "

                else:
                    current_line = word + " "

        lines.append(current_line.strip()) # Add the last line

        rendered_lines = [font.render(line, True, color) for line in lines if line] # Filter empty lines
        total_height = sum(line.get_height() for line in rendered_lines)

        current_y = y - total_height // 2 if center else y

        final_rects = []
        for i, textobj in enumerate(rendered_lines):
             textrect = textobj.get_rect()
             if center:
                 textrect.centerx = x
             else:
                 textrect.left = x
             textrect.top = current_y
             surface.blit(textobj, textrect)
             final_rects.append(textrect)
             current_y += textobj.get_height()

        # Return a combined rect for positioning reference (approximate)
        if final_rects:
             combined_rect = final_rects[0].unionall(final_rects[1:])
             return combined_rect
        else:
             return pygame.Rect(x, y, 0, 0)


    else: # No wrapping needed
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        if center:
            textrect.center = (x, y)
        else:
            textrect.topleft = (x, y)
        surface.blit(textobj, textrect)
        return textrect


# --- Pop Particle Class ---
class PopParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(POP_PARTICLE_SPEED * 0.5, POP_PARTICLE_SPEED)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = POP_PARTICLE_LIFE
        self.radius = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1 # Slight gravity effect
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, min(255, int(255 * (self.life / POP_PARTICLE_LIFE))))
            # Create a temporary surface for alpha drawing
            temp_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, self.color + (alpha,), (self.radius, self.radius), self.radius)
            surface.blit(temp_surf, (int(self.x - self.radius), int(self.y - self.radius)))

# --- Balloon Class ---
class Balloon:
    def __init__(self, x, y, radius, color, speed, text="", is_correct=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.width = int(radius * BALLOON_ASPECT_RATIO * 2)
        self.height = radius * 2
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
        self.color = color
        self.highlight_color = tuple(min(255, c + 50) for c in color) # Less intense highlight
        self.speed = speed
        self.text = text
        self.is_correct = is_correct
        self.popped = False
        self.pop_particles = []

    def move(self):
        if not self.popped:
            self.y -= self.speed
            self.rect.centery = int(self.y)

    def draw(self, surface):
        if self.popped:
            for particle in self.pop_particles:
                particle.update()
                particle.draw(surface)
            self.pop_particles = [p for p in self.pop_particles if p.life > 0]
        else:
            # Draw Balloon Body
            pygame.draw.ellipse(surface, self.color, self.rect)

            # Draw Highlight
            highlight_rect = self.rect.copy()
            highlight_rect.width = int(self.width * 0.4)
            highlight_rect.height = int(self.height * 0.4)
            highlight_rect.centerx = self.rect.centerx - int(self.width * 0.18)
            highlight_rect.centery = self.rect.centery - int(self.height * 0.18)
            pygame.draw.ellipse(surface, self.highlight_color, highlight_rect)

            # Draw Knot and String
            knot_y = self.rect.bottom
            knot_size = max(5, int(self.radius * 0.1))
            p1 = (self.rect.centerx - knot_size, knot_y)
            p2 = (self.rect.centerx + knot_size, knot_y)
            p3 = (self.rect.centerx, knot_y + knot_size)
            pygame.draw.polygon(surface, GRAY, [p1, p2, p3])
            string_end_y = knot_y + knot_size + int(self.radius * 0.5)
            pygame.draw.line(surface, LIGHT_GRAY, (self.rect.centerx, knot_y + knot_size), (self.rect.centerx, string_end_y), 2)

            # Draw Text on Balloon
            draw_text(self.text, balloon_font, BALLOON_TEXT_COLOR, surface, self.rect.centerx, self.rect.centery, center=True, max_width=self.width * 0.85)


    def is_offscreen(self):
        # Consider popped balloons with finished animations as offscreen for cleanup
        return self.rect.bottom < -self.height or (self.popped and not self.pop_particles) # Check further offscreen

    def check_pop(self, cursor_x, cursor_y):
        if self.popped:
            return False
        # Use ellipse collision check for better accuracy
        if self.rect.collidepoint(cursor_x, cursor_y):
             # Check if point is inside the ellipse equation: (dx/a)^2 + (dy/b)^2 <= 1
             dx = cursor_x - self.rect.centerx
             dy = cursor_y - self.rect.centery
             a = self.width / 2
             b = self.height / 2
             # Avoid division by zero if balloon somehow has zero size
             if a > 0 and b > 0 and (dx / a)**2 + (dy / b)**2 <= 1:
                 self.popped = True
                 self.create_pop_particles()
                 return True # Return confirmation of pop
        return False

    def create_pop_particles(self):
        particle_color = FEEDBACK_CORRECT_COLOR if self.is_correct else FEEDBACK_INCORRECT_COLOR
        for _ in range(POP_PARTICLE_COUNT):
             # Spawn particles slightly away from center for better effect
             offset_x = random.uniform(-self.width * 0.1, self.width * 0.1)
             offset_y = random.uniform(-self.height * 0.1, self.height * 0.1)
             self.pop_particles.append(PopParticle(self.rect.centerx + offset_x, self.rect.centery + offset_y, particle_color))

    def is_animation_done(self):
        return self.popped and not self.pop_particles

# --- Smoothed Hand Position Thread ---
class HandPositionThread(threading.Thread):
    def __init__(self, screen_w, screen_h):
        super().__init__()
        self.daemon = True
        self.target_x, self.target_y = screen_w // 2, screen_h // 2
        self.current_x, self.current_y = float(self.target_x), float(self.target_y) # Use float for smoother calcs
        self.screen_width = screen_w
        self.screen_height = screen_h
        self.running = True
        self.active = False
        self.lock = threading.Lock()
        self.smoothing_factor = 0.18 # Adjust for more/less smoothing

    def run(self):
        while self.running:
            if self.active:
                with self.lock:
                    # Basic linear interpolation (lerp) for smoothing
                    self.current_x += (self.target_x - self.current_x) * self.smoothing_factor
                    self.current_y += (self.target_y - self.current_y) * self.smoothing_factor
                time.sleep(0.005) # Sleep briefly to yield CPU
            else:
                time.sleep(0.1) # Sleep longer when inactive

    def update_target(self, x_rel, y_rel):
        with self.lock:
            # Map relative coordinates (0.0-1.0) to screen pixels
            # Flip x coordinate if camera is mirrored compared to screen
            self.target_x = int((1.0 - x_rel) * self.screen_width) # Flipping X assumed
            self.target_y = int(y_rel * self.screen_height)
            # Clamp values to screen bounds
            self.target_x = np.clip(self.target_x, 0, self.screen_width - 1)
            self.target_y = np.clip(self.target_y, 0, self.screen_height - 1)

    def get_position(self):
        with self.lock:
            # Return integer positions for drawing
            return int(self.current_x), int(self.current_y)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def stop(self):
        self.running = False

# --- Global Game Variables ---
game_state = GAME_STATE_MENU
current_question_index = -1
current_question_data = None
active_balloons = [] # Will hold dicts for pending, Balloon objects for active/popped
score = 0
hand_position_thread = HandPositionThread(SCREEN_WIDTH, SCREEN_HEIGHT)
hand_position_thread.start()
was_pinching = False # Tracks hand pinch state
pinch_threshold = 0.06 # Initial threshold
adaptive_threshold_factor = 0.19 # Factor based on hand size
feedback_text = ""
feedback_color = WHITE
feedback_timer = 0.0
question_answered_this_frame = False # Prevent multiple pops on one pinch


# --- Main Loop ---
running = True
try:
    while running:
        # --- Event Handling ---
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GAME_STATE_PLAYING or game_state == GAME_STATE_GAME_OVER:
                         game_state = GAME_STATE_MENU
                         # Reset game state fully when returning to menu
                         active_balloons = []
                         score = 0
                         current_question_index = -1
                         current_question_data = None
                         feedback_timer = 0
                         was_pinching = False
                         random.shuffle(questions) # Reshuffle for next game
                    else: # Already in menu
                         running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    mouse_clicked = True

        # --- Background Processing (Camera and Hand Tracking) ---
        ret, frame = cap.read()
        hand_landmarks = None # Store landmarks for the primary hand
        if ret:
            # DO NOT FLIP HERE - Flipping handled in target update
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False # Optimize processing
            results = hands.process(rgb_frame)
            rgb_frame.flags.writeable = True

            # --- Hand Detection and Control Update ---
            current_pinch_gesture = False
            hand_detected_this_frame = False
            if results.multi_hand_landmarks:
                hand_detected_this_frame = True
                # Use the first detected hand
                hand_landmarks = results.multi_hand_landmarks[0]

                # Use Index Finger Tip for cursor position
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                hand_position_thread.update_target(index_finger_tip.x, index_finger_tip.y)

                # Calculate pinch distance (Thumb tip to Index finger tip)
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_thumb_distance = get_landmark_distance(index_finger_tip, thumb_tip)

                # Adaptive Threshold based on hand size (Wrist to Middle Finger MCP)
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP] # Use MCP for stability
                hand_size = get_landmark_distance(wrist, middle_finger_mcp)

                # Set adaptive threshold, with a fallback and minimum
                if hand_size > 0.01: # Avoid division by zero or tiny values
                    adaptive_click_threshold = max(0.03, adaptive_threshold_factor * hand_size) # Ensure a minimum threshold
                else:
                    adaptive_click_threshold = pinch_threshold # Fallback

                # Check for pinch gesture
                if index_thumb_distance < adaptive_click_threshold:
                    current_pinch_gesture = True

            else:
                hand_detected_this_frame = False

            # Activate/Deactivate hand tracking thread
            if hand_detected_this_frame and not hand_position_thread.active:
                hand_position_thread.activate()
            elif not hand_detected_this_frame and hand_position_thread.active:
                hand_position_thread.deactivate()

        else:
            # Handle frame read error - maybe show a warning on screen?
            print("Warning: Failed to read frame from camera.")
            current_pinch_gesture = False
            hand_detected_this_frame = False
            if hand_position_thread.active:
                hand_position_thread.deactivate()
            time.sleep(0.05)


        # --- Get Hand Cursor Position and Detect Pinch Start ---
        cursor_x, cursor_y = hand_position_thread.get_position()
        # Pinch start: Is pinching now, but wasn't pinching last frame
        is_pinching_this_frame = current_pinch_gesture and not was_pinching
        question_answered_this_frame = False # Reset flag each frame

        # --- Game State Logic ---
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

        if game_state == GAME_STATE_MENU:
            screen.fill(SKY_BLUE)
            draw_text('Unit 5 - English Game!', menu_font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)

            # --- Menu Buttons ---
            button_width = 350
            button_height = 90
            start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2, button_width, button_height)
            quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height + 20, button_width, button_height)

            # Highlight based on MOUSE or HAND cursor
            start_hover = start_button_rect.collidepoint(mouse_pos) or (hand_position_thread.active and start_button_rect.collidepoint(cursor_x, cursor_y))
            quit_hover = quit_button_rect.collidepoint(mouse_pos) or (hand_position_thread.active and quit_button_rect.collidepoint(cursor_x, cursor_y))

            start_color = MENU_HIGHLIGHT_COLOR if start_hover else GRAY
            quit_color = MENU_HIGHLIGHT_COLOR if quit_hover else GRAY

            pygame.draw.rect(screen, start_color, start_button_rect, border_radius=15)
            pygame.draw.rect(screen, quit_color, quit_button_rect, border_radius=15)

            draw_text('Start Game', button_font, MENU_TEXT_COLOR, screen, start_button_rect.centerx, start_button_rect.centery)
            draw_text('Quit', button_font, MENU_TEXT_COLOR, screen, quit_button_rect.centerx, quit_button_rect.centery)

            # --- Menu Interaction ---
            start_clicked = (mouse_clicked and start_hover) or (is_pinching_this_frame and start_hover and hand_position_thread.active)
            quit_clicked = (mouse_clicked and quit_hover) or (is_pinching_this_frame and quit_hover and hand_position_thread.active)

            if start_clicked:
                game_state = GAME_STATE_PLAYING
                current_question_index = -1 # Start from the beginning
                score = 0
                active_balloons = []
                feedback_timer = 0
                was_pinching = False # Reset pinch state
            elif quit_clicked:
                running = False

            # Draw Hand Cursor in Menu
            if hand_position_thread.active:
                 pygame.draw.circle(screen, CURSOR_COLOR, (cursor_x, cursor_y), CURSOR_RADIUS)
                 pygame.draw.circle(screen, WHITE, (cursor_x, cursor_y), CURSOR_RADIUS, 2)


        elif game_state == GAME_STATE_PLAYING:
            # --- Game Logic ---
            screen.fill(SKY_BLUE) # Background

            # --- Question Handling ---
            if current_question_data is None and current_question_index < len(questions) - 1 and feedback_timer <= 0:
                # Load next question only if previous feedback is done
                current_question_index += 1
                current_question_data = questions[current_question_index]
                active_balloons = [] # Clear previous answer balloons
                feedback_timer = 0 # Clear feedback

                # Prepare answer options
                options = current_question_data["options"][:] # Make a copy
                correct_answer = current_question_data["correct_answer"]
                # Ensure NUM_ANSWER_BALLOONS is not more than available options
                num_options_to_show = min(NUM_ANSWER_BALLOONS, len(options))

                display_options = []
                if correct_answer in options:
                    display_options.append(correct_answer)
                    options.remove(correct_answer) # Remove correct from pool
                else:
                     print(f"Warning: Correct answer '{correct_answer}' not found in options for question: {current_question_data['question']}")
                     # Add the first option if correct is missing and options exist
                     if options:
                         correct_answer = options[0] # Assume first is correct for this case
                         display_options.append(correct_answer)
                         options.pop(0)


                # Fill remaining slots with distractors
                num_distractors_needed = num_options_to_show - len(display_options)
                random.shuffle(options) # Shuffle distractors
                display_options.extend(options[:num_distractors_needed])

                # Shuffle the final list for display
                random.shuffle(display_options)

                # Spawn answer balloons with a delay
                spawn_time_offset = 0
                for i, option_text in enumerate(display_options):
                    is_correct = (option_text == correct_answer)
                    radius = random.randint(BALLOON_RADIUS_MIN, BALLOON_RADIUS_MAX)
                    # Spread balloons horizontally more evenly
                    x_pos = int(SCREEN_WIDTH * (i + 1) / (num_options_to_show + 1) + random.randint(-30, 30)) # Add jitter
                    y_pos = SCREEN_HEIGHT + radius + random.randint(0, 50) # Start slightly off-screen
                    color = random.choice(BALLOON_COLORS)
                    speed = random.uniform(BALLOON_SPEED_MIN, BALLOON_SPEED_MAX)

                    new_balloon = Balloon(x_pos, y_pos, radius, color, speed, option_text, is_correct)

                    # Store balloon and its intended spawn time
                    active_balloons.append({"balloon": new_balloon, "spawn_at": time.time() + spawn_time_offset})
                    spawn_time_offset += BALLOON_SPAWN_DELAY

            elif current_question_data is None and current_question_index >= len(questions) - 1 and feedback_timer <= 0:
                 # Game Over condition: All questions answered and last feedback finished
                 # Check if any active or pending balloons remain
                 if not any(isinstance(item, Balloon) or (isinstance(item, dict) and time.time() < item.get("spawn_at", float('inf'))) for item in active_balloons):
                     game_state = GAME_STATE_GAME_OVER


            # --- Balloon Spawning, Movement, and Popping ---
            current_time = time.time()
            next_active_balloons = [] # Build the list for the next frame

            for item in active_balloons:
                 if isinstance(item, dict): # It's a pending balloon dictionary
                      if current_time >= item["spawn_at"]:
                           next_active_balloons.append(item["balloon"]) # Add the Balloon object
                      else:
                           next_active_balloons.append(item) # Keep the dict
                 elif isinstance(item, Balloon): # It's an active Balloon object
                    item.move()

                    # Check for pop only if hand is active, no other pop this frame, and feedback not showing
                    if hand_position_thread.active and is_pinching_this_frame and feedback_timer <= 0 and not question_answered_this_frame:
                        if item.check_pop(cursor_x, cursor_y):
                            question_answered_this_frame = True # Prevent multiple pops per pinch
                            if item.is_correct:
                                score += 1
                                feedback_text = "Correct!"
                                feedback_color = FEEDBACK_CORRECT_COLOR
                            else:
                                # Ensure correct_answer is available before showing it
                                correct_ans_text = current_question_data.get('correct_answer', 'N/A') if current_question_data else 'N/A'
                                feedback_text = f"Incorrect! Answer: {correct_ans_text}"
                                feedback_color = FEEDBACK_INCORRECT_COLOR

                            feedback_timer = FEEDBACK_DISPLAY_TIME # Start feedback timer

                    # Keep balloon if not offscreen OR if popped but animation still running
                    if not item.is_offscreen():
                        next_active_balloons.append(item)
                    elif item.popped and not item.is_animation_done():
                         next_active_balloons.append(item) # Keep until animation finishes

            active_balloons = next_active_balloons # Update the list for the next frame

            # --- Drawing ---
            # Draw active/popped balloons
            for item in active_balloons:
                 if isinstance(item, Balloon): # Only draw Balloon objects
                    item.draw(screen)

            # Draw Question Box (only if a question is loaded)
            if current_question_data:
                 q_area_height = 120 # Increased height for question text
                 q_rect = pygame.Rect(40, 15, SCREEN_WIDTH - 80, q_area_height)
                 # Draw semi-transparent background
                 s = pygame.Surface((q_rect.width, q_rect.height), pygame.SRCALPHA)
                 s.fill(QUESTION_BG_COLOR)
                 screen.blit(s, q_rect.topleft)
                 # Draw border
                 pygame.draw.rect(screen, WHITE, q_rect, 2, border_radius=10)
                 # Draw question text (wrapped)
                 draw_text(f"{current_question_index+1}/{len(questions)}. {current_question_data['question']}",
                           question_font, WHITE, screen, q_rect.centerx, q_rect.centery,
                           center=True, max_width=q_rect.width - 40) # Padding

            # Draw Score
            draw_text(f"Score: {score}", score_font, WHITE, screen, SCREEN_WIDTH - 150, 40, center=True)

            # Draw Feedback (if timer is active)
            if feedback_timer > 0:
                # Draw a semi-transparent overlay to dim the background slightly during feedback
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, (0, 0))
                # Draw the feedback text on top
                draw_text(feedback_text, feedback_font, feedback_color, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True, max_width=SCREEN_WIDTH * 0.8)
                feedback_timer -= dt
                if feedback_timer <= 0:
                    # Feedback time is over, signal to load next question by clearing current data
                    current_question_data = None
                    # Force clear remaining balloons for the answered question immediately
                    active_balloons = [item for item in active_balloons if isinstance(item, dict)] # Keep only pending ones


            # Draw Hand Cursor
            if hand_position_thread.active:
                 pygame.draw.circle(screen, CURSOR_COLOR, (cursor_x, cursor_y), CURSOR_RADIUS)
                 pygame.draw.circle(screen, WHITE, (cursor_x, cursor_y), CURSOR_RADIUS + 1, 2) # Slightly larger outline

        elif game_state == GAME_STATE_GAME_OVER:
             # Simple Game Over Screen
             screen.fill(SKY_BLUE)
             draw_text("Game Over!", menu_font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
             draw_text(f"Final Score: {score} / {len(questions)}", score_font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
             draw_text("Press ESC to return to Menu", score_font, GRAY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
             # ESC key handling is already in the main event loop


        # --- Update Pinch State for Next Frame ---
        was_pinching = current_pinch_gesture

        # --- Update Display ---
        pygame.display.flip()
        # clock is managed via dt calculation

finally:
    # --- Cleanup ---
    print("Exiting...")
    hand_position_thread.stop()
    # Wait for thread to finish
    if 'hand_position_thread' in locals() and hand_position_thread.is_alive():
         print("Waiting for hand thread to join...")
         hand_position_thread.join(timeout=1.0) # Wait up to 1 second
         if hand_position_thread.is_alive():
             print("Hand thread did not join cleanly.")
    # Release camera
    if 'cap' in locals() and cap.isOpened():
        print("Releasing camera...")
        cap.release()
    # Close Mediapipe hands
    if 'hands' in locals():
        print("Closing Mediapipe hands...")
        hands.close()
    # Quit Pygame
    print("Quitting Pygame...")
    pygame.quit()
    print(f"Final Score: {score}")
    # Exit Python script
    print("Exiting script.")
    sys.exit()