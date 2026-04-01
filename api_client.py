import requests
import json
from api_keys import api_key

class ApiClient:
def __init__(self, api_url, api_key):
self.api_url = api_url
self.api_key = api_key

def get_data(self, endpoint):
headers = {'Authorization': f'Bearer {self.api_key}'}
response = requests.get(self.api_url + endpoint, headers=headers)
if response.status_code == 200:
return json.loads(response.content)
else:
return None

def post_data(self, endpoint, data):
headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
response = requests.post(self.api_url + endpoint, headers=headers, data=json.dumps(data))
if response.status_code == 200:
return json.loads(response.content)
else:
return None

def main():
api_client = ApiClient('https://api.example.com', api_key.api_key)
data = api_client.get_data('/users')
print(data)

if __name__ == "__main__":
main()