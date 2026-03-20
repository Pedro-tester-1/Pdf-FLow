# PDFJob - Sistema de Gestión de Trabajos PDF

Versión: 1.0.0

## Descripción
Sistema web desarrollado en Django para la gestión de trabajos relacionados con archivos PDF.

## Características
- Gestión de trabajos PDF
- Sistema de autenticación de usuarios
- Interfaz web intuitiva

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/[tu-usuario]/[nombre-repo].git
cd [nombre-repo]
```

2. Crea y activa el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
```

3. Instala las dependencias:
```bash
pip install django
```

4. Ejecuta las migraciones:
```bash
python pdfjob/manage.py migrate
```

5. Inicia el servidor:
```bash
python pdfjob/manage.py runserver
```

## Uso
Accede a `http://127.0.0.1:8000/` en tu navegador.

## Versiones
- v1.0.0 (2026-03-06) - Versión inicial del proyecto
