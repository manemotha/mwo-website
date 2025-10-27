import uvicorn
from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse
from starlette import status
import base64

from core.db import add_post, get_posts, get_post_by_title
from core.authentication import token_authenticator, generate_auth_token, compare_hashed_password
from core.models import PasswordAuthModel, UpdatePasswordModel
from core.authentication import authenticate

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
        posts = get_posts()[0:4]
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

@app.post("/delete/article/{title}")
async def delete_article(title: str):
    try:
        from core.db import delete_post
        delete_post(title)
        return RedirectResponse(url="/admin", status_code=303)
    except Exception:
        return {"error": f"Error deleting article: {title}"}

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

@token_authenticator()
@app.get("/admin")
async def admin():

    # List all news articles/posts
    try:
        posts = get_posts()
    except ValueError:
        posts = None

    return template.TemplateResponse(
        name    = "admin.html",
        context = {
            "title": "Admin",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "NEWS": posts,
            "request": {}
        }
    )

@app.get("/login")
async def login():
    return template.TemplateResponse(
        name    = "login.html",
        context = {
            "title": "Login",
            "ORGANIZATION_NAME": ORGANIZATION_NAME,
            "request": {}
        }
    )

@app.post("/password_authentication")
async def password_authentication(payload: PasswordAuthModel):
    """
    Authenticate user and redirect to admin page if successful
    :param payload:
    :return: RedirectResponse to admin page or login page
    """
    is_authenticated = authenticate(payload.model_dump()['password'])

    # Redirect to admin page if authenticated
    if is_authenticated:
        return JSONResponse(content={"message": "Authenticated", "token": generate_auth_token()}, status_code=status.HTTP_200_OK)

    return JSONResponse(content={"message": "Invalid password"}, status_code=status.HTTP_403_FORBIDDEN)

@app.post("/update_password")
async def update_password(payload: UpdatePasswordModel, request: Request):
    """
    Update the authentication password
    :param request:
    :param payload:
    :return: RedirectResponse to login page
    """
    from core.authentication import hash_password
    from tinydb import TinyDB, Query


    # Update the password in the database
    db = TinyDB('db.json')
    auth_table = db.table('auth')
    query = Query()

    # Old password from the database
    old_stored_password = auth_table.get(query.hashed_password.exists())

    # Old request password
    old_password = payload.model_dump()['old_password']

    # Hash the new password
    new_hashed_password: str = hash_password(payload.model_dump()['new_password'])

    if isinstance(old_stored_password, dict) and old_stored_password.get('hashed_password'):

        # Compare old password with the stored password
        comparison_result = compare_hashed_password(old_password, old_stored_password['hashed_password'])

        if comparison_result:
            # Update the password
            auth_table.update({'hashed_password': new_hashed_password}, auth_table.get(query.key == 'hashed_password'))
            db.close()
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return JSONResponse(content={"message": "Old password does not match"}, status_code=status.HTTP_403_FORBIDDEN)

    else:
        # Create new password entry
        auth_table.insert({'hashed_password': new_hashed_password})
        db.close()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

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
