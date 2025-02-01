from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
}

def get_last_games(username, game_type, max_games=50):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    
    archives = response.json().get("archives", [])
    if not archives:
        return None
    
    last_games = []
    for archive_url in reversed(archives):
        if len(last_games) >= max_games:
            break
        try:
            games_response = requests.get(archive_url, headers=HEADERS)
            games_response.raise_for_status()
        except requests.exceptions.RequestException:
            continue

        games = games_response.json().get("games", [])
        for game in reversed(games):
            if game.get("time_class") == game_type:
                last_games.append(game)
                if len(last_games) >= max_games:
                    break
    
    return last_games[:max_games]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    username = request.form['username'].strip().lower()
    game_type = request.form['game_type']
    max_games = int(request.form['max_games'])
    
    games = get_last_games(username, game_type, max_games)
    
    return jsonify({
        "message": f"Analizando {max_games} partidas de {username} en modo {game_type}."
    })

if __name__ == '__main__':
    app.run(debug=True)
