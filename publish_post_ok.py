import requests
import json


def publish_post_ok(app_key: str, ok_token: str, id_channel: str, text: str='', urls_img: list=[]):
    attachment = {
        'media': []
    }
    if text: 
        attachment['media'].append(
            {
                "type": "text",
                "text":  text
            }
        )
    if urls_img:
        upload_url = __get_upload_urls(app_key, ok_token, id_channel, len(urls_img))
        photos = __upload_imgs(app_key, ok_token, upload_url, urls_img)
        tokens = __get_token_img(photos)
        attachment['media'].append(
            {
                'type': 'photo',
                "list": tokens
            }
        )     
    attachment = json.dumps(attachment)  
    params = {
        'application_key': app_key,
        'attachment': attachment,
        'format': 'json',
        'gid': id_channel,
        'method': 'mediatopic.post',
        'type': 'GROUP_THEME',
        'access_token': ok_token,
    }
    ok_url = 'https://api.ok.ru/fb.do'
    response = requests.post(ok_url, data=params)
    response.raise_for_status()


def __get_upload_urls(app_key: str, ok_token: str, id_channel: str, count_img: int) -> str:
    params = {
        'method': 'photosV2.getUploadUrl',
        'gid': id_channel,
        'application_key': app_key,
        'access_token': ok_token,
        'count': count_img
    }
    response = requests.post('https://api.ok.ru/fb.do', data=params)  
    response.raise_for_status()  
    response = json.loads(response.content)
    return response['upload_url']


def __upload_imgs(app_key: str, ok_token: str, upload_url: str, urls_img: list) -> dict:
    files = {}
    
    for i, url in enumerate(urls_img):
        response = requests.get(url)
        response.raise_for_status()
        photo = response.content       
        files[f'file{i}'] = photo    
        
    response = requests.post(upload_url, files=files)
    response.raise_for_status()    
    return response.json()['photos']    


def __get_token_img(photos: dict) -> list:
    tokens = []
    
    for key in photos:
            tokens.append({'id': photos[key]['token']})
            
    return tokens
