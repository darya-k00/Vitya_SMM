from environs import env
import requests
import json
import re


env.read_env()


def publiс_posts(posts):
    for post in posts:
        media = post['Ссылка на Google Документ'] 
        if post['social_media'] == 'tg':
            public_post_tg(media)
        elif post['social_media'] == 'vk':
            public_post_vk(media)
        elif post['social_media'] == 'ok':
            public_post_ok(media)


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
    group_id = env.str('GROUP_ID')

    attachments = None
    if 'image_url' in post and post['image_url']:
        match = re.search(r'photo-(\d+_\d+)', post['image_url'])
        if match:
            attachments = f'photo-{match.group(1)}'

    params = {
        'owner_id': f'-{group_id}',
        'message': post['text'],
        'access_token': api_key,
        'v': '5.199',
    }

    if attachments:
        params['attachments'] = attachments

    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()


def public_post_ok(post:dict):
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
