

'''
User Table
+-----+------------+----------+------------+
| uid | username   | password | role       |
+-----+------------+----------+------------+
| 101 | superadmin | root     | superadmin |
+-----+------------+----------+------------+
| 102 | admin      | root     | admin      |
+-----+------------+----------+------------+
| 103 | manager    | root     | manager    |
+-----+------------+----------+------------+

User Info Table
+-----+------+---------------+----------------------------------------------------------------------------------------------------------------------
-------------+
| uid | name | email         | image_url                                                                                                            
             |
+-----+------+---------------+----------------------------------------------------------------------------------------------------------------------
-------------+
| 101 | John | john@test.com | https://i.ibb.co/9hBzzCw/Portrait-of-smiling-handsome-man-in-blue-t-shirt-standing-with-crossed-arms-isolated-on-grey
-backgro.jpg |
+-----+------+---------------+----------------------------------------------------------------------------------------------------------------------
-------------+
| 102 | Jack | jack@test.com | https://i.ibb.co/9hBzzCw/Portrait-of-smiling-handsome-man-in-blue-t-shirt-standing-with-crossed-arms-isolated-on-grey
-backgro.jpg |
+-----+------+---------------+----------------------------------------------------------------------------------------------------------------------
-------------+
| 103 | Ron  | ron@test.com | https://i.ibb.co/9hBzzCw/Portrait-of-smiling-handsome-man-in-blue-t-shirt-standing-with-crossed-arms-isolated-on-grey
-backgro.jpg |
+-----+------+---------------+----------------------------------------------------------------------------------------------------------------------
-------------+



'''







from flask import Flask, render_template, request, redirect, url_for, g,jsonify
import jwt, datetime
from flaskext.mysql import MySQL

app =Flask(__name__,template_folder="templates")

#Database Configuration

app.config['MYSQL_DATABASE_HOST'] = "tejaschendekar.mysql.pythonanywhere-services.com"
app.config['MYSQL_DATABASE_USER'] = "tejaschendekar"
app.config['MYSQL_DATABASE_PASSWORD'] = "mysqlroot"
app.config['MYSQL_DATABASE_DB'] = "tejaschendekar$tools"
app.config['SECRET_KEY'] = "secretEKey"

mysql = MySQL()
mysql.init_app(app)



@app.before_request
def open_conn():
    conn = mysql.connect()
    g.db = conn

@app.after_request
def close_conn(close):
    g.db.close()
    print("Closing connection")
    return close


@app.route('/')
def index():
    return render_template("index.html")



@app.route('/login',methods=['POST'])
def login():

    if request.method=="POST":
        data = request.json;
        username = data["username"];
        password = data["password"];

        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM user where username = %s AND password = %s",(username,password,));
        row = cursor.fetchall()
        if(len(row)>0):
            uid = row[0][0]
            role = row[0][3]
            uid = int(uid)
            token = jwt.encode({'public_id': uid, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            response= {
                "result":"VALID",
                "TOKEN":token
            }
            return jsonify(response), 200
        else:
            response= {
                "result":"INVALID",
                "TOKEN":"INVALID"
            }
            return jsonify(response), 200

@app.route('/dashboard/<token>',methods=['GET','POST'])
def show_dashbaord(token):

    token = str(token)
    data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
    uid = str(data['public_id'])
    cursor = g.db.cursor()
    cursor.execute("SELECT role,name,email,image_url FROM user, user_info where user.uid=%s and user_info.uid=%s",(uid,uid,))
    rows = cursor.fetchall()

    if(len(rows)>0):
        role = rows[0][0]
        name = rows[0][1]
        email = rows[0][2]
        url = rows[0][3]
        token = str(jwt.encode({'public_id': uid, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY']))
        result = {
                'name':name,
                'role':role,
                'email':email,
                'url':url,
                'token':token
                }

        return render_template("dashboard.html",result=result)


    else:
        return "INVALID TOKEN"


    return "ERROR"

@app.route('/add-user',methods=['POST'])
def add():

    if request.method=="POST":

        data = request.json;
        token = data['token']
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
        except:
            return jsonify({"result":"INVALID"})

        uid = data['uid']
        username = data["username"];
        password = data["password"];
        role = data["role"];
        email = data["email"];
        image_url = data["url"];
        name = data['name']

        try:
            cursor = g.db.cursor()
            cursor.execute('INSERT INTO USER(uid,username,password,role) values(%s,%s,%s,%s)',(uid,username,password,role,));
            cursor.execute('INSERT INTO USER_INFO(uid,name,email,image_url) values(%s,%s,%s,%s)',(uid,name,email,image_url,));
            g.db.commit()
            return jsonify({"result":"DONE"})
        except:
            return jsonify({"result":"ERROR"})



if __name__=="__main__":
    app.run()
