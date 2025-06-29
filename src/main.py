
from fastapi import FastAPI
from .omdb import *  # Import the OMDB API wrapper
# py -m pip install peewee
from peewee import *




#database implementation soon

db = SqliteDatabase('movies.db')
db.connect()

initialMoviesAmount = 25

class Movie(Model):
    title = CharField()
    year = IntegerField()
    plot = TextField()
    imdb_id = CharField(unique=True)

    class Meta:
        database = db

def fillDB(amount):
    initialMovies = fetch_random_movies(amount)  # Fetch initial random movies from OMDB API
    for movie in initialMovies:
        strYear = movie.get('Year', '0')
        #if strYear contains - remove after the dash
        if '-' in strYear:
            strYear = strYear.split('-')[0]
        if '–' in strYear:
            strYear = strYear.split('–')[0]
        if not strYear.isdigit():
            strYear = '0'
        try:
            Movie.create(
                title=movie.get('Title', 'N/A'),
                year=int(strYear),
                plot=movie.get('Plot', 'N/A'),
                imdb_id=movie.get('imdbID', 'N/A')
            )
        except IntegrityError:
            print(f"Movie with IMDB ID {movie.get('imdbID')} already exists.")

if db.get_tables() == []:  # If there are no tables in the database
    print("Creating database and tables...")
    db.create_tables([Movie])
    fillDB(initialMoviesAmount)
    
else:
    print("Database already exists, skipping creation.")
    #get size of Movie table
    amountMovies = Movie.select().count()
    print(f"Number of movies in database: {amountMovies}")
    if (amountMovies < 1):
        print("No movies found in the database, filling with initial data...")
        fillDB(initialMoviesAmount)
        print(f"New number of movies in database: {amountMovies}")
    
    #for movie in Movie.select():
    #    print(movie.title, movie.year, movie.plot)

app = FastAPI()

def getXmovies(limit):
    query = (Movie
             .select()
             .limit(limit)
             .order_by(Movie.year.desc()))
    list = []
    for movie in query:
        list.append({
            "Title": movie.title,
            "Year": movie.year,
            "Plot": movie.plot,
            "imdbID": movie.imdb_id
        })
    return list

@app.get("/") # Root endpoint 
def get10(): #will return 10 by default
    return getXmovies(10)
    

@app.get("/limit/{limit}")
def getSpecificNum(limit: int):
    return getXmovies(limit)

@app.get("/item/{item_title}")
def read_item(item_title: str):
    #get by title
    try:
        movie = Movie.get(Movie.title == item_title)
        return {
            "Title": movie.title,
            "Year": movie.year,
            "Plot": movie.plot,
            "imdbID": movie.imdb_id
        }  
    except Movie.DoesNotExist:
        return {"error": "Item not found"}

@app.post("/item/")
def create_item(item):
    return {"item": item}


