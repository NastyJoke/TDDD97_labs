

var mailRegex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

var search;
var websocket;

generateFileName = function()
{
    var letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    var name = "";
    for (var i = 0 ; i < 36 ; ++i) {
      name += letters[Math.floor(Math.random() * letters.length)];
    }
    return name;
}


var AjaxFileUploader = function () {
    this._file = {};
    var self = this;

    this.uploadFile = function (uploadUrl, file, callback) {
        var xhr = new XMLHttpRequest();
        xhr.onprogress = function (e) {
        };

        xhr.onload = function (e) {
        };

        xhr.onerror = function (e) {
            console.log("error: " + e);
        };

        xhr.open("post", uploadUrl, true);

        //xhr.setRequestHeader("Content-Type", "multipart/form-data");
        xhr.setRequestHeader("X-File-Name", file.name);
        xhr.setRequestHeader("X-File-Size", file.size);
        xhr.setRequestHeader("X-File-Type", file.type);

        var formData = new FormData();
        formData.append("file", file);
        formData.append("fileName", generateFileName());
        formData.append("fileType", file.type)
        xhr.send(formData);


          xhr.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
              callback(xhr.responseText);
          }
        };

    };
};

AjaxFileUploader.IsAsyncFileUploadSupported = function () {
    return typeof (new XMLHttpRequest().upload) !== 'undefined';
}







function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    ev.target.appendChild(document.getElementById(data));
    delete_message();
}

function delete_message() {
    if (document.getElementById("bin").childNodes.length > 0) {
        var id = document.getElementById("bin").childNodes[0].id;
        document.getElementById("bin").innerHTML = "";
        var param = constructRequestObject("token", localStorage.getItem("token"), "id", id);
        sendRequest("delete_message", param, (response) => {
        });
    }
}

sendRequest = function(url, parameters, callback)
{

    var xhttp = new XMLHttpRequest();

    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("Content-type", "application/json");

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          //callbackResponse = xhttp.responseText;
          callback(xhttp.responseText);
      }
    };
    xhttp.send(parameters);
}


constructRequestObject = function() {
    jsonObject = {};
    for (var i = 0; i < arguments.length; i+=2)
    {
        jsonObject[arguments[i]] = arguments[i+1];
    }
    return JSON.stringify(jsonObject);
}



refreshOwnMessages = function() {
      var param = constructRequestObject("token", localStorage.getItem("token"));
      sendRequest("get_user_messages_by_token", param, (response) => {
              var info = JSON.parse(response);
              if (info.success == "true")
              {
                  messages = info.data;
                  var prevHtml = "";
                  document.getElementById("ownWall").innerHTML = "";
                  for (i = 0; i < messages.length; i++)
                  {
                    prevHtml = document.getElementById("ownWall").innerHTML;
                    var media = messages[i].media;

                    var html = "<center><div draggable='true' ondragstart='drag(event)' id='" + messages[i].id + "' class='message'>From: <i>".concat(messages[i].writer).concat("</i><br />").concat(messages[i].content).concat("<br />");

                    if (media == 1)
                    {
                        var video_types = ["mp4", "mov", "avi", "wmv"];
                        var music_types = ["mp3", "ogg", "wav"]
                        var image_types = ["jpg", "png", "bmp", "gif"]


                        var media_type = messages[i].media_type;
                        if (video_types.indexOf(media_type) >= 0) // Video
                            html = html.concat('<video controls><source src="/serve_media?id='+messages[i].id+'"">Your browser does not support HTML5 video.</video>');
                        else if (music_types.indexOf(media_type) >= 0) // Music
                            html = html.concat('<audio controls><source src="/serve_media?id='+messages[i].id+'"">Your browser does not support HTML5 audio.</audio>');
                        else if (image_types.indexOf(media_type) >= 0) // Image
                            html = html.concat('<img width="200px" height="200px" src="/serve_media?id='+messages[i].id+'"" />');
                    }

                    html = html.concat("</div></center>");
                    document.getElementById("ownWall").innerHTML = prevHtml.concat(html);

                  }
              }
      });
}

