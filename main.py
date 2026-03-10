import os
import sys
import aiohttp
from contextlib import asynccontextmanager
from fastapi import Request, FastAPI, HTTPException
from linebot import (AsyncLineBotApi, WebhookParser)
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage)
from google import genai
from dotenv import load_dotenv

load_dotenv()
# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

gemini_client = genai.Client()

#為用戶建立chatSession
class ChatSession:
    def __init__(self, user_id):
        self.user_id=user_id
        self.last_id = None

# 建立用戶表
user_sessions = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    session = aiohttp.ClientSession()
    async_http_client = AiohttpAsyncHttpClient(session)
    app.state.line_bot_api = AsyncLineBotApi(channel_access_token, async_http_client)
    app.state.line_parser = WebhookParser(channel_secret)
    print("LINE Bot 連線池已就緒")

    yield

    await session.close()
    print("連線池已安全關閉")

# 取得Gemini回覆
async def get_gemini_response(user_input:str, session:ChatSession):
    interaction = gemini_client.interactions.create(
    model="gemini-3.1-flash-lite-preview",
    input=f"請用繁體中文簡短回答以下內容:{user_input}",
    previous_interaction_id=session.last_id
    )
    session.last_id = interaction.id
    return interaction.outputs[-1].text

app = FastAPI(lifespan=lifespan)

@app.post("/callback")
async def handle_callback(request: Request):
    line_bot_api = request.app.state.line_bot_api
    parser = request.app.state.line_parser
    signature = request.headers.get('X-Line-Signature')

    # get request body as text
    body = (await request.body()).decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        uid = event.source.user_id
        user_input = event.message.text

        if uid not in user_sessions:
            user_sessions[uid] = ChatSession(uid)
        current_user = user_sessions[uid]

        #取得gemini回覆
        reply_text = await get_gemini_response(user_input, current_user)

        #回覆使用者
        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = reply_text)
        )

    return 'OK'