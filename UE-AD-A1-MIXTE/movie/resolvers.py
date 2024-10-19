import json
from graphql import GraphQLError

def movie_with_id(_,info,_id):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie
            
def movie_with_title(_,info,_title):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['title'] == _title:
                return movie
            
def all_movies(_,info):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        return movies["movies"]
    
def all_actors(_,info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        return actors["actors"]
    
def actor_with_id(_,info,_id):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        for actor in actors['actors']:
            if actor['id'] == _id:
                return actor

def update_movie_rate(_,info,_id,_rate):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def add_movie(_,info,_id,_title,_director,_rating):
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                raise GraphQLError('Error 409 : Movie already exists')
        
        newmovie['title'] = _title
        newmovie['rating'] = _rating
        newmovie['director'] = _director
        newmovie['id'] = _id
        
        movies['movies'].append(newmovie)
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return newmovie

def delete_movie(_,info,_id):
    newmovies = {}
    deleted_movie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        movies_kept = []
        for movie in movies['movies']:
            if movie['id'] == _id:
                deleted_movie = movie
            else : 
                movies_kept.append(movie)
        newmovies['movies'] = movies_kept
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return deleted_movie

def add_actor(_,info,_id,_firstname,_lastname,_birthyear):
    newactor = {}
    with open('{}/data/actors.json'.format("."), "r") as rfile:
        actors = json.load(rfile)
        for actor in actors['actors']:
            if actor['id'] == _id:
                raise GraphQLError('Error 409 : Actor already exists')
        
        newactor['id'] = _id
        newactor['firstname'] = _firstname
        newactor['lastname'] = _lastname
        newactor['birthyear'] = _birthyear
        newactor['films'] = []
        
        actors['actors'].append(newactor)
    with open('{}/data/actors.json'.format("."), "w") as wfile:
        json.dump(actors, wfile)
    return newactor

def add_movie_to_actor(_,info,_id_movie,_id_actor):
    newactors = {}
    newactor = {}
    with open('{}/data/actors.json'.format("."), "r") as rfile:
        actors = json.load(rfile)
        for actor in actors['actors']:
            if actor['id'] == _id_actor:
                if _id_movie not in actor['films']:
                    actor['films'].append(_id_movie)
                    newactor = actor
                    newactors = actors
    with open('{}/data/actors.json'.format("."), "w") as wfile:
        json.dump(newactors, wfile)
    return newactor

def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        result = [actor for actor in actors['actors'] if movie['id'] in actor['films']]
        return result