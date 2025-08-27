import sys
import threading
import time
import re
import json
import os
from datetime import datetime, timedelta
from PIL import Image, ImageOps, ImageFilter
import mss
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFrame, QScrollArea, QSizePolicy, QColorDialog, QDialog,
    QMessageBox, QTabWidget, QComboBox, QGroupBox, QFormLayout, 
    QListWidget, QLineEdit, QInputDialog, QDialogButtonBox, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QMouseEvent, QKeyEvent, QImage, QPixmap, QFont
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import hashlib
import socket
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
import getpass
import cv2
import easyocr
import torch

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

print(torch.cuda.is_available())

# Initialize Firebase
def initialize_firebase():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(script_dir, "firebase_key.json")
        if not os.path.exists(key_path):
            print(f"FATAL: firebase_key.json not found at {key_path}")
            return None
        # Prevent double initialization
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully.")
        return firestore.client()
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

# Initialize Firestore
db = initialize_firebase()
if db is None:
    print("FATAL: Firestore client could not be initialized. Exiting.")
    input("Press Enter to exit...")
    sys.exit(1)

# Globals for managing bot threads/processes
bot_threads = {}
bot_running = {
    "Scale": False,
    "Pro": False,
    "Reset": False
}
bot_instances = {
    "Scale": None,
    "Pro": None,
    "Reset": None
}

# Globals for codes tracking
codes_found = 0
counts = {
    "Scale": 0,
    "Pro": 0,
    "Reset": 0
}
found_codes_history = []

# Global for OCR region - will be loaded from config
current_ocr_region = QRect(5, 836, 1388, 112)  # Default region: x, y, width, height

# Add global variables for settings
trim_after_50_enabled = True
trim_after_25_enabled = False
show_ocr_raw_enabled = False
smart_fix_ending_enabled = True
smart_fix_ss_to_55_enabled = False
smart_fix_2s_to_25_enabled = False
smart_fix_digit_o_to_digit0_enabled = False
reverse_code_if_instructed_enabled = True
auto_remove_coupon_code_enabled = True
underscore_to_t_enabled = False
dictionary_underscore_enabled = True  # Enable by default

# Initialize EasyOCR globally
easyocr_reader = easyocr.Reader(['en'], gpu=True)

# Add global variables for underscore replacement tracking
underscore_replacements = ['T', 'N', 'S']
current_replacement_index = 0
last_attempted_code = None

# Build the master word dictionary
common_words_500 = [
    "THE","BE","AND","OF","A","IN","TO","HAVE","IT","I","THAT","FOR","YOU","HE","WITH","ON","DO","SAY","THIS","THEY",
    "AT","BUT","WE","HIS","FROM","THAT","NOT","CAN","WILL","BY","SHE","OR","AS","WHAT","GO","THEIR","GET","IF","ME",
    "WHEN","MAKE","CAN","LIKE","TIME","NO","JUST","HIM","KNOW","TAKE","PEOPLE","INTO","YEAR","YOUR","GOOD","SOME",
    "COULD","THEM","SEE","OTHER","THAN","THEN","NOW","LOOK","ONLY","COME","ITS","OVER","THINK","ALSO","BACK","AFTER",
    "USE","TWO","HOW","OUR","WORK","FIRST","WELL","WAY","EVEN","NEW","WANT","BECAUSE","ANY","THESE","GIVE","DAY",
    "MOST","US","IS","ARE","WAS","WERE","HAS","HAD","DOES","DID","SAYS","SAID","SHOULD","WOULD","MUST","MAY","MIGHT",
    "CAN'T","DON'T","WON'T","I'M","YOU'RE","HE'S","SHE'S","IT'S","WE'RE","THEY'RE","MY","YOUR","HIS","HER","ITS",
    "OUR","THEIR","ME","YOU","HIM","HER","US","THEM","WHAT","WHO","WHOM","WHERE","WHEN","WHY","HOW","ALL","ANY",
    "EVERY","SOME","NO","NONE","ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","TEN","BIG","SMALL",
    "LONG","SHORT","HIGH","LOW","NEW","OLD","GOOD","BAD","RIGHT","WRONG","EASY","HARD","FAST","SLOW","HOT","COLD",
    "RED","BLUE","GREEN","YELLOW","BLACK","WHITE","DAY","NIGHT","MORNING","EVENING","SUN","MOON","STAR","WATER",
    "FIRE","AIR","EARTH","TREE","FLOWER","GRASS","BIRD","DOG","CAT","FISH","HOUSE","HOME","CAR","ROAD","CITY",
    "COUNTRY","STREET","MARKET","SHOP","SCHOOL","BOOK","PEN","TABLE","CHAIR","DOOR","WINDOW","FOOD","DRINK",
    "APPLE","BREAD","MILK","MEAT","FISH","RICE","SUGAR","SALT","SWEET","BITTER","SALTY","HAPPY","SAD","ANGRY",
    "LOVE","HATE","LIKE","FEEL","SEE","HEAR","TASTE","SMELL","TOUCH","RUN","WALK","JUMP","SIT","STAND","SLEEP",
    "WAKE","EAT","DRINK","SAY","TALK","SING","DANCE","PLAY","WORK","HELP","WAIT","LOOK","WATCH","LISTEN","READ",
    "WRITE","BUY","SELL","GIVE","TAKE","OPEN","CLOSE","LOVE","HATE","LIKE","DISLIKE","NEED","WANT","USE","MAKE",
    "BREAK","BUILD","CREATE","DESTROY","COME","GO","LEAVE","STAY","BEGIN","END","WIN","LOSE","FIND","LOST","ASK",
    "ANSWER","CALL","REPLY","WAIT","HELP","STOP","START","CHANGE","KEEP","MOVE","TURN","FALL","RISE","LIVE","DIE",
    "LOVE","HATE","HOPE","FEAR","TRUST","DOUBT","SUCCESS","FAILURE","POWER","WEAKNESS","FREEDOM","PRISON",
    "PEACE","WAR","JOY","PAIN","LAUGHTER","TEARS","SUN","RAIN","SNOW","WIND","STORM","SEA","RIVER","LAKE","MOUNTAIN",
    "VALLEY","FOREST","DESERT","ISLAND","OCEAN","ROAD","PATH","BRIDGE","CITY","VILLAGE","TOWN","HOUSE","BUILDING",
    "ROOM","FLOOR","WALL","CEILING","DOOR","WINDOW","FURNITURE","TABLE","CHAIR","BED","COUCH","BOOK","PEN",
    "PAPER","PHONE","COMPUTER","TABLET","LAMP","CLOCK","PICTURE","TV","RADIO","MUSIC","SONG","DANCE","GAME",
    "SPORT","FOOTBALL","BASKETBALL","SOCCER","TENNIS","SWIM","RUN","JUMP","PLAY","WORK","SCHOOL","TEACHER",
    "STUDENT","CLASS","LESSON","TEST","EXAM","HOMEWORK","BOOK","PENCIL","PAPER","QUESTION","ANSWER","KNOWLEDGE",
    "LEARNING","UNDERSTAND","THINK","REMEMBER","FORGET","SEE","HEAR","TASTE","SMELL","TOUCH","FEEL","SENSE",
    "HEART","BRAIN","BODY","HAND","FOOT","EYE","EAR","MOUTH","NOSE","FACE","HEAD","ARM","LEG","FINGER","TOE",
    "LOVE","FRIEND","FAMILY","PARENT","CHILD","BROTHER","SISTER","HUSBAND","WIFE","SON","DAUGHTER","PERSON",
    "MAN","WOMAN","BOY","GIRL","BABY","PEOPLE","CROWD","GROUP","TEAM","FAMILY","FRIEND","NEIGHBOR","STRANGER",
    "POLICE","DOCTOR","NURSE","TEACHER","STUDENT","WORKER","BOSS","EMPLOYEE","MANAGER","CEO","KING","QUEEN",
    "PRINCE","PRINCESS","SOLDIER","ARMY","NAVY","AIRFORCE","FIREMAN","POLICEMAN","JUDGE","LAWYER","CITIZEN",
    "GOVERNMENT","COUNTRY","STATE","CITY","TOWN","VILLAGE","HOME","HOUSE","APARTMENT","ROOM","BUILDING","STREET",
    "ROAD","BRIDGE","PARK","GARDEN","SCHOOL","UNIVERSITY","LIBRARY","MUSEUM","THEATER","CHURCH","TEMPLE","MOSQUE",
    "SHOP","STORE","MARKET","MALL","BANK","POST","OFFICE","HOSPITAL","CLINIC","PHARMACY","HOTEL","RESTAURANT",
    "CAFE","BAR","PUB","AIRPORT","STATION","PORT","FACTORY","FARM","FIELD","FOREST","MOUNTAIN","RIVER","LAKE",
    "SEA","OCEAN","ISLAND","DESERT","BEACH","SKY","SPACE","STAR","PLANET","MOON","SUN","EARTH","LIGHT","DARKNESS,SURPISE"
    "ABOVE","ACROSS","AFTERNOON","AGAINST","AGREE","ALMOST","ALONE","ALWAYS","AMONG",
    "ANIMAL","ANSWERED","ANYONE","ANYTHING","APPLY","ARRIVE","AUTUMN","AWAKE","BEAUTY",
    "BECOME","BELOW","BETWEEN","BEYOND","BORN","BOTH","BRING","BROUGHT","BUILDING",
    "BUS","BUSY","CARE","CAREER","CAREFUL","CAUGHT","CENTER","CHANGE","CHILDREN",
    "CHOOSE","CHURCH","CLEAR","CLIMB","CLOCK","COLLEGE","COLOR","COMPANY","COMPLETE",
    "CONTROL","COOK","CORRECT","COUNTRYSIDE","COURT","CRY","CULTURE","CUSTOM","CUT",
    "DAUGHTER","DEEP","DIFFERENT","DIFFICULT","DIRECTION","DISCOVER","DRIVE","DURING",
    "EACH","EARLY","EAST","EASY","EATEN","EFFORT","ELSE","ENEMY","ENJOY","ENOUGH",
    "ENTIRE","EVER","EXACT","EXAMPLE","EXPERIENCE","EYEGLASSES","FACT","FALLEN","FAMILYMEMBER",
    "FAMOUS","FAR","FARMER","FASTEST","FESTIVAL","FIELDWORK","FINAL","FINDING","FLIGHT",
    "FOLLOW","FOOTBALLER","FOREIGN","FORGOT","FRIDAY","FRONT","FUTURE","GARDENER","GENERAL",
    "GENTLE","GIFT","GIRLFRIEND","GLASS","GLOBAL","GRANDMOTHER","GRANDFATHER","GREATEST",
    "GROW","GROWN","GUESS","HAPPEN","HARDLY","HEALTH","HEAVY","HEIGHT","HISTORY","HOLIDAY",
    "HORSE","HOUR","HUMAN","IDEA","IMAGINE","IMPORTANT","INCLUDE","INSIDE","INSTEAD",
    "INTEREST","INTERNET","INTRODUCE","ISLANDER","JOURNEY","JUSTICE","KEEPING","KEY",
    "KITCHEN","KNIFE","KNOWLEDGEABLE","LADY","LARGE","LAUGH","LEADER","LEARNING","LEFT",
    "LETTER","LIBRARYBOOK","LIGHTHOUSE","LISTENED","LOCAL","LOST","LOVELY","LUCK","MAIN",
    "MANAGER","MARK","MARKETPLACE","MARRIED","MATCH","MATTER","MEAN","MEETING","MEMBER",
    "MESSAGE","METAL","MIDDLE","MIGHTY","MINUTE","MONEY","MORAL","MOTHER","MOUNTAINEER",
    "MOVEMENT","MUSICIAN","NEAR","NECESSARY","NEIGHBORHOOD","NEVER","NEXT","NIGHTTIME",
    "NORTH","NOTHING","NOTICE","NUMBER","OBJECT","OFFER","OFTEN","OLDER","ONCE","OPENED",
    "ORDERED","OUTSIDE","OVERSEAS","PAID","PAIR","PAPERWORK","PARTNER","PASSED","PEACEFUL",
    "PERHAPS","PERSONAL","PHYSICAL","PIECE","PLACE","PLAN","PLANT","POLITICS","POPULAR",
    "POSITION","PRACTICE","PRESENT","PRESS","PRIVATE","PROBLEM","PRODUCE","PROMISE","PUBLIC",
    "PURPOSE","QUICK","QUIET","RACE","RAISE","REACH","REAL","RECEIVE","RECORD","REMEMBERED",
    "REPEAT","REPORT","RETURN","RIGHTEOUS","RIVERBANK","ROADWAY","ROOMMATE","RUNNING",
    "SAFETY","SATURDAY","SCIENCE","SECOND","SECRET","SERIOUS","SERVICE","SEVERAL","SHALL",
    "SHOPPER","SHORTER","SHOW","SHOWN","SIMPLE","SINGLE","SISTERHOOD","SKYLINE","SLEEPING",
    "SMALLER","SNOWY","SOCIETY","SOLD","SOMEBODY","SOMETIMES","SOMEWHERE","SOUTH","SPECIAL",
    "SPRING","STANDUP","STATE","STAYED","STILL","STORY","STRONG","STUDENTBODY","STUDY",
    "SUNDAY","SUPPOSE","SURE","SURPRISE","SYSTEM","TAKEN","TEACH","TEACHING","TELEPHONE",
    "TELEVISION","THERE","THIRD","THOUGHT","THOUSAND","THURSDAY","TODAY","TOGETHER","TOMORROW",
    "TONIGHT","TOWARD","TRAVEL","TRIED","TRUTH","TUESDAY","TURNED","UNDER","UNDERSTAND",
    "UNIVERSITYSTUDENT","UNTIL","UPPER","USUALLY","VACATION","VERY","VISIT","VOICE","WAITED",
    "WALKING","WALLPAPER","WATCHED","WATERFALL","WEATHER","WEEK","WEEKEND","WEST","WHILE",
    "WHOLE","WILLING","WINTER","WISH","WITHIN","WITHOUT","WONDER","WONDERFUL","WORLD",
    "WRONGFUL","YARD","YESTERDAY","YOUNG","YOUTH","ZERO"
]

