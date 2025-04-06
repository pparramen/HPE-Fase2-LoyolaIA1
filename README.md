# HPE-Fase2-LoyolaIA1
Este repositorio muestra el software desarrollado por el equipo Loyola IA 1 para la propuesta realiza del Reto de HPE Fase 2.

## Levantar el proyecto en local (Windows)

1. **Clonamos el repositorio**

```bash
git clone https://github.com/pparramen/HPE-Fase2-LoyolaIA1.git
```

2. **Creamos un entorno virtual**

Primero, asegúrate de tener Python instalado.  
Luego, ejecutamos en la terminal (CMD o PowerShell):

```bash
python -m venv hpe
```

3. **Activamos el entorno virtual**

En **Windows**, corremos en el directorio donde hemos tu entorno virtual:

```bash
hpe\Scripts\activate
```

4. **Instalamos las dependencias del proyecto**

```bash
pip install -r requirements.txt
```

5. **Levantamos la aplicación con Streamlit**

```bash
streamlit run home.py
```

6. **Listo**

Abrimos en el buscador la URL que nos aparece en la terminal, normalmente:
```
http://localhost:8501
```

## También se puede acceder al proyecto desplegado en Streamlit a través de:

