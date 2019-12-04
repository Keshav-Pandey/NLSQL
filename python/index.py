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
	''' webhook function accepts the JSON from dialogflow
	that contains the necessary parameters for query
	execution. 
	The type of query template used is dependent upon 
	the intent and the parameters obtained form that 
	itent.'''
	
	data = request.get_json(silent=True)
	
	#extracting parameters
	params = data['queryResult']['parameters']
	intentName = data['queryResult']['intent']['displayName']
	
	# BIRTHDAYS
	
	#-----------------------------------------------------------------------------------------------
    #birthdayEmployee-designation/name_with_time
	#-----------------------------------------------------------------------------------------------
	if intentName == "birthdayEmployee-designation/name_with_time":
		# extracting parameters
		name = params['given-name']
		
		# removing apostrophes
		if("'" in name):
			name = name[:-2]
			
		# job title
		title = params['title']
		
		# if its a aggregation query
		countIndicator = params['countIndicator']
		
		# date for birthday, in this case it is always a singular date
		date = params['date']
		
		#-----------------------------------------------------------------------------------------------
		# non-aggregate queries
		#-----------------------------------------------------------------------------------------------
		if(countIndicator==''):
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				if(len(str(response))==0):
					response = 'No '+title+"/s have birthdays on the specified time."
				else:
					response = 'Here is a list of '+title+'/s with birthday/s in the specified time ' + response.replace(")","").replace(",","").replace("(","")
					
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E \
								  WHERE (first_name=('" + name + "') OR last_name=('" + name + "'))  \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				if(len(str(response))==0):
					response = name+" does not have his/her birthday on the specified time."
				else:
					response = 'Yes '+name+' birthday is on the specified time'
					
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				if(len(str(response))==0):
					response = title + " " + name + " does not have his/her birthday on the specified time."
				else:
					response = title + " " + name + " has his/her birthday on the specified time"
		#-----------------------------------------------------------------------------------------------
		# aggregation queries
		#-----------------------------------------------------------------------------------------------
		else:
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
		
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "'))  \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# both title and name are not given but time is specified	
			elif(title=='' and name==''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
	
	#-----------------------------------------------------------------------------------------------
	#birthdayEmployee-designation/name_with_timeperiod
	#-----------------------------------------------------------------------------------------------
	elif intentName == "birthdayEmployee-designation/name_with_timeperiod":
	
		# extracting parameters
		name = params['given-name']
		
		# the start period for birthdays
		endDate = params['date-period']['endDate']
		
		# the end period for birthdays
		startDate = params['date-period']['startDate']
		
		# removing apostrophes
		if("'" in name):
			name = name[:-2]
			
		# job title
		title = params['title']
		
		# if its a aggregation query
		countIndicator = params['countIndicator']
		
		#-----------------------------------------------------------------------------------------------
		# non-aggregate queries
		#-----------------------------------------------------------------------------------------------
		if(countIndicator==''):
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				if(len(str(response))==0):
					response = 'No '+title+"/s have birthdays in the specified time period."
				else:
					response = 'Here is a list of '+title+'/s with birthday/s in the specified time period ' + response.replace(")","").replace(",","").replace("(","")
					
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				if(len(str(response))==0):
					response = name+" does not have his/her birthday in the specified time period."
				else:
					response = 'Yes '+name+' birthday is in the specified time period'
					
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				if(len(str(response))==0):
					response = title + " " + name + " does not have his/her birthday in the specified time period."
				else:
					response = title + " " + name + " has his/her birthday in the specified time period"
					
		#-----------------------------------------------------------------------------------------------	
		# aggregation queries
		#-----------------------------------------------------------------------------------------------
		else:
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
		
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# when neither name nor title are given but a time period is given 
			elif(title=='' and name==''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND month(birthDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(birthDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
	
	#-----------------------------------------------------------------------------------------------
	# birthdayEmployee-no_time
	#-----------------------------------------------------------------------------------------------
	elif intentName == "birthdayEmployee-no_time":
		# extracting parameters
		name = params['given-name']
		
		# removing apostrophes
		if("'" in name):
			name = name[:-2]
			
		# job title
		title = params['title']
		
		# if title is given and no name
		if(name=='' and title!=''):
			response = dbRun("SELECT birthDate \
								FROM Employee E, Title T \
								WHERE E.id = T.empID \
									  AND title=('" + title + "');")
			
			response = "List of birthdates having title as " + name + " is " + response
		
		# if the name is given and no title
		elif(name!='' and title==''):
			response = dbRun("SELECT birthDate \
								FROM Employee E \
								WHERE first_name=('" + name + "') OR last_name=('" + name + "');")
			response = "List of birthdates having names as " + name + " is " + response
			
		# if both name and title are given
		elif(name!='' and title!=''):
			response = dbRun("SELECT birthDate \
								FROM Employee E, Title T \
								WHERE E.id = T.empID \
								AND first_name=('" + name + "') OR last_name=('" + name + "') \
								AND title=('" + title + "');")
			response = "Employess with title "+title+" and names "+ name +" is/are born on "+response
	
	# TRAINING
	elif intentName == "trained_or_not":
	# extracting parameters
		name = params['given-name']
		
		# removing apostrophes
		if("'" in name):
			name = name[:-2]
			
		# job title
		title = params['title']
		
		# type of training
		training = params['event']
		
		# negator, in case the HR needs a list of those who
		# have not been trained yet
		negator = params['negator'] 
		
		# if its a aggregation query
		countIndicator = params['countIndicator']
		
		#-----------------------------------------------------------------------------------------------
		# non-aggregate queries
		#-----------------------------------------------------------------------------------------------
		if(countIndicator==''):
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT first_name, last_name \
									FROM Employee E, training t, Title T  \
									WHERE E.id=T.empID \
											AND T.empID = t.empID \
											AND title=('" + title + "') \
											AND Type=('" + training + "');")

					
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
									FROM Employee E, training t \
									WHERE E.id=t.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND Type=('" + training + "');")
				if(len(str(response))!=0):
					response = 'Yes, '+name+' has '+training+' training.'
				else:
					response = 'No, '+name+' does not have '+training+' training.'
					
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
									FROM Employee E, training t, Title T \
									WHERE E.id=t.empID \
										AND E.id = T.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND title=('" + title + "') \
										AND Type=('" + training + "');")
				if(len(str(response))!=0):
					response = 'Yes, '+title+' '+name+' has '+training+' training.'
				else:
					response = 'No, '+title+' '+name+' does not have '+training+' training.'
			
			# when neither name nor title are given but a training type is given
			elif(title=='' and name==''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, training t \
								  WHERE E.id=t.empID \
										AND Type=('" + training + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
		#-----------------------------------------------------------------------------------------------
		# aggregate queries: type 1 where we ask for those who are trained
		#-----------------------------------------------------------------------------------------------
		if(countIndicator!='' and negator==''):
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, training t, Title T  \
								  WHERE E.id=T.empID \
										AND T.empID = t.empID \
										AND title=('" + title + "') \
										AND Type=('" + training + "');")
				if((response).replace(")","").replace(",","").replace("(","")!=0):
					response = (response).replace(")","").replace(",","").replace("(","") + " " + title + " has/have " + training + " training"
				else:
					response = "None of the "+title+"s have "+training+" training"
			
			# when neither name nor title are given but a training type is given
			elif(title=='' and name==''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, training t \
								  WHERE E.id=t.empID \
										AND Type=('" + training + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				if((response).replace(")","").replace(",","").replace("(","")!=0):
						response = (response).replace(")","").replace(",","").replace("(","") + " employee has/have " + training + " training"
				else:
					response = "None of the employees have "+training+" training"
				
		#-----------------------------------------------------------------------------------------------
		# aggregate queries: type 2 where we ask for those who are "not" trained
		#-----------------------------------------------------------------------------------------------
		## !!! THE QUERY NEEDS TO BE FIXED FOR THIS PART TO WORK !!!
		# if(countIndicator!='' and negator!=''):
			# # the title is given but no name
			# if(name=='' and title!=''):
				# response = dbRun("SELECT COUNT(*) FROM ( \
													# SELECT TEMP.id \
													# FROM ( \
															# SELECT first_name, last_name, id FROM Employee E, Title T  \
															# WHERE E.id=T.empID \
																  # AND title=('" + title + "') \
														  # ) AS TEMP \
													# LEFT JOIN training ON training.empID = TEMP.id \
													# WHERE TEMP.id IS NULL \
													# AND Type=('" + training + "') \
													# ) AS Answer;")
				# # if((response).replace(")","").replace(",","").replace("(","")!=0):
					# # response = (response).replace(")","").replace(",","").replace("(","") + " " + title + " has/have " + training + " training"
				# # else:
					# # response = "None of the "+title+"s have "+training+" training"
			
			# # when neither name nor title are given but a training type is given
			# elif(title=='' and name==''):
				# response = dbRun("SELECT COUNT(*) \
								  # FROM Employee E, training t \
								  # WHERE E.id=t.empID \
										# AND Type=('" + training + "');")
				# response = str(response).replace(")","").replace(",","").replace("(","")
				# if((response).replace(")","").replace(",","").replace("(","")!=0):
						# response = (response).replace(")","").replace(",","").replace("(","") + " employee has/have " + training + " training"
				# else:
					# response = "None of the employees have "+training+" training"
	
	#-----------------------------------------------------------------------------------------------
	# joined_time
	#-----------------------------------------------------------------------------------------------
	elif intentName == "joined_time":
		# extracting parameters
		name = params['given-name']
		
		# removing apostrophes
		if("'" in name):
			name = name[:-2]
			
		# job title
		title = params['title']
		
		# date for joining, in this case it is always a singular date
		date = params['date']
		
		# if its a aggregation query
		countIndicator = params['countIndicator']
		
		#-----------------------------------------------------------------------------------------------
		# non-aggregate queries
		#-----------------------------------------------------------------------------------------------
		if(countIndicator==''):
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(hireDate) LIKE month('" + date + "') \
										AND dayofmonth(hireDate) LIKE dayofmonth('" + date + "');")
				if(len(str(response))==0):
					response = 'No '+title+"/s joined us on the specified time."
				else:
					response = 'Here is a list of '+title+'/s that joined us in the specified time ' + response.replace(")","").replace(",","").replace("(","")
					
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E \
								  WHERE (first_name=('" + name + "') OR last_name=('" + name + "'))  \
										AND month(hireDate) LIKE month('" + date + "') \
										AND dayofmonth(hireDate) LIKE dayofmonth('" + date + "');")
				if(len(str(response))==0):
					response = "Employees with names "+ name + " did not join us on the specified time."
				else:
					response = 'Employees with names '+name+' joined us on ' + response
					
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				if(len(str(response))==0):
					response = title + " " + name + " does not join us in the specified time."
				else:
					response = title + " " + name + " joined us on " + response
		#-----------------------------------------------------------------------------------------------
		# aggregation queries
		#-----------------------------------------------------------------------------------------------
		else:
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
		
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "'))  \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# both title and name are not given but time is specified	
			elif(title=='' and name==''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND month(birthDate) LIKE month('" + date + "') \
										AND dayofmonth(birthDate) LIKE dayofmonth('" + date + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
    #-----------------------------------------------------------------------------------------------
	# joined_timeperiod
	#-----------------------------------------------------------------------------------------------
	elif intentName == "joined_timeperiod":
		# extracting parameters
		name = params['given-name']

        # the start period for join date
		endDate = params['date-period']['endDate']
		
		# the end period for join date
		startDate = params['date-period']['startDate']

        # removing apostrophes
		if("'" in name):
			name = name[:-2]
			
		# job title
		title = params['title']
		
		# if its a aggregation query
		countIndicator = params['countIndicator']
		
		#-----------------------------------------------------------------------------------------------
		# non-aggregate queries
		#-----------------------------------------------------------------------------------------------
		if(countIndicator==''):
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
                                        AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				if(len(str(response))==0):
					response = 'No '+ title + "/s joined us on the specified time."
				else:
					response = 'Here is a list of '+title+'/s that joined us in the specified time ' + response.replace(")","").replace(",","").replace("(","")
					
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E \
								  WHERE (first_name=('" + name + "') OR last_name=('" + name + "'))  \
										AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				if(len(str(response))==0):
					response = "Employees with names "+ name + " did not join us in the specified time."
				else:
					response = 'Employees with names ' + name + ' joined us on ' + response
					
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT first_name, last_name \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				if(len(str(response))==0):
					response = title + " " + name + " did not join us in the specified time."
				else:
					response = title + " " + name + " has joined us on " + response
		#-----------------------------------------------------------------------------------------------
		# aggregation queries
		#-----------------------------------------------------------------------------------------------
		else:
			# the title is given but no name
			if(name=='' and title!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
		
			# the name is given but no title
			elif(title=='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND (first_name=('" + name + "') OR last_name=('" + name + "'))  \
										AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# the name and title both are given
			elif(title!='' and name!=''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND title=('" + title + "') \
										AND (first_name=('" + name + "') OR last_name=('" + name + "')) \
										AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
				
			# both title and name are not given but time is specified	
			elif(title=='' and name==''):
				response = dbRun("SELECT COUNT(*) \
								  FROM Employee E, Title T \
								  WHERE E.id=T.empID \
										AND month(hireDate) BETWEEN month('" + startDate + "') AND month('" + endDate + "') \
										AND dayofmonth(hireDate) BETWEEN dayofmonth('" + startDate + "') AND dayofmonth('" + endDate + "');")
				response = str(response).replace(")","").replace(",","").replace("(","")
	reply = {
	"response": "repsponding from server weee!",
	"fulfillmentText": "Fetching results",
	"fulfillmentMessages": [{
			"text": {
				"text": [response]
			}
		}],
    "fulfillmentText": response,
	}
	
	return jsonify(reply)


def dbRun(query):

	# connecting to SQL on AWS
	mydb = mysql.connector.connect(
		host="hr.clurfavlxnya.us-west-2.rds.amazonaws.com",
		user="admin",
		passwd="1amAdmin",
		database="hr"
	)

	mycursor = mydb.cursor()
	
	# execute the passed query
	mycursor.execute(query)

	myresult = mycursor.fetchall()
	
	# variable for final answer
	response = ""
	
	for x in myresult:	
		# converting to String to ensure it can be appended 
		x = str(x)
		print(x)
		#response += x[0] + " " + x[1] + " "
		response += x
	return response
	
#def runBdayNameTime(bday):
#    mydb = mysql.connector.connect(
#    host="hr.clurfavlxnya.us-west-2.rds.amazonaws.com",
#    user="admin",
#    passwd="1amAdmin",
#    database="hr"
#    )

#    mycursor = mydb.cursor()

#    mycursor.execute("SELECT first_name,last_name,birthDate FROM hr.Employee where month(birthDate) like month('" + bday + "') and dayofmonth(birthDate) like dayofmonth('" + bday + "');")

 #   myresult = mycursor.fetchall()
  #  response = ""
   # for x in myresult:
    #    print(x)
     #   response += x[0] + " " + x[1] + " "
    #return response