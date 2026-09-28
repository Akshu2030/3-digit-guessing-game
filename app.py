from flask import Flask, render_template, request, jsonify
import random
app = Flask(__name__)

player1_secret = ""
player2_secret = ""


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

    # Check number
    if not number or len(number) != 3 or not number.isdigit():
        return jsonify({
            "message": "❌ Please enter exactly 3 digits."
        })

    # Player 1 secret
    if player == 1:

        player1_secret = number

        return jsonify({
            "message": "✅ Player 1 number saved! Player 2, set your secret number.",
            "next_player": 2
        })

    # Player 2 secret
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

    # Player 1 guesses Player 2
    if player == 1:
        secret = player2_secret

    # Player 2 guesses Player 1
    elif player == 2:
        secret = player1_secret

    else:
        return jsonify({
            "message": "❌ Invalid player.",
            "correct": False
        })

    # Exact answer
    if guess == secret:

        return jsonify({
            "message": "🎉 CORRECT! Player " + str(player) + " Wins! 🏆",
            "correct": True
        })

    # Correct position
    correct_position = 0

    for i in range(3):

        if guess[i] == secret[i]:
            correct_position += 1

    # Correct numbers
    correct_numbers = 0

    for digit in set(guess):

        if digit in secret:
            correct_numbers += 1

    wrong_position = correct_numbers - correct_position

    # Result
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
# AI guess (used when the player's time is over)
@app.route("/ai_guess", methods=["POST"])
def ai_guess():

    guess = str(random.randint(0, 999)).zfill(3)

    return jsonify({
        "guess": guess
    })

# Restart game
@app.route("/restart", methods=["POST"])
def restart():

    global player1_secret, player2_secret

    player1_secret = ""
    player2_secret = ""

    return jsonify({
        "message": "🔄 New game started!"
    })


# Run server
if __name__ == "__main__":
    app.run(debug=True)