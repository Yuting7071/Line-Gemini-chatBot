import os
import sys
import aiohttp
from fastapi import Request, FastAPI, HTTPException
from linebot import (AsyncLineBotApi, WebhookParser)
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage)
from google import genai
from dotenv import load_dotenv
load_dotenv()

#為用戶建立chatSession
class ChatSession:
    def __init__(self, user_id):
        self.user_id=user_id
        self.last_id = None

# 建立用戶表
user_sessions = {}

client = genai.Client()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


app = FastAPI()
# 1. 建立對外的「持久連線池」
session = aiohttp.ClientSession()
async_http_client = AiohttpAsyncHttpClient(session)
line_bot_api = AsyncLineBotApi(channel_access_token, async_http_client)
parser = WebhookParser(channel_secret)

@app.post("/callback")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        
        #多輪對話核心邏輯
        uid = event.source.user_id
        user_input = event.message.text

        if uid not in user_sessions:
            user_sessions[uid] = ChatSession(uid)
        current_user = user_sessions[uid]

        interaction = client.interactions.create(
            model="gemini-3.1-flash-lite-preview",
            input=f"請用繁體中文簡短回答以下內容:{user_input}",
            previous_interaction_id=current_user.last_id
        )
        current_user.last_id = interaction.id

        reply_text = interaction.outputs[-1].text
        # ---多輪對話核心邏輯結束---

        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(reply_text)
        )
        
    return 'OK'