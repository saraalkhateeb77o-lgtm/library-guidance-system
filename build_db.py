import database.collections.books as books
from client import embed
from sqlite.client import select

books.clear()

rows = select(column='books')


for row in rows:
    (
        id,
        title_en,
        title_ar,
        author_en,
        author_ar,
        year,
        topic_en,
        topic_ar,
        call_number,
        keywords,
        keywords_ar,
        available,
        shelf,
        x,
        y,
        description_en,
        description_ar
    ) = row

    # Build text used for embedding
    bookStr = f"""
    {title_en}
    {title_ar}
    {topic_en}
    {topic_ar}
    {description_en}
    {description_ar}
    {keywords}
    {keywords_ar}
    """

    # Generate embedding vector
    embedding = embed(bookStr)[0]

    # Insert into Chroma collection
    books.collection.add(
        documents=[bookStr],
        embeddings=[embedding],
        metadatas=[{
            "id": id,
            "title_en": title_en,
            "title_ar": title_ar,
            "author_en": author_en,
            "author_ar": author_ar,
            "description_en": description_en,
            "description_ar": description_ar,
            "keywords": keywords,
            "keywords_ar": keywords_ar,
            "topic_en": topic_en,
            "topic_ar": topic_ar,

            # 🔥 الإضافة الجديدة
            "shelf": shelf,
            "call_number": call_number,
            "available": available,
            "x": x,
            "y": y
        }],
        ids=[str(id)]
    )

print("TOTAL:", books.collection.count())