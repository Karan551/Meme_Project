from django.shortcuts import render
from .utils import registerUser, loginUser
import psycopg2

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
            return render(request, "index.html", {"msg": "Successfully Registered"})
        else:
            return render(request, "index.html", {"msg": "Already Registered"})
    return render(request, "index.html")


def login(request):
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
            return render(request, "login.html", {"msg": response["message"]})
        elif response["statusCode"] == 503 and response["message"] == "Password Incorrect.":
            return render(request, "login.html", {"msg": response["message"]})
        else:
            return render(request, "login.html", {"msg": response["message"]})

    return render(request, "login.html")
