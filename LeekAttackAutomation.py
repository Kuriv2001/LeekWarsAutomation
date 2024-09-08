import urllib3
import json
import sys
import time




idOwnPlayer = <LEEK_ID_TO_PLAY_WITH> # In url when leek chosen on homepage
getOppenentsUrl = f"https://leekwars.com/api/garden/get-leek-opponents/{idOwnPlayer}"
cookieToken = "<COOKIE_IN_BROWSER>" # In browser when inspecting website network requests
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
        print("Fight won: " + str(int(json.loads(resultFight.data.decode())["winner"]) != -1))
    except:
        print("All fights used up for the moment :(")
        break

    time.sleep(1)