refreshUserMessages = function() {
      var param = constructRequestObject("token", localStorage.getItem("token"),"email",search);
      sendRequest("get_user_messages_by_email",param, (response) => {
          var serverResponse = JSON.parse(response);
          var messages = serverResponse.data;
          var prevHtml = "";
          document.getElementById("userWall").innerHTML = "";
          for (i = 0; i < messages.length; i++)
          {
            prevHtml = document.getElementById("userWall").innerHTML;
            var html = "<center><div class='message'>From: <i>".concat(messages[i].writer).concat("</i><br />").concat(messages[i].content).concat("");
            var media = messages[i].media;

            var html = "<center><div draggable='true' ondragstart='drag(event)' id='" + messages[i].id + "' class='message'>From: <i>".concat(messages[i].writer).concat("</i><br />").concat(messages[i].content).concat("<br />");

            if (media == 1)
            {
                var video_types = ["mp4", "mov", "avi", "wmv"];
                var music_types = ["mp3", "ogg", "wav"]
                var image_types = ["jpg", "png", "bmp", "gif"]


                var media_type = messages[i].media_type;
                if (video_types.indexOf(media_type) >= 0) // Video
                    html = html.concat('<video controls><source src="/serve_media?id='+messages[i].id+'"">Your browser does not support HTML5 video.</video>');
                else if (music_types.indexOf(media_type) >= 0) // Music
                    html = html.concat('<audio controls><source src="/serve_media?id='+messages[i].id+'"">Your browser does not support HTML5 audio.</audio>');
                else if (image_types.indexOf(media_type) >= 0) // Image
                    html = html.concat('<img width="200px" height="200px" src="/serve_media?id='+messages[i].id+'"" />');
            }

            html = html.concat("</div></center>");
            document.getElementById("userWall").innerHTML = prevHtml.concat(html);
          }

      });

}

activeButton = function(index) {
	buttons = ["homeButton", "browseButton", "accountButton"];
	for (buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
		if (buttonIndex != index)
			document.getElementById(buttons[buttonIndex]).style.backgroundColor = "#60b957";
		else
			document.getElementById(buttons[buttonIndex]).style.backgroundColor = "#088B00";
	}
}

displayView = function(view) {
	if (view == "welcome")
	{
		document.getElementById("mainView").style.display = "none";
		document.getElementById("welcomeView").style.display = "block";
		window.location.hash = "";
	}
	else if (view == "main")
	{
		document.getElementById("welcomeView").style.display = "none";
		document.getElementById("mainView").style.display = "block";
		document.getElementById("password").value = "";
		
		window.location = "#home";
		activeButton(0);
		
		// Fill the info in the page according to the connected user

		var param = constructRequestObject("token", localStorage.getItem("token"));

        sendRequest("get_user_data_by_token", param, (response) => {
              var info = JSON.parse(response);

              if (info.success == "true")
              {
                refreshOwnMessages();
                document.getElementById("displayName").innerHTML = info.data.firstname.concat(' '.concat((info.data.familyname)));
                document.getElementById("displayMail").innerHTML = info.data.email;
                document.getElementById("displayCity").innerHTML = info.data.city;
                document.getElementById("displayCountry").innerHTML = info.data.country;
                document.getElementById("displayGender").innerHTML = info.data.gender;
		      }
		});
	}
}

displaySearch = function()
{
    if (search != "") { // IF SEARCH NOT EMPTY

        var param = constructRequestObject("token", localStorage.getItem("token"),"email",search);
        sendRequest("get_user_data_by_email", param, (response) => {
              var info = JSON.parse(response);

              if (info.success == "true")
              {
                document.getElementById("searchMessage").innerHTML = "";
                // display layout
                document.getElementById('browseUser').style.display = "block";
                // fill data in
                document.getElementById("displayUserName").innerHTML = info.data.firstname.concat(' '.concat((info.data.familyname)));
                document.getElementById("displayUserMail").innerHTML = info.data.email;
                document.getElementById("displayUserCity").innerHTML = info.data.city;
                document.getElementById("displayUserCountry").innerHTML = info.data.country;
                document.getElementById("displayUserGender").innerHTML = info.data.gender;

                refreshUserMessages();

              }
              else {
                    document.getElementById("searchMessage").innerHTML = info.message;
                    document.getElementById("browseUser").style.display = "none";
              }
        });
    }
}



