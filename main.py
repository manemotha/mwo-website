import uvicorn
from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from core.db import add_post, get_posts, get_post_by_title

app = FastAPI()
template = Jinja2Templates(directory="templates")

# serve files inside /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# project variables
ORGANIZATION_NAME = "MASIQHAKAZE WOMEN ORGANISATION"

# Organization members
MEMBERS = [
    {"img":"1.jpg", "name": "T. Mavuso", "role": "Treasurer"},
    {"img":"2.jpg", "name": "N. Kubheka", "role": "Secretary"},
    {"img":"3.jpg", "name": "S. Nkambule", "role": "Chairperson"},
]

@app.get("/")
async def index():

    # Find two latest news articles/posts
    try:
        posts = get_posts()[0:2]
    except ValueError:
        posts = None

    return template.TemplateResponse(
        name    = "index.html",
        context = {
            "title": "Home",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "MEMBERS": MEMBERS,
            "NEWS": posts,
            "request": {}
        }
    )

@app.get("/articles")
async def article():

    # List all news articles/posts
    try:
        posts = get_posts()
    except ValueError:
        posts = None

    return template.TemplateResponse(
        name    = "news.html",
        context = {
            "title": "News",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "NEWS": posts,
            "request": {}
        }
    )

@app.get("/article/{title}")
async def get_article(title: str):

    # Get a single news article/post by title
    try:
        post = get_post_by_title(title)
    except ValueError:
        post = None

    return template.TemplateResponse(
        name    = "article.html",
        context = {
            "title": post['title'] if isinstance(post, dict) else "News Article",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "POST": post,
            "request": {}
        }
    )

@app.get("/about")
async def about():
    return template.TemplateResponse(
        name    = "about.html",
        context = {
            "title": "About",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "request": {}
        }
    )

@app.get("/admin")
async def admin():
    return template.TemplateResponse(
        name    = "admin.html",
        context = {
            "title": "Admin",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "request": {}
        }
    )

@app.post("/admin/add_post")
async def new_article(title: str = Form(...), body: str = Form(...)):
    """
    Add a new post to the database
    :param title:
    :param body:
    :return: RedirectResponse to admin page
    """
    # Check if article with the same title exists
    try:
        existing_post = get_post_by_title(title)
        # If found, redirect back to admin without adding
        return RedirectResponse(url="/admin", status_code=303)
    except ValueError:
        # Add new post to the database
        add_post(title, body)
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
