from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import MySQLdb       
import configparser as ConfigParser
import serial
import json

async_mode = None

app = Flask(__name__)


config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser = serial.Serial('/dev/tty.usbmodem112301', 9600) # middle USB port on my USB-hub

def background_thread(args):
    count = 0  
    dataCounter = 0 
    dataList = []  
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    while True:
        serialData = ser.readline().decode().removesuffix("\r\n").split(",")     #[0] = distance, [1] = temperature, [2] = humidity
        distance = serialData[0]
        temperature = serialData[1]
        humidity = serialData[2]
#        print(ser.readline().decode())

        if args:
            A = dict(args).get('A')
            dbV = dict(args).get('db_value')
            ser.write(str(int(A)*500).encode('ascii'))
        else:
            A = 1
            dbV = 'nieco'

        print("argument A: "+ str(A))
        #print(dbV) 
        #print(args)  
        print(serialData)

        #socketio.sleep(int(A))
        socketio.sleep(1)
        
        if dbV == 'start':
            count += 1
            dataCounter +=1

            dataDict = {
                "distance": distance,
                "temperature": temperature,
                "humidity": humidity
                }
            
            dataList.append(dataDict)
            socketio.emit('my_response',
                {'data': json.dumps({"distance": distance, "temperature": temperature, "humidity": humidity}),
                'count': count},
                namespace='/test')  
        else:
            if len(dataList)>0:
                fuj = str(dataList).replace("'", "\"")
                cursor = db.cursor()
                cursor.execute("SELECT MAX(id) FROM sensors")
                maxIdFromDB = cursor.fetchone()
                maxid=0     # when the DB is empty
                if(maxIdFromDB[0]): 
                    maxid=maxIdFromDB[0]

                cursor.execute("INSERT INTO sensors (id, data) VALUES (%s, %s)", (maxid + 1, fuj))
                db.commit()

                fo = open("static/files/data.txt","a+")    
                val = fuj
                fo.write("%s\r\n" %val)

            dataList = []
            dataCounter = 0

    db.close()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    return render_template('graph.html', async_mode=socketio.async_mode)

@app.route('/graphlive', methods=['GET', 'POST'])
def graphlive():
    return render_template('graphlive.html', async_mode=socketio.async_mode)

@app.route('/graphDB', methods=['GET', 'POST'])
def graphDB():
    return render_template('graphDB.html', async_mode=socketio.async_mode)

@app.route('/graphFile', methods=['GET', 'POST'])
def graphFile():
    return render_template('graphFile.html', async_mode=socketio.async_mode)

@app.route('/gaugelive', methods=['GET', 'POST'])
def gaugelive():
    return render_template('gaugelive.html', async_mode=socketio.async_mode)

@app.route('/db')
def db():
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    cursor = db.cursor()
    cursor.execute('''SELECT  data FROM  sensors WHERE id=1''')
    rv = cursor.fetchall()
    return str(rv)    


@app.route('/dbdataAll', methods=['GET', 'POST'])
def dbdataAll():
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM  sensors")
    rv = cursor.fetchall()
    return json.dumps(rv)

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    cursor = db.cursor()
    cursor.execute("SELECT data FROM  sensors WHERE id=%s", [num])
    rv = cursor.fetchone()
    return str(rv[0])

@app.route('/filedataAll', methods=['GET', 'POST'])
def filedataAll():
    fo = open("static/files/data.txt","r")
    rows = fo.readlines()
    return json.dumps(rows)

@app.route('/filedata/<string:num>', methods=['GET', 'POST'])
def filedata(num):
    fo = open("static/files/data.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

    
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})

@socketio.on('db_event', namespace='/test')
def db_message(message):   
#    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['db_value'] = message['value']    
#    emit('my_response',
#         {'data': message['value'], 'count': session['receive_count']})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
   # emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=88, debug=True)
