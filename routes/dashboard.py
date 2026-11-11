from fastapi import APIRouter, Depends, HTTPException,status, Request, Form, Response
from fastapi.security import OAuth2PasswordBearer
from models import asignados, disponibles, reparaciones, damaged, retirados, insertar, asignar, m_damaged,m_reparacion
from models import salida_mant, mant, stats
from .auth import requiere_rol
from pydantic import BaseModel, StrictInt
from fastapi. templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response


router = APIRouter()
templates = Jinja2Templates(directory="templates")

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/login')



#DASHBOARD GETTT
@router.get("/dashboard/asignados", response_class=HTMLResponse)
def v_asignados(request: Request ,payload = Depends(requiere_rol(1,2))):
  
    result = asignados()
    

    return templates.TemplateResponse(
        request=request,
        name="asignados.html",
        context={
            "asignados": result
            }
    )

@router.get("/dashboard/disponibles", response_class=HTMLResponse)
def v_disponibles(request: Request, usuario = Depends(requiere_rol(1,2))):
    result = disponibles() 
    
    return templates.TemplateResponse(
            request=request,
            name="disponibles.html",
            context={
                "disponibles": result
                }
        )

@router.get("/dashboard/reparaciones", response_class=HTMLResponse)
def v_reparaciones(request: Request, usuario = Depends(requiere_rol(1,3))):
    result = reparaciones() 
    
    return templates.TemplateResponse(
                request=request,
                name="reparaciones.html",
                context={
                    "reparaciones": result
                    }
            )
    

@router.get("/dashboard/damaged", response_class=HTMLResponse)
def v_damaged(request: Request, usuario = Depends(requiere_rol(1,2,3))):
    result = damaged() 
    return templates.TemplateResponse(
                    request=request,
                    name="damaged.html",
                    context={
                        "damaged": result
                        }
                )

@router.get("/dashboard/retirados", response_class=HTMLResponse)
def v_retirados(request: Request, usuario = Depends(requiere_rol(1,2))):
    result = retirados() 
    return templates.TemplateResponse(
                    request=request,
                    name="retirados.html",
                    context={
                        "retirados": result
                        }
                )

#---------------------------------------------
#DASHBOARD POST

#ONLY ADMIN AND TECNIHIAN
class equipo(BaseModel):
    equipo_type_id: StrictInt
    status_id: StrictInt
    brand: str 
    model: str
    serial_number: str 
    purchase_date: str
    warranty_end: str
    description: str


@router.post("/dashboard/agregar_equipo")
def agregar_equipo(
    equipo_type_id: StrictInt=Form(),               
    brand: str=Form() ,
    model: str=Form(),
    serial_number: str=Form() ,
    purchase_date: str=Form(),
    warranty_end: str=Form(),
    description: str=Form(),
    usuario = Depends(requiere_rol(1,2))):

    insertar(equipo_type_id,
    brand,
    model,
    serial_number,
    purchase_date,
    warranty_end, 
    description)
    
    return RedirectResponse(url="/dashboard/disponibles", status_code=303)



@router.get("/dashboard/agregar_equipo", response_class=HTMLResponse)
def formulario_agregar_equipo(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Agregar_equipo.html",
        context={}
    )


#------------------------------------------------------------------------------------

class asignaciones(BaseModel):
    equipo_id : StrictInt
    employee_id : StrictInt
    assigned_by: StrictInt
    notes: str

@router.post("/dashboard/asignar")
def asignar_assets(
    equipo_id :StrictInt=Form(), 
    employee_id:StrictInt=Form(),
    assigned_by:StrictInt=Form(),
    notes:str=Form(),
    usuario = Depends(requiere_rol(1,2))):

    asignar(equipo_id,employee_id,assigned_by,notes)
    return RedirectResponse(url="/dashboard/asignados", status_code=303)



@router.get("/dashboard/asignar", response_class=HTMLResponse)
def form_asignar(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Asignar_equipo.html",
        context={}
    )


#-------------------------------------------------------------------------------


class rotos(BaseModel):
    id: StrictInt
    
@router.post("/dashboard/m_damaged")
def mandar_damaged(id: StrictInt=Form(), usuario=Depends(requiere_rol(1, 2))):
    m_damaged(id)

    return RedirectResponse(url="/dashboard/damaged", status_code=303)

@router.get("/dashboard/m_damaged", response_class=HTMLResponse)
def form_damaged(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="m_damaged.html",
        context={}
    )


#-----------------------------------------------------------------------------------


class rp(BaseModel):
    id: StrictInt
    reported_by: StrictInt
    description: str
    
@router.post("/dashboard/m_reparacion")
def mandar_reparacion(id:StrictInt=Form(),reported_by:StrictInt=Form(),description:str=Form(), usuario=Depends(requiere_rol(1, 2))):
    m_reparacion(id,reported_by,description)

    return RedirectResponse (url="/dashboard/reparaciones", status_code=303)

@router.get("/dashboard/m_reparacion", response_class=HTMLResponse)
def form_reparacion(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="m_reparacion.html",
        context={}
    )
#-----------------------------------------------------------------------------------

#Arreglar esto para reparadores
class mante(BaseModel):
    id: StrictInt

@router.post("/dashboard/salida_mant")
def mant_completado(id:StrictInt=Form(), usuario=Depends(requiere_rol(1, 3))):

    salida_mant(id)
    return RedirectResponse(url="/ver_mant", status_code=303)


@router.get("/dashboard/salida_mant", response_class=HTMLResponse)
def form_mant_completado(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="salida_mant.html",
        context={}
    )


#-----------------------------------------------------------------------------------
@router.get("/ver_mant", response_class=HTMLResponse)
def ver_mant(request:Request ,usuario = Depends(requiere_rol(1,3))):

    result = mant()

    return templates.TemplateResponse(
        request=request,
        name="ver_mant.html",
        context={"result": result}

    )





#-----------------------------------------------------------------------------------
@router.get("/back", response_class=HTMLResponse)
def back_btn(payload=Depends(requiere_rol(1,2,3))):

    if payload['role_id'] == 1 or payload['role_id'] == 2:
        return RedirectResponse(url="/dashboard_adm_it")

    
    
    return RedirectResponse(url="/reparador")

    
    
    

#----------------------
@router.get("/dashboard_adm_it")
def admin(
    request: Request,
    payload=Depends(requiere_rol(1,2))
):

    result = {
    item["status_id"]: item["total"]
    for item in stats()
}
    

    roles = {
            1: "Administrador",
            2: "IT tecnico",
            3: "Reparador"
        }
    
    return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"nombre": payload["first_name"],
                     "rol":roles.get(payload["role_id"],"Desconocido"),
                     "stats_disponibles": result}
        
    )
#------------------------------------------------------------------------------

@router.get("/reparador")
def reparador(
    request: Request,
    payload=Depends(requiere_rol(1,3))
):  

    result = {
        item["status_id"]: item["total"]
        for item in stats()
    }

    
    roles = {
        1: "Administrador",
        2: "IT tecnico",
        3: "Reparador"
    }

    return templates.TemplateResponse(
            request=request,
            name="rp_dashboard.html",
            context={"nombre": payload["first_name"],
                     "rol": roles.get(payload["role_id"],"Desconocido"),
                     "stats_disponibles": result
                    }
        
    )


#---------------------------------------------------------------------------------------------
