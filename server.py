import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs(clubs_json):
    with open(clubs_json) as c:
        listOfClubs = json.load(c)['clubs']
        for club in listOfClubs:
            club["points"] = int(club["points"])
        return listOfClubs


def loadCompetitions(competitions_json):
    with open(competitions_json) as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def create_app(config={}):
    app = Flask(__name__)
    app.config.update(config)
    app.secret_key = 'something_special'

    competitions_json = 'competitions.json'
    clubs_json = 'clubs.json'
    if app.config["TESTING"] == True:
        competitions_json = 'tests/test_dataset.json'
        clubs_json = 'tests/test_dataset.json'

    competitions = loadCompetitions(competitions_json)
    clubs = loadClubs(clubs_json)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/showSummary',methods=['POST'])
    def showSummary():
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html', club=club, competitions=competitions)


    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        foundClub = [c for c in clubs if c['name'] == club][0]
        if foundClub["points"] == 0:
            flash("You have no point and cannot make any reservation!")
            return render_template('welcome.html', club=foundClub, competitions=competitions)
        foundCompetition = [c for c in competitions if c['name'] == competition][0]
        if foundClub and foundCompetition:
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        else:
            flash("Something went wrong-please try again")
            return render_template('welcome.html', club=club, competitions=competitions)


    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]
        placesRequired = int(request.form['places'])
        placesRemaining = int(competition['numberOfPlaces'])
        if placesRequired > int(club['points']):
            flash(f"Cannot book - trying to book more than what you have.")
            return render_template('booking.html',club=club, competition=competition)
        elif placesRequired > placesRemaining:
            flash(f"Cannot book - trying to book more than what remains.")
            return render_template('booking.html',club=club, competition=competition)
        else:
            flash('Great-booking complete!')
            club['points'] = int(club['points']) - placesRequired
            competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
            return render_template('welcome.html', club=club, competitions=competitions)

    # TODO: Add route for points display


    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app