custom_words = [
    "PARTY", "TREAT", "LUNCHTIME", "LAST", "DAY", "CHECK", "MARK", "CLOSER",
    "SNEAKY", "LCOKIN", "SENDIT", "WEEEE", "TRANSITION", "ONE", "YOU", "GOT",
    "SHOW", "CHAT", "ROCKS", "FOR", "VHS", "RAVE", "TY", "MODS", "MORE", "BATTERY",
    "WDENNY", "SNEAKYCODE", "FOMC", "PREP", "GMASHY", "SHIELD", "NEXTROUND",
    "LASTMINUTE", "LASTCALLZ", "CHOP", "ROCKSTAR", "FUNDAY", "AMBER"
    "SUBS", "30KSUBS", "LUKE"
]

trading_words = [
    "BUY", "SELL", "ORDER", "STOP", "LIMIT", "MARKET", "TREND", "VOLUME",
    "PRICE", "RISK", "REWARD", "CANDLE", "CHART", "FUTURES", "OPTIONS",
    "CONTRACT", "POSITION", "ENTRY", "EXIT", "STOPLOSS", "TAKEPROFIT",
    "BROKER", "EXCHANGE", "INDICATOR", "SUPPORT", "RESISTANCE", "BREAKOUT",
    "PULLBACK", "SWING", "SCALP", "DAYTRADE", "LONG", "SHORT", "VOLATILITY",
    "SLIPPAGE", "LIQUIDITY", "ORDERBOOK", "SPREAD", "ASK", "BID", "SLIPPAGE",
    "BREAKDOWN", "RALLY", "CORRECTION", "DOWNTREND", "UPTREND", "BULLISH",
    "BEARISH", "MOVINGAVERAGE", "RSI", "MACD", "STOCHASTIC", "EMA", "SMA",
    "BACKTEST", "FORWARDTEST", "ALGORITHM", "AUTOTRADE", "MANUALTRADE",
    "FUNDED", "ACCOUNT", "SCREENER", "PATTERN", "FIBONACCI", "DIVERGENCE",
    "ORDERFLOW", "LIQUIDATION", "POSITIONSIZE", "RISKMANAGEMENT", "CAPITAL",
    "PROFIT", "LOSS", "DRAWNDOWN", "TARGET", "ENTRYPOINT", "EXITPOINT",
    "STRATEGY", "SIGNAL", "TRIGGER", "CONFLUENCE", "STOPHUNT", "GAP",
    "BREAKOUT", "FAIRVALUEGAP", "KILLZONE", "SESSION", "OPEN", "CLOSE",
    "HIGH", "LOW", "CANDLESTICK", "WICK", "BODY", "TRENDLINE", "CHANNEL",
    "FLAG", "PENNANT", "HEADANDSHOULDERS", "DOUBLEBOTTOM", "DOUBLETOP",
    "VOLUMEPROFILE", "ORDERBLOCK", "MARKETPROFILE", "LIMITORDER", "STOPORDER",
    "TAKEPROFITORDER","ECONOMICCALENDAR", "FED", "FOMC", "INTERESTRATE", "RATEHIKE", "RATECUT",
    "INFLATION", "CPI", "PPI", "GDP", "UNEMPLOYMENT", "NFP", "JOBSREPORT",
    "PAYROLLS", "ISM", "PMI", "RECESSION", "EXPANSION", "BOOM", "BUST",
    "QE", "QT", "BALANCESHEET", "STIMULUS", "TAPERING", "YIELD", "YIELDCURVE",
    "INVERTEDCURVE", "BOND", "TREASURY", "TNOTE", "TBILL", "YIELDSPREAD",
    "EQUITIES", "STOCKS", "INDEX", "SP500", "NASDAQ", "DOWJONES", "FTSE",
    "DAX", "NIKKEI", "HANGSENG", "CRYPTO", "BITCOIN", "ETHEREUM", "ALTCOIN",
    "STABLECOIN", "DEFI", "NFT", "BLOCKCHAIN", "EXCHANGEHACK", "REGULATION",
    "SEC", "CFTC", "BROKERAGE", "MARGIN", "LEVERAGE", "OVERLEVERAGED",
    "MARGINCALL", "STOPOUT", "FUNDINGRATE", "ROLLOVER", "EXPIRY", "SETTLEMENT",
    "OPTIONSCHAIN", "OPENINTEREST", "DELTA", "GAMMA", "VEGA", "THETA",
    "IV", "SKEW", "STRADDLE", "STRANGLE", "IRONCONDOR", "BUTTERFLYSPREAD",
    "DERIVATIVES", "SWAP", "CFD", "ETF", "MUTUALFUND", "INDEXFUND", "HEDGEFUND",
    "INSTITUTIONAL", "RETAIL", "MARKETMAKER", "HIGHFREQUENCY", "ROBOTRADE",
    "DARKPOOL", "BLOCKTRADE", "FRONTRUNNING", "ARBITRAGE", "HEDGING",
    "DIVERSIFICATION", "PORTFOLIO", "ASSETALLOCATION", "RISKON", "RISKOFF",
    "SAFEHAVEN", "GOLD", "SILVER", "OIL", "WTI", "BRENT", "NATGAS", "COMMODITY",
    "SOYBEANS", "CORN", "WHEAT", "COFFEE", "COTTON", "LIVECATTLE", "CPO",
    "OPECPOLICY", "OPECMEETING", "GEOPOLITICS", "ELECTION", "POLICYCHANGE",
    "TRADEWAR", "SANCTIONS", "BREXIT", "COVID", "PANDEMIC", "LOCKDOWN",
    "VACCINE", "SUPPLYCHAIN", "CHIPSHORTAGE", "EARNINGS", "QUARTERLYREPORT",
    "GUIDANCE", "DIVIDEND", "BUYBACK", "SHAREISSUE", "IPOS", "SPAC", "MERGER",
    "ACQUISITION", "LAYOFFS", "COSTCUTTING", "DOWNSIZING", "BUBBLE", "BURST",
    "SPECULATION", "HYPE", "PUMP", "DUMP", "WHIPSHAW", "WHIPLASH", "CIRCUITBREAKER",
    "HALT", "LIMITUP", "LIMITDOWN", "CASHBALANCE", "EQUITYBALANCE", "MARGINBALANCE",
    "STOPRUN", "FAKEOUT", "ORDERCLUSTER", "ORDERIMBALANCE", "TAPE", "TIMESALE",
    "LEVEL2", "DOM", "VWAP", "POC", "IBRANGE", "MARKETHOURS", "PREMARKET",
    "AFTERHOURS", "OVERNIGHT", "GAPUP", "GAPDOWN", "OPENINGDRIVE", "CLOSINGBELL",
    "HALFSESSION", "QUADWITCHING", "TRIPLEWITCHING", "EXPIRATIONFRIDAY",
    "SEASONALITY", "JANUARYEFFECT", "SANTARALLY", "SELLINMAY", "SUMMERRALLY",
    "BLACKSWAN", "FATTAIL", "TAILRISK", "VOLCRUSH", "VOLBLOWUP", "VVIX",
    "FEARINDEX", "VIX", "RISKPREMIUM", "ALPHABETASORT", "BETA", "ALPHA",
    "SHARPE", "SORTINO", "DRAWDOWN", "REBALANCE", "MARKETCAP", "SMALLCAP",
    "MIDCAP", "LARGECAP", "MEGACAP", "BLUECHIP", "PENNYSTOCK", "ILLQUID",
    "FRONTMONTH", "BACKMONTH", "CONTANGO", "BACKWARDATION", "BASIS", "ROLLCOST",
    "SPREADTRADE", "PAIRTRADE", "SECTORROTATION", "CYCLES", "MARKETCYCLE",
    "ECONOMICCYCLE", "BUSINESSCYCLE", "DEPRESSION", "HYPERINFLATION", "STAGFLATION",
    "DEFLATION", "CREDITCRISIS", "BANKRUN", "DEFAULT", "RATINGDOWNGRADE",
    "DEBTCEILING", "TREASURYAUCTION", "BALANCESHEETREDUCTION", "LIQUIDITYCRUNCH",
    "MONEYMARKET", "FX", "FOREX", "EURUSD", "USDJPY", "GBPUSD", "AUDUSD",
    "USDCAD", "NZDUSD", "USDCHF", "CROSSPAIR", "EMCURRENCY", "DOLLARINDEX",
    "DXY", "CARRYTRADE", "INTERVENTION", "PEGSYSTEM", "FLOATINGRATE",
    "CURRENCYCRISIS", "SOVEREIGNDEBT", "DEBTDEFAULT", "IMF", "WORLD BANK",
    "ECB", "BOE", "BOJ", "SNB", "PBOC", "RBA", "RBNZ", "CBR", "FEDFUNDS",
    "DOTPLOT", "MINUTES", "PRESSCONFERENCE", "RATESTATEMENT", "FORWARDGUIDANCE",
    "SPEECH", "NEWSWIRE", "HEADLINE", "BREAKINGNEWS", "RUMOR", "WHISPER",
    "MARKETREACTION", "KNEEJERK", "OVERREACTION", "FADE", "REVERSAL"
]


live_streaming_words = [
    "STREAM", "CHAT", "MODERATOR", "EMOTE", "SUBSCRIBE", "DONATE",
    "FOLLOW", "ALERT", "BIT", "RAID", "HOST", "CHANNEL", "VIEWER",
    "STREAMER", "MIC", "CAMERA", "SETUP", "HIGHLIGHT", "REPLAY",
    "BITRATE", "FRAME", "RESOLUTION", "AUDIO", "VIDEO", "INTERACTION",
    "MODS", "BAN", "TIMEOUT", "FOLLOWER", "SUB", "GIF", "EMOJI",
    "TIMER", "COHOST", "COLLAB", "CHATBOT", "SOUND", "OVERLAY",
    "THEME", "SUBGOAL", "DONATIONGOAL", "MERCH", "COMMUNITY", "RAIDING",
    "STREAMLABS", "DISCORD", "YOUTUBE", "TWITCH", "FACEBOOK", "REDDIT",
    "ALERTBOX", "SPONSOR", "SUBALERT", "CHATRULES", "PRIVATEMESSAGE",
    "CHATMODE", "BITSPROGRESS", "VOD", "HYPE", "FOLLOWFRIDAY", "TAGS",
    "HOSTING", "STREAMTITLE", "SCHEDULE", "DONATIONALERT", "SUBALERT",
    "CHATCOMMAND", "CHATFILTER", "STICKER", "PARTNER", "AFFILIATE",
    "EMOTESET", "CROWN", "SUBMODE", "RAIDMODE", "CHATBOTCOMMAND", "SNIPE",
    "CHATWHEEL", "CHEER", "CHATSNIPE", "RAIDPARTY", "CHATSPAM",
    "MODPERMISSIONS", "TOGGLE", "STREAMALERT", "STREAMNOTIFICATION",
    "STREAMSCHEDULE", "SUBCOUNT", "VIEWCOUNT", "TRACKER", "MUTE",
    "UNMUTE", "BROADCAST", "LOWDELAY", "VOLUME", "DELAY", "BITCAMP"
    "ADBLOCK", "AFK", "ALTACCOUNT", "ANNOUNCEMENT", "ANONYMOUS", "API",
    "ARCHIVE", "AUTOMOD", "BADGE", "BANAPPEAL", "BANNER", "BETA",
    "BLINDPLAYTHROUGH", "BOOST", "BOTRAID", "BRB", "BUFFERING",
    "CAMOVERLAY", "CAPTURECARD", "CHANNELPOINTS", "CHATDELAY",
    "CHATEMBED", "CHATLOG", "CHATPING", "CHATTHEME", "CLIP", "CLIPBOARD",
    "CLIPSCHANNEL", "COINFLIP", "COMMANDLIST", "COMPETITION",
    "CONNECTION", "CONTROLLER", "COSPLAY", "CROSSPLATFORM",
    "CUSTOMALERT", "CUSTOMBADGE", "CUSTOMEMOTE", "DATACENTER", "DEBUG",
    "DELAYREDUCTION", "DEVICE", "DIRECTMESSAGE", "DROP", "DROPSENABLED",
    "DROPSCAMPAIGN", "EASTER EGG", "ECHAT", "ENDSTREAM", "EVENT",
    "EVENTLIST", "EXCLUSIVE", "EXTENSION", "FACEOVERLAY", "FACEFILTER",
    "FEATUREDCLIP", "FEATUREDSTREAM", "FOLLOWCHAIN", "FOLLOWLIST",
    "FOLLOWNOTIFY", "FRAMESKIP", "FRONTPAGE", "FULLSCREEN",
    "GAMECATEGORY", "GAMECAPTURE", "GAMEEVENT", "GAMEOVERLAY",
    "GAMETAG", "GAMETRACKER", "GIFTEDSUB", "GLOBALCHAT", "GLOBALBAN",
    "GLOBALMOD", "GOALPROGRESS", "GRAPHICS", "GREETING", "GROUPSTREAM",
    "HARDWARE", "HEADSET", "HEART", "HELPDESK", "HIGHLIGHTCLIP",
    "HOSTQUEUE", "HOTKEY", "HUD", "HYPECOMMAND", "HYPETRAIN", "IDLE",
    "INGAMECHAT", "INPUTDEVICE", "INTERACT", "INTERNET", "INVITE",
    "JOINQUEUE", "KEYLIGHT", "KEYSTREAM", "KEYWORD", "LAYOUT",
    "LEADERBOARD", "LIVECONTENT", "LIVEEVENT", "LIVEINDICATOR",
    "LIVEMATCH", "LIVEREACTION", "LOBBY", "LOCALRECORDING",
    "LOGOUT", "LOOT", "LOWLATENCY", "LUCKYDROP", "MATCHMAKING",
    "MAXQUALITY", "MEMBERBADGE", "MENTION", "MICSTAND", "MICVOLUME",
    "MOBILESTREAM", "MODACTION", "MODCALL", "MODCHAT", "MODQUEUE",
    "MULTISTREAM", "MULTIVIEW", "NETWORK", "NIGHTBOT", "NINJALOOT",
    "NONSUBMODE", "NOTIFY", "OFFLINE", "OFFLINECHAT", "OFFLINEMODE",
    "ONSCREENALERT", "OVERLAYEDITOR", "PACKETLOSS", "PARTNERBADGE",
    "PAYPALDONATION", "PEAKVIEWERS", "PING", "PINGCHECK", "PLATFORM",
    "PLAYALONG", "PLAYLISTOVERLAY", "POPUP", "PRELOAD", "PRESSF",
    "PRIMESUB", "PRIVATECHAT", "PRODUCER", "PROXY", "PUBLICCHAT",
    "PUSHNOTIFY", "QUEUECHAT", "QUEUESYSTEM", "RANDOMDROP",
    "RANKEDMATCH", "REACTIONEMOTE", "REDEMPTION", "REGIONLOCK",
    "REMOTESUPPORT", "REPLAYBUFFER", "RESTREAM", "ROOMCODE",
    "ROUTER", "SAVESTREAM", "SCENE", "SCENESWITCH", "SCREENSHARE",
    "SERVER", "SERVERISSUE", "SESSIONID", "SHARESCREEN", "SHORTCLIP",
    "SHOWSUPPORT", "SKIN", "SKIPSONG", "SKIPVOTE", "SOUNDBOARD",
    "SOUNDEFFECT", "SPEEDTEST", "SPLITSCREEN", "SPOTLIGHT",
    "SPOTLIGHTCLIP", "SPOTLIGHTSTREAM", "SQUADSTREAM", "STARTSTREAM",
    "STATUS", "STREAMELEMENTS", "STREAMKEY", "STREAMKIT",
    "STREAMLINK", "STREAMMANAGER", "STREAMMARKER", "STREAMMODE",
    "STREAMOVERLAY", "STREAMPACKAGE", "STREAMPASS", "STREAMPLAYLIST",
    "STREAMQUEUE", "STREAMRECORDER", "STREAMREPLAY", "STREAMSETTINGS",
    "STREAMSNIPER", "STREAMTAG", "STREAMTEAM", "SUBATHON",
    "SUBBADGE", "SUBFEST", "SUBLEADERBOARD", "SUBONLYMODE",
    "SUPPORTCHAT", "SUPPORTER", "TECHCHECK", "TECHTEST", "THEATREMODE",
    "TIMESTAMP", "TOKEN", "TOURNAMENT", "TRACKLIST", "TRANSITION",
    "TROLL", "TTS", "UPGRADE", "UPLOADSPEED", "USERNAME",
    "VERIFIEDBADGE", "VIEWERLIST", "VIEWERSHIP", "VIPBADGE",
    "VIRTUALCAM", "VIRTUALCURRENCY", "VOICEMOD", "VOICENOTE",
    "VOICEROOM", "WAITLIST", "WATCHALONG", "WATCHLIST",
    "WEBCAM", "WEBCAMOVERLAY", "WELCOME", "WHISPER", "WIDGET",
    "WIDGETALERT", "WINNINGPLAY", "WIRELESS", "XLR", "ZONEMATCH"
]

