from flask import Flask
from flask import request
import random
import json
import sqlite3
import database_helper as db

app = Flask(__name__)

# Error messages in english
ERR_USER_NOT_CONNECTED = "User not connected"
ERR_USER_NOT_FOUND = "User not found"
ERR_INVALID_PASSWORD = "Invalid password"
ERR_USER_ALREADY_CONNECTED = "User already connected"
ERR_GENDER_IS_NOT_CORRECT = "Gender is not correct"
ERR_PASSWORD_TOO_SHORT = "Password should be at least 6 characters long"
ERR_EMPTY_MESSAGE = "You can't send an empty message"
ERR_USER_ALREADY_EXISTS = "User already exists"
ERR_EMPTY_COUNTRY = "Please enter your country"
ERR_EMPTY_CITY = "Please enter your city"
ERR_EMPTY_FAMILY_NAME = "Please enter your family name"
ERR_EMPTY_FIRST_NAME = "Please enter your first name"
ERR_EMPTY_EMAIL = "Please enter your email"

# Success messages in english
SUC_INIT = ""
SUC_USER_LOGGED_IN = "User logged in"
SUC_USER_LOGGED_OUT = "User logged out"
SUC_USER_SIGNED_UP = "User signed up"
SUC_USER_DELETED = "User deleted"
SUC_MESSAGE_POSTED = "Message posted"
SUC_GET_USER_DATA = "Data retrieved"
SUC_PASSWORD_CHANGED = "Password changed"


output = {"success" : "true", "message" : "", "data" : None}
data = {}


# Server responses

def err(message):
	output["message"] = message
	output["success"] = "false"
	output["data"] = {}
	
def success(message, data = {}):
	output["message"] = message
	output["success"] = "true"
	output["data"] = data
	

def get_param_or_default(param, default = ""):
	getParam = request.form.get(param)
	if getParam == None:
		return default
	else:
		return getParam

def generate_token():
	# Taken from serverstub.js
	letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
	token = ""
	for i in range(0, 36):
		token += letters[random.randint(0, len(letters)-1)]
	return token

@app.route("/")
def hello():
	app.send_static_file("client.html")
	db.init_tables()
	success(SUC_INIT, dict())
	return json.dumps(output)

# form: email, password
@app.route("/sign_in", methods=['POST'])
def sign_in():
	email = get_param_or_default("email")
	user = db.find_user(email)
	if (user == None):
		err(ERR_USER_NOT_FOUND)
		return json.dumps(output)
	
	user = json.loads(user)
	if user != None:
		if db.get_token(user["email"]) == None:
			password = user["password"]
			typed_password = get_param_or_default("password")
			if typed_password == password:
				token = generate_token()
				db.log_user(email, token)
				success(SUC_USER_LOGGED_IN,token)
			else:
				err(ERR_INVALID_PASSWORD)
		else:
			err(ERR_USER_ALREADY_CONNECTED)
	else:
		err(ERR_USER_NOT_FOUND);
	return json.dumps(output)

# form: token
@app.route("/sign_out", methods=['POST']) 
def sign_out():
	token = get_param_or_default("token")
	if db.is_connected(token):
		db.logout_user(token)
		success(SUC_USER_LOGGED_OUT)
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)

