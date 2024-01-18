from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from openai import OpenAI
import json
from firebase_admin import credentials, firestore, initialize_app
import base64
import  firebase_admin
app = Flask(__name__)
app.config['SECRET_KEY'] = 'foodie'
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
encoded_creds = os.getenv('FIREBASE_CREDENTIALS_BASE64')

decoded_creds = base64.b64decode(encoded_creds)

cred = credentials.Certificate(json.loads(decoded_creds))
initialize_app(cred)

db = firestore.client()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        user_data = user.to_dict()
        return User(id=user_id, name=user_data['name'], email=user_data['email'], password=user_data['password'])
    return None


@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_ref = db.collection('users').document(email)
        user = user_ref.get()

        if not user.exists or not check_password_hash(user.to_dict()['password'], password):
            flash('Sprawdź swoje dane logowania i spróbuj ponownie.')
            return redirect(url_for('login'))

        user_data = user.to_dict()
        user_obj = User(id=user.id, name=user_data['name'], email=user_data['email'], password=user_data['password'])
        login_user(user_obj)
        return redirect(url_for('dashboard'))

    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user_ref = db.collection('users').document(email)
        user = user_ref.get()

        if user.exists:
            flash('Email już istnieje.')
            return redirect(url_for('signup'))

        user_ref.set({
            'name': name,
            'email': email,
            'password': generate_password_hash(password)
        })

        return redirect(url_for('login'))

    return render_template('signup.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)


@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    diet_plan = []
    data = request.json

    ingredients = data.get('ingredients')
    selected_day = data.get('day')
    selected_meal = data.get('meal')
    selected_calories = data.get('calories')
    dietary_requirements = data.get('dietary')

    for i in range(0, int(selected_day)):

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f'''Based on the provided data, please create a detailed meal plan for one day. It should contain {selected_meal} meals, 
                                with a total calorie count of about {selected_calories} kcal. All recipes must comply with dietary requirements: {dietary_requirements}, 
                                and use only ingredients from the list: {ingredients}. Please ensure that each meal includes information about its calorie content, 
                                precise units of measurement, and conversions to common kitchen measurement systems (spoon, glass, teaspoon). 
                                Please diversify the meals with a detailed description of ingredients, their quantities, and method of preparation, 
                                taking into account the proportions of macronutrients. Each meal should be balanced and matched to the calorie content. 
                                I want the full number of meals to be included in the response without repetition and without abbreviation. 
                                Please write just the plan, without any comments from yourself and do not use markdown. The key in the JSON should be 'day' and the values 
                                should be correspondingly numbered 'meal'. Each 'meal' should contain the following information: title, calories, ingredients, preparation, macros. 
                                Do not use any ingredients that is not on this list: {ingredients}.'''
                }
            ],
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"}
        )
        diet_plan.append(response.choices[0].message.content.strip())

    print(diet_plan)
    session['diet_plan_display'] = diet_plan
    session['diet_plan_download'] = diet_plan
    session['diet_plan_save'] = diet_plan
    return jsonify({'success': True})


@app.route('/recipes')
@login_required
def show_recipes():
    diet_plan_display_json = session.get('diet_plan_display', [])
    diet_plan_display = [json.loads(plan) for plan in diet_plan_display_json]
    
    return render_template('recipes.html', diet_plan=diet_plan_display)


@app.route('/download-diet-plan/<name>')
@login_required
def download_diet_plan(name):
    diet_plan_download = session.get('diet_plan_download', [])

    if not diet_plan_download:
        return "No diet plan available for download", 404

    diet_plan = [json.loads(plan) for plan in diet_plan_download]

    diet_plan_text = ""

    for day_plan in diet_plan:
        for meal_number, meal in day_plan['day'].items():
            diet_plan_text += f"Recipe Title: {meal['title']}\n"
            diet_plan_text += f"Calories: {meal['calories']}\n"
            diet_plan_text += "Ingredients:\n"
            for ingredient, quantity in meal['ingredients'].items():
                diet_plan_text += f"- {ingredient}: {quantity}\n"
            diet_plan_text += "Preparation:\n"
            diet_plan_text += f"{meal['preparation']}\n\n"

    print("Diet plan text:", diet_plan_text)

    response = make_response(diet_plan_text)
    response.headers["Content-Disposition"] = f"attachment; filename={name}.txt"
    response.headers["Content-type"] = "text/plain"
    return response


@app.route('/save-diet-plan', methods=['POST'])
@login_required
def save_diet_plan():
    data = request.json
    plan_name = data.get('name', 'diet')
    user_id = current_user.id

    diet_plan_save = session.get('diet_plan_save', [])

    if not diet_plan_save:
        return "No diet plan available for saving", 404

    diet_plan = [json.loads(plan) for plan in diet_plan_save]

    diet_plan_text = ""

    for day_plan in diet_plan:
        for meal_number, meal in day_plan['day'].items():
            diet_plan_text += f"Recipe Title: {meal['title']}\n"
            diet_plan_text += f"Calories: {meal['calories']}\n"
            diet_plan_text += "Ingredients:\n"
            for ingredient, quantity in meal['ingredients'].items():
                diet_plan_text += f"- {ingredient}: {quantity}\n"
            diet_plan_text += "Preparation:\n"
            diet_plan_text += f"{meal['preparation']}\n\n"


    diet_plan_ref = db.collection('users').document(user_id).collection('diet_plans').document(plan_name)
    diet_plan_ref.set({
        'plan': diet_plan
    })

    return jsonify({'success': 'Diet plan saved successfully'})


@app.route('/get-recipes')
@login_required
def get_recipes():
    user_id = current_user.id
    diet_plans = db.collection('users').document(user_id).collection('diet_plans').stream()

    recipes = [{"id": diet_plan.id, "name": diet_plan.id} for diet_plan in diet_plans]
    return jsonify(recipes)


@app.route('/delete-recipe/<int:id>', methods=['POST'])
@login_required
def delete_recipe(id):
    user_id = current_user.id
    db.collection('users').document(user_id).collection('diet_plans').document(str(id)).delete()
    return jsonify({'success': True})


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


@app.route('/account-settings')
@login_required
def account_settings():
    return render_template('account_settings.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
