@echo off
setlocal
echo ============================================================
echo    CONFIGURACION INICIAL DEL PMS - HOTEL SALMA SUITES VIP
echo ============================================================
echo.

:: 1. Backend Setup
echo [1/5] Configurando entorno virtual de Python...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo   Entorno virtual creado.
) else (
    echo   Entorno virtual ya existe.
)

echo.
echo [2/5] Activando entorno virtual e instalando dependencias del Backend...
call backend\venv\Scripts\activate
pip install -r backend\requirements.txt
echo   Dependencias instaladas.

echo.
echo [3/5] Ejecutando migraciones de base de datos...
cd backend
python manage.py makemigrations
python manage.py migrate
echo   Migraciones aplicadas.

echo.
echo ============================================================
echo    CREACION DE SUPERUSUARIO ADMINISTRADOR
echo ============================================================
echo   Usa 'admin' como username y una contraseña segura.
echo   Email: admin@salmasuite.com (o el que prefieras)
echo.
python manage.py createsuperuser
cd ..

echo.
echo [4/5] Instalando dependencias del Frontend (puede tardar unos minutos)...
cd frontend
call npm install
cd ..

echo.
echo [5/5] Instalando dependencias raiz (concurrently)...
call npm install

echo.
echo ============================================================
echo    CONFIGURACION COMPLETADA CON EXITO
echo ============================================================
echo.
echo   Usuarios por defecto:
echo     Admin:         admin / (la contraseña que creaste)
echo     Recepcionista: recepcion / recepcion123
echo     Recepcionista: recepcion2 / recepcion123
echo.
echo   Para cargar datos de prueba:
echo     cd backend ^&^& venv\Scripts\activate ^&^& python seed.py
echo.
echo   Para iniciar el sistema:
echo     npm run dev
echo.
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo.
pause