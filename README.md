# Sistema de Gestión de Inventario - DIANCA

Este proyecto es una aplicación web de gestión de stock desarrollada con Django, diseñada para cumplir con los flujos de trabajo de administración de compras, registro de entradas de almacén y auditoría de inventario físico en
la empresa dianca

## 📋 Requisitos del Sistema

Para garantizar la compatibilidad, asegúrese de utilizar el siguiente entorno de ejecución:

* **Python:** 3.13.5 (main, Jun 11 2025)
* **Framework:** Django 6.0.1
* **Base de Datos:** SQLite (para desarrollo) / MySQL (preparado para producción)

---

## 🛠️ Instalación y Configuración

Siga estos pasos para configurar el entorno de desarrollo local:

### 1. Preparar el Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (macOS/Linux)
source venv/bin/activate

# Activar entorno (Windows)
# venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Migrar la base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```


## Gestion de usuarios y roles
### 1. Crear el super usuario inicial
```bash
python manage.py createsuperuser
```

## Ejecución del proyecto
```bash
python manage.py runserver
Luego ir a la direccion local http://127.0.0.1:8000/
```