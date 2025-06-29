
from fastapi import FastAPI
from .omdb import *  # Import the OMDB API wrapper
# py -m pip install peewee
from peewee import *




#database implementation soon

db = SqliteDatabase('movies.db')
db.connect()

class Movie(Model):
    title = CharField()
    year = IntegerField()
    plot = TextField()
    imdb_id = CharField(unique=True)

    class Meta:
        database = db



if db.get_tables() == []:  # If there are no tables in the database
    print("Creating database and tables...")
    db.create_tables([Movie])
    initialMovies = fetch_random_movies(10)  # Fetch initial random movies from OMDB API
    for movie in initialMovies:
        strYear = movie.get('Year', '0')
        #if strYear contains - remove after the dash
        if '-' in strYear:
            strYear = strYear.split('-')[0]
        if '–' in strYear:
            strYear = strYear.split('–')[0]
        try:
            Movie.create(
                title=movie.get('Title', 'N/A'),
                year=int(strYear),
                plot=movie.get('Plot', 'N/A'),
                imdb_id=movie.get('imdbID', 'N/A')
            )
        except IntegrityError:
            print(f"Movie with IMDB ID {movie.get('imdbID')} already exists.")
else:
    print("Database already exists, skipping creation.")
    #get size of Movie table
    print(f"Number of movies in database: {Movie.select().count()}")
    for movie in Movie.select():
        print(movie.title, movie.year, movie.plot)

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


