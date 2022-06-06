# ArchitectSQLite

Cet outil permet de créer un script sqlite et les fonctions pythons associées à partir d'un schéma
de base de données stocké dans un fichier PowerArchitect.

usage:

```
main.py [-h] [-s SQLITE] [-p PY] script

positional arguments:
  script                     architect script path(*.xml)

optional arguments:
  -h, --help                 show this help message and exit
  -s SQLITE, --sqlite SQLITE sqlite file path, default:script.sqlite
  -p PY, --py PY             python file path, default:architect.py
```


## Script sqlite

| Element | pris en compte | remarque |
|---|---|---|
| CREATE TABLE | [x] | création d'une table |
| TEXT | [x] | type primaire |
| INTEGER | [x] | type primaire |
| BLOB | [x] | type primaire |
| REAL | [x] | type primaire |
| NULL | [x] | type primaire |
| PRIMARY KEY | [x] | clef primaire |
| FOREIGN KEY | [x] | clef étrangère |
| NOT NULL | [x] |  |
| AUTOINCREMENT | [ ] | TODO |

## Fonctions python

Crée deux fonctions par table: une pour insérer une ligne, l'autre pour en insérer plusieurs.
