#!/bin/bash
# Script com atalhos para Docker

# Atalho para listar todas as imagens Docker
alias dimages="docker images"

# Atalho para listar todos os containers (ativos e inativos)
alias dpsall="docker ps -a"

# Atalho para listar apenas os containers ativos
alias dps="docker ps"

# Atalho para parar todos os containers ativos
# Atalho para parar todos os containers ativos
stop_all_containers() {
    # Verifica se há containers ativos
    CONTAINERS=$(docker ps -q)
    
    if [ -z "$CONTAINERS" ]; then
        echo "Nenhum container ativo para parar."
    else
        docker stop $CONTAINERS
        echo "Containers parados: $CONTAINERS"
    fi
}


# Atalho para remover todos os containers (ativos ou inativos)
remove_all_containers() {
    docker rm $(docker ps -aq)
}

# Atalho para remover todas as imagens Docker
remove_all_images() {
    docker rmi $(docker images -q)
}

# Atalho para remover containers e imagens não utilizados (prune)
clean_docker() {
    docker system prune -af
}

echo "Atalhos Docker carregados!"
