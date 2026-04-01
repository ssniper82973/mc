import requests
import time
import json
from datetime import datetime

# --- CONFIG ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1488799304381501480/DTCvjpFEymnkhLUpI1vMQ240hN4PmYzDsR1L-gkH-a66KBuuNh5diTsx6zQCt6XQjPkc"
SERVER_IP = "thetismmsmp.falixsrv.me"
SERVER_PORT = 25565
UPDATE_INTERVAL = 60  # seconds between updates
# --------------

def get_server_status():
    try:
        url = f"https://api.mcsrvstat.us/3/{SERVER_IP}:{SERVER_PORT}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("online"):
            players_on = data.get("players", {}).get("online", 0)
            players_max = data.get("players", {}).get("max", 0)
            player_list = data.get("players", {}).get("list", [])
            motd = data.get("motd", {}).get("clean", [""])[0].strip()
            version = data.get("version", "Unknown")
            return {
                "online": True,
                "players_on": players_on,
                "players_max": players_max,
                "player_list": player_list,
                "motd": motd,
                "version": version
            }
        else:
            return {"online": False}
    except Exception as e:
        return {"online": False, "error": str(e)}

def build_embed(status):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    if status["online"]:
        player_list = status["player_list"]
        if player_list:
            players_str = "\n".join(f"• {p}" for p in player_list)
        else:
            players_str = "*No player list available*"

        embed = {
            "embeds": [{
                "title": f"🟢  {SERVER_IP}",
                "color": 0x57F287,
                "fields": [
                    {
                        "name": "Players",
                        "value": f"`{status['players_on']}/{status['players_max']}`",
                        "inline": True
                    },
                    {
                        "name": "Version",
                        "value": f"`{status['version']}`",
                        "inline": True
                    },
                    {
                        "name": "Online players",
                        "value": players_str if players_str else "*none*",
                        "inline": False
                    }
                ],
                "footer": {"text": f"Last updated: {now}"}
            }]
        }
        if status.get("motd"):
            embed["embeds"][0]["description"] = status["motd"]
    else:
        embed = {
            "embeds": [{
                "title": f"🔴  {SERVER_IP}",
                "description": "Server is offline or unreachable.",
                "color": 0xED4245,
                "footer": {"text": f"Last updated: {now}"}
            }]
        }
    return embed

def send_initial_message(embed):
    r = requests.post(
        WEBHOOK_URL + "?wait=true",
        json=embed,
        timeout=10
    )
    data = r.json()
    return data["id"]

def edit_message(message_id, embed):
    url = WEBHOOK_URL + f"/messages/{message_id}"
    requests.patch(url, json=embed, timeout=10)

def main():
    print(f"Starting MC monitor for {SERVER_IP}...")
    print(f"Updating every {UPDATE_INTERVAL} seconds")

    status = get_server_status()
    embed = build_embed(status)
    message_id = send_initial_message(embed)
    print(f"Posted message ID: {message_id}")

    while True:
        time.sleep(UPDATE_INTERVAL)
        status = get_server_status()
        embed = build_embed(status)
        edit_message(message_id, embed)
        ts = datetime.utcnow().strftime("%H:%M:%S")
        state = "ONLINE" if status["online"] else "OFFLINE"
        players = f"{status.get('players_on', 0)}/{status.get('players_max', 0)}" if status["online"] else "—"
        print(f"[{ts}] {state} | Players: {players}")

if __name__ == "__main__":
    main()
