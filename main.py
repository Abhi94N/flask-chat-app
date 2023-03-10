from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "kasjfdldk"
socketio = SocketIO(app)

# store information regarding rooms
rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
        
     #return code if it exists in a room
    return code
            

@app.route("/", methods=["POST", "GET"])
def home():
    # clear session and delete anything inside of it
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        # if join doesn't exist, it is false
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        
        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        # get the room code
        room = code
        # if create is not false, tehy are trying to create a room
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {
                "members": 0,
                "messages": []
            }
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist", code=code, name=name)

        # store temporary session info
        session["room"] = room
        session["name"] = name
        
        return redirect(url_for("room"))
    
    return render_template("home.html")

@app.route("/room")
def room():
    
    # get data from session
    room = session.get("room")
    
    # returns home if issue fetching room code
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    
    
    # messages persiste the message for the duration of the room session
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    
    # if room or name doesn't exist, don't connect
    if not room or not name:
        return 
    
    #socketio functions
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    # send data to room code
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")
    
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    
    # delete room if empty
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

# send messages
@socketio.on("message")
def message(data):
    room = session.get("room")
    
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    
    # store history in rooms
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

if __name__ == "__main__":
    socketio.run(app, debug=True)