youtube_words = [
    "VIDEO", "CHANNEL", "SUBSCRIBE", "LIKE", "COMMENT", "VIEW", "UPLOAD",
    "PLAYLIST", "TAGS", "THUMBNAIL", "MONETIZE", "DASHBOARD", "YOUTUBER",
    "CONTENT", "LIVE", "STREAM", "NOTIFICATION", "ALGORITHM", "SHORTS",
    "MEMBERSHIP", "ANALYTICS", "ADSENSE", "SPONSOR", "COLLABORATION",
    "VLOG", "TUTORIAL", "REVIEWS", "UNBOXING", "GAMING", "MUSIC", "RECOMMENDATION",
    "SEARCH", "TRENDING", "COMMENTARY", "SUBSCRIBERS", "LIKES", "DISLIKES",
    "PLAYBACK", "SETTINGS", "CHANNELART", "DESCRIPTION", "VIDEOEDITING",
    "LIVECHAT", "YTSTUDIO", "YTAPP", "COPYRIGHT", "COMMUNITY", "PLAYBACK",
    "REPORT", "VIDEOIDEA", "CAPTION", "METADATA", "ANNOYINGADS", "DEMOS",
    "WATCHTIME", "RETENTION", "CLICKTHROUGH", "SEO", "HASHTAGS", "OUTRO",
    "INTRO", "BROLL", "GREENSCREEN", "FILTERS", "TRANSITIONS", "SCHEDULE",
    "PREMIERE", "HIGHLIGHTS", "REACTION", "COMMENTSECTION", "PINNEDCOMMENT",
    "LIKERAID", "DISLIKERAID", "VIRAL", "ENGAGEMENT", "SHARE", "DOWNLOAD",
    "UPLOADSCHEDULE", "DAILYUPLOAD", "WEEKLYUPLOAD", "ALTTEXT", "TIMESTAMP",
    "AUTOPLAY", "ENDSCREEN", "CARDS", "BRANDDEAL", "MERCH", "PATREON",
    "DONATION", "SUPERSUBS", "SUPERSCHAT", "SUPERSHOUTOUT", "SHOUTOUT",
    "HATEREPORT", "CHANNELBAN", "BLOCKUSER", "SHARELINK", "YOUTUBESHORT",
    "YTALGORITHM", "YTPREMIUM", "YTMUSIC", "YTKIDS", "YTGAMING", "YTPARTNER",
    "FAIRUSE", "STRIKE", "COPYSTRIKE", "DEMOTIZATION", "REVENUE", "RPM",
    "CPM", "MIDROLL", "PREROLL", "POSTROLL", "SKIPPABLEAD", "NONSKIPPABLEAD",
    "BANNER", "CAROUSEL", "ADBREAK", "BRANDSAFETY", "AGEGATE", "TRENDJACKING",
    "NICHETOPIC", "FACECAM", "SCREENRECORD", "MICROPHONE", "LIGHTING",
    "BACKDROP", "SETDESIGN", "CAMERAANGLE", "CLOSEUP", "JUMPCUT", "TIMELAPSE",
    "SLOWMOTION", "FASTFORWARD", "ZOOMIN", "ZOOMOUT", "SPLITSCREEN", "REACTIONS",
    "COMMENTREPLY", "SPAMFILTER", "MODERATOR", "CHANNELMOD", "COMMUNITYPOST",
    "POLL", "STORY", "CHANNELUPDATE", "ALGORITHMBOOST", "NICHEREACH",
    "TARGETAUDIENCE", "DEMONETIZED", "REUSEDCONTENT", "STRIKESYSTEM", "YTNOTICES",
    "REPORTSPAM", "DISPUTE", "CLAIM", "APPEAL", "YTPOLICY", "GUIDELINES",
    "TOS", "COMMUNITYSTRIKE", "CHANNELWARNING", "EMAILALERT", "BANNEDWORD",
    "FILTERLIST", "VIDEORECOMMEND", "CROSSPROMOTION", "SHARETOWHATSAPP",
    "SHARETOTWITTER", "SHARETOFACEBOOK", "SHARETOINSTAGRAM", "SHARETOTIKTOK",
    "COLLABVIDEO", "DUET", "REACTIONVIDEO", "CHALLENGE", "TAGVIDEO",
    "HAUL", "MAKEUPTUTORIAL", "TECHREVIEW", "MUKBANG", "ASMR", "STORYTIME",
    "DAYINTHELIFE", "PRANK", "EXPERIMENT", "ANIMATION", "PARODY", "MUSICVIDEO",
    "LYRICVIDEO", "COVERSONG", "REMIX", "MASHUP", "BEAT", "INSTRUMENTAL",
    "FREESTYLE", "CYBERBULLYING", "HATECOMMENT", "POSITIVECOMMENT",
    "SUB4SUB", "FAKESUB", "BOTVIEW", "FAKEVIEWS", "REALENGAGEMENT",
    "WATCHPARTY", "LIVECOUNT", "SUBCOUNT", "VIEWSCOUNT", "YTANALYTICS",
    "HEATMAP", "AUDIENCERETENTION", "CTR", "CLICKRATE", "AVGDURATION",
    "TOPLOCATION", "TRAFFICSOURCE", "DEVICESTATS", "REACH", "IMPRESSION",
    "SUGGESTEDVIDEO", "ENDSCREENCTA", "BRANDCOLLAB", "ADREAD", "SPONSOREDPOST",
    "MERCHLINK", "AFFILIATELINK", "UNLISTED", "PRIVATEVIDEO", "PUBLICVIDEO",
    "DRAFT", "REUPLOAD", "CROSSPOST", "SECONDCHANNEL", "ALTCHANNEL",
    "BRANDEDCHANNEL", "TEAMCHANNEL", "GROUPUPLOAD", "COHOST", "FEATUREDCHANNEL",
    "CHANNELTRAILER", "WELCOMEVIDEO", "FANART", "FANBASE", "SUBFAM",
    "COMMUNITYNAME", "FANMEETUP", "LIVEEVENT", "STREAMHIGHLIGHT", "AFTERMOVIE",
    "BTS", "BEHINDTHESCENES", "CUTCONTENT", "DELETEDSCENE", "EXTENDEDVERSION",
    "DIRECTORSCUT", "WATCHLATER", "HISTORY", "QUEUE", "AUTOGENERATED",
    "CAPTIONTRACKS", "SUBTITLE", "CLOSEDcaption", "AUTOCAPTION", "LANGUAGE",
    "TRANSLATION", "MULTILINGUAL", "DUBBED", "SUBBED", "COMMENTLIKES",
    "COMMENTDISLIKES", "THREAD", "REPLYCHAIN", "SPAMCOMMENT", "TOPCOMMENT",
    "PINNEDTOPIC", "SUGGESTEDTOPIC", "TRENDINGPAGE", "EXPLOREPAGE",
    "HOMEPAGE", "SUBFEED", "NOTIFICATIONBELL", "BELLON", "BELLALL",
    "BELLNONE", "SHADOWBAN", "GHOSTBAN", "ALGORITHMPUSH", "YTSUGGESTIONS",
    "HOMERECOMMEND", "CROSSPLATFORM", "YOUTUBESHORTS", "SHORTSVIEW",
    "SHORTSUPLOAD", "SHORTSFEED", "YOUTUBEMEMES", "COMMENTMEMES",
    "FUNNYEDIT", "MONTAGE", "COMPILATION", "BESTOF", "TOP10", "LISTICLE",
    "EXPLAINER", "DOCUSERIES", "MINISERIES", "EPISODE", "PLAYTHROUGH",
    "SPEEDRUN", "LET'SPLAY", "WALKTHROUGH", "HIGHLIGHTREEL", "GAMEPLAY",
    "PATCHNOTES", "REVIEWVIDEO", "FIRSTLOOK", "REACTIONCLIP", "DISCUSSION"

]


word_dictionary = set(
    w.upper() for w in (
        common_words_500 +
        custom_words +
        trading_words +
        live_streaming_words +
        youtube_words
    )
)

def dictionary_fill_code(code):
    """
    If code contains '_', try to fill missing letters using best dictionary match.
    Returns corrected code or original if no match.
    """
    if not code or "_" not in code:
        return code

    code = code.strip().upper()
    print(f"[DICTIONARY] Attempting to fill code: {code}")

    # Extract the base part before any numbers
    base_match = re.match(r'^([A-Z_]+)', code)
    if not base_match:
        return code

    base_part = base_match.group(1)
    number_part = code[len(base_part):]

    print(f"[DICTIONARY] Base part: '{base_part}', Number part: '{number_part}'")

    best_score = -1
    best_word = None

    # Only handle codes with a single underscore for now
    if base_part.count('_') != 1:
        print(f"[DICTIONARY] Multiple or no underscores, skipping advanced fill.")
        return code

    for word in word_dictionary:
        # Only consider words that fit the base_part up to the underscore (allow extra trailing letters in base_part)
        if len(word) <= len(base_part):
            score = 0
            mismatch = False
            for i, code_char in enumerate(base_part[:len(word)]):
                if code_char == '_':
                    continue
                if code_char == word[i]:
                    score += 1
                else:
                    mismatch = True
                    break
            if not mismatch and score > best_score:
                best_score = score
                best_word = word

    if best_word:
        # Fill the underscore with the letter from the best matched word
        underscore_index = base_part.index('_')
        filled_base = (
            base_part[:underscore_index] +
            best_word[underscore_index] +
            base_part[underscore_index+1:]
        )
        filled_code = filled_base + number_part
        print(f"[DICTIONARY] Best match: '{best_word}' → Final code: '{filled_code}'")
        return filled_code

    print(f"[DICTIONARY] No match found for: {code}")
    return code

def get_device_info():
    pc_name = socket.gethostname()
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                        for ele in range(0, 8 * 6, 8)][::-1])
    except Exception:
        mac = "unknown"
    try:
        ip = socket.gethostbyname(pc_name)
    except Exception:
        ip = "unknown"
    return pc_name, mac, ip

def get_current_hwid():
    # Use MAC as HWID for simplicity
    return get_device_info()[1]

def get_current_ip():
    return get_device_info()[2]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def deskew_image(pil_img):
    # Convert PIL image to OpenCV format
    img = np.array(pil_img)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Threshold to get binary image
    _, img_bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(img_bin < 255))
    angle = 0
    if coords.shape[0] > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    # Rotate to deskew
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)

