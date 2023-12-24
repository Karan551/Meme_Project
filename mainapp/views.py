from django.shortcuts import render, redirect
from .utils import registerUser, loginUser
import psycopg2
# For session storage.
from django.contrib.sessions.backends.db import SessionStore


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
# print(s)


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


# Create your views here.
def index(request):
    if request.method == "POST":
        # print(request.POST)
        name = request.POST["name"]
        email = request.POST["email"]
        contact = request.POST["contact"]
        password = request.POST["password"]
        # Collect User Details in Dictionary Format.
        userDetails = {
            "name": name,
            "email": email,
            "contact": contact,
            "password": password,
        }
        # ------------------------Register User-----------
        response = registerUser(userDetails, cursor)
        # print("Total User is:", response["totalUsers"])
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


def login(request):
    sessionExist = checkSession()
    # if session doesn't exist then login user and if user's session exist
    # then show private page(meme page).
    if not sessionExist:
        if request.method == "POST":
            email = request.POST["email"]
            password = request.POST["password"]
            # print("User email is :", email)
            # print("User password is :", password)
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
    sessionExists = checkSession()
    # if user's session doesn't exist the redirect to login user.
    if not sessionExists:
        redirect("/login/")
    # if user's session exist then redirect to private page.
    else:
        return render(request, "memes.html")


def logout(request):
    # if user logged out successfully then redirect to the login page.
    try:
        s.clear()
        return redirect("/login")
    # if user already logged in then redirect to the private page.
    except Exception as error:
        print("This is error:", error)
        return redirect("/memes/")