initSocket = function()
{
    websocket = new WebSocket("ws://localhost:5555/connect");
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
}


  function onOpen(evt)
  {
        var param = constructRequestObject("token", localStorage.getItem("token"));
        sendRequest("is_connected", param, (response) => {
            var param = constructRequestObject("token", localStorage.getItem("token"));
            sendRequest("open_socket", param, (response) => {
                websocket.send(localStorage.getItem("token"));
            });
        });
  }
  function onClose(evt)
  {
    disconnect();
  }








{

  function onError(evt)
  {
    console.log('ERROR: ' + evt.data);
  }

  function doSend(message)
  {
    websocket.send(message);
  }
}

window.onload = function(){


          if (window.location.hash = "")
            window.location.hash = "#home";
          window.scrollTo(0,0);

          // buttons listeners
          document.getElementById("loginSubmit").addEventListener("click", function(event){
            event.preventDefault();
            if (validateLogin())
                refreshOwnMessages();
            window.scrollTo(0,0);
            });
          document.getElementById("signupSubmit").addEventListener("click", function(event){
            event.preventDefault();
            validateSignup();
            });
          document.getElementById("postSubmit").addEventListener("click", function(event){
          event.preventDefault();
            validatePostMessage();
            refreshOwnMessages();
            });
          document.getElementById("homeButton").addEventListener("click", function(event){
            event.preventDefault();
            window.location = "#home";
            window.scrollTo(0,0);
            });
          document.getElementById("browseButton").addEventListener("click", function(event){
            event.preventDefault();
            displaySearch();
            window.location = "#browse";
            window.scrollTo(0,0);
            });
          document.getElementById("accountButton").addEventListener("click", function(event){
            event.preventDefault();
            window.location = "#account";
            window.scrollTo(0,0);
            });
          document.getElementById("searchSubmit").addEventListener("click", function(event){
            event.preventDefault();
            searchUser();
            window.scrollTo(0,0);
            });
          document.getElementById("changePwdSubmit").addEventListener("click", function(event){
            event.preventDefault();
            validateChangePassword();
            window.scrollTo(0,0);
            });
          document.getElementById("postMessageSubmit").addEventListener("click", function(event){
            event.preventDefault();
            validatePostMessage(0);
            window.scrollTo(0,0);
            });



    var param = constructRequestObject("token", localStorage.getItem("token"));
    sendRequest("is_connected", param, (response) => {
          serverResponse = JSON.parse(response)
          if (serverResponse.data)
          {
              initSocket();

              search = "";


              // Show the Connected view instead of the connect view
              displayView("main");
              refreshOwnMessages();

          }
          else
          {
              displayView("welcome");
          }
      });

};


validateLogin = function() {

  var email = document.getElementById('email').value;
  var password = document.getElementById('password').value;
  if (!mailRegex.test(email)) {
    document.getElementById('loginErrorMessage').innerHTML = "<center>Please enter your email.</center>";
    return false;
  }
  if (password.length < 6) {
        document.getElementById('loginErrorMessage').innerHTML = "<center>Your password must be at least 6 characters long.</center>";
        return false;
      }
  //else signin


  var param = constructRequestObject("email", email, "password", hex_md5(password));
        sendRequest("sign_in", param, (response) => {

        var serverResponse = JSON.parse(response);
        if (serverResponse.success == "true") // Authentication succeeded
          {
            localStorage.setItem("token",serverResponse.data);
            displayView("main");
            initSocket();
          }
          else
          {
            document.getElementById('loginErrorMessage').innerHTML = "<center>" + serverResponse.message + "</center>";
            return false;
          }
        });
};











