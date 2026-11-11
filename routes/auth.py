from fastapi import APIRouter, Form, HTTPException,status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import crear_users, buscar_user, buscar_id 
import jwt 
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import bcrypt
from fastapi. templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response, FileResponse
from config import SECRET_KEY, ALGORITHM

router = APIRouter()
oauth_scheme = OAuth2PasswordBearer(tokenUrl='/login')

templates = Jinja2Templates(directory="templates")
    
class SesionExpirada(Exception):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
         
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)

    to_encode.update({"exp":expire})
    enconded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return enconded_jwt
    
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise SesionExpirada()
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalido o expiro, {e}")
    


def requiere_rol(*roles_permitidos):
    def verificador(request:Request):
        token = request.cookies.get("token")
        if token is None:
            raise SesionExpirada()

        payload = decode_token(token) 


        user_id = payload['sub']
        usuario = buscar_id(user_id)

        if usuario is None:
            raise SesionExpirada()
        
        if usuario["role_id"] not in roles_permitidos:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos"
            )

        
        return usuario
    return verificador

class User(BaseModel):
    first_name: str
    last_name : str
    email : str
    password : str
    
    

@router.post("/crear_user")
def crear_user(user: User):

    result = crear_users(
        user.first_name,
        user.last_name,
        user.email,
        user.password
        
       
    )
    
    return result


class Login(BaseModel):
    email: str
    password: str
    



@router.post("/login")
def login(response: Response, email: str=Form(), password: str=Form()):

    user = buscar_user(email)

    if user is None:
        return {"error": "Usuario no existe"}

    if not bcrypt.checkpw(
    password.encode("utf-8"),
    user["password"].encode("utf-8")
    ):
        return {"error": "Contraseña incorrecta"}

    
    
    token = create_access_token(
        data={
        "sub": str(user["id"]),
        "username":str(user["first_name"])
         
        }
    )

    if user["role_id"] == 1 or user["role_id"] == 2:
        response = RedirectResponse("/dashboard_adm_it", status_code=303)


    elif user["role_id"] == 3:
        response = RedirectResponse("/reparador", status_code=303)

    else:
        response = RedirectResponse("/login", status_code=303)

    response.set_cookie(
        key="token",
        value=token,
        httponly=True
    )

    return response


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(
        url="/login",
        status_code=303
    )

    response.delete_cookie("token")

    return response


@router.get("/sesion_exp")
def mostrar_sesion_expirada():
    return FileResponse("templates/token_exp.html")
