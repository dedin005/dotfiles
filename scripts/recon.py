#!/usr/bin/env python3
"""
recon.py - Simple Instagram OSINT + cross-platform username checker.
No external dependencies — just Python 3 stdlib + curl.

Usage:
    python3 recon.py -s <instagram_session_id> -u <username>
    python3 recon.py -s <instagram_session_id> -u <username> --save
    python3 recon.py -u <username> --skip-ig
"""

import argparse
import subprocess
import json
import os
import sys
from datetime import datetime
from urllib.parse import quote_plus

# --- Config ---

ANDROID_UA = (
    "Instagram 344.0.0.0.98 Android (33/13; 420dpi; 1080x2400; "
    "samsung; SM-S911B; e1q; exynos2400; en_US; 617734938)"
)
BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) "
    "Gecko/20100101 Firefox/128.0"
)

# Platforms to check: (name, url_template, method, indicator_type, indicator)
# indicator_type: "status" = check HTTP status, "body_missing" = 404 if body contains string
PLATFORMS = [
    ("Twitter/X",    "https://x.com/{}",                    "GET", "status",       200),
    ("TikTok",       "https://www.tiktok.com/@{}",          "GET", "status",       200),
    ("GitHub",       "https://api.github.com/users/{}",     "GET", "status",       200),
    ("Reddit",       "https://www.reddit.com/user/{}/about.json", "GET", "status", 200),
    ("Snapchat",     "https://www.snapchat.com/add/{}",     "GET", "status",       200),
    ("Pinterest",    "https://www.pinterest.com/{}/",       "GET", "status",       200),
    ("Twitch",       "https://www.twitch.tv/{}",            "GET", "status",       200),
    ("Steam",        "https://steamcommunity.com/id/{}",    "GET", "status",       200),
    ("Spotify",      "https://open.spotify.com/user/{}",    "GET", "status",       200),
    ("SoundCloud",   "https://soundcloud.com/{}",           "GET", "status",       200),
    ("YouTube",      "https://www.youtube.com/@{}",         "GET", "status",       200),
    ("Telegram",     "https://t.me/{}",                     "GET", "status",       200),
    ("LinkedIn",     "https://www.linkedin.com/in/{}/",     "GET", "status",       200),
    ("Facebook",     "https://www.facebook.com/{}",         "GET", "status",       200),
]

# Platforms that return 200 for nonexistent users — need body inspection
# mode: "missing_means_exists" = if the string is NOT in body, user exists
#        "present_means_exists" = if the string IS in body, user exists
BODY_CHECKS = {
    "TikTok":    {"string": "could not find this account",    "mode": "missing_means_exists"},
    "Pinterest": {"string": "profile_cover",                  "mode": "present_means_exists"},
    "Twitch":    {"string": "content=\"profile\"",            "mode": "present_means_exists"},
    "Steam":     {"string": "the specified profile could not be found", "mode": "missing_means_exists"},
    "Spotify":   {"string": "og:title",                       "mode": "present_means_exists"},
    "Telegram":  {"string": "tgme_page_title",                "mode": "present_means_exists"},
    "Twitter/X": {"string": "\"screen_name\"",                "mode": "present_means_exists"},
    "Facebook":  {"string": "pageID",                         "mode": "present_means_exists"},
}

# --- Colors ---

class C:
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"


# --- Helpers ---

def curl_get(url, session_id=None, extra_headers=None, timeout=10):
    """GET via curl, returns (status_code, parsed_json_or_None, raw_body)."""
    cmd = ["curl", "-s", "-w", "\n%{http_code}", "-m", str(timeout), url]
    cmd.extend(["-H", f"User-Agent: {BROWSER_UA}"])
    if session_id:
        cmd.extend(["-H", f"Cookie: sessionid={session_id}"])
    if extra_headers:
        for k, v in extra_headers.items():
            cmd.extend(["-H", f"{k}: {v}"])

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()

    # Last line is the status code
    lines = output.rsplit("\n", 1)
    if len(lines) == 2:
        body, status = lines[0], lines[1]
    else:
        body, status = "", lines[0] if lines else ""

    try:
        status_code = int(status)
    except ValueError:
        status_code = 0

    try:
        data = json.loads(body) if body else None
    except json.JSONDecodeError:
        data = None

    return status_code, data, body


