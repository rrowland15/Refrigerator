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
    ingredient = db.Column(db.String, unique=True)
    # this will need to changed to a date format?
    expiration_date = db.Column(db.String)

    def __init__(self, ingredient, expiration_date):
        self.ingredient = ingredient
        self.expiration_date = expiration_date


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pass
    return render_template("refrigerator2.html")

# to add an ingredient along with it's expiration date


@app.route("/addIngredient", methods=['POST'])
def gfg():
    ingredient_record = Ingredients(request.form.get(
        "ingredient"), request.form.get("expiration_date"))
    db.create_all()
    db.session.add(ingredient_record)
    db.session.commit()
    return redirect(url_for('home'))

# to remove an ingredient by name


@app.route("/removeIngredient", methods=['POST'])  # This works now!!
def removal():
    item = request.form.get("removedingredient")
    removal_id = (Ingredients.query.filter_by(ingredient=item).first()).id
    Ingredients.query.filter_by(id=removal_id).delete()
    db.session.commit()
    return redirect(url_for('home'))


# To navigate to the Fridge page
@app.route("/myfridge", methods=['GET'])
def myfridge():
    if request.method == 'POST':
        pass
    else:
        try:
            ingredients = Ingredients.query.all()
            content = ''
            for ingredient_record in ingredients:
                content += ingredient_record.ingredient + " "
            return render_template("fridgeinventory.html", content=content)

        except Exception as e:
            print(e)
            return 'Something is wrong'

        # return render_template("fridgeinventory.html")

# To navigate to the about.html page


@app.route("/about", methods=['Get'])
def about():
    if request.method == 'POST':
        pass
    return render_template("about.html")


# For database printing purposes (to print out the data currently in the database): delete decorator and function after done with the project
# make sure to add "/database" to the url
@app.route("/database", methods=['GET'])
def database():
    try:
        ingredients = Ingredients.query.all()
        ingredient_text = '<ul>'
        for ingredient_record in ingredients:
            ingredient_text += '<li>' + ingredient_record.ingredient + \
                ',' + ingredient_record.expiration_date + '</li>'
        ingredient_text += '</ul>'
        return ingredient_text
    except Exception as e:
        print(e)
        return 'Something is wrong'


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
