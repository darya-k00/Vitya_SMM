import time
from create_post import get_posts
import schedule
from public_post import schedule_posts


def main():
    while True:
        posts = get_posts()
        schedule_posts(posts)
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