def curl_ig_get(url, session_id):
    """Instagram-specific GET using Android UA."""
    cmd = [
        "curl", "-s", url,
        "-H", f"User-Agent: {ANDROID_UA}",
        "-H", f"Cookie: sessionid={session_id}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def curl_post(url, data, headers):
    """POST via curl."""
    cmd = ["curl", "-s", "-X", "POST", url]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["-d", data])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def section(title):
    print(f"\n{C.BOLD}{C.CYAN}{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}{C.RESET}\n")


def field(label, value, indent=0):
    pad = " " * indent
    print(f"{pad}{C.DIM}{label:25s}{C.RESET} {value}")


# --- Instagram ---

def ig_profile_lookup(username, session_id):
    """Get basic profile info via web_profile_info endpoint."""
    section("Instagram Profile")

    data = curl_ig_get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
        session_id,
    )

    if not data or "data" not in data or not data["data"].get("user"):
        msg = data.get("message", "Unknown error") if data else "Empty response / rate limited"
        print(f"  {C.RED}Failed: {msg}{C.RESET}")
        return None

    user = data["data"]["user"]
    user_id = user["id"]

    field("Username",         user.get("username", "N/A"))
    field("User ID",          user_id)
    field("Full Name",        user.get("full_name", "N/A"))
    field("Biography",        user.get("biography", "(empty)") or "(empty)")
    field("Private",          str(user.get("is_private", "N/A")))
    field("Verified",         str(user.get("is_verified", "N/A")))
    field("Business Account", str(user.get("is_business_account", "N/A")))
    field("Followers",        str(user.get("edge_followed_by", {}).get("count", "N/A")))
    field("Following",        str(user.get("edge_follow", {}).get("count", "N/A")))
    field("Posts",            str(user.get("edge_owner_to_timeline_media", {}).get("count", "N/A")))

    if user.get("external_url"):
        field("External URL", user["external_url"])

    if user.get("business_email"):
        field("Business Email", user["business_email"])
    if user.get("business_phone_number"):
        field("Business Phone", user["business_phone_number"])

    # Mutual followers
    mutuals = user.get("edge_mutual_followed_by", {})
    mutual_count = mutuals.get("count", 0)
    if mutual_count > 0:
        names = [e["node"]["username"] for e in mutuals.get("edges", [])]
        field("Mutual Followers", f"{mutual_count} ({', '.join(names)}{'...' if mutual_count > len(names) else ''})")

    return user_id, user


def ig_detailed_info(user_id, session_id):
    """Get detailed user info via /users/ID/info/ endpoint."""
    section("Instagram Detailed Info")

    data = curl_ig_get(
        f"https://i.instagram.com/api/v1/users/{user_id}/info/",
        session_id,
    )

    if not data or not data.get("user"):
        print(f"  {C.RED}Failed or rate limited{C.RESET}")
        return None

    user = data["user"]

    field("Linked WhatsApp",  str(user.get("is_whatsapp_linked", "N/A")))
    field("Memorial Account", str(user.get("is_memorialized", "N/A")))
    field("New to Instagram", str(user.get("is_new_to_instagram", "N/A")))

    if user.get("public_email"):
        field("Public Email", user["public_email"])
    if user.get("public_phone_number"):
        cc = user.get("public_phone_country_code", "")
        field("Public Phone", f"+{cc} {user['public_phone_number']}")

    return user


