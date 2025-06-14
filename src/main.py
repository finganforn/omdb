
from fastapi import FastAPI
from .omdb import *  # Import the OMDB API wrapper


movies = []  # Initialize an empty list to store movies

#database implementation later

if movies.__len__() == 0:  # Check if the list is empty
    movies = fetch_random_movies(20)  # Fetch random movies from OMDB API

app = FastAPI()

@app.get("/") # Root endpoint 
def get10(): #will return 10 by default
    return movies[:10]

@app.get("/limit/{limit}")
def getSpecificNum(limit: int):
    return movies[:limit]

@app.get("/item/{item_title}")
def read_item(item_title: str):
    print(f"Searching for item: {item_title}")
    for movie in movies:
        if movie.get('Title', '').lower() == item_title.lower():
            return movie
    return {"error": "Item not found"}

@app.post("/item/")
def create_item(item):
    return {"item": item}


