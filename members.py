from getpass import getpass
from pathlib import Path
import json
import time

import httpx
from bs4 import BeautifulSoup

from get_token import get_session_token

EMAIL = input("Email: ")
PASSWORD = getpass("Password: ")
SESSION_TOKEN = get_session_token(EMAIL, PASSWORD)
BASE_URL = "https://ca-net.schoology.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
CLIENT = httpx.Client(
    http2=True,
    verify=False,
    follow_redirects=True,
    headers=HEADERS,
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
    timeout=10.0,
    trust_env=False,
)


def request_single(session_token, url):
    CLIENT.cookies.update(session_token)

    while True:
        try:
            response = CLIENT.get(url)
            if response.status_code == 429:
                time.sleep(0.5)
                continue
            return response
        except (httpx.TimeoutException, httpx.RemoteProtocolError, httpx.ProxyError):
            time.sleep(0.25)


def get_json(session_token, url):
    return request_single(session_token, url).json()


def get_html(session_token, url):
    return BeautifulSoup(request_single(session_token, url).text, "lxml")


members = []
seen_members = set()
seen_courses = set()
sections = get_json(SESSION_TOKEN, f"{BASE_URL}/v2/sections")["@items"]


def loop_course(course_id):
    if course_id in seen_courses:
        return

    seen_courses.add(course_id)
    print(f"Processing course: {course_id}")

    members_json = get_json(SESSION_TOKEN, f"{BASE_URL}/v2/sections/{course_id}/members")
    if not members_json or "@items" not in members_json:
        print(f"No members found for course: {course_id}")
        return

    for member in members_json["@items"]:
        member = get_json(SESSION_TOKEN, member["@id"])
        member_id = member["lisPersonSourcedid"].split("::")[0]

        if member_id not in seen_members:
            seen_members.add(member_id)
            members.append(member)
            print(f"Added member: {member['name']['full']}")

        wrapper = get_html(SESSION_TOKEN, f"{BASE_URL}/user/{member_id}/courses/list").find(
            "ul", class_="my-courses-item-list"
        )
        if wrapper is None:
            print(f"Could not find course list for {member['name']['full']}")
            continue

        for link in wrapper.find_all("a", href=True):
            href = link["href"]
            parts = href.split("/")
            if len(parts) >= 3:
                loop_course(parts[2])


for section in sections:
    loop_course(section["@id"].split("/")[5])

print("\nFinished!")
print(f"Courses processed: {len(seen_courses)}")
print(f"Unique members: {len(members)}")

output_path = Path(__file__).resolve().parent / "members.json"
with output_path.open("w", encoding="utf-8") as file:
    json.dump(members, file, indent=2, ensure_ascii=False)

print(f"Saved {len(members)} unique members to {output_path}")
