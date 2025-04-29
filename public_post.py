from environs import env
import requests
from create_post import get_text_from_docs, change_status_post
import json
import re
import schedule
from datetime import datetime
import pytz


env.read_env()


def schedule_posts(posts):
    tz = pytz.timezone('Asia/Yekaterinburg')
    time_now = datetime.now(tz)

    for post in posts:
        date_post = f"{post['Дата']} {post['Время']}"
        naive_time = datetime.strptime(date_post, '%Y-%m-%d %H:%M')
        post_time = tz.localize(naive_time)

        if post_time >= time_now:
            schedule.every().day.at(
                post_time.strftime('%H:%M'),
                tz='Asia/Yekaterinburg'
            ).do(public_post, post)


def public_post(post):
    docs_id = post['Ссылка на Google Документ']
    post['text'] = get_text_from_docs(docs_id)
    if post['social_media'] == 'tg':
        public_post_tg(post)
    elif post['social_media'] == 'vk':
        public_post_vk(post)
    elif post['social_media'] == 'ok':
        public_post_ok(post)
    
    change_status_post(post)


def public_post_tg(post: dict):
    token = env.str('TG_API_KEY')
    response = requests.post(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data={
            'chat_id': post['social_media'],
            'text': post['text'],
        }
    )
    response.raise_for_status()


def public_post_vk(post: dict):
    api_key = env.str('VK_API_KEY')
    group_id = post['id_media']

    text = post['text']['text']

    attachments = None
    if 'image_url' in post['text'] and post['text']['image_url']:
        image_url = post['text']['image_url']
        match = re.search(r'photo-(\d+_\d+)', str(image_url))
        if match:
            attachments = f'photo-{match.group(1)}'

    params = {
        'owner_id': f'-{group_id}',
        'message': text,
        'access_token': api_key,
        'v': '5.199',
    }

    if attachments:
        params['attachments'] = attachments

    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()


def public_post_ok(post: dict):
    app_key = env.str('OK_API_KEY')
    ok_group_id = post['id_media']
    ok_token = env.str('OK_TOKEN')
    session_key = env.str('OK_SESSION_KEY')

    attachment = {
        "media": [
            {
                "type": "text",
                "text":  post['text']
            }
        ]
    }

    attachment_json = json.dumps(attachment)

    params = {
        'application_key': app_key,
        'attachment': attachment_json,
        'format': 'json',
        'gid': ok_group_id,
        'method': 'mediatopic.post',
        'type': 'GROUP_THEME',
        'access_token': ok_token,
        }

    ok_url = 'https://api.ok.ru/fb.do'
    response = requests.post(ok_url, params=params)
    response.raise_for_status()
