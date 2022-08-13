from urllib import request
from flask import Flask,session,redirect,render_template,flash,request
from werkzeug.utils import secure_filename
import pyrebase
import json 
import requests
import os
app=Flask(__name__)

app.secret_key=("cre=ebrorU#Ipr&b#gibapreyAqlmLwufof+7ipo4uJa@rozi2")
config={    
  "apiKey":"AIzaSyBnCCbpSWMYA2e2tJRRTodVamxQZquYCt4",
  "authDomain": "vctok-23317.firebaseapp.com",
  "projectId":"vctok-23317",
  "storageBucket":"vctok-23317.appspot.com",
  "messagingSenderId":"298643790200",
  "appId":"1:298643790200:web:92e1d8247d0392c56ad08d",
  "databaseURL":"https://vctok-23317-default-rtdb.asia-southeast1.firebasedatabase.app/"
}
app.config["uploads"]="uploads"

firebase=pyrebase.initialize_app(config)
auth=firebase.auth()
db=firebase.database()
storage = firebase.storage()


@app.route("/")
def home():
    return render_template("base.html")

@app.route("/loginuser")
def loginuser():
    return render_template("login.html")

@app.route("/registeruser")
def reg():
    return render_template("register.html")
@app.route("/login",methods=["POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        if (email is not None)&(password is not None):
                    
                try:
                    user=auth.sign_in_with_email_and_password(email,password)
                except:
                    print("Failed to login check your email and password","error")
                    return redirect("/loginuser")
                UserInfo=auth.get_account_info(user["idToken"])
                session["Verified"]=UserInfo["users"][0]["emailVerified"]
                if session["Verified"]:    
                        session["UserName"]=user["displayName"]
                        session["UserID"]=UserInfo["users"][0]["localId"]
                        return redirect("/")
                else:
                    print("Verify email to login")
                    return redirect("/loginuser")
        else:
            print("Check email and password and try again","error")
            return redirect("/loginuser")

@app.route("/register",methods=["POST"])
def registerUser():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        passwd=request.form.get("password")
        cpasswd=request.form.get("cpassword")
        if "UserID" not in session:
                    
                if "" not in[username,email,passwd,cpasswd]:
                            

                        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={0}".format(config["apiKey"])
                        headers = {"content-type": "application/json; charset=UTF-8"}
                        data = json.dumps({"email": email, "password": passwd, "returnSecureToken": True,"displayName":username})
                        try:
                            request_object = requests.post(request_ref, headers=headers, data=data)
                        except:
                            flash("Unable to register you please try again later","error")
                            return redirect("/registernew")
                        
                        out=request_object.json()
                        
                        if "error" in out:
                            flash(out["error"]["message"].replace("_"," "),"error")
                            return redirect("/registernew")
                        else:
                            #db.child(session["UserID"])
                            auth.send_email_verification(out["idToken"])
                            db.child(out["localId"]).set("")
                            flash("Please verify email to login","warning")
                            return redirect("/loginuser")
                else:
                    flash("Check if all field are entered","warning")
                    return redirect("/registernew")
        else:
            flash("You are already registered!!","warning")
            return redirect("/loginuser")

@app.route("/create")
def create():
    return render_template("upload.html")
@app.route("/upload",methods=["POST"])
def upload():
    if request.method=="POST":
        file=request.files.get("file")
        
        
        product_name=request.form.get("productName")
        # product_description=request.form.get("productDescription")
        # funding_goal=request.form.get("fundingGoal")
        # product_category=request.form.get("productCategory")

        filename=secure_filename(file.filename)
        file.save(os.path.join(app.config["uploads"],filename))
        storage.child("user_uploads").put(os.path.join(app.config["uploads"],filename))
        return "file saved"

if __name__=="__main__":
    app.run(debug=True)