from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

player1_secret = ""
player2_secret = ""

# Guess history for each player: (guess, correct_numbers, correct_position)
history = {1: [], 2: []}


def get_feedback(guess, secret):
    """Returns (correct_numbers, correct_position) for a guess."""

    correct_position = 0

    for i in range(3):
        if guess[i] == secret[i]:
            correct_position += 1

    correct_numbers = 0

    for digit in set(guess):
        if digit in secret:
            correct_numbers += 1

    return correct_numbers, correct_position


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Save secret number
@app.route("/set_secret", methods=["POST"])
def set_secret():

    global player1_secret, player2_secret

    data = request.get_json()

    player = data.get("player")
    number = data.get("number")

    if not number or len(number) != 3 or not number.isdigit():
        return jsonify({
            "message": "❌ Please enter exactly 3 digits."
        })

    if player == 1:

        player1_secret = number

        return jsonify({
            "message": "✅ Player 1 number saved! Player 2, set your secret number.",
            "next_player": 2
        })

    elif player == 2:

        player2_secret = number

        return jsonify({
            "message": "✅ Player 2 number saved! Player 1 can start guessing.",
            "next_player": 1
        })

    return jsonify({
        "message": "❌ Invalid player."
    })


# Check guess
@app.route("/guess", methods=["POST"])
def check_guess():

    data = request.get_json()

    player = data.get("player")
    guess = data.get("guess")

    if not guess or len(guess) != 3 or not guess.isdigit():
        return jsonify({
            "message": "❌ Please enter exactly 3 digits.",
            "correct": False
        })

    if player == 1:
        secret = player2_secret

    elif player == 2:
        secret = player1_secret

    else:
        return jsonify({
            "message": "❌ Invalid player.",
            "correct": False
        })

    if guess == secret:

        return jsonify({
            "message": "🎉 CORRECT! Player " + str(player) + " Wins! 🏆",
            "correct": True
        })

    correct_numbers, correct_position = get_feedback(guess, secret)

    # Save this guess so the AI can learn from it
    history[player].append((guess, correct_numbers, correct_position))

    wrong_position = correct_numbers - correct_position

    if correct_numbers == 0:

        message = "❌ No number is correct."

    elif wrong_position == 0:

        message = (
            "🎯 "
            + str(correct_numbers)
            + " number(s) correct and in correct position."
        )

    else:

        message = (
            "🔥 "
            + str(correct_numbers)
            + " number(s) correct | "
            + str(correct_position)
            + " correct position | "
            + str(wrong_position)
            + " wrong position"
        )

    return jsonify({
        "message": message,
        "correct": False
    })


# Smart AI guess (used when the player's time is over)
@app.route("/ai_guess", methods=["POST"])
def ai_guess():

    data = request.get_json(silent=True) or {}

    player = data.get("player")

    past = history.get(player, [])

    candidates = []

    for n in range(1000):

        candidate = str(n).zfill(3)

        possible = True

        for old_guess, old_numbers, old_position in past:

            # Candidate must give the same hints as the real secret gave
            if candidate == old_guess or \
               get_feedback(old_guess, candidate) != (old_numbers, old_position):
                possible = False
                break

        if possible:
            candidates.append(candidate)

    if not candidates:
        candidates = [str(random.randint(0, 999)).zfill(3)]

    return jsonify({
        "guess": random.choice(candidates)
    })


# Restart game
@app.route("/restart", methods=["POST"])
def restart():

    global player1_secret, player2_secret

    player1_secret = ""
    player2_secret = ""

    history[1] = []
    history[2] = []

    return jsonify({
        "message": "🔄 New game started!"
    })


# Run server
if __name__ == "__main__":
    app.run(debug=True)