# form: email, password, firstname, familyname, gender, city, country
@app.route("/sign_up", methods=['POST']) # CHANGE TO POST 
def sign_up():
	user = {"email" : get_param_or_default("email"), \
			"password" : get_param_or_default("password"), \
			"firstname" : get_param_or_default("firstname"), \
			"familyname" : get_param_or_default("familyname"), \
			"gender" : get_param_or_default("gender"), \
			"city" : get_param_or_default("city"), \
			"country" : get_param_or_default("country") \
			}
	if user["email"] != "":
		if user["firstname"] != "":
			if user["familyname"] != "":
				if user["city"] != "":
					if user["country"] != "":
						if db.find_user(user["email"]) == None:
							if len(user["password"]) > 5:
								if user["gender"] == "male" or user["gender"] == "female":
									db.sign_up(user)
									success(SUC_USER_SIGNED_UP)
								else:
									err(ERR_GENDER_IS_NOT_CORRECT)
							else:
								err(ERR_PASSWORD_TOO_SHORT)
						else:
							err(ERR_USER_ALREADY_EXISTS)
					else:
						err(ERR_EMPTY_COUNTRY)
				else:
					err(ERR_EMPTY_CITY)
			else:
				err(ERR_EMPTY_FAMILY_NAME)
		else:
			err(ERR_EMPTY_FIRST_NAME)
	else:
		err(ERR_EMPTY_EMAIL)
	return json.dumps(output)

# form: token
@app.route("/remove_user", methods=['POST'])
def remove_user():
	token = get_param_or_default("token")
	if db.is_connected(token):
		email = db.get_email(token)[0]
		db.logout_user(token)
		db.remove_user(email)
		success(SUC_USER_DELETED)
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)

# form: token, message, email
@app.route("/post_message",methods=['POST']) 
def post_message():
	token = get_param_or_default("token")
	receiver = get_param_or_default("email")
	message = get_param_or_default("message")
	if db.is_connected(token):
		sender = db.get_email(token)[0]
		if db.find_user(receiver) != None:
			if message != "":
				db.post_message(sender, receiver, message)
				success(SUC_MESSAGE_POSTED)
			else:
				err(ERR_EMPTY_MESSAGE)
		else:
			err(ERR_USER_NOT_FOUND)
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)
	
# form: token, email
@app.route("/get_user_data_by_email",methods=['POST']) 
def get_user_data_by_email():
	token = get_param_or_default("token")
	email = get_param_or_default("email")
	if db.is_connected(token):
		if db.find_user(email) != None:
			success(SUC_GET_USER_DATA,db.find_user(email))
		else:
			err(ERR_USER_NOT_FOUND)
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)
		
# form: token
@app.route("/get_user_data_by_token",methods=['POST']) 
def get_user_data_by_token():
	token = get_param_or_default("token")
	if db.is_connected(token):
		success(SUC_GET_USER_DATA,db.find_user(db.get_email(token)[0]))
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)
	
# form: token
@app.route("/get_user_messages_by_token",methods=['POST']) 
def get_user_messages_by_token():
	token = get_param_or_default("token")
	if db.is_connected(token):
		success(SUC_GET_USER_DATA,db.get_user_messages_by_token(token))
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)
	
# form: token, email
@app.route("/get_user_messages_by_email",methods=['POST']) 
def get_user_messages_by_email():
	token = get_param_or_default("token")
	email = get_param_or_default("email")
	if db.is_connected(token):
		if db.find_user(email) != None:
			success(SUC_GET_USER_DATA,db.get_user_messages_by_email(token, email))
		else:
			err(ERR_USER_NOT_FOUND)
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)

	
# form: token, oldPassword, newPassword
@app.route("/change_password",methods=['POST']) 
def change_password():
	
	token = get_param_or_default("token")
	
	userMail = db.get_email(token)
	if userMail != None:
		userMail = userMail[0]
		oldPassword = get_param_or_default("oldPassword")
		newPassword = get_param_or_default("newPassword")
		user = db.find_user(userMail)
		if user != None:
			user = json.loads(user)
			if user["password"] == oldPassword:
				if len(newPassword) > 5:
					db.change_password(userMail, newPassword)
					success(SUC_PASSWORD_CHANGED)
				else:
					err(ERR_PASSWORD_TOO_SHORT)
			else:
				err(ERR_INVALID_PASSWORD)
		else:
			err(ERR_USER_NOT_FOUND)
	else:
		err(ERR_USER_NOT_CONNECTED)
	return json.dumps(output)

if __name__ == "__main__":
    app.run()








