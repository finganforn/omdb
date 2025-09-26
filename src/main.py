
from fastapi import FastAPI
from omdb import *  # Import the OMDB API wrapper
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
        
def parseYear(yearStr):
    strYear = str(yearStr)
    #if strYear contains - remove after the dash
    if '-' in strYear:
        strYear = strYear.split('-')[0]
    if '–' in strYear:
        strYear = strYear.split('–')[0]
    if not strYear.isdigit():
        strYear = '0'
    return strYear

def fillDB(amount):
    initialMovies = fetch_random_movies(amount)  # Fetch initial random movies from OMDB API
    for movie in initialMovies:
        strYear = movie.get('Year', '0')
        strYear = parseYear(strYear)
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
def get10(): #will return 10 by default
    return getXmovies(10)

@app.get("/time")
def getAll():
    #get all movies
    query = Movie.select().order_by(Movie.year.asc())
    list = []
    for movie in query:
        list.append(movieToJson(movie))
    return list
    

@app.get("/limit/{limit}")
def getSpecificNum(limit: int):
    return getXmovies(limit)

@app.get("/title/{item_title}")
async def read_item(item_title: str):
    #get by title
    try:
        movie = Movie.get(Movie.title == item_title)
        return movieToJson(movie)
    
    except Movie.DoesNotExist:
        #print(f"fetch the new movie {item_title} ")
        newMovie = fetch_movie_by_title(item_title)
        if newMovie:
            print(f"add the new movie {item_title} with async and return it")
            await create_item(newMovie)
            movieMovie = jsonToMovie(newMovie)
            jsonMovie = movieToJson(movieMovie)
            #jreturn = movieToJson(newMovie)
            print("API CALL DONE, RETURNING")
            return jsonMovie
        return {"error": "Item not found"}
    
@app.get("/id/{imdb_id}")
async def get_by_imdb(imdb_id: str):
    #get by imdb_id
    try:
        movie = Movie.get(Movie.imdb_id == imdb_id)
        # return 201 status code
        return movieToJson(movie)
        
    
    except Movie.DoesNotExist:
        newMovie = fetch_movie_by_id(imdb_id)
        if newMovie:
            await create_item(newMovie)
            return movieToJson(newMovie)
        return {"error": "Item not found"}

from pydantic import BaseModel

class MovieItem(BaseModel):
    title: str
    year: int
    plot: str
    imdb_id: str

@app.post("/item")
async def create_item_ep(item: MovieItem):
    #create item
    print("POST ENDPOINT: *********************** Creating item:", item)

    newMovie = {
        'Title': item.title,
        'Year': item.year,
        'Plot': item.plot,
        'imdbID': item.imdb_id
    }
    res = await create_item(newMovie)
    if res is None:
        return {"message": "Item created successfully"}
    return {"error": res}


async def create_item(newMovie):
    #create item from newMovie
    
    try:
        #print(f"trying to parse year of {newMovie}")
        year = parseYear(newMovie.get('Year', 0))
        #print(f"parsed year as {year}")
        Movie.create(
            title=newMovie.get('Title', 'N/A'),
            #year=int(newMovie.get('Year', 0)),
            year=int(year),
            plot=newMovie.get('Plot', 'N/A'),
            imdb_id=newMovie.get('imdbID', 'N/A')
        )
        
        #print(f"CREATE FUNC for {newMovie.get('Title', 'N/A')} FINISHED WITHOUT CRASHING")
        
    except IntegrityError as e:
        print(f"Movie with IMDB ID {newMovie.get('imdbID')} already exists.")
        return e
    except Exception as e:
        print(f"Error creating movie: {str(e)}")
    
