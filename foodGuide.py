from flask import Flask, render_template, request, Markup

import json
import re
import random
import os

app = Flask(__name__)

# os-independent path to files
dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

# filenames for the data
FOODGROUPS_DATA = os.path.join(dir_path, 'foodgroups-en.json')
FOODS_DATA = os.path.join(dir_path, 'foods-en.json')
SERVINGS_PER_DAY_DATA = os.path.join(dir_path, 'servings_per_day-en.json')


@app.route('/')
def index():
    """*****************************************************************
        The main page
    *****************************************************************"""

    return render_template("index.html", ages_list=get_age_categories())


@app.route('/foodguide')
def foodguide():
    """*****************************************************************
        display results to user
    *****************************************************************"""

    # get form data
    gender = request.args.get('gender')
    age_range = request.args.get('age_range')

    # dictionary of food groups - {fgid: foodgroup}
    food_groups = get_food_group_names()

    # dictionary of servings for age and gender specified - {fgid: serving}
    servings = get_serving_per_fg(gender, age_range)

    # get random list of food items -
    foods_list = get_foods_list(servings)

    return render_template("foodguide.html",
                           food_group=food_groups,
                           servings=servings,
                           foods_list=foods_list,
                           gender=gender,
                           age_range=age_range)


def get_age_categories():
    """*****************************************************************
        Extract list of age categories from data
    *****************************************************************"""

    # first clean the data
    lst = clean_json(SERVINGS_PER_DAY_DATA)

    # build list for return
    age_categories = []
    for key in lst:
        if key['ages'] not in age_categories:
            age_categories.append(key['ages'])

    return age_categories


def clean_json(json_data_file):
    """*****************************************************************
        Remove initial text from JSON and return the remaining list
        Accepts a file of JSON
        e.g. {'text_to_remove':[{data_to_return}]}
    *****************************************************************"""

    # get the data
    json_data = json.load(open(json_data_file))

    # build list for return
    lst = []
    for items in json_data:
        lst = json_data[items]

    return lst


def get_foods_list(servings_per_fg):
    """*****************************************************************
        accepts: servings_per_fg - {fgid: serving}
        returns: randomized dictionary in the format of fgid:[{srvg_sz:food}]
    *****************************************************************"""

    # build dictionary for return
    foods_by_fg = {}
    for fg in servings_per_fg:
        num_foods = highest_value(servings_per_fg[fg])
        foods = get_num_foods(fg, num_foods)
        foods_by_fg.update({fg: foods})

    return foods_by_fg


def get_num_foods(fgid, num_foods):
    """*****************************************************************
    Accepts a food group id, and number of (randomized) food items
        to retrieve in that food group
        e.g.  [{'food', 'srvg_sz'},...,{'food_n', 'srvg_sz_n'}]
    *****************************************************************"""

    # get the records
    food_records = clean_json(FOODS_DATA)

    # first get all foods in food group for indexing below
    foods_lst = []
    for f in food_records:
        if ((f['fgid']) == fgid or (f['fgid'] == 'da' and fgid == 'mi')):  # the JSON has 'da' where it should be 'mi' ??
            d = {f['food']: f['srvg_sz']}  # make a dictionary record
            foods_lst.append(d)  # add to list

    # obtain a dictionary of random values (in number specified) from list above
    random_list = random.sample(range(len(foods_lst)), num_foods)

    # build list of {'food':'serving_size'} pairs for return in size specified
    final_list = []
    for i in random_list:
        final_list.append(foods_lst[i])

    return final_list


def highest_value(serving_sz):
    """*****************************************************************
        extract largest integer in a string
        okay to pass an integer
    *****************************************************************"""

    # extract to list - all integer instances for string
    sz = [int(s) for s in re.findall(r'\d+', str(serving_sz))]

    # sort the list to find the biggest one
    if len(sz) > 1:
        sz.sort()
        return sz[-1]
    else:  # there was only one value, so return it
        return sz[0]


def get_food_group_names():
    """*****************************************************************
        get names of all the food groups from file
        return list of food groups by fgid
        e.g. {'fgid': 'foodgroup_name"}
    *****************************************************************"""

    # clean the data
    all_food_groups = clean_json(FOODGROUPS_DATA)

    # build list of food groups
    food_groups = {}
    for fg in all_food_groups:
        food_groups.update({fg['fgid']: fg['foodgroup']})

    return food_groups


def get_serving_per_fg(gender, ages):
    """*****************************************************************
        from the gender and age categories, get recommended servings
        e.g. {'fgid': 'servings'}
    *****************************************************************"""

    # first clean the data
    all_servings = clean_json(SERVINGS_PER_DAY_DATA)

    # return dictionary of servings per food group
    servings_per_fg = {}
    for fg in all_servings:
        if fg['gender'] == gender and fg['ages'] == ages:
            servings_per_fg.update({fg['fgid']: fg['servings']})

    return servings_per_fg


if __name__ == '__main__':
    app.run(debug=True)
