import os
from flask import render_template, request, json, jsonify
import requests, asyncio

from app import app


async def fetch_recipe(username, password, selected_vegan, selected_gluten_free, selected_lactose_free):
    session = requests.Session()
    session.post('https://cloud.mindsdb.com/cloud/login', json={
        'email': username,
        'password': password
    })
   
    custom_query = " "
    if selected_gluten_free is not False:
        custom_query += "gluten free " 
    if selected_lactose_free is not False:
        custom_query += "lactose free "
    if selected_vegan is not False:
        custom_query += "vegan "

    
    if custom_query == " ":
        query = "SELECT answer FROM mindsdb.recipemaster6 WHERE question = 'Start your response with the sentence Hola Amigo !  Do not add salutations or anything else to your response. Behave like a chef who knows a ton of different recipes. You are responding to an audience that is looking to loose weight. Now suggest me just one new recipe each time I ask you, in the form of bullet points, that is healthy and easy to cook?';"
    else:
         query = "SELECT answer FROM mindsdb.recipemaster6 WHERE question = 'Start your response with the sentence Hola Amigo !  Do not add salutations or anything else to your response. Behave like a chef who knows a ton of different recipes. You are responding to an audience that is looking to loose weight. Now suggest me just one new " + custom_query +  " recipe each time I ask you, in the form of bullet points, that is healthy and easy to cook?';"
    resp = session.post('https://cloud.mindsdb.com/api/sql/query', json={'query': query})
    
    json_response = resp.json()
    
    # Assuming there's only one element in the inner list
    data_value = json_response['data'][0][0]  
    
    # Remove special characters from start and end
    data_value = data_value.strip('[\n]').strip()

    #Debug and print value
    #print(data_value2)

    if resp.status_code == 200:
        return data_value
    else:
        return 'Error fetching recipe'
    
async def fetch_calories(username, password):
    session = requests.Session()
    session.post('https://cloud.mindsdb.com/cloud/login', json={
        'email': username,
        'password': password
    })
    food_item_to_check = request.form['food_item']
    custom_query = "SELECT answer FROM mindsdb.recipemaster6 WHERE question = 'answer in exactly this format: It has xx calories. This is the question: What are the number of calories in an average sized" + food_item_to_check +"?';"
    
    query_calories = custom_query
    resp_calories = session.post('https://cloud.mindsdb.com/api/sql/query', json={'query': query_calories})

    json_response_calories = resp_calories.json()

    #if 'data' in json_response_calories and json_response_calories['data']:
    data_value_calories = json_response_calories['data'][0][0]

    # Remove special characters from start and end
    data_value_calories = data_value_calories.strip('[\n]').strip()

    # Debug and print value
    #print(data_value_calories)

    if resp_calories.status_code == 200:
        return data_value_calories
    else:
        return 'Error fetching calories'

async def fetch_plans(username, password, flag):
    session = requests.Session()
    session.post('https://cloud.mindsdb.com/cloud/login', json={
        'email': username,
        'password': password
    })
    if flag == 1:
        plan = "45 days"
    if flag == 2:
        plan = "90 days"
    if flag == 3:
        plan = "180 days"    
        
    custom_query = "SELECT answer FROM mindsdb.recipemaster6 WHERE question = 'Act as an expert health coach who has helped many people lose weight naturally through exercises and proper diet routines. answer in pointwise format, starting your sentence with: Hola Amigo! This is the question: Give me a good transformation plan if my goal is to complete it in " + plan + " days?';"
    resp = session.post('https://cloud.mindsdb.com/api/sql/query', json={'query': custom_query})
    
    json_response = resp.json()
    
    # Assuming there's only one element in the inner list
    transformation_plan = json_response['data'][0][0]  
    
    # Remove special characters from start and end
    transformation_plan = transformation_plan.strip('[\n]').strip()

    #Debug and print value
    #print(transformation_plan)

    if resp.status_code == 200:
        return transformation_plan
    else:
        return 'Error fetching your customised plan'


def read_env_vars():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_file_directory, 'env_vars.txt')

    username = None
    password = None

    with open(env_file_path) as file:
        for line in file:
            key, value = line.strip().split('=')
            if key == 'USERNAME':
                username = value
            elif key == 'PASSWORD':
                password = value

    return username, password

