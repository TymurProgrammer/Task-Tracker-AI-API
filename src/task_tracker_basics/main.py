from task_tracker_basics.routers.auth import auth_router

from fastapi import FastAPI


app = FastAPI(title="Task Tracker AI API")
app.include_router(auth_router)

