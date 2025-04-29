import gspread
from pathlib import Path
from environs import env
import os.path
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


env.read_env()


def get_posts():
    gc = gspread.service_account(filename=Path('google_api.json'))
    url = env.str('SHEET_URL')
    sheet = gc.open_by_url(url)
    posts = sheet.sheet1.get_all_records(
        expected_headers=[
            'ID'
            'Дата',
            'Время',
            'Ссылка на Google Документ',
            'social_media',
            'id_media',
            'Опубликован'
        ]
    )
    return [post for post in posts if post['Опубликован'] == '']


def get_text_from_docs(docs_id):
    match = re.search(r'/document/d/([a-zA-Z0-9-_]{20,})', docs_id)
    docs_id = match.group(1)
    scopes = ['https://www.googleapis.com/auth/documents.readonly']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('docs', 'v1', credentials=creds)  
        document = service.documents().get(documentId=docs_id).execute()

    except HttpError as err:
        print(err)

    text_parts = []
    all_urls = set()
    pattern = re.compile(r'(https?://[^\s]*)')

    for element in document.get('body', {}).get('content', []):
        if 'paragraph' not in element:
            continue

        for p_element in element['paragraph'].get('elements', []):
            text_run = p_element.get('textRun', {})
            content = text_run.get('content', '')

            clean_content = content
            for url in pattern.findall(content):
                all_urls.add(url)
                clean_content = clean_content.replace(url, '')

            text_parts.append(clean_content)

            if 'textStyle' in text_run and 'link' in text_run['textStyle']:
                link_url = text_run['textStyle']['link'].get('url')
                if link_url:
                    all_urls.add(link_url)

    clean_text = re.sub(r'\n+', '\n', ''.join(text_parts)).strip()

    return {
        'text': clean_text,
        'image_url': all_urls,
    }


#FIXME Доделать учитывать [{}]
def validate_post(post: dict):
    required_fields = ['Ссылка на Google Документ', 'social_media', 'id_media', 'Статус']
    for field in required_fields:
        if field not in post:
            return f'Отсутствует обязательное поле: {field}'

    if post['Статус'] != 'В обработке':
        return 'Пост уже опубликован'

    if not post['social_media']:
        return 'Не указана социальная сеть'

    if post['social_media'] == 'tg':
        if post['id_media'].startswith('@'):
            if not post['id_media'][1:].isalnum():
                return 'Некорректный Telegram id'
        else:
            return 'Id канала в tg, должен начинаться с @'
    if post['social_media'] == 'vk':
        if not post['id_media'].isalnum():
            return 'Некорректный vk id'

    if post['social_media'] == 'ok':
        if not post['id_media'].isalnum():
            return 'Некорректный ok id'


def change_status_post(post):
    gc = gspread.service_account(filename=Path('google_api.json'))
    url = env.str('SHEET_URL')
    sheet = gc.open_by_url(url)
    headers = sheet.row_values(1)
    column_index = headers.index('Опубликован') + 1
    sheet.sheet1.update_cell(post['ID']+1, column_index, 'Да')