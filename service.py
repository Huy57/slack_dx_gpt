from fastapi import APIRouter
from fastapi import Request
import requests
import os
import logging
router = APIRouter()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_API_URL = 'https://slack.com/api/chat.postMessage'

logger = logging.getLogger(__name__)

@router.post("/slack/events")
async def slack_events(request: Request):
    data = await request.json()

    logger.info(f"data123: {data}")
    # Xác thực URL từ Slack khi bật Events API (challenge request)
    if 'challenge' in data:
        return {"challenge": data["challenge"]}

    # Xử lý khi có tin nhắn gửi đến bot (tin nhắn trực tiếp - IM)
    if 'event' in data:
        event = data['event']

        # Kiểm tra loại sự kiện là tin nhắn trong cuộc hội thoại trực tiếp (IM)
        if event.get('type') == 'message' and event.get('channel_type') == 'im':
            user_message = event.get('text')  # Tin nhắn từ người dùng
            user_id = event.get('user')  # ID người dùng gửi tin nhắn

            # Gửi phản hồi tới người dùng
            reply_message = f"Bạn đã gửi: {user_message}"
            send_message_to_user(user_id, reply_message)

    return {"status": "ok"}


def send_message_to_user(user_id, text):
    """Hàm gửi tin nhắn phản hồi qua Slack API"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
    }
    payload = {
        'channel': user_id,
        'text': text
    }

    response = requests.post(SLACK_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Lỗi khi gửi tin nhắn: {response.status_code}, {response.text}")