def ig_advanced_lookup(username):
    """Obfuscated email/phone lookup."""
    section("Instagram Advanced Lookup")

    body = "signed_body=SIGNATURE." + quote_plus(json.dumps(
        {"q": username, "skip_recovery": "1"},
        separators=(",", ":")
    ))
    headers = {
        "Accept-Language": "en-US",
        "User-Agent": "Instagram 344.0.0.0.98",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-IG-App-ID": "124024574287414",
        "Accept-Encoding": "gzip, deflate",
        "Host": "i.instagram.com",
        "Connection": "keep-alive",
        "Content-Length": str(len(body)),
    }

    data = curl_post("https://i.instagram.com/api/v1/users/lookup/", body, headers)

    if not data:
        print(f"  {C.RED}Rate limited or failed{C.RESET}")
        return

    if "message" in data:
        if data["message"] == "No users found":
            print(f"  {C.DIM}Lookup returned no results{C.RESET}")
        else:
            print(f"  {C.DIM}{data['message']}{C.RESET}")
        return

    obf_email = data.get("obfuscated_email")
    obf_phone = data.get("obfuscated_phone")

    if obf_email:
        field("Obfuscated Email", obf_email)
    else:
        field("Obfuscated Email", "not found")

    if obf_phone:
        field("Obfuscated Phone", str(obf_phone))
    else:
        field("Obfuscated Phone", "not found")


def ig_friendship(user_id, session_id):
    """Check friendship status."""
    data = curl_ig_get(
        f"https://i.instagram.com/api/v1/friendships/show/{user_id}/",
        session_id,
    )
    if not data or data.get("status") != "ok":
        return

    interesting = {}
    for key in ["following", "followed_by", "blocking", "incoming_request",
                "outgoing_request", "is_restricted", "is_bestie"]:
        if data.get(key):
            interesting[key] = True

    if interesting:
        section("Friendship Status")
        for k, v in interesting.items():
            field(k.replace("_", " ").title(), str(v))


def ig_download_pfp(username, pic_url):
    """Download profile picture for reverse image search."""
    if not pic_url:
        return None
    filename = f"{username}_pfp.jpg"
    subprocess.run(
        ["curl", "-s", "-o", filename, pic_url],
        capture_output=True,
    )
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        return filename
    return None


# --- Cross-Platform ---

