@echo off
setlocal
:: Asegurar que el script se ejecute desde la raíz del proyecto sin importar dónde se llame
cd /d "%~dp0.."

echo ============================================================
echo    CONFIGURACION INICIAL DEL PMS - HOTEL SALMA SUITES VIP
echo ============================================================
echo.

:: 1. Backend Setup
echo [1/5] Configurando entorno virtual de Python...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo   Entorno virtual creado exitosamente.
) else (
    echo   El entorno virtual ya existe.
)

echo.
echo [2/5] Activando entorno virtual e instalando dependencias del Backend...
call backend\venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r backend\requirements.txt
echo   Dependencias del Backend instaladas.

echo.
echo [3/5] Verificando conexion y aplicando migraciones de base de datos...
cd backend
python manage.py migrate
echo   Migraciones aplicadas correctamente.
cd ..

echo.
echo [4/5] Instalando dependencias del Frontend (SvelteKit)...
cd frontend
call npm install
cd ..
echo   Dependencias del Frontend instaladas.

echo.
echo [5/5] Instalando dependencias raiz (Concurrently)...
call npm install
echo   Dependencias raiz instaladas.

echo.
echo ============================================================
echo    CONFIGURACION COMPLETADA CON EXITO
echo ============================================================
echo.
echo  Para iniciar el sistema de desarrollo, ejecuta:
echo    npm run dev
echo.
echo  Frontend : http://localhost:5173
echo  Backend  : http://localhost:8000
echo.
pause
