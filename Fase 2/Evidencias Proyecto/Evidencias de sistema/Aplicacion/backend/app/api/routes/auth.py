"""
Endpoints de autenticación.

POST /auth/register  -> crea un usuario nuevo
POST /auth/login      -> recibe email + contraseña, devuelve un token JWT
GET  /auth/me         -> devuelve los datos del usuario dueño del token actual
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.limitador import LimitadorIntentos
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Frena la adivinanza de contraseñas: ver app/core/limitador.py y las variables LOGIN_* del .env.
limitador_login = LimitadorIntentos()


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def register(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario."""
    ya_existe = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if ya_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta registrada con ese correo",
        )

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=hash_password(datos.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Inicia sesión. Usa el formulario estándar OAuth2 (username + password),
    donde 'username' es en realidad el correo electrónico.

    Tras varios intentos fallidos seguidos (LOGIN_MAX_INTENTOS por cuenta e IP, o
    LOGIN_MAX_INTENTOS_IP por IP) responde 429 hasta que pase la ventana.
    """
    ip = request.client.host if request.client else "desconocida"
    clave_cuenta = f"cuenta:{form_data.username.strip().lower()}|{ip}"
    clave_ip = f"ip:{ip}"
    ventana = settings.LOGIN_VENTANA_MINUTOS * 60
    espera = max(
        limitador_login.segundos_de_espera(clave_cuenta, settings.LOGIN_MAX_INTENTOS, ventana),
        limitador_login.segundos_de_espera(clave_ip, settings.LOGIN_MAX_INTENTOS_IP, ventana),
    )
    if espera:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Espera unos minutos e inténtalo de nuevo.",
            headers={"Retry-After": str(espera)},
        )

    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        limitador_login.registrar_fallo(clave_cuenta)
        limitador_login.registrar_fallo(clave_ip)
        raise credenciales_invalidas

    limitador_login.limpiar(clave_cuenta)
    access_token = create_access_token(subject=usuario.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UsuarioOut)
def read_current_user(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario propietario del token enviado."""
    return current_user
