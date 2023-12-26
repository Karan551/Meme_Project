# ---------------This behaves like a database temporary.---------
# user=[{"name":name,"email":email,"password":password},{}.....]
import bcrypt

users = []


# userDetails=[{user-1},{user-2},.....](parameter that is passed via user from webpage.)
# ---------------To check a user data in our database.--------------
def userExist(user_details, cursor):
    """
    @brief:This function is used to check user is already registered or not.
    @:param:user_details-->dictionary
    """
    # collect user email that is passed user via webpage.
    email = user_details["email"]
    # To fetch email,password from database.
    sql_query = f'''
                    SELECT email,password FROM registration;
                '''

    try:
        # To execute sql query.
        cursor.execute(sql_query)
        # This returns list of tuple in the tuple has data that is come via database.
        response = cursor.fetchall()
        for user in response:
            if user[0] == email:
                # To return a tuple to validate the user password for login system.
                return {"response": True, "user": user}
        # To return empty dictionary to validate the user password for login system.
        return {"response": False, "user": ()}

    except Exception as e:
        print("Error", e)


# ---------------To register a new user in our database.--------------
def registerUser(user_details, cursor):
    """
    :param cursor: To execute sql query.
    :brief:-> This function is used to register a new user in our database.,
    :param user_details:dict
    :return:->dict
    """
    # call userExist Function that check user is already registered or not.
    # user_details->dict
    checkUser = userExist(user_details, cursor)
    if checkUser["response"]:
        # if user exist.
        return {"statusCode": 503, "message": "Already Registered"}
    else:
        # users.append(user_details)    #(In memory concept.)
        # store the user data(collect user data)
        name = user_details["name"]
        email = user_details["email"]
        contact = user_details["contact"]
        password = user_details["password"]

        sql_query = f"""
                   INSERT INTO  registration(name,email,contact,password)
                    VALUES('{name}','{email}','{contact}','{password}');
                    """
        # To execute sql query.
        try:
            cursor.execute(sql_query)
        except Exception as e:
            print("Error ", e)

    # return message and status code.
    return {"statusCode": 200, "message": "Successfully Registered"}


# ----------------------To Login User---------------

def loginUser(user_details, cursor):
    """
    :param cursor: To execute sql query
    :brief:->This function is used to log in a user.
    :param user_details: dict
    :return:-> dict
    """
    # To check that is already registered or not.
    checkUser = userExist(user_details, cursor)
    if checkUser["response"]:
        db_stored_password = checkUser["user"][1]
        # if user exist then check user password with registered password in our database.
        # form_password == database password
        if bcrypt.checkpw(user_details["password"].encode(), db_stored_password.encode()):
            return {"statusCode": 200, "message": "Successfully Logged In."}
        else:
            # If password doesn't match then do this.
            return {"statusCode": 503, "message": "Password Incorrect."}
    else:
        return {"statusCode": 503, "message": "Please Register First."}
