import requests

BASE = "https://api-rest-t2.herokuapp.com/"

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
