@echo off
setlocal
echo === CONFIGURACION INICIAL DEL PMS - HOTEL SALMA SUITE ===

:: 1. Backend Setup
echo [1/3] Configurando entorno virtual de Python...
if not exist "backend\venv" (
    python -m venv backend\venv
)
call backend\venv\Scripts\activate
echo [2/3] Instalando dependencias del Backend...
pip install -r backend\requirements.txt

echo [3/3] Ejecutando migraciones de base de datos...
cd backend
python manage.py migrate
echo.
echo === ATENCION: Crea tu usuario administrador ===
python manage.py createsuperuser
cd ..

:: 2. Frontend Setup
echo.
echo [4/3] Instalando dependencias del Frontend (Esto puede tardar)...
cd frontend
call npm install
cd ..

echo.
echo === CONFIGURACION COMPLETADA CON EXITO ===
echo Para iniciar el sistema usa: npm run dev
echo NOTA: Ejecuta npm install en la raíz del proyecto antes del paso anterior
pause