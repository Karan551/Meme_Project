from django.shortcuts import render, redirect, HttpResponse
from .utils import registerUser, loginUser
import psycopg2
# For session storage.
from django.contrib.sessions.backends.db import SessionStore
import bcrypt
import requests

# from django.http import HttpResponse

# ---------------To connect a database--------------
try:
    connection = psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        database="memestore",
        user="postgres",
        password="Karan@2025"
    )
    print("Database connected Successfully.")

    connection.autocommit = True  # "autocommit" set to True, so you don't have to commit your queries.
    cursor = connection.cursor()
except Exception as e:
    print("Error :", e)
    print("Database Connection failed")

# ---------------For Session Handling--------------
s = SessionStore()


# ---Middle ware---
def checkSession():
    """
    brief: This function is used to check user's session is existed or not,
            if exist then return True otherwise return False.
    :return:bool
    """
    try:
        email = s["email"]
        return True
    except Exception as error:
        print("error:", error)
        return False


# -------------- Create your views here.
def index(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        contact = request.POST["contact"]
        password = request.POST["password"]
        # Encode your password
        password = password.encode()
        print("Encode password:", password)
        # Hashed your password
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        # print("Hashed Password:", hashed)
        # print("This is decoded password:", hashed.decode("utf-8"))

        # Decode your password (And store the hashed password in our database.
        hashedPassword = hashed.decode("utf-8")
        # Collect User Details in Dictionary Format.
        userDetails = {
            "name": name,
            "email": email,
            "contact": contact,
            "password": hashedPassword,
        }
        # ------------------------Register User-----------
        response = registerUser(userDetails, cursor)
        if response["statusCode"] == 200:
            s["email"] = userDetails["email"]
            s["contact"] = userDetails["contact"]
            print("This is registered user session:", s["email"])
            print("This is session for register", s)
            return redirect("/memes/")
            # return render(request, "index.html", {"msg": "Successfully Registered"})
        else:
            return render(request, "index.html", {"msg": "Already Registered"})
    return render(request, "index.html")


# ---------------------Login api-----------
def login(request):
    sessionExist = checkSession()
    # if session doesn't exist then login user and if user's session exist
    # then show private page(meme page).
    if not sessionExist:
        if request.method == "POST":
            email = request.POST["email"]
            password = request.POST["password"]
            # collect user data to logged-in user.
            userData = {
                "email": email,
                "password": password
            }
            # call the loginUser() function that is import from utils file.
            response = loginUser(userData, cursor)
            if response["statusCode"] == 200:
                # To Store Session
                s["email"] = userData["email"]
                s["password"] = userData["password"]
                #  Then Redirect to the private route.
                return redirect("/memes/")
                # This is normally action occurs when user register.
                # return render(request, "login.html", {"msg": response["message"]})
            elif response["statusCode"] == 503 and response["message"] == "Password Incorrect.":
                return render(request, "login.html", {"msg": response["message"]})
            else:
                return render(request, "login.html", {"msg": response["message"]})

        return render(request, "login.html")

    # If session already exist then redirect to user memes/ route.
    else:
        return redirect("/memes/")


def get_memes(request):
    # URL: https://api.imgflip.com/get_memes
    meme_data = requests.get("https://api.imgflip.com/get_memes")
    web_data = meme_data.json()
    # this will gives us:-> [{},{},{},.....]
    # print("this is data:", web_data["data"]["memes"])  # this will gives list of dictionary.
    sessionExists = checkSession()
    # if user's session exist then redirect to private page.
    if sessionExists:
        context = {"meme_list": web_data["data"]["memes"]}
        return render(request, "memes.html", context)

    # if user's session doesn't exist the redirect to login user.
    else:
        return redirect("/login/")


def logout(request):
    # if user logged out successfully then redirect to the login page.
    try:
        s.clear()
        return redirect("/login")
    # if user already logged in then redirect to the private page.
    except Exception as error:
        print("This is error:", error)
        return redirect("/memes/")


def edit_memes(request):
    sessionStatus = checkSession()
    if sessionStatus:
        # Get the meme id that we get with the help of GET request.
        template_id = request.GET["id"]
        context = {
            "meme_id": template_id
        }
        return render(request, "editMeme.html", context)
    else:
        return redirect("/login/")


def meme_details(request):
    sessionStatus = checkSession()
    # If session exist then do this.
    if sessionStatus:
        if request.method == "POST":
            meme_id = request.POST["meme_id"]
            text0 = request.POST["text0"]
            text1 = request.POST["text1"]

            # POST request for meme api
            payload = {
                "template_id": meme_id,
                "username": 'Adityachaudhary2',
                "password": 'qweasd01!@',
                "text0": text0,
                "text1": text1
            }
            response = requests.post("https://api.imgflip.com/caption_image", params=payload).json()
            context = {
                "url": response['data']['url']
            }
            # html_str = f'''
            #             <img src="{response['data']['url']}" alt="meme">
            #             <a href="{response['data']['url']}" alt="memes">View Meme</a>
            #             '''
            # return HttpResponse(html_str)
            return render(request, "showEditedMemes.html", context)

    else:
        redirect("/login/")