validateSignup = function(){

  var data = {"firstname":document.getElementById('firstName').value,
              "familyname":document.getElementById('familyName').value,
              "gender":document.getElementById('gender').value,
              "city":document.getElementById('city').value,
              "country":document.getElementById('country').value,
              "email":document.getElementById('newEmail').value,
              "password":document.getElementById('newPassword').value};
  var repeat_password = document.getElementById('repeatPassword').value;



  // errors
  var errorMessage = "<center>";
  if (data.firstname == "") {
        errorMessage += "Please enter your first name.";
  }
  else if (data.familyname == "") {
        errorMessage += "Please enter your last name.";
  }
  else if (data.gender != "male" && data.gender != "female") {
        errorMessage += "Please select your gender.";
  }
  else if (data.city == "") {
        errorMessage += "Please enter your city.";
  }
  else if (data.country == "") {
        errorMessage += "Please enter your country.";
  }
  else if (!mailRegex.test(data.email)) {
        errorMessage += "Please enter your email.";
  }
  else if (data.password.length < 6) {
        errorMessage += "Password should be at least 6 characters.";
  }
  else if (data.password != repeat_password) {
        errorMessage += "Passwords mismatch.";
  }
  
  errorMessage += "</center>";
  document.getElementById('signupMessage').innerHTML = errorMessage;
  
  
  if (errorMessage != "<center></center>")
	return false;


  //else signup

  // hash password
  data.password = hex_md5(data.password);

  var param = JSON.stringify(data);
  sendRequest("sign_up",param, (response) => {
      var serverResponse = JSON.parse(response);
      if (serverResponse.success == "false")
      {
        // server error
        document.getElementById('signupMessage').innerHTML = "<center>"+serverResponse.message+"</center>";
        return false;
      }
      else
      {
        document.getElementById('signupMessage').innerHTML = '<center><span class="successMessage">Your account has been created!</span></center>';
        document.getElementById('firstName').value = "";
        document.getElementById('familyName').value = "";
        document.getElementById('gender').selectedIndex = "0";
        document.getElementById('city').value = "";
        document.getElementById('country').value = "";
        document.getElementById('newEmail').value = "";
        document.getElementById('newPassword').value = "";
        document.getElementById('repeatPassword').value = "";
      }
      });

};


validateChangePassword = function(){
  var oldPassword = document.getElementById('oldPassword').value;
  var newPassword = document.getElementById('changePassword').value;
  var repeatPassword = document.getElementById('repeatChangePassword').value;

  if (oldPassword.length < 6)
      {
        document.getElementById('changePasswordErrorMessage').innerHTML = "Your password should be at least 6 characters long.";
        return false;
      }
  if (repeatPassword != newPassword)
  {
        document.getElementById('changePasswordErrorMessage').innerHTML = "Passwords mismatch.";
        return false;
  }
  if (newPassword.length < 6)
      {
        document.getElementById('changePasswordErrorMessage').innerHTML = "Your new password should be at least 6 characters long.";
        return false;
      }

  //else changePassword
  var param = constructRequestObject("token", localStorage.getItem("token"), "oldPassword", oldPassword, "newPassword", newPassword);
  sendRequest("change_password",param, (response) => {
      var serverResponse = JSON.parse(response);
      if (serverResponse.success == "false")
      {
            document.getElementById('changePasswordErrorMessage').innerHTML = serverResponse.message;
            return false;
      }
      else
      {
            document.getElementById('changePasswordErrorMessage').innerHTML = "<span style='color:green;'>Your password has been changed.</span>";
      }
  });
}

formatMessage = function(message) {
  message = message.replace(new RegExp("<","g"),"&lt;");
  message = message.replace(new RegExp(">","g"),"&gt;");
  message = message.replace(new RegExp("\n","g"),"<br />");
  return message;
}

