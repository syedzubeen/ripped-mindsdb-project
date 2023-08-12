import os
from flask import render_template, request, json, jsonify
import requests, asyncio

from app import app


async def fetch_recipe(username, password):
    session = requests.Session()
    session.post('https://cloud.mindsdb.com/cloud/login', json={
        'email': username,
        'password': password
    })

    query = "SELECT answer FROM mindsdb.recipemaster6 WHERE question = 'Start your response with the sentence Hola Amigo !  Do not add salutations or anything else to your response. Behave like a chef who knows a ton of different recipes. You are responding to an audience that is looking to loose weight. Now suggest me just one new recipe each time I ask you, in the form of bullet points, that is healthy and easy to cook?';"
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
    print(data_value_calories)

    if resp_calories.status_code == 200:
        return data_value_calories
    else:
        return 'Error fetching calories'


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


@app.route('/', methods=['GET', 'POST'])
def index():


    if request.method == 'POST':


        username, password = read_env_vars()

        if username is None or password is None:
            return "Credentials not found."

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        recipe_response = None
        calories_response = None

        if 'recipe_button' in request.form:
            recipe_response = loop.run_until_complete(fetch_recipe(username, password))
        elif 'calories_button' in request.form:
            calories_response = loop.run_until_complete(fetch_calories(username, password))

        loop.close()

        return render_template('index.html', recipe_response=recipe_response, calories_response=calories_response)

    return render_template('index.html', recipe_response=None, calories_response=None)

