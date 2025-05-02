from environs import env
import time
from get_posts import get_posts_from_gsheets
from datetime import datetime
import pytz
from publish_post_tg import publish_post_tg
from publish_post_ok import publish_post_ok
from publish_post_vk import publish_post_vk
from get_posts import get_media_from_docs, change_status_post


env.read_env()


def main():
    tz_str = 'Asia/Yekaterinburg'
    tg_token = env.str('TG_API_KEY')
    ok_app_key = env.str('OK_API_KEY')
    ok_token = env.str('OK_TOKEN')
    sheet_url = env.str('SHEET_URL')
    google_api_json = env.str('GOOGLE_API')
        
    while True:
        posts = get_posts_from_gsheets(sheet_url, google_api_json)
        
        if not posts:
            time.sleep(60)
            continue
        
        for post in posts:       
            time_of_publish = datetime.strptime(f'{post['Дата']} {post['Время']}', '%Y-%m-%d %H:%M')
            tz = pytz.timezone(tz_str)
            time_of_publish = tz.localize(time_of_publish)
            if time_of_publish > datetime.now(tz):
                continue
            
            docs_id = post['Ссылка на Google Документ']
            media = get_media_from_docs(docs_id)
            text = media['text']
            urls_img = media['image_url']
            
            if post['social_media'] == 'tg':
                publish_post_tg(tg_token, post['id_media'], text, urls_img)
            # elif post['social_media'] == 'vk':
            #     publish_post_vk(api_key, post['id_media'], text, urls_img)
            elif post['social_media'] == 'ok':
                publish_post_ok(ok_app_key, ok_token, post['id_media'], text, urls_img)
    
            change_status_post(sheet_url, post['ID'])
        
        time.sleep(60)


if __name__ == "__main__":
    main()
