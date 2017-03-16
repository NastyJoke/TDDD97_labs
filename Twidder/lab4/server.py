import os.path

import flask
from flask import Flask, request
import random
import json

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import database_helper as db
import re


app = Flask(__name__, static_url_path='/static')

emailRegex = re.compile("^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$")


socket_dict = dict()


# Error messages in english
ERR_USER_NOT_CONNECTED = "User not connected"
ERR_USER_NOT_FOUND = "User not found"
ERR_INVALID_PASSWORD = "Invalid password"
ERR_INVALID_USER_PASSWORD = "Invalid email or password"
ERR_USER_ALREADY_CONNECTED = "User already connected"
ERR_GENDER_IS_NOT_CORRECT = "Gender is not correct"
ERR_PASSWORD_TOO_SHORT = "Password should be at least 6 characters long"
ERR_EMPTY_MESSAGE = "You can't send an empty message"
ERR_USER_ALREADY_EXISTS = "User already exists"
ERR_EMPTY_COUNTRY = "Please enter your country"
ERR_EMPTY_CITY = "Please enter your city"
ERR_EMPTY_FAMILY_NAME = "Please enter your family name"
ERR_EMPTY_FIRST_NAME = "Please enter your first name"
ERR_INVALID_EMAIL = "Please enter a correct email"
ERR_MEDIA_NOT_EXISTS = "Media does not exist"

# Success messages in english
SUC_INIT = ""
SUC_USER_LOGGED_IN = "User logged in"
SUC_USER_LOGGED_OUT = "User logged out"
SUC_USER_SIGNED_UP = "User signed up"
SUC_USER_DELETED = "User deleted"
SUC_MESSAGE_POSTED = "Message posted"
SUC_GET_USER_DATA = "Data retrieved"
SUC_PASSWORD_CHANGED = "Password changed"
SUC_MESSAGE_DELETED = "Message deleted"
SUC_FILE_UPLOADED = "File uploaded"
SUC_MEDIA_SERVED = "Media served"
SUC_MESSAGE_RETRIEVED = "Message retrieved"

output = {"success" : "true", "message" : "", "data" : {}}
data = {}

MIME_TO_TYPE = {"audio/mpeg" : "mp3", "audio/ogg" : "ogg", "audio/vnd.wav" : "wav", "video/mp4" : "mp4", "video/quicktime" : "mov", "video/x-msvideo" : "avi", "video/x-ms-wmv" : "wmv", "image/png" : "png", "image/jpeg" : "jpg", "image/gif" : "gif", "image/x-ms-bmp" : "bmp" }

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
    jsonObject = request.json
    if param in jsonObject:
        return jsonObject[param]
    else:
        return default

def generate_token():
    # Taken from serverstub.js
    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""
    for i in range(0, 36):
        token += letters[random.randint(0, len(letters)-1)]
    return token


@app.route("/", methods=['GET', 'POST'])
def root():
    db.init_tables()
    return app.send_static_file("client.html")








@app.route('/connect')
def connect():
    #send message to client with the token
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            user_token = ws.receive()
            if user_token != None:
                if (db.is_connected(user_token)):
                    email = db.get_email(user_token)[0]
                    if email in socket_dict:
                        db.update_token(email, user_token)
                        socket_dict[email].close()
                    socket_dict[email] = ws
    success("Socket closed")
    return json.dumps(output)


# form: tocken
@app.route('/is_connected', methods=["POST"])
def is_connected():
    token = get_param_or_default("token")
    success("User connected", db.is_connected(token))
    return json.dumps(output)


# form: token
@app.route('/open_socket', methods=["POST"])
def open_socket():
    token = get_param_or_default('token')
    email = db.get_email(token)[0]
    if (db.is_connected_mail(email)):
        db.update_token(email, token)
    success("Socket opened")
    return json.dumps(output)


# form: token
@app.route('/close_socket', methods=["POST"])
def close_socket():
    email = db.get_email(get_param_or_default('token'))
    if email != None:
        email = email[0]
        socket_dict[email].close()
        socket_dict.pop(email)
        success("Socket closed")
    return json.dumps(output)



# form: fileName, fileType, file
@app.route("/upload", methods=['POST'])
def upload():
    input = request.files['file']
    fileName = str(request.form['fileName'])
    fileType = MIME_TO_TYPE[str(request.form['fileType'])]

    fullName = fileName+"."+fileType

    if not os.path.exists("uploads/"):
        os.makedirs("uploads")

    input.save("uploads/"+fullName)

    # upload file to server
    success(SUC_FILE_UPLOADED, {"name" : fileName, "type" : fileType})
    return json.dumps(output)

