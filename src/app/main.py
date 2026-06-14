from fastapi import FastAPI

from app.routers import auth, venues, events, feed

app = FastAPI(title="Local Events API", version="0.1.0")

app.include_router(auth.router)
app.include_router(venues.router)
app.include_router(events.router)
app.include_router(feed.router)
