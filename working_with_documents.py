import gspread
from pathlib import Path
import os.path
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_posts_from_gsheets(sheet_url: str, filename: str) -> list:
    gc = gspread.service_account(filename=Path(filename))
    sheet = gc.open_by_url(sheet_url)
    posts = sheet.sheet1.get_all_records(
        expected_headers=[
            'ID',
            'Дата',
            'Время',
            'Ссылка на Google Документ',
            'social_media',
            'id_media',
            'Опубликован',
        ]
    )
    return [post for post in posts if post['Опубликован'] == 'Нет']


def get_media_from_docs(docs_id) -> dict:
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
        'image_url': list(all_urls),
    }


def validate_post(post: dict, sheet_url: str) -> bool:
    fields = [
        'Дата',
        'Время',
        'Ссылка на Google Документ',
        'social_media',
        'id_media',
    ]
    
    for field in fields:
        if not post[field]:
            status = f'Не указно поле {field}, укажите и измените статус на "Нет"!'
            change_status_post(sheet_url, post['ID'], status)
            return False

    return True


def change_status_post(sheet_url: str, post_id: str, status: str='Да'):
    gc = gspread.service_account(filename=Path('google_api.json'))
    sheet = gc.open_by_url(sheet_url)
    headers = sheet.worksheet('Лист1').row_values(1)
    column_index = headers.index('Опубликован') + 1
    sheet.sheet1.update_cell(post_id+1, column_index, status)
    

def format_text(text):
    try:
        text = re.sub(r'\s+', ' ', text)        
        text = text.replace('“', '«').replace('”', '»').replace(' - ', ' – ')
        return text.strip()
    except Exception as e:
        return text
