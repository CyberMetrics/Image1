# services/web/config/oauth_keys.py
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# OAUTH CREDENTIALS
# ==========================================

# GITHUB
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API = "https://api.github.com/user"
GITHUB_USER_EMAIL_API = "https://api.github.com/user/emails"

# FLASK SECURITY
SECRET_KEY = os.getenv("SECRET_KEY", "radar_secret_key_change_me_in_prod")