# form: token, id
@app.route("/delete_message", methods=['POST'])
def delete_message():
    token = get_param_or_default("token")
    message_id = get_param_or_default("id")
    if (db.is_connected(token)):
        db.delete_message(message_id)
        success(SUC_MESSAGE_DELETED)
    else:
        err(ERR_USER_NOT_CONNECTED)
    return json.dumps(output)


# form: media_id
@app.route("/get_message_with_media", methods=['POST'])
def get_message_with_media():
    id = get_param_or_default("id")
    message = json.loads(db.get_message_by_id(id))
    media = json.loads(db.get_media_path(id))
    message["media_name"] = media["name"]
    message["media_type"] = media["type"]
    success(SUC_MESSAGE_RETRIEVED, message)
    return json.dumps(output)

# form: media_id
@app.route("/serve_media", methods=['GET'])
def serve_media():
    id = request.args['id']
    media_path = json.loads(db.get_media_path(id))
    file = "uploads/"+media_path["name"]+"."+media_path["type"]
    return flask.send_file(file,media_path["type"])

# form: media_name, media_type
@app.route("/add_media", methods=['POST'])
def add_media():
    media_name = get_param_or_default("media_name")
    media_type = get_param_or_default("media_type")
    db.add_media(media_name, media_type, db.get_last_message_id()[0])
    success(SUC_FILE_UPLOADED)
    return json.dumps(output)

# form: email, password
@app.route("/sign_in", methods=['POST'])
def sign_in():
    email = get_param_or_default("email")
    user = db.find_user(email)
    if (user == None):
        err(ERR_INVALID_USER_PASSWORD)
        return json.dumps(output)
    
    user = json.loads(user)
    if user != None:
        password = user["password"]
        typed_password = get_param_or_default("password")
        if typed_password == password:
            token = generate_token()
            connected = db.is_connected_mail(email)
            if (connected):
                db.update_token(email, token)
            else:
                db.log_user(email, token)
            success(SUC_USER_LOGGED_IN,token)
        else:
            err(ERR_INVALID_USER_PASSWORD)
    else:
        err(ERR_INVALID_USER_PASSWORD)
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
@app.route("/sign_up", methods=['POST'])
def sign_up():



    user = {"email" : get_param_or_default("email"), \
            "password" : get_param_or_default("password"), \
            "firstname" : get_param_or_default("firstname"), \
            "familyname" : get_param_or_default("familyname"), \
            "gender" : get_param_or_default("gender"), \
            "city" : get_param_or_default("city"), \
            "country" : get_param_or_default("country") \
            }


    if emailRegex.match(user["email"]):
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
        err(ERR_INVALID_EMAIL)

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
    fileName = get_param_or_default("media_path")
    if fileName == "":
        media = 0
    else:
        media = 1
    if db.is_connected(token):
        sender = db.get_email(token)[0]
        if db.find_user(receiver) != None:
            if message != "":
                db.post_message(sender, receiver, message, media)
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
            user_data = db.find_user(email)
            user_data = json.loads(user_data)
            user_data.pop("password",None)
            success(SUC_GET_USER_DATA,user_data)
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
        user_data = db.find_user(db.get_email(token)[0])
        user_data = json.loads(user_data)
        user_data.pop("password",None)
        success(SUC_GET_USER_DATA,user_data)
    else:
        err(ERR_USER_NOT_CONNECTED)
    return json.dumps(output)
    
# form: token
@app.route("/get_user_messages_by_token",methods=['POST']) 
def get_user_messages_by_token():
    token = get_param_or_default("token")
    if db.is_connected(token):
        messages = []
        for message_id, message, sender, media, media_name, media_type in db.get_user_messages_by_token(token):
            messageObject = {"id" : message_id, "content" : message, "writer" : sender, "media" : media, "media_name" : media_name, "media_type" : media_type}
            messages.append(messageObject)
        success(SUC_GET_USER_DATA,messages)
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
            messages = []
            for message_id, message, sender, media, media_name, media_type in db.get_user_messages_by_email(email):
                messageObject = {"id": message_id, "content": message, "writer": sender, "media": media, "media_name": media_name, "media_type": media_type}
                messages.append(messageObject)
            success(SUC_GET_USER_DATA, messages)
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
    http_server = WSGIServer(('', 5555), app, handler_class=WebSocketHandler)
    http_server.serve_forever()