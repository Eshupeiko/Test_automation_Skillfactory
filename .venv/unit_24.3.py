import requests

status='available'
res = requests.get(f"https://petstore.swagger.io/v2/pet/findByStatus", params={'status': 'available'}, headers={'accept': 'application/json'})

print(f"Код ответа: {res.status_code}")
print(res.text)
print(type(res.text))
print(res.json())
print(type(res.json()))