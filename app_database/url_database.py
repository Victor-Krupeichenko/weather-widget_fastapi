from setting_env import post_user, post_pass, post_host, post_port, post_db


_URL = f"postgresql+asyncpg://{post_user}:{post_pass}@{post_host}:{post_port}/{post_db}"
