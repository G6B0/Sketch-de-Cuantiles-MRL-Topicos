# Análisis Experimental: MRL Sketch

Este proyecto realiza un análisis experimental del algoritmo MRL Sketch utilizando C++ para el procesamiento de datos y Python para la visualización de resultados.

## Requisitos Previos

Se debe tener instalado:

* **Compilador C++** compatible con el estándar C++14.
* **Python 3** para la generación de gráficos.
* **Librerías de Python** (pandas, numpy).

## Estructura de Datos

El programa requiere una carpeta específica para los datasets.

1.  Crea un directorio llamado `data` en la raíz del proyecto.
2.  Asegúrate de colocar **al menos uno** de los siguientes archivos dentro de esa carpeta:
    * `data/chicago2015.txt`
    * `data/chicago2016.txt`
    * `data/Uniform.txt`
    * `data/Log-normal.txt`

## ⚙️ Compilación y ejecucion

Para compilar el código fuente, utiliza el siguiente comando:

```bash
g++ experimental_analysis.cpp MRL_sketch.cpp -o experimental -std=c++14 -O2
```

Ejecuta el binario generado.

```bash
./experimental
```
Una vez finalizado el experimento, utiliza el script de Python para visualizar los resultados y generar respectivos graficos:
Bash

```bash
python3 plot.py
```
