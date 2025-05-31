import requests
import random

omdbkey1 = '5869c44e'
omdbkey2 = 'bc8babb5'


url0 = 'http://www.omdbapi.com/?apikey=' + omdbkey2
#url0 = url0 + '&plot=full&'
headers = {'Authorization': 'Bearer YOUR_API_TOKEN'}



def randId():
    #return 'tt' + str(random.randint(1000000, 9999999))  
    if random.randint(0, 1) == 0:
        res = 'tt00'
    else:
        res = 'tt01'
    return res + str(random.randint(10000, 99999))

movies = []

i = 0
fails = 0
bigFails = 0
while movies.__len__() < 100 and i < 500:
    i = i + 1  

    url = url0 + '&i=' + randId()
    #url = url + 'type=movie'

    #randomYear = random.randint(1940, 2023)
    #randomLetter = chr(random.randint(65, 90))
    #url = f"{url0}&s={randomLetter}&y={randomYear}&type=movie&page=1"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('Plot') == 'N/A' or response.json().get('Response') == 'False':
            fails += 1
        else:
            movies.append(data)
    else:
        bigFails += 1
        print(f"Error: {response.status_code}")

for movie in movies:
    print(f"Title: {movie.get('Title', 'N/A')}, Year: {movie.get('Year', 'N/A')}, Plot: {movie.get('Plot', 'N/A')}")
print(str(fails) + ' fails')
print('Total movies found:', len(movies))