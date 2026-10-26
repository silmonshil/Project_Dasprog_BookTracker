import json

# Open the JSON file and load its contents
with open('contoh.json', 'r') as file:
    data = json.load(file)

# Accessing the data (assuming the JSON has a 'nama' key)
print(data['nama'])
