from flask import Flask, request, render_template, url_for, redirect
import sqlite3
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.sql import text


# We are not using this sqlconnection but this line just creates a sqlite db file
sqlconnection = sqlite3.connect('recipes.db')

app = Flask(__name__)


db_name = 'recipes.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.debug = True
#db_name = 'recipes.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Ingredients(db.Model):
    __tablename__ = 'ingredients_table'
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String)
    expiration_date = db.Column(db.String) # this will need to changed to a date format?

    def __init__(self, ingredient, expiration_date):
        self.ingredient = ingredient
        self.expiration_date = expiration_date


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pass
    return render_template("refrigerator2.html")

@app.route("/addIngredient", methods=['POST'])
def gfg():
    ingredient_record = Ingredients(request.form.get("ingredient"), request.form.get("expiration_date"))
    db.create_all()
    db.session.add(ingredient_record)
    db.session.commit()
    return redirect(url_for('home'))







"""
used to test the database connection, placed inside a flask function

 try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return '<h1> It works.</h1>'
 except Exception as e:
        # e holds description of the error
        error_text = "<p> The error:<br>" + str(e) + "</p>"
        hed = '<h1> Something is broken.</h1>'
        return hed + error_text
"""


if __name__ == "__main__":
    app.run()
