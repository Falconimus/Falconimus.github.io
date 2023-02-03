import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from playsound import playsound 
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import g, request, redirect, url_for, json

# Flask configuration.
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == "__main__":
    app.run(debug=false, host="0.0.0.0")
    
# Config for accounts.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Sql database.
db = SQL("sqlite:///Eartraining.db")
# Arrays for all exercise and difficulties.
Exercises = ['Intervals', 'Absolute']
Difficulties = ['Easy', 'Medium', 'Hard']

# Login_required function.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Route for deregistering.
@app.route("/deregister", methods=["GET", "POST"])
@login_required
def deregister():
    # Check request.method.
    if request.method == "GET":
        # Render the template for the user so he can input his.
        return render_template("deregister.html")
    else:
        # Make sure the user provides a username.
        if not request.form.get("username"):
            return render_template("deregister.html", Error = "Please provide username")
        # Make sure the user provides and confirms his password.
        elif not request.form.get("password") or not request.form.get("password_confirmation"):
            return render_template("deregister.html", Error = "Please enter and repeat your password")
        # Make sure the password confirmation matches the original password.
        elif request.form.get("password") != request.form.get("password_confirmation"):
            return render_template("deregister.html", Error = "Confirmation must match password")
        # Get info about user from Database.
        user = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))
        # Make sure Username and Password match and are valid.
        if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
            return render_template("deregister.html", Error = "Invalid Username and/or password")
        # Make sure the user is logged in with the account he is trying to delete.
        elif user[0]["id"] != session["user_id"]:
            return render_template("deregister.html", Error = "Please login with the account you´re trying to deregister")
        # Delete account.
        else:
            db.execute("DELETE FROM stats WHERE user_id = ?", user[0]["id"])
            db.execute("DELETE FROM users WHERE id = ?", user[0]["id"])
            # Log user out.
            session.clear()
            # Go back to login page.
            return redirect("/")

# Index page.
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# Sound test page.
@app.route("/sounds")
@login_required
def sounds():
    return render_template("sounds.html")

# Leaderboard page.
@app.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    # Generate the leaderboards.
    generate_leaderboards()
    # Make array of all Leaderboards (For each exercise and difficulty).
    leaderboards = []
    for Exercise in Exercises:
        for Difficulty in Difficulties:
            # Check wether or not the exercise was already played.
            if db.execute("SELECT * FROM stats WHERE exercise = ? AND difficulty = ?", Exercise, Difficulty)[0]["total_rounds"] != 0:
                lists = db.execute("SELECT * FROM stats WHERE exercise = ? AND difficulty = ? AND total_rounds > 0 ORDER BY leaderbord_p ASC", Exercise, Difficulty)
            else:
                lists = db.execute("SELECT * FROM stats WHERE exercise = ? AND difficulty = ? ORDER BY leaderbord_p ASC", Exercise, Difficulty)
            leaderboards.append(lists)
    # Render page.
    return render_template("leaderboard.html", leaderboards=leaderboards)

# Exercise route.
@app.route("/exercises", methods=["GET", "POST"])
@login_required
def exercises():
    # Check request method.
    if request.method == 'GET':
        # Render template for Exercise and Difficulty Selection.
        return render_template("exercises.html")
    # Make sure Exercise and Difficulty was provided.
    elif not request.form.get("exercise") or not request.form.get("difficulty"):
        return redirect("/")
    else:
        # See if the user is already on a streak.
        if request.form.get("streak") != None:
            streak = request.form.get("streak")
        else:
            streak = 0
        # Get the submitted exercise and Difficulty.
        exercise = request.form.get("exercise")
        difficulty = request.form.get("difficulty")
        # Render different template depending on Exercise.
        if exercise == 'Absolute':
            return render_template("Absolute.html", streak=streak, difficulty=difficulty)
        elif exercise == 'Intervals':
            return render_template("Intervals.html", streak=streak, difficulty=difficulty)