def check_platform(platform_name, url, timeout=10):
    """Check if a username exists on a platform. Returns (exists, url, status)."""
    # Some platforms need body inspection to avoid false positives
    needs_body = platform_name in BODY_CHECKS

    if needs_body:
        cmd = [
            "curl", "-s",
            "-w", "\n__STATUS__%{http_code}",
            "-m", str(timeout),
            "-L",
            "-H", f"User-Agent: {BROWSER_UA}",
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout

        # Split body and status
        if "__STATUS__" in output:
            body, status_str = output.rsplit("__STATUS__", 1)
        else:
            body, status_str = output, "0"

        try:
            status = int(status_str.strip())
        except ValueError:
            status = 0

        if status != 200:
            return False, url, status

        # Check for platform-specific "not found" indicators in body
        check = BODY_CHECKS[platform_name]
        if check["mode"] == "missing_means_exists":
            # If the "not found" string is ABSENT, user exists
            exists = check["string"].lower() not in body.lower()
        else:
            # If the "found" string is PRESENT, user exists
            exists = check["string"].lower() in body.lower()

        return exists, url, status

    else:
        cmd = [
            "curl", "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            "-m", str(timeout),
            "-L",
            "-H", f"User-Agent: {BROWSER_UA}",
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            status = int(result.stdout.strip())
        except ValueError:
            status = 0

        exists = status == 200
        return exists, url, status


def cross_platform_search(username):
    """Check username across multiple platforms."""
    section("Cross-Platform Username Search")

    found = []
    not_found = []

    for name, url_template, method, indicator_type, indicator in PLATFORMS:
        url = url_template.format(username)
        sys.stdout.write(f"  Checking {name:15s} ... ")
        sys.stdout.flush()

        exists, full_url, status = check_platform(name, url)

        if exists:
            print(f"{C.GREEN}FOUND{C.RESET} ({status})")
            found.append((name, full_url))
        elif status == 0:
            print(f"{C.YELLOW}TIMEOUT{C.RESET}")
        else:
            print(f"{C.DIM}not found ({status}){C.RESET}")
            not_found.append(name)

    if found:
        print(f"\n  {C.GREEN}{C.BOLD}Found on {len(found)} platform(s):{C.RESET}")
        for name, url in found:
            print(f"    {C.GREEN}✓{C.RESET} {name:15s} {C.DIM}{url}{C.RESET}")

    return found


# --- Report ---

def save_report(username, ig_user, ig_detail, platform_hits):
    """Save a JSON report to disk."""
    report = {
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "instagram": {},
        "platforms": [],
    }

    if ig_user:
        report["instagram"]["profile"] = {
            "user_id": ig_user.get("id"),
            "full_name": ig_user.get("full_name"),
            "biography": ig_user.get("biography"),
            "is_private": ig_user.get("is_private"),
            "is_verified": ig_user.get("is_verified"),
            "followers": ig_user.get("edge_followed_by", {}).get("count"),
            "following": ig_user.get("edge_follow", {}).get("count"),
            "posts": ig_user.get("edge_owner_to_timeline_media", {}).get("count"),
            "external_url": ig_user.get("external_url"),
            "profile_pic": ig_user.get("profile_pic_url_hd"),
        }

    if ig_detail:
        report["instagram"]["detail"] = {
            "public_email": ig_detail.get("public_email"),
            "public_phone": ig_detail.get("public_phone_number"),
            "is_whatsapp_linked": ig_detail.get("is_whatsapp_linked"),
            "is_memorialized": ig_detail.get("is_memorialized"),
        }

    if platform_hits:
        report["platforms"] = [{"name": n, "url": u} for n, u in platform_hits]

    filename = f"{username}_report.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  {C.DIM}Report saved to {filename}{C.RESET}")
    return filename


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="recon.py - Instagram OSINT + cross-platform username checker"
    )
    parser.add_argument("-s", "--sessionid", help="Instagram session ID")
    parser.add_argument("-u", "--username", help="Username to investigate", required=True)
    parser.add_argument("--save", action="store_true", help="Save JSON report to file")
    parser.add_argument("--skip-ig", action="store_true", help="Skip Instagram lookup")
    parser.add_argument("--skip-platforms", action="store_true", help="Skip cross-platform search")
    parser.add_argument("--download-pfp", action="store_true", help="Download profile picture")
    args = parser.parse_args()

    # Resolve session ID: flag > env var > config file
    if not args.sessionid and not args.skip_ig:
        if os.environ.get("IG_SESSION"):
            args.sessionid = os.environ["IG_SESSION"]
        elif os.path.exists(os.path.expanduser("~/.ig_session")):
            with open(os.path.expanduser("~/.ig_session")) as f:
                args.sessionid = f.read().strip()

    if not args.skip_ig and not args.sessionid:
        print(f"{C.RED}Error: No session ID found. Provide one via:{C.RESET}")
        print(f"  1. {C.DIM}-s <session_id>{C.RESET}")
        print(f"  2. {C.DIM}export IG_SESSION=<session_id>{C.RESET}")
        print(f"  3. {C.DIM}echo '<session_id>' > ~/.ig_session{C.RESET}")
        sys.exit(1)

    print(f"\n{C.BOLD}{'═'*50}")
    print(f"  recon.py — {args.username}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═'*50}{C.RESET}")

    ig_user = None
    ig_detail = None
    user_id = None

    # Instagram
    if not args.skip_ig:
        result = ig_profile_lookup(args.username, args.sessionid)
        if result:
            user_id, ig_user = result

            ig_detail = ig_detailed_info(user_id, args.sessionid)
            ig_advanced_lookup(args.username)
            ig_friendship(user_id, args.sessionid)

            if args.download_pfp:
                pic_url = ig_user.get("profile_pic_url_hd") or ig_user.get("profile_pic_url")
                pfp_file = ig_download_pfp(args.username, pic_url)
                if pfp_file:
                    print(f"\n  {C.DIM}Profile pic saved to {pfp_file}{C.RESET}")

    # Cross-platform
    platform_hits = []
    if not args.skip_platforms:
        platform_hits = cross_platform_search(args.username)

    # Save report
    if args.save:
        section("Report")
        save_report(args.username, ig_user, ig_detail, platform_hits)

    print(f"\n{C.BOLD}{'═'*50}")
    print(f"  Done.")
    print(f"{'═'*50}{C.RESET}\n")


if __name__ == "__main__":
    main()
