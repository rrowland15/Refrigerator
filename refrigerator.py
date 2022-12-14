from flask import Flask, request, render_template, url_for, redirect
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import config
import requests





# We are not using this sqlconnection but this line just creates a sqlite db file
sqlconnection = sqlite3.connect('recipes.db')

app = Flask(__name__)


db_name = 'recipes.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.debug = True


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Ingredients(db.Model):
    __tablename__ = 'ingredients_table'
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String, unique=True)
    expiration_date = db.Column(db.Date)

    def __init__(self, ingredient, expiration_date):
        self.ingredient = ingredient
        if (type(expiration_date) != datetime):
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
        self.expiration_date = expiration_date


def missing_ingredients_not_in_db(api_missing_ingredients_set):
    """ This function takes in the missing ingredients from the api in a set
    and removes ingredients which overlap with the records in the database
    """
    with app.app_context():
        db_ingredients = Ingredients.query.order_by(Ingredients.expiration_date)
        ingredient_name_set = set()
        for ingredient_entry in db_ingredients:
            ingredient_name_set.add(ingredient_entry.ingredient)
        print(ingredient_name_set)
        test_missed_ingredient_set = api_missing_ingredients_set
        truly_missing_ingredients = test_missed_ingredient_set.difference(ingredient_name_set)
        return truly_missing_ingredients




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


# remove all ingredients that have expired
@app.route("/removeExpired", methods=["POST", "GET"])
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
            ingredients = Ingredients.query.order_by(
                Ingredients.expiration_date)
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
    postfix_url = "&number=1&ignorePantry=true&apiKey=" + config.api_key

    ingredients = Ingredients.query.order_by(Ingredients.expiration_date)

    def callFirstNFoods(n):
        search_q = ""
        for i in range(n):
            search_q += ingredients[i].ingredient
            if (i < n - 1):
                search_q += ",+"
        return search_q

    # call for first n expiring foods
    if (len(Ingredients.query.all()) >= 3):
        search_q = callFirstNFoods(3)
    elif (len(Ingredients.query.all()) > 0):
        search_q = callFirstNFoods(1)
    else:  # if fridge is empty
        search_q + "eggs"


    get_url = base_url + search_q + postfix_url
    api_response = requests.get(get_url).content
    api_dict_object = json.loads(api_response)
    recipe_id = api_dict_object[0]["id"]
    title = api_dict_object[0]["title"]
    recipe_image = api_dict_object[0]["image"]
    potential_missed_ingredients_dict_list = api_dict_object[0]["missedIngredients"]

    potential_missed_ingredients = set()
    potential_missed_ingredients_jpgs = []

    for ingredient_dict in potential_missed_ingredients_dict_list:
        name = ingredient_dict["name"]
        potential_missed_ingredients.add(name)


    potential_missed_ingredients_set = missing_ingredients_not_in_db(potential_missed_ingredients)
    potential_missed_ingredient_count = len(potential_missed_ingredients_set)

    potential_missed_ingredients = '<span>'

    ingredient_counter = 0
    for ingredient_string in potential_missed_ingredients_set:
        if ingredient_counter != potential_missed_ingredient_count - 1:
            potential_missed_ingredients += ingredient_string + ", " + "</span>"
            ingredient_counter += 1
        else:
            potential_missed_ingredients += ingredient_string + "</span>"
            ingredient_counter += 1


    for ingredient_dict in potential_missed_ingredients_dict_list:
        image = ingredient_dict["image"]
        potential_missed_ingredients_jpgs.append(image)

    recipe_url_prefix = "https://api.spoonacular.com/recipes/"
    recipe_url_postfix = "/card?apiKey=" + config.api_key
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



if __name__ == "__main__":
    app.run()
