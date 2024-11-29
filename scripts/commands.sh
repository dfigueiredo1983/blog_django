#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

wait_psql.sh
echo 'Iniciando o collecstatic.sh'
collectstatic.sh
echo 'Iniciando o migrate.sh'
migrate.sh
echo 'Iniciando o runserver.sh'
runserver.sh