// self = 1 for message on your own wall
// self = 0 for message on someone's wall
validatePostMessage = function(self = 1) {
  //if (AjaxFileUploader.IsAsyncFileUploadSupported) {
        //ajaxFileUploader = new AjaxFileUploader();
        //var uploader = document.getElementById("ofd");
        //if (uploader.files.length == 0) {
        var senderToken = localStorage.getItem("token");
        if (self)
        {
            var message = document.getElementById("postMessage").value;
                ajaxFileUploader = new AjaxFileUploader();
                var uploader = document.getElementById("ofd");
                if (uploader.files.length == 0) { // THERE IS NO FILE
                    var param = constructRequestObject("token", senderToken);
                    sendRequest("get_user_data_by_token",param, (response) => {
                        var serverResponse = JSON.parse(response);
                        var receiver = serverResponse.data.email;
                        message = formatMessage(message);

                        if (message == "")
                            return false;

                        var param = constructRequestObject("token", localStorage.getItem("token"), "message", message, "email", receiver);
                        sendRequest("post_message",param, (response) => {
                            refreshOwnMessages();
                            document.getElementById("postMessage").value = "";
                            document.getElementById("ofd").value = "";
                        });
                    });

                }
                else
                { // THERE IS A FILE
                    if (AjaxFileUploader.IsAsyncFileUploadSupported) {
                        var param = constructRequestObject("token", senderToken);
                        sendRequest("get_user_data_by_token",param, (response) => {
                            var serverResponse = JSON.parse(response);
                            var receiver = serverResponse.data.email;
                            message = formatMessage(message);

                            ajaxFileUploader.uploadFile("/upload", uploader.files[0], (response) => {
                                media_name = JSON.parse(response).data["name"];
                                media_type = JSON.parse(response).data["type"];
                                if (document.getElementById("postMessage").value == "")
                                {
                                    var message = " ";
                                }
                                else
                                {
                                    var message = document.getElementById("postMessage").value;
                                }
                                var param = constructRequestObject("token", localStorage.getItem("token"), "message", message, "email", receiver, "media_path", 1);
                                sendRequest("post_message",param, (response) => {
                                    param = constructRequestObject("media_name", media_name, "media_type", media_type);
                                    sendRequest("add_media", param, (response) => {
                                        refreshOwnMessages();
                                        document.getElementById("postMessage").value = "";
                                        document.getElementById("ofd").value = "";

                                    });
                                });

                            });

                        });
                    }

                }
        }
        else // Post on someone's wall
        {
            var message = document.getElementById("postUserMessage").value;
            var receiver = search;
            message = formatMessage(message);
            ajaxFileUploader = new AjaxFileUploader();
            var uploader = document.getElementById("ofdUser");
            if (uploader.files.length == 0) { // THERE IS NO FILE
                if (message == "")
                    return false;

                var param = constructRequestObject("token", localStorage.getItem("token"), "message", message, "email", receiver);
                sendRequest("post_message",param, (response) => {
                    document.getElementById("postUserMessage").value = "";
                    refreshUserMessages();

                });

            }
            else
            { // THERE IS A FILE
                if (AjaxFileUploader.IsAsyncFileUploadSupported) {
                        ajaxFileUploader.uploadFile("/upload", uploader.files[0], (response) => {
                            media_name = JSON.parse(response).data["name"];
                            media_type = JSON.parse(response).data["type"];
                            if (document.getElementById("postUserMessage").value == "")
                            {
                                var message = " ";
                            }
                            else
                            {
                                var message = document.getElementById("postUserMessage").value;
                            }
                            var param = constructRequestObject("token", localStorage.getItem("token"), "message", message, "email", receiver, "media_path", 1);
                            sendRequest("post_message",param, (response) => {
                                param = constructRequestObject("media_name", media_name, "media_type", media_type);
                                sendRequest("add_media", param, (response) => {
                                    refreshUserMessages();
                                    document.getElementById("postUserMessage").value = "";
                                    document.getElementById("ofdUser").value = "";

                                });
                            });

                        });
                }

            }

        }

        return false;

}


disconnect = function() {
  var param = constructRequestObject("token", localStorage.getItem("token"));
  sendRequest("close_socket", param, (response) => {
      localStorage.removeItem("token");
      displayView("welcome");
  });
}


searchUser = function() {
	var s = document.getElementById('search').value;
	if (!mailRegex.test(s)) {
		document.getElementById('searchMessage').innerHTML = "Please enter a valid email.";
		return false;
	}
	else
	{
	    var param = constructRequestObject("token", localStorage.getItem("token"));
        sendRequest("get_user_data_by_token", param, (response) => {
              var serverResponse = JSON.parse(response);
              if (serverResponse.success == "true")
              {
                  var selfMail = serverResponse.data.email;
                    if (s == selfMail) {
                        search = "";
                        document.getElementById('searchMessage').innerHTML = "You narcissistic.";
                    }
                    else
                        search = s;
                    displaySearch();
              }
              else
              {
                    document.getElementById('searchMessage').innerHTML = serverResponse.data.message;
              }
	    });

    }
}

