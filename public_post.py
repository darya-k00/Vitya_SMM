from environs import env
import requests
import json

env.read_env()


def public_post(posts):
    for post in posts:
        if post['social_media'][0] == '@':
            public_post_tg(post)


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
    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params={
            'owner_id': f'-{group_id}',
            'message': post['text'],
            'access_token': api_key,
            'v': '5.199',
        }
    )
    response.raise_for_status()


def public_post_ok(post):
    app_key = env.str('OK_API_KEY')
    group_id = env.str('OK_GROUP_ID')
    token = env.str('OK_TOKEN')
    session_key = env.str('OK_SESSION_KEY')
    
    attachment = {
        "media": [
            {
                "type": "text",
                "text": 'Ваш текст поста'  
            }
        ]
    }
    
    attachment_json = json.dumps(attachment)

    signature = f'application_key={app_key}attachment={attachment_json}format=jsongid={group_id}method=mediatopic.posttype=GROUP_THEME{session_key}'
    sig = signature 
    
    params = {
        'application_key': app_key,
        'attachment': attachment_json,
        'format': 'json',
        'gid': group_id,
        'method': 'mediatopic.post',
        'type': 'GROUP_THEME',
        'access_token': token,
        'sig': sig
        }
    
    ok_url = 'https://api.ok.ru/fb.do'
    response = requests.get(ok_url, data=params)
    response.raise_for_status()
    return response.json()
   
