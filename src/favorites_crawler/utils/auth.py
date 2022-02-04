from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_urlsafe
from urllib.parse import urlencode
from webbrowser import open as open_url

import requests

from favorites_crawler.constants.endpoints import PIXIV_REDIRECT_URI, PIXIV_LOGIN_URL, PIXIV_AUTH_TOKEN_URL
from favorites_crawler.constants.headers import PIXIV_ANDROID_USER_AGENT
from favorites_crawler.utils.config import dump_config, load_config

CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


def s256(data):
    """S256 transformation method."""
    return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")


def oauth_pkce(transform):
    """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""
    code_verifier = token_urlsafe(32)
    code_challenge = transform(code_verifier.encode("ascii"))
    return code_verifier, code_challenge


def login_pixiv():
    config = load_config('pixiv.yml')
    try:
        user_id = input("user id: ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    code_verifier, code_challenge = oauth_pkce(s256)
    login_params = {
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "client": "pixiv-android",
    }

    open_url(f"{PIXIV_LOGIN_URL}?{urlencode(login_params)}")

    try:
        code = input("code: ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    response = requests.post(
        PIXIV_AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
            "include_policy": "true",
            "redirect_uri": PIXIV_REDIRECT_URI,
        },
        headers={"User-Agent": PIXIV_ANDROID_USER_AGENT},
        timeout=5,
    )

    data = response.json()
    config['user_id'] = user_id
    config['access_token'] = data['access_token']
    config['refresh_token'] = data['refresh_token']
    dump_config('pixiv.yml', config)
    return config


def refresh_pixiv():
    config = load_config('pixiv.yml')
    if not config:
        return

    refresh_token = config['refresh_token']
    response = requests.post(
        PIXIV_AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "include_policy": "true",
            "refresh_token": refresh_token,
        },
        headers={"User-Agent": PIXIV_ANDROID_USER_AGENT},
        timeout=5,
    )

    data = response.json()
    access_token = data['access_token']
    config['access_token'] = access_token
    dump_config('pixiv.yml', config)
    return access_token