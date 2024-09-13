import urllib3
import json
import sys
import time
import re
import getpass


# Use login
loginUrl = "https://leekwars.com/api/farmer/login"
username = input('Enter your username/e-mail for Leekwars: ')
password = getpass.getpass(prompt='Enter your Leekwars password for the account ' + username + ": ")
payload = {
    "keep_connected": "false",
    "login": username,
    "password": password
}
headers = {
    "Content-Type": "application/json"
}

http = urllib3.PoolManager()
loginRequest = http.request("POST", loginUrl, body=json.dumps(payload).encode(), headers=headers)

# Get the cookie out of the header
cookies_header = loginRequest.headers.get('Set-Cookie')
token_match = re.search(r'token=(?!deleted)([^\s;]+)', cookies_header)
sess_id_match = re.search(r'PHPSESSID=[A-Za-z0-9]+', cookies_header)

if token_match:
    token = token_match.group(1)
    phpSessId = sess_id_match.group()
    cookieToken = phpSessId + "; token=" + token + "; lang=en"
else:
    print("Error: Couldn't find cookie in response")


# TODO: Make player able to choose leak from name
idOwnPlayer = <CHOSEN_LEEK_ID> # In url when leek chosen on homepage
getOppenentsUrl = f"https://leekwars.com/api/garden/get-leek-opponents/{idOwnPlayer}"
#cookieToken = "<COOKIE_IN_BROWSER>" # In browser when inspecting website network requests
headers = {
    "Cookie": cookieToken,
    "Content-Type": "application/json"
}

http = urllib3.PoolManager()

#websiteContent = http.get("GET", "https://leekwars.com/", headers=headers) => Todo to make work for everyone

while True:
    resp = http.request("GET", getOppenentsUrl, headers=headers)
    playersToAttack = json.loads(resp.data.decode())

    minTalent = sys.maxsize
    opponentChosen = None
    for opponent in playersToAttack["opponents"]:
        if opponent["talent"] < minTalent:
            minTalent = opponent["talent"]
            opponentChosen = opponent["id"]

    startFightUrl = "https://leekwars.com/api/garden/start-solo-fight"
    getFightUrl = "https://leekwars.com/api/fight/get/{opponentChosen}"

    payload = {
        "leek_id": idOwnPlayer,
        "target_id": opponentChosen
    }
    encoded_data = json.dumps(payload).encode()

    try:
        fightId = int(json.loads(http.request("POST", startFightUrl, body=encoded_data, headers=headers).data.decode())["fight"])
        resultFight = http.request("GET", f"https://leekwars.com/api/fight/get/{fightId}", headers=headers)
        # TODO: Make visible who won and against who
        print("Fight done")
    except:
        print("All fights used up for the moment :(")
        break

    time.sleep(1)
