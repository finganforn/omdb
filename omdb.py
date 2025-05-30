import requests
import random

#omdb key 5869c44e
#andor tt9253284

#url = 'http://www.omdbapi.com/?apikey=5869c44e&t=The+Matrix&plot=full'
url0 = 'http://www.omdbapi.com/?apikey=5869c44e'
url = url0 + '&i=tt9253284&plot=full' #andor
headers = {'Authorization': 'Bearer YOUR_API_TOKEN'}



def randId():
    return 'tt' + str(random.randint(1000000, 9999999))

movies = []

i = 0
while movies.__len__() < 100 and i < 1000:
    i = i + 1  
    url = url0 + '&i=' + randId() + '&plot=full'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('Title') == 'N/A' or response.json().get('Response') == 'False':
            print(f"Movie not found for ID: {url.split('=')[-1]}")
        else:
            movies.append(data)
    else:
        print(f"Error: {response.status_code}")
for i in range(20):
    url = url0 + '&i=' + randId() + '&plot=full'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('Plot') == 'N/A' or response.json().get('Response') == 'False':
            print(f"Movie not found for ID: {url.split('=')[-1]}")
        else:
            movies.append(data)
    else:
        print(f"Error: {response.status_code}")
for movie in movies:
    print(f"Title: {movie.get('Title', 'N/A')}, Year: {movie.get('Year', 'N/A')}, Plot: {movie.get('Plot', 'N/A')}")
