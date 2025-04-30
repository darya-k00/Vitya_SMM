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


def public_post_tg(text: str, id_channel: str, url_img: str=''):
    token = env.str('TG_API_KEY')
    if url_img:
        response = requests.post(
            f'https://api.telegram.org/bot{token}/sendPhoto',
            data={
                'chat_id': id_channel,
                'photo': url_img,
                'caption': text
            }
        )
        response.raise_for_status()
    else:
        response = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data={
                'chat_id': id_channel,
                'text': text,
            }
        )
        response.raise_for_status()


def public_post_vk(text: str, id_channel: str, url_img: str=''):
    api_key = env.str('VK_API_KEY')    
    params = {
        'owner_id': f'-{id_channel}',
        'message': text,
        'access_token': api_key,
        'v': '5.199',
    }
    
    attachments = None
    if url_img:
        match = re.search(r'photo-(\d+_\d+)', url_img)
        if match:
            attachments = f'photo-{match.group(1)}'
            params['attachments'] = attachments

    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()


def public_post_ok(text: str, id_channel: str, url_img: str=''):
    app_key = env.str('OK_API_KEY')
    ok_token = env.str('OK_TOKEN')
    session_key = env.str('OK_SESSION_KEY')
    params = {
        'application_key': app_key,
        'attachment': attachment_json,
        'format': 'json',
        'gid': id_channel,
        'method': 'mediatopic.post',
        'type': 'GROUP_THEME',
        'access_token': ok_token,
    }
    attachment = {
        "media": [
            {
                "type": "text",
                "text":  post['text']
            }
        ]
    }
    if url_img:
        attachment['media'].append(
            {
                'type': 'photo',
                'photo': url_img
            }
        )  
    attachment_json = json.dumps(list(attachment))  
    ok_url = 'https://api.ok.ru/fb.do'
    response = requests.post(ok_url, data=params)
    response.raise_for_status()
