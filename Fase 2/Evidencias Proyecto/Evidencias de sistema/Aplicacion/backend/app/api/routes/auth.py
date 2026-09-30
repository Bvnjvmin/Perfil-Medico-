"""
Endpoints de autenticación.

POST /auth/register  -> crea un usuario nuevo (titular o cuidador)
POST /auth/login      -> recibe email + contraseña, devuelve un token JWT
GET  /auth/me         -> devuelve los datos del usuario dueño del token actual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def register(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario (titular o cuidador)."""
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
        rol=datos.rol,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Inicia sesión. Usa el formulario estándar OAuth2 (username + password),
    donde 'username' es en realidad el correo electrónico.
    """
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise credenciales_invalidas

    access_token = create_access_token(subject=usuario.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UsuarioOut)
def read_current_user(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario propietario del token enviado."""
    return current_user
