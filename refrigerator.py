from flask import Flask, request, render_template, url_for, redirect
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
#import config
import requests

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
    expiration_date = db.Column(db.Date)

    def __init__(self, ingredient, expiration_date):
        self.ingredient = ingredient
        if (type(expiration_date) != datetime):
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
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


#remove all ingredients that have expired 
@app.route("/removeExpired", methods = ["POST", "GET"])
def removeExpired():
    now = datetime.now()
    Ingredients.query.filter(Ingredients.expiration_date < now).delete()
    db.session.commit() 
    return redirect(url_for('myfridge'))


# To navigate to the Fridge page
@app.route("/myfridge", methods=['GET'])
def myfridge():
    if request.method == 'POST':
        pass
    else:
        try:
            # show up in order of expiring first to last
            ingredients = Ingredients.query.order_by(Ingredients.expiration_date)
            content = ''
            for ingredient_record in ingredients:
                content += ingredient_record.ingredient + "&emsp;" + \
                    ingredient_record.expiration_date.strftime(
                        '%m-%d-%y') + "<br>"
            return render_template("fridgeinventory.html", content=content)

        except Exception as e:
            print(e)
            return 'Something is wrong'


# To navigate to the recipe.html page
@app.route("/recipe", methods=['GET'])
def recipe():
    base_url = "https://api.spoonacular.com/recipes/findByIngredients?ingredients="
    postfix_url = "&number=1&ignorePantry=true&apiKey=291bc42edd5b45fca7c83089d1f1da9b"
    temporary = "orange,+banana"

    # real call for first n expiring foods
    n = 3
    ingredients = Ingredients.query.order_by(Ingredients.expiration_date)
    search_q = ""
    for i in range(n):
        search_q += ingredients[i].ingredient
        if (i < n - 1):
            search_q += ",+"

    #get_url = base_url + temporary + postfix_url
    get_url = base_url + search_q + postfix_url
    api_response = requests.get(get_url).content
    api_dict_object = json.loads(api_response)
    print(api_dict_object)
    recipe_id = api_dict_object[0]["id"]
    title = api_dict_object[0]["title"]
    recipe_image = api_dict_object[0]["image"]
    potential_missed_ingredient_count = api_dict_object[0]["missedIngredientCount"]
    potential_missed_ingredients_dict_list = api_dict_object[0]["missedIngredients"]
    potential_missed_ingredients = []
    potential_missed_ingredients_jpgs = []
    for ingredient_dict in potential_missed_ingredients_dict_list:
        name = ingredient_dict["originalName"]
        potential_missed_ingredients.append(name)

    for ingredient_dict in potential_missed_ingredients_dict_list:
        image = ingredient_dict["image"]
        potential_missed_ingredients_jpgs.append(image)

    # Build the recipe card https://api.spoonacular.com/recipes/634206/card?apiKey=291bc42edd5b45fca7c83089d1f1da9b
    recipe_url_prefix = "https://api.spoonacular.com/recipes/"
    recipe_url_postfix = "/card?apiKey=291bc42edd5b45fca7c83089d1f1da9b"
    recipe_url = recipe_url_prefix + str(recipe_id) + recipe_url_postfix
    api_card = json.loads(requests.get(recipe_url).content)["url"]

    return render_template("recipe.html", title=title, recipe_image=recipe_image, potential_missed_ingredient_count=potential_missed_ingredient_count, potential_missed_ingredients=potential_missed_ingredients, recipe_card=api_card)


# To navigate to the about.html page


@app.route("/about", methods=['GET'])
def about():
    if request.method == 'POST':
        pass
    return render_template("about.html")


# For database printing purposes (to print out the data currently in the database): delete decorator and function after done with the project
# make sure to add "/database" to the url
@app.route("/database", methods=['GET'])
def database():
    try:
        ingredients = Ingredients.query.order_by(Ingredients.expiration_date)
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
