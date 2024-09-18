from flask import Flask, render_template, request
import urllib3
import json
import time
import re

app = Flask(__name__)

# Function to automate Leekwars login and fight initiation
def start_leekwars_fights(leek_id, username, password):
    # Use login
    loginUrl = "https://leekwars.com/api/farmer/login"
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
        return "Error: Couldn't find cookie in response"

    getOppenentsUrl = f"https://leekwars.com/api/garden/get-leek-opponents/{leek_id}"
    headers = {
        "Cookie": cookieToken,
        "Content-Type": "application/json"
    }

    fight_ids = []  # List to collect fight IDs

    while True:
        resp = http.request("GET", getOppenentsUrl, headers=headers)
        playersToAttack = json.loads(resp.data.decode())

        minTalent = float('inf')
        opponentChosen = None
        for opponent in playersToAttack["opponents"]:
            if opponent["talent"] < minTalent:
                minTalent = opponent["talent"]
                opponentChosen = opponent["id"]

        startFightUrl = "https://leekwars.com/api/garden/start-solo-fight"

        payload = {
            "leek_id": leek_id,
            "target_id": opponentChosen
        }
        encoded_data = json.dumps(payload).encode()

        try:
            fight_response = http.request("POST", startFightUrl, body=encoded_data, headers=headers)
            fight_data = json.loads(fight_response.data.decode())
            fightId = int(fight_data.get("fight"))
            fight_ids.append(fightId)  # Add fight ID to the list
        except:
            if not fight_ids:
                return "All fights used up for the moment :("
            break  # Stop the loop if no more fights are available

        time.sleep(1)

    return fight_ids

@app.route("/")
def indexPage():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def startFights():
    leek_id = request.form.get("leekId")
    username = request.form.get("uname")
    password = request.form.get("passw")
    
    # Call the function to start Leekwars fights
    fight_ids = start_leekwars_fights(leek_id, username, password)
    
    # Render the results on the webpage
    return render_template("results.html", fight_ids=fight_ids)

if __name__ == "__main__":
    app.run(debug=False)