# Register route.
@app.route("/register", methods=["GET", "POST"])
def register():
    # Make sure user is not already logged in.
    session.clear()
    # Check request method.
    if request.method == 'GET':
        # Render registration template.
        return render_template("register.html")
    else: 
        # Make sure the user provides a username.
        if not request.form.get('username'):
            return render_template("register.html", Error_message='Please provide a username')
        # Make sure the username doesn´t already exist.
        if len(db.execute("SELECT name FROM users WHERE name = ?", request.form.get("username"))) != 0:
            return render_template("register.html", Error_message="Username already exists")
        # Make sure a password is provided.
        if not request.form.get("password"):
            return render_template("register.html", Error_message="Please provide a password")
        # Make sure the password is confirmed.
        if not request.form.get("password_confirmation"):
            return render_template("register.html", Error_message="Please repeat your password")
        # Make sure password and confirmation match.
        if request.form.get("password") != request.form.get("password_confirmation"):
            return render_template("register.html", Error_message="Passwords do not match")
        # Get the input from the user.
        username = request.form.get('username')
        password_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        # Insert user into database.
        db.execute('INSERT INTO users (name, hash) VALUES (?, ?)', username, password_hash)
        # Log user in.
        session["user_id"] = db.execute("SELECT * FROM users WHERE name = ?", username)[0]["id"]
        # Setup all the stats for the user (for each exercise and difficulty).
        for Exercise in Exercises:
            for Difficulty in Difficulties:
                db.execute('INSERT INTO stats (user_id, exercise, difficulty, user_name) VALUES (?, ?, ?, ?)', session["user_id"], Exercise, Difficulty, username)
    # Redirect user to index page.
    return redirect("/")
        
# Logout route.
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Route for user´s statistics.
@app.route("/stats")
@login_required
def stats():
        # Generate the leaderboards so the user can see his ranks.
        generate_leaderboards()
        # Get user stats.
        user_stats = db.execute("SELECT * FROM stats WHERE user_id = ?", session["user_id"])
        # Load stats template.
        return render_template("stats.html", user_stats=user_stats)

# Login route.
@app.route("/login", methods=["GET", "POST"])
def login():
    # Make sure user is not logged in.
    session.clear()
    # Check request method.
    if request.method == 'GET':
        # Render login page.
        return render_template("login.html")
    else:
        # Make sure the user provided a username.
        if not request.form.get('username'):
            return render_template("login.html", Error_message='Please provide a username')
        # Make sure the user provided a password.
        if not request.form.get("password"):
            return render_template("login.html", Error_message="Please provide a password")
        # Search name in database.
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))
        # Make sure username and password match.
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", Error_message="Invalid Username and/or password")
        # Log user in.
        session["user_id"] = rows[0]["id"]
        # Redirect to index page.
        return redirect("/")

# Result route.
@app.route("/result", methods=['GET'])
@login_required
def result():
    # Render slightly different results based on exercise.
    if mode == 'Absolute':
        return render_template("result.html", correct_img_nmb=correct_img_nmb, difficulty=difficulty, result=result, mode=mode, win_streak=win_streak, highscore=highscore, correct_note=correct_note, submitted_note=submitted_note)
    elif mode == 'Intervals':
        return render_template("result.html", correct_img_nmb=correct_img_nmb, correct_img_nmb2=correct_img_nmb2, difficulty=difficulty, result=result, mode=mode, win_streak=win_streak, highscore=highscore, correct_note=correct_note, correct_note_2=correct_note_2, 
        correct_distance=correct_distance, submitted_distance=submitted_distance, correct_direction=correct_direction, submitted_direction=submitted_direction)
    # If no exercise was provided, redirect to Index page.
    else:
        return redirect("/")

