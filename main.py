import time
from create_post import get_post
from public_post import public_post


def main():
    while True:
        get_post()
        public_post()
        time.sleep(10)

if __name__ == "__main__":
    main()
    