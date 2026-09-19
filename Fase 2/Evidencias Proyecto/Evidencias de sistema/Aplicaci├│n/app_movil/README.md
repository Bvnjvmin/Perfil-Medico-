# App móvil — Perfil Médico+ (Flutter)

Rol: **App Developer (Flutter)** · Sprint 1 (S5-S6) — Autenticación, modelo de datos, estructura base.

## Qué incluye este Sprint 1

- Estructura base del proyecto (`lib/models`, `lib/services`, `lib/screens`).
- Modelo `Usuario` alineado con el esquema `UsuarioOut` del backend.
- `ApiService` que consume los 3 endpoints de autenticación (`/auth/register`, `/auth/login`, `/auth/me`).
- Almacenamiento seguro del JWT (`flutter_secure_storage`), nunca en texto plano.
- 3 pantallas: Login, Registro y Home (protegida).
- 2 pruebas automatizadas (modelo + validación de formulario).

## Instalación

```bash
cd app_movil
flutter pub get
```

## Antes de correr la app: levantar el backend

Desde la carpeta del backend (con Docker):

```bash
cd "Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicación/backend"
cp .env.example .env
docker compose up --build
```

La API queda en `http://localhost:8000` (docs interactivas en `/docs`).

## Configurar la URL de la API según dónde pruebes

En `lib/services/api_service.dart`, la constante `baseUrl` cambia según el entorno:

| Dónde corres la app | `baseUrl` |
|---|---|
| Emulador Android | `http://10.0.2.2:8000` (valor por defecto) |
| Simulador iOS / Flutter Web | `http://localhost:8000` |
| Celular físico (misma red Wi-Fi) | `http://<IP-de-tu-PC>:8000` |

El backend ya tiene CORS abierto (`allow_origins=["*"]`) en `app/main.py`, así que no hay que tocar nada del lado del servidor.

## Ejecutar la app

```bash
flutter run
```

## Ejecutar las pruebas

```bash
flutter test
```

## Flujo implementado

```
LoginScreen ──(sin cuenta)──> RegisterScreen ──(POST /auth/register)──> vuelve a Login
LoginScreen ──(POST /auth/login)──> guarda JWT (secure storage) ──> HomeScreen
HomeScreen ──(GET /auth/me con Bearer token)──> muestra nombre, email y rol
HomeScreen ──(logout)──> borra el token ──> LoginScreen
```

## Checklist Sprint 1 — Rol Frontend

- [x] Proyecto Flutter creado con estructura de carpetas (`models/`, `services/`, `screens/`)
- [x] Modelo `Usuario` en Dart, espejo de `UsuarioOut`
- [x] `ApiService` con `registrar()`, `login()`, `obtenerUsuarioActual()`
- [x] Almacenamiento seguro del token JWT
- [x] Pantalla de registro conectada a `POST /auth/register`
- [x] Pantalla de login conectada a `POST /auth/login` (form-urlencoded, no JSON)
- [x] Pantalla protegida conectada a `GET /auth/me`, con logout
- [x] Pruebas automatizadas (modelo + validación de formulario)
- [ ] Probar el flujo completo con el backend corriendo (registro → login → home → logout)
- [ ] Captura de pantalla / evidencia del flujo funcionando, para el Sprint Backlog / Definition of Done