def find_colored_box_and_crop(pil_img):
    # Convert PIL image to OpenCV format
    img = np.array(pil_img.convert("RGB"))
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # Define lower and upper HSV bounds for the colored box (example: blue)
    lower = np.array([100, 50, 50])   # Adjust these values to match your box color
    upper = np.array([130, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour (assume it's the box)
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        cropped = img[y:y+h, x:x+w]
        return Image.fromarray(cropped)
    else:
        # Fallback: return original image if no box found
        return pil_img

def clean_and_replace_underscores(code, replacement_index=0):
    """
    Clean code and replace underscores with letters in order: T, N, S
    Also strips non-alphanumeric characters as a final step
    """
    if not code:
        return None
        
    # Try underscore replacement if there are any underscores
    if '_' in code and replacement_index < len(underscore_replacements):
        # Replace all underscores with the current replacement letter
        return code.replace('_', underscore_replacements[replacement_index])
    
    # Strip non-alphanumeric as a final fallback
    return ''.join(c for c in code if c.isalnum())

def repair_missing_underscore(code):
    """
    If code contains a space, replace it with an underscore and apply dictionary fill.
    """
    if code and " " in code:
        # Replace all spaces with underscores
        code_with_underscore = code.replace(" ", "_")
        print(f"[POSTPROCESS] Replaced space with underscore: {code_with_underscore}")
        # Try dictionary fill if enabled
        if dictionary_underscore_enabled and "_" in code_with_underscore:
            filled_code = dictionary_fill_code(code_with_underscore)
            if filled_code != code_with_underscore:
                print(f"[POSTPROCESS] Dictionary filled code: {filled_code}")
                return filled_code
        return code_with_underscore
    return code

def extract_code_with_reverse(text, patterns, require_keyword=None):
    """
    Extracts code using provided regex patterns.
    If 'backwards' or 'reverse' is in the text, reverses the code (if enabled).
    Optionally, require a keyword (e.g. 'SCALE' or 'PRO') to be present in text.
    """
    text_upper = text.upper()
    if require_keyword and require_keyword not in text_upper:
        return None
    
    print(f"[EXTRACT] Looking for codes in text: {text_upper}")
    reverse_needed = ("BACKWARDS" in text_upper) or ("REVERSE" in text_upper)
    
    for pattern in patterns:
        match = re.search(pattern, text_upper)
        if match:
            code = match.group(1)
            print(f"[EXTRACT] Found potential code: {code}")

            # Post-process to repair missing underscores and dictionary fill
            code = repair_missing_underscore(code)
            
            # Try dictionary filling first if enabled and code contains underscore
            if dictionary_underscore_enabled and "_" in code:
                filled_code = dictionary_fill_code(code)
                if filled_code != code:
                    code = filled_code
                    print(f"[EXTRACT] Dictionary filled code: {code}")
            
            # Clean and replace underscores with first attempt (T)
            if "_" in code:
                code = clean_and_replace_underscores(code, 0)
                print(f"[EXTRACT] Cleaned code: {code}")
            
            if reverse_needed and reverse_code_if_instructed_enabled:
                code = code[::-1]
                print(f"[EXTRACT] Reversed code: {code}")
            
            # Optionally apply smart fix
            if smart_fix_ending_enabled:
                code = fix_common_ending_errors(code)
                print(f"[EXTRACT] Smart fixed code: {code}")
            
            return code
    
    print(f"[EXTRACT] No code found")
    return None

def fix_common_ending_errors(code):
    """Correct codes ending in SO, S0, 5O to 50. Optionally, SS or 5S to 55, 2S to 25, and endings like 2O→20, 1OO→100."""
    if len(code) >= 2:
        last_two = code[-2:]
        if smart_fix_ending_enabled and last_two in ['SO', 'S0', '5O']:
            corrected = code[:-2] + '50'
            print(f"[SMART FIX] Replaced ending '{last_two}' with '50' → {corrected}")
            return corrected
        if smart_fix_ss_to_55_enabled and last_two in ['SS', '5S']:
            corrected = code[:-2] + '55'
            print(f"[SMART FIX] Replaced ending '{last_two}' with '55' → {corrected}")
            return corrected
        if smart_fix_2s_to_25_enabled and last_two == '2S':
            corrected = code[:-2] + '25'
            print(f"[SMART FIX] Replaced ending '{last_two}' with '25' → {corrected}")
            return corrected
        # Now only apply this if enabled
        if smart_fix_digit_o_to_digit0_enabled and last_two[0].isdigit() and last_two[1] == 'O':
            corrected = code[:-2] + last_two[0] + '0'
            print(f"[SMART FIX] Replaced ending '{last_two}' with '{last_two[0]}0' → {corrected}")
            return corrected
    # New: Replace ending 1OO with 100
    if len(code) >= 3 and code[-3:] == '1OO':
        corrected = code[:-3] + '100'
        print(f"[SMART FIX] Replaced ending '1OO' with '100' → {corrected}")
        return corrected
    return code

# ==========================================
# OVERLAY WINDOW WITH SNIPPING TOOL FUNCTIONALITY
# ==========================================

class OverlayWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), 
                         QApplication.primaryScreen().size().height())
        
        self.region = current_ocr_region
        self.dragging = False
        self.resizing = False
        self.drag_offset = QPoint()
        self.border_color = QColor(0, 255, 136)  # Modern green
        self.border_width = 3
        self.selection_active = True
        self.start_point = QPoint()
        self.end_point = QPoint()
        
        # Initialize with current region if it exists
        if not self.region.isNull():
            self.start_point = self.region.topLeft()
            self.end_point = self.region.bottomRight()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent overlay with modern gradient
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
        # Draw the region rectangle only if we have a valid selection
        if self.selection_active and not self.start_point.isNull() and not self.end_point.isNull():
            # Calculate the selection rectangle
            rect = QRect(self.start_point, self.end_point).normalized()
            
            # Draw modern selection rectangle with glow effect
            painter.setBrush(Qt.BrushStyle.NoBrush)
            pen = QPen(self.border_color, self.border_width)
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # Draw inner glow
            inner_pen = QPen(QColor(255, 255, 255, 100), 1)
            painter.setPen(inner_pen)
            painter.drawRect(rect.adjusted(1, 1, -1, -1))
            
            # Draw modern resize handles
            painter.setBrush(QBrush(self.border_color))
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            handle_size = 12
            # Corner handles with rounded corners
            handles = [
                rect.topLeft(),
                rect.topRight() + QPoint(-handle_size, 0),
                rect.bottomLeft() + QPoint(0, -handle_size),
                rect.bottomRight() + QPoint(-handle_size, -handle_size)
            ]
            
            for handle_pos in handles:
                painter.drawRoundedRect(handle_pos.x(), handle_pos.y(), handle_size, handle_size, 2, 2)
            
            # Draw modern instruction text with background
            font = QFont("Segoe UI", 12, QFont.Weight.Medium)
            painter.setFont(font)
            text_rect = QRect(rect.bottomRight() + QPoint(15, -35), QSize(250, 30))
            
            # Text background
            painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(text_rect, 8, 8)
            
            # Text
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Drag to resize • ESC to confirm")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.selection_active:
                # Starting a new selection
                self.start_point = event.pos()
                self.end_point = event.pos()
                self.selection_active = True
                self.region = QRect(self.start_point, self.end_point)
            else:
                # Check if we're clicking on the existing selection
                current_rect = QRect(self.start_point, self.end_point).normalized()
                if current_rect.contains(event.pos()):
                    self.dragging = True
                    self.drag_offset = event.pos() - current_rect.topLeft()
                else:
                    # Start a new selection
                    self.start_point = event.pos()
                    self.end_point = event.pos()
                    self.region = QRect(self.start_point, self.end_point)
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.dragging:
                # Move the existing selection
                new_top_left = event.pos() - self.drag_offset
                rect_size = QRect(self.start_point, self.end_point).normalized().size()
                self.start_point = new_top_left
                self.end_point = new_top_left + QPoint(rect_size.width(), rect_size.height())
            else:
                # Resize the selection
                self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            # Update the global region
            global current_ocr_region
            current_ocr_region = QRect(self.start_point, self.end_point).normalized()
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            # Update the global region one more time
            global current_ocr_region
            current_ocr_region = QRect(self.start_point, self.end_point).normalized()
            print(f"OCR Region updated to: {current_ocr_region.getRect()}")

# ==========================================
# BASE BOT CLASS
# ==========================================

class BaseBot:
    def __init__(self, bot_type):
        self.bot_type = bot_type
        self.running = False
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--log-level=3")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(f"[{self.bot_type}] Chrome driver initialized successfully")
            
        except Exception as e:
            print(f"[{self.bot_type}] Error setting up driver: {str(e)}")
            self.driver = None

    def run(self):
        """Main bot loop"""
        if not self.driver:
            print(f"[{self.bot_type}] Cannot start - driver not initialized")
            return
            
        self.running = True
        
        try:
            # Navigate to the page
            self.navigate_to_page()
            print(f"[{self.bot_type}] Navigated to target page")
            
            # Wait for page to load
            time.sleep(0.2)
            
            while self.running and bot_running.get(self.bot_type, False):
                try:
                    # Capture and process image
                    with mss.mss() as sct:
                        region = current_ocr_region.getRect()
                        if region[2] == 0 or region[3] == 0:
                            print(f"[{self.bot_type}] Invalid region size")
                            time.sleep(0.05)
                            continue
                            
                        monitor = {
                            "top": region[1],
                            "left": region[0],
                            "width": region[2],
                            "height": region[3],
                        }
                        
                        sct_img = sct.grab(monitor)
                        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                        
                        # Preprocess image
                        processed_img = self.preprocess_image(img)
                        
                        # Use EasyOCR for text extraction
                        img_np = np.array(processed_img)
                        results = easyocr_reader.readtext(img_np)
                        
                        # Combine all text
                        extracted_text = " ".join([result[1] for result in results])
                        
                        if show_ocr_raw_enabled and hasattr(self, 'parent'):
                            self.parent.ocr_raw_signal.emit(f"[{self.bot_type}] OCR RAW: {extracted_text}")
                        
                        if extracted_text.strip():
                            print(f"[{self.bot_type}] Extracted text: {extracted_text}")
                            
                            # Extract code
                            code = self.extract_code(extracted_text)
                            if code:
                                print(f"[{self.bot_type}] Code found: {code}")
                                success = self.apply_code(code)
                                if success:
                                    if hasattr(self, 'parent'):
                                        self.parent.code_found_signal.emit(self.bot_type)
                                    # Wait longer after successful application
                                    time.sleep(0.2)
                                else:
                                    time.sleep(1)
                            else:
                                time.sleep(1)
                        else:
                            time.sleep(1)
                            
                except Exception as e:
                    print(f"[{self.bot_type}] Error in main loop: {str(e)}")
                    time.sleep(2)
                    
        except Exception as e:
            print(f"[{self.bot_type}] Critical error: {str(e)}")
        finally:
            self.cleanup()

    def stop(self):
        """Stop the bot"""
        self.running = False
        print(f"[{self.bot_type}] Stop requested")

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print(f"[{self.bot_type}] Driver closed")
            except Exception as e:
                print(f"[{self.bot_type}] Error closing driver: {str(e)}")

    def navigate_to_page(self):
        """Override in subclasses"""
        pass

    def preprocess_image(self, image):
        """Override in subclasses"""
        return image

    def extract_code(self, text):
        """Override in subclasses"""
        return None

    def apply_code(self, code):
        """Override in subclasses"""
        return False

# ==========================================
# SPECIFIC BOT IMPLEMENTATIONS
# ==========================================

class ScaleBot(BaseBot):
    def __init__(self, parent):
        super().__init__("Scale")
        self.parent = parent
        self.page_url = "https://myfundedfutures.com/login"

    def navigate_to_page(self):
        self.driver.get(self.page_url)

    def preprocess_image(self, image):
        image = image.convert('L')
        scale = 1
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)
        image = ImageOps.invert(image)
        image = ImageOps.autocontrast(image)
        img_np = np.array(image)
        img_np = cv2.bilateralFilter(img_np, 9, 75, 75)
        _, img_np = cv2.threshold(img_np, 100, 255, cv2.THRESH_BINARY)
        processed = Image.fromarray(img_np)
        return processed

    def extract_code(self, text):
        # More flexible patterns that can handle underscores
        patterns = [
            r'CODE[:\s]*([A-Z0-9_]{4,16})',
            r'USE CODE[:\s]*([A-Z0-9_]{4,16})',
            r'\b([A-Z_]{3,}[0-9]{2,})\b',
            r'\b([A-Z0-9_]{5,}\d{1,})\b'
        ]
        return extract_code_with_reverse(text, patterns, require_keyword="SCALE")

    def apply_code(self, code):
        if not code:
            return False

        print(f"[SCALE] Attempting to apply code: {code}")
        
        # Try dictionary filling first if enabled
        codes_to_try = []
        if dictionary_underscore_enabled and "_" in code:
            dict_filled = dictionary_fill_code(code)
            if dict_filled != code:
                codes_to_try.append(dict_filled)
                print(f"[SCALE] Added dictionary filled code: {dict_filled}")
        
        # Add original code and variations
        codes_to_try.append(code)
        
        # Add underscore replacement variations
        for i in range(len(underscore_replacements)):
            if "_" in code:
                var_code = clean_and_replace_underscores(code, i)
                if var_code and var_code not in codes_to_try:
                    codes_to_try.append(var_code)
        
        # Add stripped version as last resort
        stripped_code = ''.join(c for c in code if c.isalnum())
        if stripped_code and stripped_code not in codes_to_try:
            codes_to_try.append(stripped_code)

        try:
            wait = WebDriverWait(self.driver, 15, poll_frequency=0.1)
            
            for attempt_code in codes_to_try:
                print(f"[SCALE] Trying code: {attempt_code}")
                
                coupon_input = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder="Coupon code"]')))
                coupon_input.clear()
                coupon_input.send_keys(attempt_code)

                apply_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[normalize-space(text())="Apply"]')))
                apply_button.click()

                try:
                    message = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[contains(@class, "MuiTypography-caption") and (' +
                                       'contains(text(), "Coupon code accepted") or ' +
                                       'contains(text(), "Coupon not found"))]')
                        )
                    )
                    text = message.text.strip()

                    if "Coupon code accepted" in text:
                        self.parent.log_signal.emit(f"[SCALE] ✅ Coupon accepted: {attempt_code}")
                        submit_button = self.driver.find_element(
                            By.XPATH, '//button[normalize-space(text())="Submit"]'
                        )
                        submit_button.click()
                        self.parent.log_signal.emit(f"[SCALE] ✅ Submit button clicked")
                        return True

                    elif "Coupon not found" in text:
                        self.parent.log_signal.emit(f"[SCALE] ❌ Code not found: {attempt_code}")
                        if auto_remove_coupon_code_enabled:
                            coupon_input.clear()

                except TimeoutException:
                    self.parent.log_signal.emit(f"[SCALE] ⏰ No response for: {attempt_code}")
                    continue

            self.parent.log_signal.emit(f"[SCALE] ❌ All variations failed for: {code}")
            return False

        except Exception as e:
            self.parent.log_signal.emit(f"[SCALE] ❌ Error applying code: {str(e)}")
            return False

