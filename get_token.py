import time
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
import json
from api_utils import base_url

from error_classes import InvalidCredentials, AccountNotFound


def get_saml2_url(session):
    response = session.get(base_url, allow_redirects=True)
    return response.url


def get_ctx(config):
    return config["sCtx"]


def get_canary(config):
    return config["canary"]


def get_session_id(config):
    return config["sessionId"]


def extract_config_json(text: str):
    start = text.find("$Config=")
    if start == -1:
        return None

    json_part = text[start + len("$Config=") :]

    brace_count = 0
    end_index = None

    for i, char in enumerate(json_part):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1

        if brace_count == 0 and i > 0:
            end_index = i + 1
            break

    if end_index is None:
        return None

    json_str = json_part[:end_index]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def config_json(response):
    return extract_config_json(response.text)


def get_flow_token(config):
    return config["sFT"]


def get_login_url(saml2_url):
    parsed = urlparse(saml2_url)
    segments = parsed.path.split("/")
    segments[-1] = "login"
    new_path = "/".join(segments)

    return urlunparse((parsed.scheme, parsed.netloc, new_path, "", "", ""))


def submit_form(session, response):
    soup = BeautifulSoup(response.text, "html.parser")

    form = soup.find("form")
    if not form:
        return None

    action = form.get("action")

    payload = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        value = inp.get("value", "")
        if name:
            payload[name] = value

    if action.startswith("/"):
        action = "https://login.microsoftonline.com" + action

    new_response = session.post(action, data=payload)

    return new_response


def get_session_token(email, password):
    cookies_list = get_cookies_list(email, password)

    session_token = {}
    for cookie in cookies_list:
        if cookie["name"].startswith("SES"):
            session_token[cookie["name"]] = cookie["value"]

    return session_token


def account_exists(email):
    url = "https://login.microsoftonline.com/common/GetCredentialType?mkt=en-US"

    payload = {"username": email}

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    return response.json()["IfExistsResult"] == 0


def get_cookies_list(email, password):
    session = requests.Session()
    start_time = time.time()

    saml2_url = get_saml2_url(session)
    response = session.get(saml2_url, allow_redirects=False)
    config = config_json(response)
    flow_token = get_flow_token(config)
    ctx = get_ctx(config)
    canary = get_canary(config)
    session_id = get_session_id(config)

    i19_value = int((time.time() - start_time) * 1000)

    if not account_exists(email):
        raise AccountNotFound

    payload = {
        "i13": "0",
        "login": email,
        "loginfmt": email,
        "type": "11",
        "LoginOptions": "3",
        "lrt": "",
        "lrtPartition": "",
        "hisRegion": "",
        "hisScaleUnit": "",
        "passwd": password,
        "ps": "2",
        "psRNGCDefaultType": "",
        "psRNGCEntropy": "",
        "psRNGCSLK": "",
        "canary": canary,
        "ctx": ctx,
        "hpgrequestid": session_id,
        "flowToken": flow_token,
        "PPSX": "",
        "NewUser": "1",
        "FoundMSAs": "",
        "fspost": "0",
        "i21": "0",
        "CookieDisclosure": "0",
        "IsFidoSupported": "1",
        "isSignupPost": "0",
        "DfpArtifact": "",
        "i19": str(i19_value),
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://login.microsoftonline.com",
        "Referer": response.url,
    }

    start_time = time.time()

    login_url = get_login_url(saml2_url)
    response = session.post(
        login_url, data=payload, headers=headers, allow_redirects=True
    )
    config = config_json(response)
    flow_token = get_flow_token(config)
    ctx = get_ctx(config)
    canary = get_canary(config)
    session_id = get_session_id(config)

    kmsi_url = "https://login.microsoftonline.com/kmsi"

    i19_value = int((time.time() - start_time) * 1000)
    payload = {
        "LoginOptions": "1",
        "type": "28",
        "ctx": ctx,
        "hpgrequestid": session_id,
        "flowToken": flow_token,
        "DontShowAgain": "true",
        "canary": canary,
        "i19": str(i19_value),
    }

    response = session.post(kmsi_url, data=payload, allow_redirects=True)

    response = submit_form(session, response)
    if response is None:
        raise InvalidCredentials

    cookies_list = []

    for cookie in session.cookies:
        cookies_list.append(
            {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires,
            }
        )

    return cookies_list
