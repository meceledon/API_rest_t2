import requests

BASE = "http://127.0.0.1:5000/"

data = [{'name': "Elena Celedon", 'age': 23},
        {'name': "Cher", 'age': 67},
        {'name': "Peter Gabriel", 'age': 71},
        {'name': "Sin edad"}]

for i in range(len(data)):
    response = requests.post(BASE + "artists", data[i])
    print(response.json())

input()
response = requests.get(BASE + "artists")
print(response.json())
input()
response = requests.get(BASE + "artists/holi")
print(response.json())
input()
response = requests.post(BASE + "artists/RWxlbmEgQ2VsZWRvbg==/albums", {'name': "album1", 'genre': "pop"})
print(response.json())
input()
response = requests.get(BASE + "artists/RWxlbmEgQ2VsZWRvbg==/albums")
print(response.json())
input()
response = requests.put(BASE + "artists/RWxlbmEgQ2VsZWRvbg==/albums/play")
print(response)
'''input()
response = requests.get(BASE + "artists/RWxlbmEgQ2VsZWRvbg==/tracks")
print(response.json())
'''