# Route that check the result and provides "/result" with answer.
@app.route("/resultcheck", methods=['GET', 'POST'])
@login_required
def resultcheck():
    # Make sure request method is "Post".
    if request.method == 'GET':
        return redirect("/")
    # Setup global variables so "/result" can access them.
    global result, correct_note, win_streak, correct_img_nmb, mode, difficulty, highscore
    result = request.form.get("result")
    correct_note = request.form.get("correct_note")
    win_streak = int(request.form.get("streak"))
    correct_img_nmb = json.dumps(request.form.get("correct_img_nmb"))
    mode = request.form.get("mode")
    difficulty = request.form.get("difficulty")
    highscore = int(db.execute("SELECT streak_highscore FROM stats WHERE user_id = ? AND exercise = ? AND difficulty = ?", session["user_id"], mode, difficulty)[0]["streak_highscore"])
    # Slightly different variables depending on exercise.
    if mode == 'Absolute':
        global submitted_note
        submitted_note = request.form.get("submitted_note")
    elif mode == 'Intervals':
        global correct_img_nmb2, correct_note_2, correct_distance, submitted_distance, correct_direction, submitted_direction
        correct_img_nmb2 = request.form.get("correct_img_nmb2")
        correct_note_2 = request.form.get("correct_note_2")
        correct_distance = request.form.get("correct_distance")
        submitted_distance = request.form.get("submitted_distance")
        correct_direction = request.form.get("correct_direction")
        submitted_direction = request.form.get("submitted_direction")
    # Update the database depending on win/loss.
    if win_streak > 0:
        if win_streak > highscore:
            db.execute("UPDATE stats SET streak_highscore = ? WHERE user_id = ? AND exercise = ? AND difficulty = ?", win_streak, session["user_id"], mode, difficulty)
        db.execute("UPDATE stats SET total_wins = total_wins+1 WHERE user_id = ? AND exercise = ? AND difficulty = ?", session["user_id"], mode, difficulty)
    else:
        db.execute("UPDATE stats SET total_losses = total_losses+1 WHERE user_id = ? AND exercise = ? AND difficulty = ?", session["user_id"], mode, difficulty)
    # Update amount of played rounds.
    db.execute("UPDATE stats SET total_rounds = total_rounds+1 WHERE user_id = ? AND exercise = ? AND difficulty = ?", session["user_id"], mode, difficulty)
    total_wins = float(db.execute("SELECT total_wins FROM stats WHERE user_id = ? AND exercise = ? AND difficulty = ?", session["user_id"], mode, difficulty)[0]["total_wins"])
    total_losses = float(db.execute("SELECT total_losses FROM stats WHERE user_id = ? AND exercise = ? AND difficulty = ?", session["user_id"], mode, difficulty)[0]["total_losses"])
    # Calculate winrate.
    if total_losses > 0:
        win_rate = "{:.3f}".format(total_wins / total_losses)
    else:
        win_rate = 'perfect'
    # Log winrate in database.
    db.execute("UPDATE stats SET win_rate = ? WHERE user_id = ? AND exercise = ? AND difficulty = ?", win_rate, session["user_id"], mode, difficulty)
    # Redirect to "/result".
    return redirect("/result")
    
# Function that puts the Leaderboard ranks right in the database.
def generate_leaderboards():
    # Get all users from database.
    users = db.execute('SELECT * FROM users;')
    # Generate a leaderboard for each exercise and difficulty.
    for Exercise in Exercises:
        for Difficulty in Difficulties:
            rows = db.execute('SELECT * FROM stats WHERE exercise = ? AND difficulty = ? ORDER BY streak_highscore DESC, win_rate DESC;', Exercise, Difficulty)
            i = 0
            for user in users:
                user_id = rows[i]["user_id"]
                i += 1
                db.execute("UPDATE stats SET leaderbord_p = ? WHERE exercise = ? AND difficulty = ? AND user_id = ?", ('#'+str(i)), Exercise, Difficulty, user_id)
    # Return from function.
    return
                    
