from tinydb import TinyDB, Query
import datetime
import asyncio

db = TinyDB('db.json')

# Add new post to the database
def add_post(title: str, body: str):
    posts_table = db.table('posts')
    posts_table.insert({
        'title': title.upper(),
        'body': body,
        'date': str(datetime.datetime.now()),
    })

# Get all posts from the database
def get_posts() -> list:
    posts_table = db.table('posts')
    posts = posts_table.all()
    if isinstance(posts, list) and len(posts) > 0:
        # Sort posts by date in descending order
        posts.sort(key=lambda x: x['date'], reverse=True)
        for post in posts:
            post['title'] = post['title'].title()
        return posts

    raise ValueError("No posts found in the database.")

# Get a single post by title
def get_post_by_title(title: str) -> dict:
    posts_table = db.table('posts')
    post = Query()
    result = posts_table.search(post.title == title.upper())
    if result:
        article = result[0]
        article['title'] = article['title'].title()
        return article
    raise ValueError(f"No post found with title: {title}")
