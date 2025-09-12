import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api import db_test, passport
from app.db.db_setup import Base, engine
import time
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Content Security Policy Middleware
class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'"
        return response


# Performance Monitoring Middleware
class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        return response


app = FastAPI()


# # Initiallizing the logging file
# setup_logging()


# Directory to store the uploaded images
UPLOAD_DIR = "uploads"

"""Mounting the upload folder so that can be shown to the front end"""
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Setup templates
templates = Jinja2Templates(directory="templates")

# These are used to remove the CORS error B/W different server in my case Python Back-end and flutter-dart front-end

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Just for checking if the application is working properly
@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("passport.html", {"request": request})
# async def main():
#     return {"message": "Indus Specialty Application is Working (use: /docs to visit swagger documentation)"}


# Routers Here
# Testing DB Connection
app.include_router(db_test.router)

# Forms APIs
app.include_router(passport.router)





# # This function calls the ORM declerative base so that it may catch the difference and create DB by default if you want to handle all the DB manually by migrations comment this line
# Base.metadata.create_all(bind=engine)


# Application Starting
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5021, reload=True)