from environs import env


env.read_env()


def public_post():
    pass


def public_post_tg():
    api_key = env.str('TG_API_KEY')
    pass


def public_post_vk():
    api_key = env.str('VK_API_KEY')
    pass


def public_post_ok():
    api_key = env.str('OK_API_KEY')
    pass
