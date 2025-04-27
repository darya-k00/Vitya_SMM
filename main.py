import time
from create_post import get_posts
from public_post import publiс_posts


def main():
    while True:
        posts = get_posts()
        publiс_posts(posts)
        time.sleep(10)


if __name__ == "__main__":
    main()
