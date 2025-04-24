from environs import env
import requests


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
    api_key = env.str('OK_API_KEY')
    pass
