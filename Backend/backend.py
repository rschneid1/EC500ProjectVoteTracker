# Backend for VoteTracker application
# Manages the representatives user accounts and the polling data from the users
# Author: Ryan Schneider

# flask
from flask import Flask, redirect, url_for, request
from flask_restful import reqparse
import json

# mongo
from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client['VoteTracker']

#set up collections
polls = db['polls']
reps = db['reps']

app = Flask(__name__)

# define polls
Poll = {
    "_id": "",
    "username": "",
    "zip": "",
    "question": "",
    "options": [],
    "tally": []    
}

# reps
aRep = {
    "_id": "",
    "rep": "",
    "username": "",
    "password": "",
}

# Welcome function
@app.route('/vote', methods=['GET'])
def mainPageRender():
    if request.method == 'POST':
        user = request.form['nm']
    return 'Welcome to Vote Tracker!'


# create account
@app.route('/vote/create/rep', methods=['PUT'])
def create_account():
    parser = reqparse.RequestParser()
    parser.add_argument('rep' , type=str, required=True, help="must include full name ! \n")
    parser.add_argument('username' , type=str, required=True, help="username cannot be blank! \n")
    parser.add_argument('password' , type=str, required=True, help="password cannot be blank! \n")
    args = parser.parse_args()
    rep = args['rep']
    username = args['username']
    password = args['password']

    # check if user already exists
    tmpUser = reps.find_one({"rep": rep})
    # check if user name already exists
    print(username)
    usernameCheck = reps.find_one({"username": username})

    if (tmpUser == None) and (usernameCheck == None):
        # instantiate rep user
        newRep = aRep
        newRep['_id'] = rep
        newRep['rep'] = rep
        newRep['username'] = username
        newRep['password'] = password
        post_id = reps.insert_one(newRep).inserted_id
        print(post_id)
        return "User Created!"
    else:
        return "User already exists!"


# check if account and password combo exists
@app.route('/vote/check', methods=['PUT'])
def check_account():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="username cannot be blank! \n")
    parser.add_argument('password', type=str, required=True, help="password cannot be blank! \n")
    args = parser.parse_args()
    username = args['username']
    password = args['password']

    print(username)
    print(password)
    comboCheck = reps.find_one({"username": username, "password": password})

    if comboCheck == None:
        return "DNE"
    else:
        return "E"

# create a poll
@app.route('/vote/create/poll' , methods=['PUT'])
def create_poll():
    #parser = reqparse.RequestParser()
    #parser.add_argument('username', type=str, required=True,location='json', help="username cannot be blank! \n")
    #parser.add_argument('zip', type=str, required=True,location='json', help="zip cannot be blank! \n")
    #parser.add_argument('question', type=str, required=True,location='json', help="question cannot be blank! \n")
    #parser.add_argument('options', type=list, required=True, location='json',help="password cannot be blank! \n")
    #parser.add_argument('tally', type=list, required=True, location='json', help="password cannot be blank! \n")
    #args = parser.parse_args()
    args = request.get_json(force=True)
    print(args)
    username = args[0]['username']
    zipCode = args[0]['zipcode']
    question = args[0]['question']
    options = args[0]['options']
    tally = args[0]['tally']

    # check if user name exists
    check = reps.find_one({"username": username})
    
    # if not found
    if check == None:
        return "DNE"
    else:
        newPoll = Poll
        newPoll['_id'] = question + username
        newPoll['username'] = username
        newPoll['zip'] = zipCode
        newPoll['question'] = question
        newPoll['options'] = options
        newPoll['tally'] = tally

        print(question)
        print(username)
        print(zipCode)
        print(options)
        print(tally)

        post_id = polls.insert_one(newPoll).inserted_id
        print(post_id)
        return "E"


# username read all polls with that username
@app.route('/vote/poll/username', methods=['PUT','GET'])
def read_poll_username():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True,help="username cannot be blank! \n")
    args = parser.parse_args()
    username = args['username']

    listPolls = polls.find({'username': username})

    output = {}
    count = 0
    for x in listPolls:
        output[count] = x
        count = count + 1
        print(x['question'])

    if listPolls != None:
        return output
    elif listPolls == None:
        return "DNE"
    
# zip code read a poll
@app.route('/vote/poll/zip' , methods=['PUT'])
def read_poll_zipcode():
    parser = reqparse.RequestParser()
    parser.add_argument('zipcode', type=str, required=True,help="zipcode cannot be blank! \n")
    args = parser.parse_args()
    zipcode = args['zipcode']
    print(zipcode)

    listPolls = polls.find({'zip': zipcode})

    output = {}
    count = 0
    for x in listPolls:
        output[count] = x
        count = count + 1
        print(x['question'])

    if listPolls != None:
        return output
    elif listPolls == None:
        return "DNE"


# add vote to poll
@app.route('/vote/poll/update' , methods=['PUT'])
def add_vote_zipcode():
    parser = reqparse.RequestParser()
    parser.add_argument('zipcode', type=str, required=True,help="zipcode cannot be blank! \n")
    parser.add_argument('question', type=str, required=True,help="question cannot be blank! \n")
    parser.add_argument('index', type=int, required=True,help="index cannot be blank! \n")
    args = parser.parse_args()
    zipcode = args['zipcode']
    question = args['question']
    index = args['index']

    tmpPoll = polls.find_one({'zip': zipcode, 'question': question})

    if tmpPoll != None:
        # add one to the tally index of that array
        newQuery = { 'zip': zipcode, 'question': question}
        # add one to index
        tmpPoll['tally'][index] = tmpPoll['tally'][index] + 1
        newValues = {"$set" : {'tally': tmpPoll['tally'] } }
        polls.update_one(newQuery, newValues)
        return "E"
    elif tmpPoll == None:
        return "DNE"


if __name__ == '__main__':
    app.run()

