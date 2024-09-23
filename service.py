from fastapi import APIRouter
from fastapi import Request
import requests
import os
import logging
from slack_sdk import WebClient
router = APIRouter()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_API_URL = 'https://slack.com/api/chat.postMessage'

logger = logging.getLogger(__name__)

@router.post("/slack/events")
async def slack_events(request: Request):
    data = await request.json()

    logger.info(f"data123: {data}")
    print(f"data123: {data}")
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
            if event.get('bot_id'):
                return {"status": "ignored"}
            # Gửi phản hồi tới người dùng
            reply_message = f"Bạn đã gửi: {user_message}"
            send_message_to_user(user_id, reply_message)
            # Xử lý tin nhắn từ kênh
        elif event.get('channel_type') == 'channel':
            channel_id = event.get('channel')
            user_message = event.get('text')
            user_id = event.get('user')

            # Loại trừ tin nhắn từ bot chính nó
            if event.get('bot_id'):
                return {"status": "ignored"}

            # Gửi phản hồi tới kênh
            reply_message = f"Tin nhắn từ kênh: {user_message}"
            # send_message_to_channel(channel_id, reply_message)
            send_image_to_channel(channel_id)
    return {"status": "ok"}


def send_message_to_channel(channel_id: str, message: str):
    # Gửi tin nhắn tới kênh
    slack = WebClient(SLACK_BOT_TOKEN)
    response = slack.chat_postMessage(channel=channel_id, text=message)
    return response


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


def send_image_to_channel(slack_channel: str):
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        image_url ='https://www.google.com/imgres?q=%E1%BA%A3nh%20m%C3%A8o&imgurl=https%3A%2F%2Flookaside.fbsbx.com%2Flookaside%2Fcrawler%2Fmedia%2F%3Fmedia_id%3D100064549818192&imgrefurl=https%3A%2F%2Fwww.facebook.com%2Fcatengucute%2F%3Flocale%3Dvi_VN&docid=gzqtA11_BSt3bM&tbnid=752Ch-CGhkwK0M&vet=12ahUKEwjsir_T6tiIAxXbs1YBHTgABKQQM3oECG4QAA..i&w=687&h=687&hcb=2&ved=2ahUKEwjsir_T6tiIAxXbs1YBHTgABKQQM3oECG4QAA'
        post_image_result = client.files_upload(channels=slack_channel, file=image_url, title='ảnh mèo')

        logger.info(f"Sent image to Slack channel successfully result={post_image_result}")
        return post_image_result

    except requests.RequestException as e:
        logger.error(f"Error accessing Slack API: {str(e)}")
        return None
