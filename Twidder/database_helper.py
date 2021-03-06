import sqlite3
import json
from flask import g


db = sqlite3.connect("database.db")
cursor = db.cursor()

def init_tables():
	cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email VARCHAR(50), password TEXT, firstname TEXT, familyname TEXT, gender TEXT, city TEXT, country TEXT, UNIQUE(email), CONSTRAINT check_gender CHECK (gender = 'male' OR gender = 'female'));")
	cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, receiver TEXT, sender TEXT, message TEXT);")
	cursor.execute("CREATE TABLE IF NOT EXISTS logged_users (email VARCHAR(50), token VARCHAR(36), UNIQUE(email), UNIQUE(token));")
	db.commit()

def find_user(email):
	cursor.execute("SELECT * FROM users WHERE email = '"+email+"';")
	user = cursor.fetchone()
	if user == None:
		return None;
	else:
		return json.dumps({"email" : user[1], "password" : user[2], "firstname" : user[3], "familyname" : user[4], "gender" : user[5], "city" : user[6], "country" : user[7]});

def is_connected(token):
	connected = cursor.execute("SELECT * FROM logged_users WHERE token = '"+token+"';").fetchone()
	if connected == None:
		return False
	else:
		return True

def get_token(email):
	return cursor.execute("SELECT token FROM logged_users WHERE email = '"+email+"';").fetchone()
	
def get_email(token):
	return cursor.execute("SELECT email FROM logged_users WHERE token = '"+token+"';").fetchone()

def get_user_messages_by_email(token, email):
	return cursor.execute("SELECT id, message, sender FROM messages WHERE receiver = '"+email+"' ORDER BY id DESC;").fetchall()
	
def get_user_messages_by_token(token):
	return get_user_messages_by_email(token,get_email(token)[0])

def log_user(mail, token):
	cursor.execute("INSERT INTO logged_users VALUES ('"+mail+"','"+token+"');")
	db.commit()
	
def logout_user(token):
	cursor.execute("DELETE FROM logged_users WHERE token = '"+token+"';")
	db.commit()
	
def sign_up(user):
	cursor.execute("INSERT INTO `users` (`email`,`password`,`firstname`,`familyname`,`gender`,`city`,`country`) " \
	+ "VALUES ('"+user['email']+"','"+user['password']+"','"+user['firstname']+"','"+user['familyname']+"','"+user['gender']+"','"+user['city']+"','"+user['country']+"');")
	db.commit()
	

def get_message(email):
	cursor.execute("SELECT * FROM messages WHERE receiver = '"+email+"';")
	entries = [dict(name=row[2], message=row[3]) for row in cursor.fetchall()]
	return entries[0]['name'] + " says: " + entries[0]['message']
	
def remove_user(email):
	cursor.execute("DELETE FROM users WHERE email = '"+email+"';")
	db.commit()

def db_close():
	db.close()

def post_message(sender, receiver, message):
	cursor.execute("INSERT INTO messages ('sender', 'receiver', 'message') VALUES ('"+sender+"','"+receiver+"','"+message+"');");
	db.commit()
	
def change_password(email, newPassword):
	cursor.execute("UPDATE users SET password = '"+newPassword+"' WHERE email = '"+email+"';")
	db.commit()
