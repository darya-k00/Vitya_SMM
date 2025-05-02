import requests


def public_post_vk(api_key: str, id_channel: str, text: str='', urls_img: list=[]):
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