class ProBot(BaseBot):
    def __init__(self, parent):
        super().__init__("Pro")
        self.parent = parent
        self.page_url = "https://myfundedfutures.com/login"

    def navigate_to_page(self):
        self.driver.get(self.page_url)

    def preprocess_image(self, image):
        image = image.convert('L')
        scale = 1
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)
        image = ImageOps.invert(image)
        image = ImageOps.autocontrast(image)
        img_np = np.array(image)
        img_np = cv2.bilateralFilter(img_np, 9, 75, 75)
        _, img_np = cv2.threshold(img_np, 100, 255, cv2.THRESH_BINARY)
        processed = Image.fromarray(img_np)
        return processed

    def extract_code(self, text):
        # More flexible patterns that can handle underscores
        patterns = [
            r'CODE[:\s]*([A-Z0-9_]{4,16})',
            r'USE CODE[:\s]*([A-Z0-9_]{4,16})',
            r'\b([A-Z_]{3,}[0-9]{2,})\b',
            r'\b([A-Z0-9_]{5,}\d{1,})\b'
        ]
        return extract_code_with_reverse(text, patterns, require_keyword="PRO")

    def apply_code(self, code):
        if not code:
            return False

        print(f"[PRO] Attempting to apply code: {code}")
        
        # Try dictionary filling first if enabled
        codes_to_try = []
        if dictionary_underscore_enabled and "_" in code:
            dict_filled = dictionary_fill_code(code)
            if dict_filled != code:
                codes_to_try.append(dict_filled)
                print(f"[PRO] Added dictionary filled code: {dict_filled}")
        
        # Add original code and variations
        codes_to_try.append(code)
        
        # Add underscore replacement variations
        for i in range(len(underscore_replacements)):
            if "_" in code:
                var_code = clean_and_replace_underscores(code, i)
                if var_code and var_code not in codes_to_try:
                    codes_to_try.append(var_code)
        
        # Add stripped version as last resort
        stripped_code = ''.join(c for c in code if c.isalnum())
        if stripped_code and stripped_code not in codes_to_try:
            codes_to_try.append(stripped_code)

        try:
            wait = WebDriverWait(self.driver, 15, poll_frequency=0.1)
            
            for attempt_code in codes_to_try:
                print(f"[PRO] Trying code: {attempt_code}")
                
                coupon_input = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder="Coupon code"]')))
                coupon_input.clear()
                coupon_input.send_keys(attempt_code)

                apply_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[normalize-space(text())="Apply"]')))
                apply_button.click()

                try:
                    message = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[contains(@class, "MuiTypography-caption") and (' +
                                       'contains(text(), "Coupon code accepted") or ' +
                                       'contains(text(), "Coupon not found"))]')
                        )
                    )
                    text = message.text.strip()

                    if "Coupon code accepted" in text:
                        self.parent.log_signal.emit(f"[PRO] ✅ Coupon accepted: {attempt_code}")
                        submit_button = self.driver.find_element(
                            By.XPATH, '//button[normalize-space(text())="Submit"]'
                        )
                        submit_button.click()
                        self.parent.log_signal.emit(f"[PRO] ✅ Submit button clicked")
                        return True

                    elif "Coupon not found" in text:
                        self.parent.log_signal.emit(f"[PRO] ❌ Code not found: {attempt_code}")
                        if auto_remove_coupon_code_enabled:
                            coupon_input.clear()

                except TimeoutException:
                    self.parent.log_signal.emit(f"[PRO] ⏰ No response for: {attempt_code}")
                    continue

            self.parent.log_signal.emit(f"[PRO] ❌ All variations failed for: {code}")
            return False

        except Exception as e:
            self.parent.log_signal.emit(f"[PRO] ❌ Error applying code: {str(e)}")
            return False

class ResetBot(BaseBot):
    def __init__(self, parent):
        super().__init__("Reset")
        self.parent = parent
        self.page_url = "https://myfundedfutures.com/login"

    def navigate_to_page(self):
        self.driver.get(self.page_url)

    def preprocess_image(self, image):
        image = image.convert('L')
        scale = 1
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)
        image = ImageOps.invert(image)
        image = ImageOps.autocontrast(image)
        img_np = np.array(image)
        img_np = cv2.bilateralFilter(img_np, 9, 75, 75)
        _, img_np = cv2.threshold(img_np, 100, 255, cv2.THRESH_BINARY)
        processed = Image.fromarray(img_np)
        return processed

    def extract_code(self, text):
        # More flexible patterns that can handle underscores
        patterns = [
            r'CODE[:\s]*([A-Z0-9_]{4,16})',
            r'USE CODE[:\s]*([A-Z0-9_]{4,16})',
            r'\b([A-Z_]{3,}[0-9]{2,})\b',
            r'\b([A-Z0-9_]{5,}\d{1,})\b'
        ]
        return extract_code_with_reverse(text, patterns, require_keyword="RESET")

    def apply_code(self, code):
        if not code:
            return False

        print(f"[RESET] Attempting to apply code: {code}")
        
        # Try dictionary filling first if enabled
        codes_to_try = []
        if dictionary_underscore_enabled and "_" in code:
            dict_filled = dictionary_fill_code(code)
            if dict_filled != code:
                codes_to_try.append(dict_filled)
                print(f"[RESET] Added dictionary filled code: {dict_filled}")
        
        # Add original code and variations
        codes_to_try.append(code)
        
        # Add underscore replacement variations
        for i in range(len(underscore_replacements)):
            if "_" in code:
                var_code = clean_and_replace_underscores(code, i)
                if var_code and var_code not in codes_to_try:
                    codes_to_try.append(var_code)
        
        # Add stripped version as last resort
        stripped_code = ''.join(c for c in code if c.isalnum())
        if stripped_code and stripped_code not in codes_to_try:
            codes_to_try.append(stripped_code)

        try:
            wait = WebDriverWait(self.driver, 15, poll_frequency=0.1)
            
            for attempt_code in codes_to_try:
                print(f"[RESET] Trying code: {attempt_code}")
                
                coupon_input = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder="Coupon code"]')))
                coupon_input.clear()
                coupon_input.send_keys(attempt_code)

                apply_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[normalize-space(text())="Apply"]')))
                apply_button.click()

                try:
                    message = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[contains(@class, "MuiTypography-caption") and (' +
                                       'contains(text(), "Coupon code accepted") or ' +
                                       'contains(text(), "Coupon not found"))]')
                        )
                    )
                    text = message.text.strip()

                    if "Coupon code accepted" in text:
                        self.parent.log_signal.emit(f"[RESET] ✅ Coupon accepted: {attempt_code}")
                        submit_button = self.driver.find_element(
                            By.XPATH, '//button[normalize-space(text())="Submit"]'
                        )
                        submit_button.click()
                        self.parent.log_signal.emit(f"[RESET] ✅ Submit button clicked")
                        return True

                    elif "Coupon not found" in text:
                        self.parent.log_signal.emit(f"[RESET] ❌ Code not found: {attempt_code}")
                        if auto_remove_coupon_code_enabled:
                            coupon_input.clear()

                except TimeoutException:
                    self.parent.log_signal.emit(f"[RESET] ⏰ No response for: {attempt_code}")
                    continue

            self.parent.log_signal.emit(f"[RESET] ❌ All variations failed for: {code}")
            return False

        except Exception as e:
            self.parent.log_signal.emit(f"[RESET] ❌ Error applying code: {str(e)}")
            return False

# ==========================================
# INSTRUCTIONS DIALOG
# ==========================================

class InstructionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Code Sniper Instructions")
        self.setGeometry(200, 200, 700, 500)
        
        layout = QVBoxLayout()
        
        instructions = QLabel(
            "<h2 style='color: #00ff88;'>🚀 Code Sniper Instructions</h2>"
            "<p><b style='color: #64b5f6;'>1. Setup:</b></p>"
            "<ul>"
            "<li>Open your trading platform with coupon codes visible</li>"
            "<li>Position the coupon code display in your screen</li>"
            "</ul>"
            
            "<p><b style='color: #64b5f6;'>2. Region Selection:</b></p>"
            "<ul>"
            "<li>Click <b>'Show Overlay'</b> to activate the modern snipping tool</li>"
            "<li>Drag to create a rectangle around the coupon code area</li>"
            "<li>Resize using corner handles for precise selection</li>"
            "<li>Press <b>ESC</b> to confirm selection</li>"
            "</ul>"
            
            "<p><b style='color: #64b5f6;'>3. Bot Operation:</b></p>"
            "<ul>"
            "<li>Select the account type (Reset, Scale, Pro)</li>"
            "<li>Click <b>'Start'</b> to begin monitoring for codes</li>"
            "<li>The bot will automatically apply valid codes with smart corrections</li>"
            "<li>Dictionary-based underscore correction is now enabled by default</li>"
            "</ul>"
            
            
            
            
            "<p><b style='color: #64b5f6;'>4. Advanced Features:</b></p>"
            "<ul>"
            "<li><b>Smart Dictionary Filling:</b> Automatically converts codes like 'PAR_Y25' to 'PARTY25'</li>"
            "<li><b>Multiple Code Attempts:</b> Tries dictionary correction, then fallback methods</li>"
            "<li><b>Enhanced Logging:</b> Shows detailed extraction and attempt process</li>"
            "<li><b>Modern UI:</b> Fresh, dark theme with visual indicators</li>"
            "</ul>"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #f0f0f0; background-color: #1a1a1a; padding: 20px; border-radius: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(instructions)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: #1a1a1a; border: none; }")
        
        ok_button = QPushButton("Got it! 🚀")
        ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #00ff88, stop: 1 #00cc66);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #00cc66, stop: 1 #00aa44);
            }
        """)
        ok_button.clicked.connect(self.accept)
        
        layout.addWidget(scroll)
        layout.addWidget(ok_button)
        self.setLayout(layout)

        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #232629;
                color: #f0f0f0;
            }
        """)

# ==========================================
# USER MANAGEMENT WIDGET (ADMIN PANEL)
# ==========================================

class UserManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.users = []
        self.selected_user = None
        layout = QVBoxLayout()
        
        # User list with modern styling
        self.user_list = QListWidget()
        self.user_list.itemClicked.connect(self.on_user_selected)
        self.user_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 10px;
                color: #f0f0f0;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #00ff88, stop: 1 #00cc66);
                color: white;
            }
            QListWidget::item:hover {
                background-color: #333;
            }
        """)
        self.refresh_user_list()
        layout.addWidget(self.user_list)
        
        # User details
        self.user_details = QTextEdit()
        self.user_details.setReadOnly(True)
        self.user_details.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 10px;
                color: #f0f0f0;
            }
        """)
        layout.addWidget(self.user_details)
        
        # Action buttons with modern styling
        btn_layout = QHBoxLayout()
        
        button_style = """
            QPushButton {
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                margin: 2px;
            }
        """
        
        self.add_btn = QPushButton("Add User")
        self.add_btn.setStyleSheet(button_style + "background-color: #4CAF50; color: white;")
        self.add_btn.clicked.connect(self.add_user)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit User")
        self.edit_btn.setStyleSheet(button_style + "background-color: #2196F3; color: white;")
        self.edit_btn.clicked.connect(self.edit_user)
        btn_layout.addWidget(self.edit_btn)
        
        self.reset_pwd_btn = QPushButton("Reset Password")
        self.reset_pwd_btn.setStyleSheet(button_style + "background-color: #FF9800; color: white;")
        self.reset_pwd_btn.clicked.connect(self.reset_password)
        btn_layout.addWidget(self.reset_pwd_btn)
        
        self.suspend_btn = QPushButton("Suspend User")
        self.suspend_btn.setStyleSheet(button_style + "background-color: #f44336; color: white;")
        self.suspend_btn.clicked.connect(self.suspend_user)
        btn_layout.addWidget(self.suspend_btn)
        
        self.unsuspend_btn = QPushButton("Unsuspend User")
        self.unsuspend_btn.setStyleSheet(button_style + "background-color: #9C27B0; color: white;")
        self.unsuspend_btn.clicked.connect(self.unsuspend_user)
        btn_layout.addWidget(self.unsuspend_btn)
        
        self.kick_btn = QPushButton("Kick Out")
        self.kick_btn.setStyleSheet(button_style + "background-color: #607D8B; color: white;")
        self.kick_btn.clicked.connect(self.kick_user)
        btn_layout.addWidget(self.kick_btn)

        self.delete_btn = QPushButton("Delete User")
        self.delete_btn.setStyleSheet(button_style + "background-color: #e53935; color: white;")
        self.delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def refresh_user_list(self):
        try:
            self.user_list.clear()
            users_ref = db.collection("users")
            self.users = [doc.to_dict() for doc in users_ref.stream()]
            for user in self.users:
                username = user.get("username", "Unknown")
                role = user.get("role", "user")
                status = "🟢" if user.get("is_online") else "🔴"
                if user.get("suspended_until"):
                    status = "⛔"
                self.user_list.addItem(f"{status} {username} ({role})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {e}")

    def on_user_selected(self, item):
        try:
            idx = self.user_list.currentRow()
            if 0 <= idx < len(self.users):
                self.selected_user = self.users[idx]
                self.display_user_details()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select user: {e}")

    def display_user_details(self):
        if not self.selected_user:
            return
            
        details = []
        details.append(f"Username: {self.selected_user.get('username', 'N/A')}")
        details.append(f"Role: {self.selected_user.get('role', 'user')}")
        details.append(f"Created: {self.selected_user.get('created_at', 'N/A')}")
        details.append(f"HWID: {self.selected_user.get('hwid', 'Not set')}")
        details.append(f"IP: {self.selected_user.get('ip', 'Not set')}")
        details.append(f"Status: {'Online' if self.selected_user.get('is_online') else 'Offline'}")
        
        suspended = self.selected_user.get("suspended_until")
        if suspended:
            details.append(f"Suspended Until: {suspended}")
        
        admin_note = self.selected_user.get("admin_note")
        if admin_note:
            details.append(f"Admin Note: {admin_note}")
        
        self.user_details.setText("\n".join(details))
    
    def add_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")
        dialog.setStyleSheet("QDialog { background-color: #232629; color: #f0f0f0; }")
        layout = QVBoxLayout()
        
        username = QLineEdit()
        username.setPlaceholderText("Username")
        username.setStyleSheet("QLineEdit { background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px; padding: 8px; color: #f0f0f0; }")
        layout.addWidget(username)
        
        password = QLineEdit()
        password.setPlaceholderText("Password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setStyleSheet("QLineEdit { background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px; padding: 8px; color: #f0f0f0; }")
        layout.addWidget(password)
        
        role = QComboBox()
        role.addItems(["user", "admin"])
        role.setStyleSheet("QComboBox { background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px; padding: 8px; color: #f0f0f0; }")
        layout.addWidget(role)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_user = {
                "username": username.text().strip(),
                "password": hash_password(password.text()),
                "role": role.currentText(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "is_online": False,
                "hwid": None,
                "ip": None,
                "bot_speed": "default",
                "suspended_until": None,
                "logs": []
            }
            try:
                db.collection("users").document(new_user["username"]).set(new_user)
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add user: {e}")

    def edit_user(self):
        if not self.selected_user:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit User")
        dialog.setStyleSheet("QDialog { background-color: #232629; color: #f0f0f0; }")
        layout = QVBoxLayout()
        
        username = QLabel(f"Username: {self.selected_user['username']}")
        layout.addWidget(username)
        
        role = QComboBox()
        role.addItems(["user", "admin"])
        role.setCurrentText(self.selected_user.get("role", "user"))
        role.setStyleSheet("QComboBox { background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px; padding: 8px; color: #f0f0f0; }")
        layout.addWidget(role)

        admin_note_label = QLabel("Admin Note:")
        layout.addWidget(admin_note_label)
        admin_note_edit = QTextEdit()
        admin_note_edit.setPlaceholderText("Enter a note about this user (visible only to admins)")
        admin_note_edit.setMinimumHeight(50)
        admin_note_edit.setText(self.selected_user.get("admin_note", ""))
        admin_note_edit.setStyleSheet("QTextEdit { background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px; padding: 8px; color: #f0f0f0; }")
        layout.addWidget(admin_note_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                db.collection("users").document(self.selected_user["username"]).update({
                    "role": role.currentText(),
                    "admin_note": admin_note_edit.toPlainText()
                })
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update user: {e}")

    def reset_password(self):
        if not self.selected_user:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
            
        new_password, ok = QInputDialog.getText(self, "Reset Password", "Enter new password:")
        if ok and new_password:
            try:
                db.collection("users").document(self.selected_user["username"]).update({
                    "password": hash_password(new_password)
                })
                log_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "action": "Password reset by admin"
                }
                db.collection("users").document(self.selected_user["username"]).update({
                    "logs": firestore.ArrayUnion([log_entry])
                })
                QMessageBox.information(self, "Success", "Password reset successfully")
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset password: {e}")

    def suspend_user(self):
        if not self.selected_user:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
            
        days, ok = QInputDialog.getInt(self, "Suspend User", "Suspend for how many days?", 1, 1, 365, 1)
        if ok:
            end_time = datetime.now() + timedelta(days=days)
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M")
            try:
                db.collection("users").document(self.selected_user["username"]).update({
                    "suspended_until": end_time_str,
                    "is_online": False
                })
                log_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "action": f"Suspended for {days} days until {end_time_str}"
                }
                db.collection("users").document(self.selected_user["username"]).update({
                    "logs": firestore.ArrayUnion([log_entry])
                })
                QMessageBox.information(self, "Success", f"User suspended until {end_time_str}")
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to suspend user: {e}")

    def unsuspend_user(self):
        if not self.selected_user:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
        try:
            db.collection("users").document(self.selected_user["username"]).update({
                "suspended_until": None
            })
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action": "Suspension removed by admin"
            }
            db.collection("users").document(self.selected_user["username"]).update({
                "logs": firestore.ArrayUnion([log_entry])
            })
            QMessageBox.information(self, "Success", "User unsuspended")
            self.refresh_user_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to unsuspend user: {e}")

    def kick_user(self):
        if not self.selected_user:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
        try:
            db.collection("users").document(self.selected_user["username"]).update({
                "is_online": False
            })
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action": "Kicked by admin"
            }
            db.collection("users").document(self.selected_user["username"]).update({
                "logs": firestore.ArrayUnion([log_entry])
            })
            QMessageBox.information(self, "Success", "User kicked out")
            self.refresh_user_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to kick user: {e}")

    def delete_user(self):
        if not self.selected_user:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
        username = self.selected_user.get("username")
        if not username:
            QMessageBox.warning(self, "Warning", "Invalid user selected")
            return
        reply = QMessageBox.question(
            self, "Delete User",
            f"Are you sure you want to permanently delete user '{username}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db.collection("users").document(username).delete()
                QMessageBox.information(self, "Success", f"User '{username}' deleted.")
                self.refresh_user_list()
                self.selected_user = None
                self.user_details.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {e}")

# ==========================================
# MAIN APPLICATION WINDOW
# ==========================================

class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str)
    code_found_signal = pyqtSignal(str)
    ocr_raw_signal = pyqtSignal(str)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("🚀 Code Sniper - Advanced Bot")
        self.setGeometry(100, 100, 900, 800)
        
        # Modern dark theme styling
        self.setStyleSheet("""
            QMainWindow { 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #1a1a2e, stop: 1 #16213e); 
                color: #f0f0f0; 
            }
            QWidget { 
                background-color: transparent; 
                color: #f0f0f0; 
            }
            QPushButton { 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #333, stop: 1 #555); 
                color: #fff; 
                border: 2px solid #666;
                border-radius: 8px; 
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #555, stop: 1 #777); 
                border: 2px solid #888;
            }
            QPushButton:pressed { 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #222, stop: 1 #444); 
            }
            QTextEdit, QLineEdit { 
                background-color: #1a1a1a; 
                color: #f0f0f0; 
                border: 2px solid #333;
                border-radius: 8px;
                padding: 8px;
            }
            QLabel { 
                color: #f0f0f0; 
            }
            QTabWidget::pane { 
                border: 2px solid #333; 
                border-radius: 8px;
                background-color: rgba(26, 26, 26, 0.8);
            }
            QTabBar::tab { 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #333, stop: 1 #555); 
                color: #f0f0f0; 
                padding: 12px 20px; 
                margin: 2px;
                border-radius: 6px 6px 0px 0px;
                border: 2px solid #666;
            }
            QTabBar::tab:selected { 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #00ff88, stop: 1 #00cc66); 
                color: white;
                border: 2px solid #00ff88;
            }
            QTabBar::tab:hover { 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #555, stop: 1 #777); 
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: rgba(26, 26, 26, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff88;
            }
            QCheckBox {
                color: #f0f0f0;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #666;
                background-color: #333;
            }
            QCheckBox::indicator:checked {
                background-color: #00ff88;
                border: 2px solid #00cc66;
            }
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 6px;
                padding: 8px;
                color: #f0f0f0;
            }
            QComboBox:hover {
                border: 2px solid #555;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #f0f0f0;
                width: 0;
                height: 0;
            }
            QProgressBar {
                border: 2px solid #333;
                border-radius: 6px;
                text-align: center;
                background-color: #1a1a1a;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #00ff88, stop: 1 #00cc66);
                border-radius: 4px;
            }
        """)

        # Create overlay window
        self.overlay = OverlayWindow(self)
        self.overlay.hide()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Main Tab ---
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Welcome header with modern styling
        header = QLabel("🚀 Code Sniper Pro")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #00ff88;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 rgba(0, 255, 136, 0.1), stop: 1 rgba(0, 204, 102, 0.1));
                border: 2px solid #00ff88;
                border-radius: 15px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header)

        # Status indicator
        self.status_label = QLabel("🔴 Ready to start")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        main_layout.addWidget(self.status_label)

        # Bot Controls Group
        bot_group = QGroupBox("🤖 Bot Controls")
        bot_layout = QHBoxLayout()
        self.buttons = {}

        # RESET Bot Button
        self.reset_button = QPushButton("Start RESET")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #42a5f5, stop: 1 #1976d2);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #64b5f6, stop: 1 #1976d2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #1565c0, stop: 1 #0d47a1);
            }
        """)
        self.reset_button.clicked.connect(lambda: self.toggle_bot("Reset"))
        bot_layout.addWidget(self.reset_button)
        self.buttons["Reset"] = self.reset_button

        # SCALE Bot Button
        self.scale_button = QPushButton("Start SCALE")
        self.scale_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #ba68c8, stop: 1 #7b1fa2);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #ce93d8, stop: 1 #8e24aa);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #6a1b9a, stop: 1 #4a148c);
            }
        """)
        self.scale_button.clicked.connect(lambda: self.toggle_bot("Scale"))
        bot_layout.addWidget(self.scale_button)
        self.buttons["Scale"] = self.scale_button

        # PRO Bot Button
        self.pro_button = QPushButton("Start PRO")
        self.pro_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #ff8a65, stop: 1 #d84315);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #ffab91, stop: 1 #f4511e);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #bf360c, stop: 1 #bf360c);
            }
        """)
        self.pro_button.clicked.connect(lambda: self.toggle_bot("Pro"))
        bot_layout.addWidget(self.pro_button)
        self.buttons["Pro"] = self.pro_button

        bot_group.setLayout(bot_layout)
        main_layout.addWidget(bot_group)

        # Region Controls Group
        region_group = QGroupBox("📍 Region Controls")
        region_layout = QHBoxLayout()
        
        self.snip_button = QPushButton("Show Overlay")
        self.snip_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #4CAF50, stop: 1 #2E7D32);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #66BB6A, stop: 1 #388E3C);
            }
        """)
        self.snip_button.clicked.connect(self.toggle_overlay)
        region_layout.addWidget(self.snip_button)

        self.color_btn = QPushButton("Change Color")
        self.color_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #f44336, stop: 1 #c62828);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #ef5350, stop: 1 #d32f2f);
            }
        """)
        self.color_btn.clicked.connect(self.change_overlay_color)
        region_layout.addWidget(self.color_btn)

        self.preview_btn = QPushButton("Preview Capture")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #2196F3, stop: 1 #1565C0);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #42A5F5, stop: 1 #1976D2);
            }
        """)
        self.preview_btn.clicked.connect(self.show_preview)
        region_layout.addWidget(self.preview_btn)

        region_group.setLayout(region_layout)
        main_layout.addWidget(region_group)

        # Region status
        self.region_status = QLabel(f"📍 Current Region: {current_ocr_region.getRect()}")
        self.region_status.setStyleSheet("""
            QLabel {
                color: #64b5f6; 
                font-weight: bold; 
                font-size: 14px;
                padding: 8px;
                background-color: rgba(100, 181, 246, 0.1);
                border: 1px solid #64b5f6;
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(self.region_status)

        # Progress bar for bot activity
        self.activity_progress = QProgressBar()
        self.activity_progress.setRange(0, 0)  # Indeterminate progress
        self.activity_progress.hide()
        main_layout.addWidget(self.activity_progress)

        # Codes Info Group
        codes_group = QGroupBox("📊 Code Statistics")
        codes_layout = QVBoxLayout()
        codes_layout.setSpacing(12)

        self.codes_found_label = QLabel("Total Codes Found: 0")
        self.codes_found_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 18px; 
                color: #00ff88;
                text-align: center;
                padding: 10px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 rgba(0, 255, 136, 0.1), stop: 1 rgba(0, 204, 102, 0.1));
                border-radius: 8px;
            }
        """)
        codes_layout.addWidget(self.codes_found_label)

        counts_layout = QHBoxLayout()
        # RESET count label
        self.reset_count_label = QLabel("RESET Found: 0")
        self.reset_count_label.setStyleSheet("color: #42a5f5; font-weight: bold; padding: 8px; background-color: rgba(66, 165, 245, 0.1); border-radius: 6px;")
        counts_layout.addWidget(self.reset_count_label)
        
        # SCALE count label
        self.scale_count_label = QLabel("SCALE Found: 0")
        self.scale_count_label.setStyleSheet("color: #ba68c8; font-weight: bold; padding: 8px; background-color: rgba(186, 104, 200, 0.1); border-radius: 6px;")
        counts_layout.addWidget(self.scale_count_label)
        
        # PRO count label
        self.pro_count_label = QLabel("PRO Found: 0")
        self.pro_count_label.setStyleSheet("color: #ff8a65; font-weight: bold; padding: 8px; background-color: rgba(255, 138, 101, 0.1); border-radius: 6px;")
        counts_layout.addWidget(self.pro_count_label)
        
        codes_layout.addLayout(counts_layout)

        # Recent codes
        recent_label = QLabel("🕒 Recent Codes:")
        recent_label.setStyleSheet("font-weight: bold; margin-top: 8px; color: #64b5f6;")
        codes_layout.addWidget(recent_label)

        self.codes_list = QTextEdit()
        self.codes_list.setReadOnly(True)
        self.codes_list.setMaximumHeight(150)
        self.codes_list.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a; 
                color: #f0f0f0; 
                border-radius: 8px; 
                border: 2px solid #333;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        codes_layout.addWidget(self.codes_list)

        codes_group.setLayout(codes_layout)
        main_layout.addWidget(codes_group)
        main_layout.addStretch(1)

        # --- Activity Log Tab ---
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(25, 25, 25, 25)
        log_layout.setSpacing(15)
        
        log_header = QLabel("📋 Activity Log")
        log_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #64b5f6;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 rgba(100, 181, 246, 0.1), stop: 1 rgba(25, 118, 210, 0.1));
                border: 2px solid #64b5f6;
                border-radius: 12px;
            }
        """)
        log_layout.addWidget(log_header)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a; 
                color: #f0f0f0; 
                border-radius: 10px; 
                border: 2px solid #333;
                padding: 15px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        log_layout.addWidget(self.log_area)

        # --- Instructions Tab ---
        instructions_tab = QWidget()
        instructions_layout = QVBoxLayout(instructions_tab)
        instructions_layout.setContentsMargins(25, 25, 25, 25)
        instructions_layout.setSpacing(15)
        
        instructions_header = QLabel("📖 Instructions & Features")
        instructions_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ff8a65;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 rgba(255, 138, 101, 0.1), stop: 1 rgba(212, 67, 21, 0.1));
                border: 2px solid #ff8a65;
                border-radius: 12px;
            }
        """)
        instructions_layout.addWidget(instructions_header)
        
        # Create instructions content
        instructions_content = QLabel(
            "<h2 style='color: #00ff88;'>🚀 Code Sniper Instructions</h2>"
            "<p><b style='color: #64b5f6;'>1. Setup:</b></p>"
            "<ul>"
            "<li>Open your trading platform with coupon codes visible</li>"
            "<li>Position the coupon code display in your screen</li>"
            "</ul>"
            
            "<p><b style='color: #64b5f6;'>2. Region Selection:</b></p>"
            "<ul>"
            "<li>Click <b>'Show Overlay'</b> to activate the modern snipping tool</li>"
            "<li>Drag to create a rectangle around the coupon code area</li>"
            "<li>Resize using corner handles for precise selection</li>"
            "<li>Press <b>ESC</b> to confirm selection</li>"
            "</ul>"
            
            "<p><b style='color: #64b5f6;'>3. Bot Operation:</b></p>"
            "<ul>"
            "<li>Select the account type (Reset, Scale, Pro)</li>"
            "<li>Click <b>'Start'</b> to begin monitoring for codes</li>"
            "<li>The bot will automatically apply valid codes with smart corrections</li>"
            "<li>Dictionary-based underscore correction is now enabled by default</li>"
            "</ul>"
            
            "<p><b style='color: #64b5f6;'>4. Advanced Features:</b></p>"
            "<ul>"
            "<li><b>Smart Dictionary Filling:</b> Automatically converts codes like 'PAR_Y25' to 'PARTY25'</li>"
            "<li><b>Multiple Code Attempts:</b> Tries dictionary correction, then fallback methods</li>"
            "<li><b>Enhanced Logging:</b> Shows detailed extraction and attempt process</li>"
            "<li><b>Modern UI:</b> Fresh, dark theme with visual indicators</li>"
            "</ul>"
        )
        instructions_content.setWordWrap(True)
        instructions_content.setStyleSheet("color: #f0f0f0; background-color: #1a1a1a; padding: 20px; border-radius: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(instructions_content)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        instructions_layout.addWidget(scroll)

        # --- Settings Tab ---
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(25, 25, 25, 25)
        settings_layout.setSpacing(15)
        
        settings_header = QLabel("⚙️ Advanced Settings")
        settings_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ba68c8;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 rgba(186, 104, 200, 0.1), stop: 1 rgba(123, 31, 162, 0.1));
                border: 2px solid #ba68c8;
                border-radius: 12px;
            }
        """)
        settings_layout.addWidget(settings_header)
        
        # Theme controls
        theme_group = QGroupBox("🎨 Appearance")
        theme_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText("Dark")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addRow("Select Theme:", self.theme_combo)
        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)
        
        # Smart features group
        smart_group = QGroupBox("🧠 Smart Features")
        smart_layout = QVBoxLayout()
        
        # Dictionary correction (enabled by default)
        self.dictionary_underscore_checkbox = QCheckBox("✅ Use dictionary to auto-fill missing letters (PAR_Y25 → PARTY25)")
        self.dictionary_underscore_checkbox.setChecked(True)
        self.dictionary_underscore_checkbox.stateChanged.connect(self.toggle_dictionary_underscore)
        smart_layout.addWidget(self.dictionary_underscore_checkbox)
        
        # Other smart features
        self.smart_fix_ending_checkbox = QCheckBox("Smart code ending correction (SO/S0/5O → 50)")
        self.smart_fix_ending_checkbox.setChecked(smart_fix_ending_enabled)
        self.smart_fix_ending_checkbox.stateChanged.connect(self.toggle_smart_fix_ending)
        smart_layout.addWidget(self.smart_fix_ending_checkbox)
        
        self.reverse_code_if_instructed_checkbox = QCheckBox("Reverse code if instructed (e.g. 'type it backwards')")
        self.reverse_code_if_instructed_checkbox.setChecked(reverse_code_if_instructed_enabled)
        self.reverse_code_if_instructed_checkbox.stateChanged.connect(self.toggle_reverse_code_if_instructed)
        smart_layout.addWidget(self.reverse_code_if_instructed_checkbox)
        
        self.auto_remove_coupon_code_checkbox = QCheckBox("Auto remove failed codes from input")
        self.auto_remove_coupon_code_checkbox.setChecked(auto_remove_coupon_code_enabled)
        self.auto_remove_coupon_code_checkbox.stateChanged.connect(self.toggle_auto_remove_coupon_code)
        smart_layout.addWidget(self.auto_remove_coupon_code_checkbox)
        
        smart_group.setLayout(smart_layout)
        settings_layout.addWidget(smart_group)
        
        # Legacy features group
        legacy_group = QGroupBox("🔧 Legacy Features")
        legacy_layout = QVBoxLayout()
        
        self.trim_after_50_checkbox = QCheckBox("Trim everything after 50 (ABC5000XYZ → ABC50)")
        self.trim_after_50_checkbox.setChecked(trim_after_50_enabled)
        self.trim_after_50_checkbox.stateChanged.connect(self.toggle_trim_after_50)
        legacy_layout.addWidget(self.trim_after_50_checkbox)
        
        self.trim_after_25_checkbox = QCheckBox("Trim everything after 25 (XYZ2500ABC → XYZ25)")
        self.trim_after_25_checkbox.setChecked(trim_after_25_enabled)
        self.trim_after_25_checkbox.stateChanged.connect(self.toggle_trim_after_25)
        legacy_layout.addWidget(self.trim_after_25_checkbox)
        
        self.smart_fix_ss_to_55_checkbox = QCheckBox("Smart SS→55 correction")
        self.smart_fix_ss_to_55_checkbox.setChecked(smart_fix_ss_to_55_enabled)
        self.smart_fix_ss_to_55_checkbox.stateChanged.connect(self.toggle_smart_fix_ss_to_55)
        legacy_layout.addWidget(self.smart_fix_ss_to_55_checkbox)
        
        self.smart_fix_2s_to_25_checkbox = QCheckBox("Smart 2S→25 correction")
        self.smart_fix_2s_to_25_checkbox.setChecked(smart_fix_2s_to_25_enabled)
        self.smart_fix_2s_to_25_checkbox.stateChanged.connect(self.toggle_smart_fix_2s_to_25)
        legacy_layout.addWidget(self.smart_fix_2s_to_25_checkbox)
        
        self.smart_fix_digit_o_to_digit0_checkbox = QCheckBox("Smart digit+O → digit+0 correction")
        self.smart_fix_digit_o_to_digit0_checkbox.setChecked(smart_fix_digit_o_to_digit0_enabled)
        self.smart_fix_digit_o_to_digit0_checkbox.stateChanged.connect(self.toggle_smart_fix_digit_o_to_digit0)
        legacy_layout.addWidget(self.smart_fix_digit_o_to_digit0_checkbox)
        
        self.underscore_to_t_checkbox = QCheckBox("Replace all '_' with 'T' (fallback)")
        self.underscore_to_t_checkbox.setChecked(underscore_to_t_enabled)
        self.underscore_to_t_checkbox.stateChanged.connect(self.toggle_underscore_to_t)
        legacy_layout.addWidget(self.underscore_to_t_checkbox)
        
        legacy_group.setLayout(legacy_layout)
        settings_layout.addWidget(legacy_group)
        
        # Admin features (if admin)
        if self.user.get("role", "user") == "admin":
            admin_features_group = QGroupBox("👑 Admin Features")
            admin_features_layout = QVBoxLayout()
            
            self.show_ocr_raw_checkbox = QCheckBox("Show OCR RAW logs")
            self.show_ocr_raw_checkbox.setChecked(show_ocr_raw_enabled)
            self.show_ocr_raw_checkbox.stateChanged.connect(self.toggle_show_ocr_raw)
            admin_features_layout.addWidget(self.show_ocr_raw_checkbox)
            
            admin_features_group.setLayout(admin_features_layout)
            settings_layout.addWidget(admin_features_group)
        
        settings_layout.addStretch(1)

        # --- Admin Control Panel Tab (only for admins) ---
        if self.user.get("role", "") == "admin":
            admin_tab = QWidget()
            admin_layout = QVBoxLayout(admin_tab)
            admin_layout.setContentsMargins(25, 25, 25, 25)
            admin_layout.setSpacing(15)
            
            admin_header = QLabel("👑 Admin Control Panel")
            admin_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            admin_header.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #f44336;
                    padding: 15px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                        stop: 0 rgba(244, 67, 54, 0.1), stop: 1 rgba(183, 28, 28, 0.1));
                    border: 2px solid #f44336;
                    border-radius: 12px;
                }
            """)
            admin_layout.addWidget(admin_header)
            
            # Embed UserManagementWidget
            self.user_mgmt_widget = UserManagementWidget()
            admin_layout.addWidget(self.user_mgmt_widget)
            self.tabs.addTab(admin_tab, "👑 Admin Panel")

            # --- Add OCR RAW Log Tab for admins ---
            self.ocr_raw_tab = QWidget()
            ocr_raw_layout = QVBoxLayout(self.ocr_raw_tab)
            ocr_raw_layout.setContentsMargins(25, 25, 25, 25)
            ocr_raw_layout.setSpacing(15)
            
            ocr_raw_header = QLabel("🧪 OCR RAW Debug Log")
            ocr_raw_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ocr_raw_header.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #9c27b0;
                    padding: 15px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                        stop: 0 rgba(156, 39, 176, 0.1), stop: 1 rgba(74, 20, 140, 0.1));
                    border: 2px solid #9c27b0;
                    border-radius: 12px;
                }
            """)
            ocr_raw_layout.addWidget(ocr_raw_header)
            
            self.ocr_raw_area = QTextEdit()
            self.ocr_raw_area.setReadOnly(True)
            self.ocr_raw_area.setStyleSheet("""
                QTextEdit {
                    background: #1a1a1a; 
                    color: #f0f0f0; 
                    border-radius: 10px; 
                    border: 2px solid #333;
                    padding: 15px;
                    font-family: 'Consolas', monospace;
                    font-size: 12px;
                    line-height: 1.3;
                }
            """)
            ocr_raw_layout.addWidget(self.ocr_raw_area)
            self.tabs.addTab(self.ocr_raw_tab, "🧪 OCR RAW")

        # --- Add the tabs ---
        self.tabs.addTab(main_tab, "🏠 Dashboard")
        self.tabs.addTab(log_tab, "📋 Activity Log")
        self.tabs.addTab(instructions_tab, "📖 Instructions")
        self.tabs.addTab(settings_tab, "⚙️ Settings")

        # Connect signals to slots
        self.log_signal.connect(self.log)
        self.code_found_signal.connect(self.add_new_code)
        self.ocr_raw_signal.connect(self.append_ocr_raw)

        # Initialize UI state
        self.update_codes_display()
        self.log("🚀 Code Sniper Pro initialized with dictionary correction enabled")
        self.log(f"📍 Current OCR region: {current_ocr_region.getRect()}")
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def update_status(self):
        """Update the status indicator"""
        active_bots = [bot for bot, running in bot_running.items() if running]
        if active_bots:
            self.status_label.setText(f"🟢 Active: {', '.join(active_bots)}")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 8px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                        stop: 0 rgba(0, 255, 136, 0.2), stop: 1 rgba(0, 204, 102, 0.2));
                    color: #00ff88;
                    border: 2px solid #00ff88;
                }
            """)
            if not self.activity_progress.isVisible():
                self.activity_progress.show()
        else:
            self.status_label.setText("🔴 Ready to start")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 8px;
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #f0f0f0;
                    border: 2px solid #666;
                }
            """)
            if self.activity_progress.isVisible():
                self.activity_progress.hide()
    
    def log(self, message):
        """Add message to log area with enhanced formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add colors and emojis based on message type
        if "✅" in message or "accepted" in message.lower():
            formatted_message = f"<span style='color: #00ff88;'>[{timestamp}] {message}</span>"
        elif "❌" in message or "error" in message.lower() or "failed" in message.lower():
            formatted_message = f"<span style='color: #ff6b6b;'>[{timestamp}] {message}</span>"
        elif "⏰" in message or "timeout" in message.lower():
            formatted_message = f"<span style='color: #ffa500;'>[{timestamp}] {message}</span>"
        elif "extracted" in message.lower():
            formatted_message = f"<span style='color: #64b5f6;'>[{timestamp}] {message}</span>"
        elif "DICTIONARY" in message:
            formatted_message = f"<span style='color: #ba68c8;'>[{timestamp}] {message}</span>"
        else:
            formatted_message = f"<span style='color: #f0f0f0;'>[{timestamp}] {message}</span>"
        
        self.log_area.append(formatted_message)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )
    
    def add_new_code(self, account_type):
        """Handle new code found with enhanced feedback"""
        global codes_found, counts
        codes_found += 1
        counts[account_type] += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        found_codes_history.append((account_type, timestamp))
        self.update_codes_display()
        self.log(f"🎉 [{account_type.upper()}] Valid code found and applied!")

    def update_codes_display(self):
        """Update all code-related displays with enhanced styling"""
        self.codes_found_label.setText(f"🏆 Total Codes Found: {codes_found}")
        self.reset_count_label.setText(f"🔵 RESET Found: {counts.get('Reset', 0)}")
        self.scale_count_label.setText(f"🟣 SCALE Found: {counts.get('Scale', 0)}")
        self.pro_count_label.setText(f"🟠 PRO Found: {counts.get('Pro', 0)}")

        # Update recent codes with better formatting
        self.codes_list.clear()
        if found_codes_history:
            self.codes_list.append("<b>Recent successful codes:</b><br>")
            for acct_type, timestamp in found_codes_history[-10:]:
                color = "#42a5f5" if acct_type == "Reset" else "#ba68c8" if acct_type == "Scale" else "#ff8a65"
                self.codes_list.append(f"<span style='color: {color};'>{timestamp} - {acct_type}</span>")
        else:
            self.codes_list.append("<i>No codes found yet. Start a bot to begin monitoring!</i>")

    def toggle_bot(self, bot_name):
        """Start or stop a bot with enhanced feedback"""
        if not bot_running.get(bot_name, False):
            if bot_name == "Reset":
                bot = ResetBot(self)
            elif bot_name == "Scale":
                bot = ScaleBot(self)
            elif bot_name == "Pro":
                bot = ProBot(self)
            else:
                return

            bot_running[bot_name] = True
            bot_instances[bot_name] = bot
            thread = threading.Thread(target=bot.run, daemon=True)
            bot_threads[bot_name] = thread
            thread.start()
            self.buttons[bot_name].setText(f"🛑 Stop {bot_name}")
            self.log(f"🚀 [{bot_name.upper()}] Bot started with smart dictionary correction")
        else:
            bot = bot_instances.get(bot_name)
            if bot:
                bot.stop()
            bot_running[bot_name] = False
            self.buttons[bot_name].setText(f"▶️ Start {bot_name}")
            self.log(f"⏹️ [{bot_name.upper()}] Bot stopped")

    def toggle_overlay(self):
        """Show/hide the overlay window with enhanced feedback"""
        if self.overlay.isVisible():
            self.overlay.hide()
            self.snip_button.setText("Show Overlay")
        else:
            self.overlay.showFullScreen()
            self.overlay.raise_()
            self.overlay.activateWindow()
            self.snip_button.setText("Confirm Selection (ESC)")
            self.log("📍 Overlay activated - drag to select OCR region")
            
            # Update status immediately
            self.region_status.setText(f"📍 Current Region: {current_ocr_region.getRect()}")
    
    def change_overlay_color(self):
        """Change the color of the overlay rectangle"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.overlay.border_color = color
            self.overlay.update()
            self.log(f"🎨 Overlay color changed to {color.name()}")
    
    def change_theme(self, theme):
        """Change the application theme"""
        if theme == "Light":
            # Apply light theme (simplified for demo)
            self.setStyleSheet("")
            self.log_area.setStyleSheet("background: #f5f5f5; color: #333;")
            self.codes_list.setStyleSheet("background: #f5f5f5; color: #333;")
            self.log("☀️ Switched to light theme")
        else:
            # Keep the current dark theme
            self.log("🌙 Using dark theme")

    def show_preview(self):
        """Show an enhanced preview of what the bot sees"""
        try:
            with mss.mss() as sct:
                region = current_ocr_region.getRect()
                if region[2] == 0 or region[3] == 0:
                    self.log("❌ Invalid region size for preview")
                    return
                    
                monitor = {
                    "top": region[1],
                    "left": region[0],
                    "width": region[2],
                    "height": region[3],
                }
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Convert to QImage and display
                qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                
                # Create enhanced preview window
                preview = QDialog(self)
                preview.setWindowTitle("🔍 Bot Vision Preview")
                preview.setFixedSize(700, 500)
                preview.setStyleSheet("QDialog { background-color: #232629; color: #f0f0f0; }")
                
                layout = QVBoxLayout()
                
                header = QLabel("📸 Current OCR Capture Region")
                header.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #00ff88;
                        padding: 10px;
                        background: rgba(0, 255, 136, 0.1);
                        border-radius: 8px;
                        margin-bottom: 10px;
                    }
                """)
                layout.addWidget(header)
                
                label = QLabel()
                label.setPixmap(pixmap.scaled(650, 350, Qt.AspectRatioMode.KeepAspectRatio))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("QLabel { border: 2px solid #333; border-radius: 8px; padding: 10px; background-color: #1a1a1a; }")
                layout.addWidget(label)
                
                info = QLabel(f"📍 Region: {region} | 📐 Size: {img.width}x{img.height} pixels")
                info.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info.setStyleSheet("QLabel { color: #64b5f6; font-weight: bold; padding: 10px; }")
                layout.addWidget(info)
                
                close_btn = QPushButton("Close Preview")
                close_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                            stop: 0 #00ff88, stop: 1 #00cc66);
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-weight: bold;
                    }
                """)
                close_btn.clicked.connect(preview.accept)
                layout.addWidget(close_btn)
                
                preview.setLayout(layout)
                preview.exec()
                self.log("🔍 Preview window displayed")
                
        except Exception as e:
            self.log(f"❌ Preview error: {str(e)}")

    # Toggle methods for settings
    def toggle_trim_after_50(self, state):
        global trim_after_50_enabled
        trim_after_50_enabled = bool(state)
        self.log(f"🔧 Trim after 50: {'Enabled' if state else 'Disabled'}")

    def toggle_trim_after_25(self, state):
        global trim_after_25_enabled
        trim_after_25_enabled = bool(state)
        self.log(f"🔧 Trim after 25: {'Enabled' if state else 'Disabled'}")

    def toggle_show_ocr_raw(self, state):
        global show_ocr_raw_enabled
        show_ocr_raw_enabled = bool(state)
        self.log(f"🔧 OCR RAW logging: {'Enabled' if state else 'Disabled'}")
        if hasattr(self, "ocr_raw_area"):
            if show_ocr_raw_enabled:
                self.ocr_raw_area.setPlainText("🧪 OCR RAW logging enabled.\n")
            else:
                self.ocr_raw_area.setPlainText("🧪 OCR RAW logging disabled.\n")

    def toggle_smart_fix_ending(self, state):
        global smart_fix_ending_enabled
        smart_fix_ending_enabled = bool(state)
        self.log(f"🧠 Smart ending correction: {'Enabled' if state else 'Disabled'}")

    def toggle_smart_fix_ss_to_55(self, state):
        global smart_fix_ss_to_55_enabled
        smart_fix_ss_to_55_enabled = bool(state)
        self.log(f"🧠 SS→55 correction: {'Enabled' if state else 'Disabled'}")

    def toggle_smart_fix_2s_to_25(self, state):
        global smart_fix_2s_to_25_enabled
        smart_fix_2s_to_25_enabled = bool(state)
        self.log(f"🧠 2S→25 correction: {'Enabled' if state else 'Disabled'}")

    def toggle_smart_fix_digit_o_to_digit0(self, state):
        global smart_fix_digit_o_to_digit0_enabled
        smart_fix_digit_o_to_digit0_enabled = bool(state)
        self.log(f"🧠 Digit+O→Digit+0 correction: {'Enabled' if state else 'Disabled'}")

    def toggle_reverse_code_if_instructed(self, state):
        global reverse_code_if_instructed_enabled
        reverse_code_if_instructed_enabled = bool(state)
        self.log(f"🔄 Reverse code if instructed: {'Enabled' if state else 'Disabled'}")

    def toggle_auto_remove_coupon_code(self, state):
        global auto_remove_coupon_code_enabled
        auto_remove_coupon_code_enabled = bool(state)
        self.log(f"🗑️ Auto remove failed codes: {'Enabled' if state else 'Disabled'}")

    def toggle_underscore_to_t(self, state):
        global underscore_to_t_enabled
        underscore_to_t_enabled = bool(state)
        self.log(f"🔧 Underscore→T replacement: {'Enabled' if state else 'Disabled'}")

    def toggle_dictionary_underscore(self, state):
        global dictionary_underscore_enabled
        dictionary_underscore_enabled = bool(state)
        self.log(f"📚 Dictionary underscore correction: {'Enabled' if state else 'Disabled'}")

    def append_ocr_raw(self, text):
        """Append OCR raw data with better formatting"""
        if hasattr(self, "ocr_raw_area") and show_ocr_raw_enabled:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            formatted_text = f"[{timestamp}] {text}"
            self.ocr_raw_area.append(formatted_text)
            self.ocr_raw_area.verticalScrollBar().setValue(
                self.ocr_raw_area.verticalScrollBar().maximum()
            )
    
# ==========================================
# LOGIN DIALOG
# ==========================================

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚀 Code Sniper - Login")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🚀 Code Sniper Pro")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00ff88;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 rgba(0, 255, 136, 0.1), stop: 1 rgba(0, 204, 102, 0.1));
                border: 2px solid #00ff88;
                border-radius: 12px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(header)
        
        self.info = QLabel("Please log in to continue.")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info.setStyleSheet("color: #f0f0f0; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.info)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("👤 Username")
        self.username.setStyleSheet("""
            QLineEdit { 
                background-color: #1a1a1a; 
                color: #f0f0f0; 
                border-radius: 8px; 
                border: 2px solid #333; 
                padding: 12px 15px;
                font-size: 14px;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
            }
        """)
        layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("🔒 Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("""
            QLineEdit { 
                background-color: #1a1a1a; 
                color: #f0f0f0; 
                border-radius: 8px; 
                border: 2px solid #333; 
                padding: 12px 15px;
                font-size: 14px;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
            }
        """)
        layout.addWidget(self.password)
        
        self.login_btn = QPushButton("🚀 Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #00ff88, stop: 1 #00cc66);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #00cc66, stop: 1 #00aa44);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #00aa44, stop: 1 #008833);
            }
        """)
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)
        
        # Allow Enter key to login
        self.password.returnPressed.connect(self.try_login)
        
        self.setLayout(layout)
        self.user = None

        # Set modern dark theme for login dialog
        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #1a1a2e, stop: 1 #16213e); 
                color: #f0f0f0; 
            }
        """)

    def try_login(self):
        if not db:
            self.info.setText("❌ Firebase connection failed")
            self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            return

        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            self.info.setText("❌ Please enter both username and password")
            self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            return

        # Show loading state
        self.login_btn.setText("🔄 Logging in...")
        self.login_btn.setEnabled(False)
        QApplication.processEvents()

        try:
            # Get user document from Firestore
            user_ref = db.collection("users").document(username)
            user_doc = user_ref.get()

            if not user_doc.exists:
                self.info.setText("❌ User does not exist")
                self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                self.reset_login_button()
                return

            user = user_doc.to_dict()

            # Password check
            if user["password"] != hash_password(password):
                self.info.setText("❌ Incorrect password")
                self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                self.reset_login_button()
                return

            # Suspension check
            suspended_until = user.get("suspended_until")
            if suspended_until:
                try:
                    suspend_time = datetime.strptime(suspended_until, "%Y-%m-%d %H:%M")
                    if datetime.now() < suspend_time:
                        self.info.setText(f"⛔ Account suspended until {suspended_until}")
                        self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                        self.reset_login_button()
                        return
                except Exception:
                    pass

            # Device locking check (for non-admins)
            if user.get("role", "user") != "admin":
                pc_name, mac, ip = get_device_info()
                current_hwid = mac
                current_ip = ip

                # HWID check (if already bound)
                if user.get("hwid") and user["hwid"] != current_hwid:
                    self.info.setText("❌ This device is not authorized")
                    self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                    self.reset_login_button()
                    return

                # Only 1 login per account
                if user.get("is_online", False):
                    self.info.setText("🔒 Account already in use")
                    self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                    self.reset_login_button()
                    return

                # First-time binding
                if not user.get("hwid") or not user.get("ip"):
                    update_data = {
                        "hwid": current_hwid,
                        "ip": current_ip,
                        "bound_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    user_ref.update(update_data)

            # Mark user as online
            user_ref.update({"is_online": True})

            # Add login log
            login_log = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action": "Logged in",
                "ip": get_current_ip()
            }
            user_ref.update({"logs": firestore.ArrayUnion([login_log])})

            self.user = user
            self.user["username"] = username  # Add username to user dict
            self.info.setText("✅ Login successful!")
            self.info.setStyleSheet("color: #00ff88; font-weight: bold;")
            self.accept()

        except Exception as e:
            self.info.setText(f"❌ Login error: {str(e)}")
            self.info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.reset_login_button()

    def reset_login_button(self):
        """Reset login button to normal state"""
        self.login_btn.setText("🚀 Login")
        self.login_btn.setEnabled(True)

# Main execution block
if __name__ == "__main__":
    try:
        print("🚀 Launching Code Sniper Pro...")
        app = QApplication(sys.argv)
        print("📋 Showing login dialog...")
        login = LoginDialog()
        if login.exec() == QDialog.DialogCode.Accepted:
            print("✅ Login successful, launching main window...")
            # Prevent window from being garbage collected
            main_window_instance = MainWindow(login.user)
            main_window_instance.show()
            sys.exit(app.exec())
        else:
            print("❌ Login cancelled or failed.")
            sys.exit(0)
    except Exception as e:
        import traceback
        print("💥 An error occurred:")
        traceback.print_exc()
        input("Press Enter to exit...")