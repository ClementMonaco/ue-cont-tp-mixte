from flask import Flask, render_template, request, jsonify, make_response
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict
import userClient
import requests
import json
from werkzeug.exceptions import NotFound
import time

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

# utility function : write changes to bookings.json database
def write(users):
    with open('{}/data/users.json'.format("."), 'w') as f:
        json.dump({"users" : users}, f)

# homepage of the User service
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# get the full users.json JSON
@app.route("/users", methods=['GET'])
def get_users():
    res = make_response(jsonify(users), 200)
    return res

# get user info by its ID
@app.route("/user/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res
    return make_response(jsonify({"error":"User ID not found"}),400)

# get info on user bookings by passing in the user ID
@app.route("/userbookings/<userid>", methods=['GET'])
def get_bookings_by_userid(userid):
    
    # call the Bookings service
    bookings_req = userClient.run_get_bookings_by_userid(str(userid))
    # bookings_req = requests.get('http://127.0.0.1:3201/bookings/' + str(userid))
    if bookings_req == 404:
        return make_response(jsonify({"error":"User not found in bookings"}),404)
    
    res = make_response(MessageToJson(bookings_req),200)
    return res

# get the list of movies on air at a given date
@app.route("/moviesbydate/<date>", methods=['GET'])
def get_movies_by_date(date):
    # Call the Bookings Service
    booking_req = userClient.get_schedule_date(str(date))
    if booking_req == []:
        return make_response(jsonify({"error":"No movies on air at this date"}),404)

    return make_response(MessageToJson(booking_req),200)

# get the movies booked by a user; by passing in the user ID
@app.route("/moviesbyuser/<userid>", methods=['GET'])
def get_movies_by_userid(userid):
    
    # call the Bookings service
    bookings_req = userClient.run_get_bookings_by_userid(str(userid))
    # bookings_req = requests.get('http://127.0.0.1:3201/bookings/' + str(userid))
    if bookings_req == 404:
        return make_response(jsonify({"error":"User not found in bookings"}),404)
    
    bookings_data_str = MessageToJson(bookings_req)
    bookings_data_json = json.loads(bookings_data_str)
    bookings_data = bookings_data_json["schedule"]
    json_ = []
    
    for date in bookings_data:
        for movie in date["movies"]:
            body = """
                query Movie_with_id {
                  movie_with_id(_id: \""""+ str(movie) +"""\") {
                     id
                     title
                     director
                     rating
                  }
               }
            """
            movie_req= requests.post('http://127.0.0.1:3001/graphql', json={"query": body})

            json_.append(movie_req.json())

    res = make_response(jsonify(json_),200)
    return res

# get the movie info; by passing in the movie ID
@app.route("/movie/<movieid>", methods=['GET'])
def get_movie_info_by_id(movieid):
    
    body = """
        query Movie_with_id {
          movie_with_id(_id: \""""+ str(movieid) +"""\") {
             id
             title
             director
             rating
             actors {
                id
                firstname
                lastname
                birthyear
                films
            }
          }
       }
        """

    #Calling the movie service
    movie_req= requests.post('http://127.0.0.1:3001/graphql', json={"query": body})

    res = make_response(jsonify(movie_req.json()),200)
    return res

# add a movie to the system
@app.route("/useraddmovie/<movieid>", methods=['POST'])  
def add_movie(movieid):
    req = request.get_json()
    print(req)
    body = """mutation Add_movie {
                 add_movie(_id: \"""" + str(movieid) +"""\", _title: \"""" + str(req['title']) +"""\", _director: \"""" + str(req['director']) +"""\", _rating: """ + str(req['rating']) + """)    {
                    id
                    title
                    director
                    rating
                 }
              }"""

    print(body)
    

    # call the Movies service
    movieadd_req = requests.post('http://127.0.0.1:3001/graphql', json = {"query": body})

    print(movieadd_req.status_code)

    if movieadd_req.status_code != 200:
        return make_response(jsonify({"error":"Movie ID already exists"}),405)
    else :
        response_json = movieadd_req.json()

    # check if there are any GraphQL errors in the response
    if 'errors' in response_json:
        error_message = response_json['errors'][0]['message']
        return make_response(jsonify({"error": error_message}), 409)

    res = make_response(jsonify({"message":"movie added"}),200)
    return res

# add a user by providing only its username
@app.route("/adduser/<username>", methods=['POST']) 
def add_user(username):

    userid = username.lower().replace(" ","_") 
    for user in users:
        if str(user["id"]) == str(userid):
            return make_response(jsonify({"error":"user already exists"}),409)
        
    req = {
        "id" : str(userid),
        "name" : str(username), 
        "last_active" : int(time.time())
    }

    users.append(req)
    write(users)
    res = make_response(jsonify({"message":"user added"}),200)
    return res

# add a booking for a user, given a user id, a date and a movie id
@app.route("/userbookings/<userid>", methods=['POST'])  #rename ?
def add_booking_byuser(userid):
    req = request.get_json()
    movie_id = req["movieid"]
    body = """ 
      query Movie_with_id {
                  movie_with_id(_id: \""""+ str(movie_id) +"""\") {
                     id
                     title
                     director
                     rating
                  }
               }
   """

    # check that the movie exists in the system
    # call the Movies service
    movie_req = requests.post('http://127.0.0.1:3001/graphql', json = {"query": body})
    print(movie_req)
    #print(movie_req.json())
    if movie_req.status_code != 200:
        return make_response(jsonify({"error":"Movie does not exist"}),410)

    # check that the booking can be added (no duplicates and the movie is on air at given date)
    # call the Bookings service
    booking_req = userClient.run_add_booking_user(str(userid), req)
    #booking_req = requests.post('http://127.0.0.1:3201/bookings/' + str(userid), json=req)
    if booking_req == 404:
        return make_response(jsonify({"error":"Movie not found on this day"}),404)
    
    if booking_req == 405:
        return make_response(jsonify({"error":"Booking already registered"}),405)
    
    res = make_response(jsonify({"message":"booking added"}),200)
    return res

# update the rating of a movie by passing in its id and the new rating
@app.route("/usermovies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):

    body = """ 
         mutation Update_movie_rate {
            update_movie_rate(_id: \""""+str(movieid) +"""\", _rate: """+str(rate)+""") {
               id
               title
               director
               rating
            }
         }
      """
    update_req = requests.post('http://127.0.0.1:3001/graphql', json = {"query": body})

    if update_req.status_code != 200:
        print(update_req.status_code)
        return make_response(jsonify({"error":"Movie ID does not exist"}),409)

    res = make_response(jsonify({"error":"Movie rating updated"}),201) #not error
    return res

# help endpoint : displays all available endpoints for the bookings service
@app.route("/help", methods=['GET'])
def help():
    endpoints = {}
    for rule in app.url_map.iter_rules():
        # get the methods allowed for the route
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})  # Exclude HEAD and OPTIONS
        endpoints[str(rule)] = {
            "methods": methods,
            "endpoint": rule.endpoint
        }
    return make_response(jsonify(endpoints), 200)



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)