from io import BytesIO

from fastapi import APIRouter
from fastapi import Request
import requests
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

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
            print(f"user_id: {user_id}")
            get_user_info(user_id)
            if event.get('bot_id'):
                return {"status": "ignored"}
            # Gửi phản hồi tới người dùng
            reply_message = f"Bạn đã gửi: {user_message}"
            send_message_to_user(user_id, reply_message)
            # Xử lý tin nhắn từ kênh
        elif event.get('channel_type') == 'channel':
            channel_id = event.get('channel')
            user_message = event.get('text')

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
        image_url ='https://moc247.com/wp-content/uploads/2023/12/loa-mat-voi-101-hinh-anh-avatar-meo-cute-dang-yeu-dep-mat_22-678x381.jpg'
        data =[(image_url, "ảnh 1"), (image_url, "ảnh 2"), (image_url, "ảnh 3")]

        # Tạo cấu trúc blocks cho tin nhắn
        blocks = []

        for url, title in data:
            # Thêm tiêu đề cho ảnh
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": title  # Sử dụng title từ dữ liệu
                }
            })
            # Thêm khối hình ảnh
            blocks.append({
                "type": "image",
                "image_url": url,
                "alt_text": title  # Sử dụng title làm alt_text
            })
        # post_image_result = client.files_upload_v2(channels=slack_channel, file=image_data, filename='image.jpg', title='ảnh mèo')
        client.chat_postMessage(channel=slack_channel, blocks=blocks)
        logger.info(f"Sent image to Slack channel successfully result")
        return None

    except requests.RequestException as e:
        logger.error(f"Error accessing Slack API: {str(e)}")
        return None


def get_user_info(user_id):
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        # Gửi yêu cầu lấy thông tin người dùng
        response = client.users_info(user=user_id)
        # In ra thông tin người dùng nhận được
        if response['ok']:
            user_info = response['user']
            print(f'user_data: {user_info}')
            print(f"User ID: {user_info['id']}")
            print(f"Name: {user_info['profile']['real_name']}")
            print(f"Email: {user_info['profile'].get('email', 'No email available')}")
        else:
            print("Failed to get user info")
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
