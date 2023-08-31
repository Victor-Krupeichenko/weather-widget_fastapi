import os
from dotenv import load_dotenv

load_dotenv()

post_db = os.getenv("POSTGRES_DB")
post_host = os.getenv("POSTGRES_HOST")
post_port = os.getenv("POSTGRES_PORT")
post_user = os.getenv("POSTGRES_USER")
post_pass = os.getenv("POSTGRES_PASSWORD")
algorithm = os.getenv("_ALGORITHM")
secret_key = os.getenv("_SECRET_KEY")
token_expiration_date = os.getenv("_TOKEN_EXPIRATION_DATE")
name_cookies = os.getenv("_NAME_COOKIES")
