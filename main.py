import time
from create_post import get_posts
from public_post import public_post


def main():
    while True:
        posts = get_posts()
        public_post(posts)
        time.sleep(10)


if __name__ == "__main__":
    main()
