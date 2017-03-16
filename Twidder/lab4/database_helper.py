import sqlite3
import json
from flask import g


db = sqlite3.connect("database.db")
cursor = db.cursor()

def init_tables():
	cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email VARCHAR(50), password TEXT, firstname TEXT, familyname TEXT, gender TEXT, city TEXT, country TEXT, UNIQUE(email), CONSTRAINT check_gender CHECK (gender = 'male' OR gender = 'female'));")
	cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, receiver TEXT, sender TEXT, message TEXT, media BOOL, display BOOL DEFAULT 1);")
	cursor.execute("CREATE TABLE IF NOT EXISTS logged_users (email VARCHAR(50), token VARCHAR(36), UNIQUE(email), UNIQUE(token));")
	cursor.execute("CREATE TABLE IF NOT EXISTS media (media_id INTEGER PRIMARY KEY, name TEXT, type TEXT, UNIQUE(name));")
	db.commit()

def find_user(email):
	cursor.execute("SELECT * FROM users WHERE email = ?;", [email])
	user = cursor.fetchone()
	if user == None:
		return None;
	else:
		return json.dumps({"email" : user[1], "password" : user[2], "firstname" : user[3], "familyname" : user[4], "gender" : user[5], "city" : user[6], "country" : user[7]});

def update_token(email, new):
	cursor.execute("UPDATE logged_users SET `token` = ? WHERE email = ?;", (new, email))
	db.commit()

def is_connected(token):
	connected = cursor.execute("SELECT * FROM logged_users WHERE token = ?;", [token]).fetchone()
	if connected == None:
		return False
	else:
		return True

def get_last_message_id():
	cursor.execute("SELECT MAX(id) FROM messages;")
	return cursor.fetchone()

def add_media(name, type, id):
	cursor.execute("INSERT INTO media VALUES (?, ?, ?);", (id, name, type))
	db.commit()

def get_media_path(id):
	cursor.execute("SELECT * FROM media WHERE media_id = ?;", [id])
	path = cursor.fetchone()
	if path == None:
		return None;
	else:
		return json.dumps({"name" : path[1], "type" : path[2]});

def get_message_by_id(id):
	cursor.execute("SELECT id, message, sender, receiver FROM messages WHERE id = ?;", [id])
	message = cursor.fetchone()
	if message == None:
		return None;
	else:
		return json.dumps({"id" : message[0], "message" : message[1], "sender" : message[2], "receiver" : message[3]});

def is_connected_mail(email):
	connected = cursor.execute("SELECT * FROM logged_users WHERE email = ?;", [email]).fetchone()
	if connected == None:
		return False
	else:
		return True

def delete_message(id):
	cursor.execute("UPDATE messages SET `display` = 0 WHERE id = ?;", [id])

def get_token(email):
	return cursor.execute("SELECT token FROM logged_users WHERE email = ?;", [email]).fetchone()
	
def get_email(token):
	return cursor.execute("SELECT email FROM logged_users WHERE token = ?;", [token]).fetchone()

def get_user_messages_by_email(email):
	return cursor.execute("SELECT DISTINCT msg.id, msg.message, msg.sender, msg.media, m.name, m.type FROM messages AS msg LEFT JOIN media AS m ON (msg.id = m.media_id) WHERE receiver = ? AND display = 1 ORDER BY id DESC;", [email]).fetchall()
	
def get_user_messages_by_token(token):
	return get_user_messages_by_email(get_email(token)[0])

def log_user(mail, token):
	cursor.execute("INSERT INTO logged_users VALUES (?, ?);", (mail, token))
	db.commit()
	
def logout_user(token):
	cursor.execute("DELETE FROM logged_users WHERE token = ?;", [token])
	db.commit()
	
def sign_up(user):
	cursor.execute("INSERT INTO `users` (`email`,`password`,`firstname`,`familyname`,`gender`,`city`,`country`) " \
	+ "VALUES (?,?,?,?,?,?,?);", (user['email'], user['password'], user['firstname'], user['familyname'], user['gender'], user['city'], user['country']))
	db.commit()
	

def get_message(email):
	cursor.execute("SELECT * FROM messages WHERE receiver = ?;", [email])
	entries = [dict(name=row[2], message=row[3]) for row in cursor.fetchall()]
	return entries[0]['name'] + " says: " + entries[0]['message']
	
def remove_user(email):
	cursor.execute("DELETE FROM users WHERE email = ?;", [email])
	db.commit()

def db_close():
	db.close()

def post_message(sender, receiver, message, media=0):
	cursor.execute("INSERT INTO messages ('sender', 'receiver', 'message', 'media') VALUES (?, ?, ?, ?);", (sender, receiver, message, media));
	db.commit()
	
def change_password(email, newPassword):
	cursor.execute("UPDATE users SET password = ? WHERE email = ?;", (newPassword, email))
	db.commit()
