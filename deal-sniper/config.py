from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALERT_CHAT_ID = os.getenv("ALERT_CHAT_ID")

CHANNELS = [
    -1001412868909,  
    -1001596448068,
    -1001493857075,
    -1001346861267
]

DEAL_SCORE_THRESHOLD = 60
DRY_RUN = True
