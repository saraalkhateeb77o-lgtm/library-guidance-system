import database.collections.books as books
import json
from client import embed

books.clear()

with open('./books.json') as f:
    array = json.load(f)
    for book in array:
        # Convert book into a string
        bookStr = f"""
        {book['title']}
        {book['title']}
        {book['title']}
        {book['title']}
        {book['title']}
        {book['title']}
        {book['description']}
        {book['description']}
        {book['description']}
        {' '.join(book['keywords'])}
        {' '.join(book['keywords'])}
        {' '.join(book['keywords'])}
        {' '.join(book['keywords'])}
        """

        # Generate book's embedding
        embeddings = embed(bookStr).embeddings[0].values
        
        books.add(book, embeddings)

