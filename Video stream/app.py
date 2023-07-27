from flask import *
import cv2
import sqlite3
from flask_restful import Api,Resource

class deleteid(Resource):
    def get(self):
        with sqlite3.connect("static/streams.db") as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM hosts")
            conn.commit()
        return {"message":f"{id} deleted!"}

app = Flask(__name__)
api = Api(app)

api.add_resource(deleteid,"/deleteallchannels")

camera = cv2.VideoCapture(0)

def getChannels():
    with sqlite3.connect("static/streams.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM hosts")
        channels = cur.fetchall()
    return channels
def createTable():
    with sqlite3.connect("static/streams.db") as conn:
        cur = conn.cursor()
        # cur.execute("DROP TABLE IF EXISTS hosts")
        cur.execute("CREATE TABLE hosts(hoster TEXT,host_id INT PRIMARY KEY)")
        conn.commit()


def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.errorhandler(500)
def funcerr(err):
    return "Error happened ";
            
@app.route("/")
def index():
    channels = getChannels()
    return render_template("home.html",channels=channels)

@app.route("/hostvideo")
def hostVideo():
    return render_template("form.html")

@app.route("/failedtohost")
def failMessage():
    return "<script>alert('Failed to host because the id you chose already exists!');window.location.href='/hostvideo';</script>"

@app.route("/success",methods=["POST"])
def hostSuc():
    hoster = request.form.get("host")
    id = request.form.get("id")
    try:
        with sqlite3.connect("static/streams.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO hosts(hoster,host_id) VALUES (?,?)",(hoster,id,))
            conn.commit()
        return redirect(f"/video/{id}")
    except:
        return redirect("/failedtohost")
        



@app.route('/video/<int:channel>')
def video_feed(channel):
    ids = getChannels()


    numbers_only = [t[1] for t in ids]


    if channel in numbers_only:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "<script>alert('Streaming id not found');window.location.href='/';</script>"

@app.route("/admin/delete")
def adminctrl():
    channels = getChannels()
    return render_template("admin.html",channels = channels)

if __name__ == '__main__':
    app.run()
