import requests


def public_post_tg(token: str, id_channel: str, text: str='', urls_img: list=[]):
    if urls_img:
        media = [
            {
                'type': 'photo',
                'media': url,
                'caption': text if i == 0 else ''
            }
            for i, url in enumerate(urls_img)
        ]
        
        response = requests.post(
            f'https://api.telegram.org/bot{token}/sendMediaGroup',
            json={
                'media': media,
                'chat_id': id_channel,
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
        