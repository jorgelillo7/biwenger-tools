# Lillorepo 👾

Nuestro monorepo de proyectos y locuras.

## ¿Qué es esto?

Este es un **monorepo**, un lugar centralizado donde guardamos y gestionamos todos nuestros proyectos de software. La idea es simple: en lugar de tener un montón de repositorios pequeños y dispersos, tenemos uno solo, grande y organizado.


Esto nos permite compartir código común de forma muy sencilla, mantener las dependencias bajo control y tener una visión global de todo lo que estamos construyendo.

## Estructura del Repositorio

La organización es la clave. La estructura principal que encontrarás es:

-   `📁 /core`: Nuestra caja de herramientas compartida. Aquí vive toda la lógica, los clientes de API y las utilidades que pueden ser reutilizadas por cualquier proyecto dentro del repo. Si algo se va a usar más de una vez, probablemente debería estar aquí.

-   `📁 /packages`: El corazón del lillorepo. Dentro de esta carpeta vive cada uno de nuestros proyectos principales, agrupados en sus propios directorios. Cada subcarpeta es un universo en sí mismo, pero todos comparten las herramientas de `core`.

## 🛠️ Construido con Bazel

Todo este tinglado se gestiona con **Bazel**, un sistema de construcción que nos permite manejar las dependencias entre los diferentes paquetes de forma eficiente y garantiza que nuestras builds sean rápidas y reproducibles.
