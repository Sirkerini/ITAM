from fastapi import FastAPI, Request
from routes import auth, dashboard
from fastapi. templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import  RedirectResponse
from routes.auth import SesionExpirada


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return RedirectResponse(url="/login", status_code=303)

@app.exception_handler(SesionExpirada)
async def manejar_sesion_expirada(request: Request, exc: SesionExpirada):
    return RedirectResponse(
        url="/sesion_exp",
        status_code=303
    )
