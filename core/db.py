import datetime
from tinydb import TinyDB, Query
from core.formatters import iso_format_datetime


# Add new post to the database
def add_post(title: str, body: str):
    db = TinyDB('db.json')
    posts_table = db.table('posts')
    posts_table.insert({
        'title': title.upper(),
        'body': body,
        'date': str(iso_format_datetime(datetime.datetime.now())),
    })
    db.close()

# Delete a post by title
def delete_post(title: str):
    try:
        db = TinyDB('db.json')
        posts_table = db.table('posts')
        post = Query()
        posts_table.remove(post.title == title.upper())
        db.close()
    except Exception as error:
        raise error

# Get all posts from the database
def get_posts() -> list:
    db = TinyDB('db.json')
    posts_table = db.table('posts')
    posts = posts_table.all()
    db.close()
    if isinstance(posts, list) and len(posts) > 0:
        # Sort posts by date in descending order
        posts.sort(key=lambda x: x['date'], reverse=True)
        for post in posts:
            post['title'] = post['title'].title()
        return posts
    raise ValueError("No posts found in the database.")

# Get a single post by title
def get_post_by_title(title: str) -> dict:
    db = TinyDB('db.json')
    posts_table = db.table('posts')
    post = Query()
    result = posts_table.search(post.title == title.upper())
    db.close()
    if result:
        article = result[0]
        article['title'] = article['title'].title()
        return article
    raise ValueError(f"No post found with title: {title}")
