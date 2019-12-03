# /index.py
from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher
import mysql.connector

app = Flask(__name__)

# run Flask app
if __name__ == "__main__":
    app.run()

# default route
@app.route('/')
def index():
    return 'Hello World!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    params = data['queryResult']['parameters']
    intentName = data['queryResult']['intent']['displayName']
    # actualQuestion = data['queryResult']['queryText']
    if intentName == "birthdayEmployee-designation/name_with_time":
        response = runBdayNameTime(params['date'])
    elif intentName == "birthdayEmployee-designation/name_with_timeperiod":
        endDate = params['date-period']['endDate']
        startDate = params['date-period']['startDate']
        response = runQuery(startDate,endDate)
    reply = {
        "response": "reposnding from server weee!",
        "fulfillmentText": "Fetching results",
        "fulfillmentMessages": [{
            "text": {
                "text": [response]
            }
        }]
    }
    return jsonify(reply)

def runQuery(startDate, endDate):
    mydb = mysql.connector.connect(
    host="hr.clurfavlxnya.us-west-2.rds.amazonaws.com",
    user="admin",
    passwd="1amAdmin",
    database="hr"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM hr.Employee where month(birthDate) between month('" + startDate + "') and month('" + endDate + "') and dayofmonth(birthDate) between dayofmonth('" + startDate + "') and dayofmonth('" + endDate + "')")

    myresult = mycursor.fetchall()
    response = ""
    for x in myresult:
        print(x)
        response += x[1] + " " + x[2] + " "
    return response

def runBdayNameTime(bday):
    mydb = mysql.connector.connect(
    host="hr.clurfavlxnya.us-west-2.rds.amazonaws.com",
    user="admin",
    passwd="1amAdmin",
    database="hr"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT first_name,last_name,birthDate FROM hr.Employee where month(birthDate) like month('" + bday + "') and dayofmonth(birthDate) like dayofmonth('" + bday + "');")

    myresult = mycursor.fetchall()
    response = ""
    for x in myresult:
        print(x)
        response += x[0] + " " + x[1] + " "
    return response