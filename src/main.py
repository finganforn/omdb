
from fastapi import FastAPI
from .omdb import *  # Import the OMDB API wrapper
# py -m pip install peewee
from peewee import *





#database implementation soon

db = SqliteDatabase('movies.db')
db.connect()

initialMoviesAmount = 50

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


def movieToJson(movie):
    return {
        "Title": movie.title,
        "Year": movie.year,
        "Plot": movie.plot,
        "imdbID": movie.imdb_id
    }
def jsonToMovie(json):
    return Movie(
        title=json.get('Title', 'N/A'),
        year=json.get('Year', 0),
        plot=json.get('Plot', 'N/A'),
        imdb_id=json.get('imdbID', 'N/A')
    )
def getXmovies(limit):
    query = (Movie
             .select()
             .limit(limit)
             .order_by(Movie.title.asc()))
    list = []
    for movie in query:
        list.append(movieToJson(movie))
    return list

@app.get("/") # Root endpoint 
async def get10(): #will return 10 by default
    return getXmovies(10)

@app.get("/time")
async def getAll():
    #get all movies
    query = Movie.select().order_by(Movie.year.asc())
    list = []
    for movie in query:
        list.append(movieToJson(movie))
    return list
    

@app.get("/limit/{limit}")
async def getSpecificNum(limit: int):
    return getXmovies(limit)

@app.get("/name/{item_title}")
async def read_item(item_title: str):
    #get by title
    try:
        movie = Movie.get(Movie.title == item_title)
        return movieToJson(movie)
    
    except Movie.DoesNotExist:
        newMovie = await fetch_movie_by_title(item_title)
        if newMovie:
            create_item(newMovie)
            return movieToJson(newMovie)
        return {"error": "Item not found"}
    
@app.get("/id/{imdb_id}")
async def get_by_imdb(imdb_id: str):
    #get by imdb_id
    try:
        movie = Movie.get(Movie.imdb_id == imdb_id)
        # return 201 status code
        return movieToJson(movie)
        
    
    except Movie.DoesNotExist:
        newMovie = await fetch_movie_by_id(imdb_id)
        if newMovie:
            create_item(newMovie)
            return movieToJson(newMovie)
        return {"error": "Item not found"}

from pydantic import BaseModel

class MovieItem(BaseModel):
    title: str
    year: int
    plot: str
    imdb_id: str

@app.post("/item")
async def create_item(item: MovieItem):
    #create item
    print("*********************** Creating item:", item)

    print("Creating item:", item)
    try:
        movie = Movie.create(
        title=item.title,
           year=item.year,
           plot=item.plot,
           imdb_id=item.imdb_id
        )
        return 
    
    except IntegrityError:
        return {"error": "Item already exists"}
    except Exception as e:
        return {"error": str(e)}
    

        