def calculate_bmi(sex, weight, height):
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    rounded_bmi = round(bmi, 1)
    print(bmi)
    if bmi < 18.5:
        category = 'Underweight'
    elif bmi < 24.9:
        category = 'Normal weight'
    elif bmi < 29.9:
        category = 'Overweight'
    else:
        category = 'Obese'
    
    return rounded_bmi, category

@app.route('/aiassistant')
def aiassistant():
    # Your code for this route
    return render_template('chat.html')

@app.route('/send', methods=['POST'])
async def send_message():
    print(f"Request Form: {request.form}")  # Debugging line
    print(f"Request Form: {request.form}")
    user_message = request.json.get('user_message')
    print(f"Received user message: {user_message}")


    if user_message:
        print(f"User input received: {user_message}")  # Debugging line

        try:
            # Await the query_mindsdb function asynchronously
            bot_response = await query_mindsdb(user_message)
            
            # Return the bot's response as JSON
            return jsonify({"bot_response": bot_response})

        except Exception as e:
            # Handle any exceptions that might occur during the query
            return jsonify({"error": str(e)})
    
    else:
        # Handle the case when user_message is empty (no input provided)
        return jsonify({"error": "No user input provided"})

def setup_mindsdb_session():
    try:
        username, password = read_env_vars()
        session = requests.Session()
        response = session.post('https://cloud.mindsdb.com/cloud/login', json={
           'email': username,
           'password': password
        })

        # Check if the login was successful 
        if response.status_code == 200:
            return session
        else:
            # Log an error message or raise an exception if login fails
            print(f"Login failed with status code: {response.status_code}")
            return "Login failed with status code"
    except requests.exceptions.RequestException as e:
        # Handle connection or request errors here
        print(f"An error occurred during login: {e}")
        return "An error occurred during login"

    
async def query_mindsdb(user_message):
    session = setup_mindsdb_session()
    if session is not None:
        test = user_message
        print(test)
        custom_query = "SELECT answer FROM mindsdb.recipemaster6 WHERE question = '" + user_message +"?';"
        resp_calories = session.post('https://cloud.mindsdb.com/api/sql/query', json={'query': custom_query})
        print(resp_calories)
        if resp_calories.status_code == 200:
            chat_bot_response = resp_calories.json()
            print(chat_bot_response)
            if 'data' in chat_bot_response and chat_bot_response['data']:
                data_value_calories = chat_bot_response['data'][0][0]
                # Remove special characters from start and end
                data_value_calories = data_value_calories.strip('[\n]').strip()
                return data_value_calories
            else:
                return 'No data found'  # Handle the case when there's no valid response
        else:
            # Log the error for debugging
            print(f"API Error: Status Code {resp_calories.status_code}")
            return 'Error fetching data'  # Handle the case when there's an API error
    else:
        return 'Session setup failed'  # Handle the case when session setup fails

@app.route('/', methods=['GET', 'POST'])
def index():

    bmi = None
    category = None

    if request.method == 'POST':

        if 'sex' in request.form and 'weight' in request.form and 'height' in request.form:
            sex = request.form['sex']
            weight = float(request.form['weight'])
            height = float(request.form['height'])
            
            bmi, category = calculate_bmi(sex, weight, height)

        username, password = read_env_vars()

        if username is None or password is None:
            return "Credentials not found."

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        recipe_response = None
        calories_response = None
        transformation_response = None
        flag = 0

        if 'recipe_button' in request.form:
            selected_vegan = 'vegan' in request.form
            selected_gluten_free = 'gluten_free' in request.form
            selected_lactose_free = 'lactose_free' in request.form
            recipe_response = loop.run_until_complete(fetch_recipe(username, password, selected_vegan, selected_gluten_free, selected_lactose_free))
        elif 'calories_button' in request.form:
            calories_response = loop.run_until_complete(fetch_calories(username, password))
        elif '45_day_challenge' in request.form:
            flag = 1
            transformation_response = loop.run_until_complete(fetch_plans(username, password, flag))
        elif '90_day_challenge' in request.form:
            flag = 2
            transformation_response = loop.run_until_complete(fetch_plans(username, password, flag))
        elif '180_day_challenge' in request.form:
            flag = 3
            transformation_response = loop.run_until_complete(fetch_plans(username, password, flag))

        loop.close()

        return render_template('index.html', bmi=bmi, category=category, recipe_response=recipe_response, calories_response=calories_response, transformation_response=transformation_response)

    return render_template('index.html', recipe_response=None, calories_response=None, transformation_response=None)

