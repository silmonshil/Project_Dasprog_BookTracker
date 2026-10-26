import json
import os

FILE = "books.json"

def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(books):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

books = load()
judul = input("Judul: ")
penulis = input("Penulis: ")
books.append({"judul": judul, "penulis": penulis})
save(books)

print("Tersimpan! Total buku:", len(books))
print("Dawam")