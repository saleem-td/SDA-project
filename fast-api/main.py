from fastapi import FastAPI, Body
from books_data import BOOKS

app = FastAPI()


@app.get("/books")
async def get_all_books():
    return BOOKS

@app.get("/books/{book_title}")
def get_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book
