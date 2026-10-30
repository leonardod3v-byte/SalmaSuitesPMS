@echo off
setlocal
echo ============================================================
echo    CONFIGURACION INICIAL DEL PMS - HOTEL SALMA SUITE VIP
echo ============================================================
echo.

:: 1. Backend Setup
echo [1/6] Configurando entorno virtual de Python...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo   Entorno virtual creado.
) else (
    echo   Entorno virtual ya existe.
)

echo.
echo [2/6] Activando entorno virtual e instalando dependencias del Backend...
call backend\venv\Scripts\activate
pip install -r backend\requirements.txt
echo   Dependencias instaladas.

echo.
echo [3/6] Configurando variables de entorno (.env)...
if not exist "backend\.env" (
    echo   Creando archivo .env base...
    (
        echo SECRET_KEY=tu_clave_secreta_aqui
        echo DEBUG=True
        echo.
        echo # EMAIL
        echo EMAIL_HOST_USER=tu_correo@gmail.com
        echo EMAIL_HOST_PASSWORD=tu_app_password
        echo DEFAULT_FROM_EMAIL=Sistema PMS ^<tu_correo@gmail.com^>
        echo.
        echo # BASE DE DATOS (SUPABASE)
        echo DATABASE_URL=postgresql://postgres:TU_PASSWORD@db.TU_PROYECTO.supabase.co:5432/postgres
    ) > backend\.env
    echo   Archivo .env creado. POR FAVOR EDITALO con tus credenciales de Supabase antes de continuar.
    pause
) else (
    echo   Archivo .env ya existe. Asegurate de que tenga la DATABASE_URL de Supabase.
)

echo.
echo [4/6] Ejecutando migraciones de base de datos en Supabase...
cd backend
python manage.py makemigrations
python manage.py migrate
echo   Migraciones aplicadas.

echo.
echo ============================================================
echo    CREACION DE SUPERUSUARIO ADMINISTRADOR
echo ============================================================
echo   Usa 'admin' como username y una contraseña segura.
echo.
python manage.py createsuperuser
cd ..

echo.
echo [5/6] Instalando dependencias del Frontend (puede tardar unos minutos)...
cd frontend
call npm install
cd ..

echo.
echo [6/6] Instalando dependencias raiz (concurrently)...
call npm install

echo.
echo ============================================================
echo    CONFIGURACION COMPLETADA CON EXITO
echo ============================================================
echo.
echo   Para cargar datos de prueba (opcional):
echo     cd backend ^&^& venv\Scripts\activate ^&^& python seed.py
echo.
echo   Para iniciar el sistema localmente:
echo     npm run dev
echo.
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo.
pause
