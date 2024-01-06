#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Utilisation : $0 <mot_de_passe_postgres>"
    exit 1
fi

POSTGRES_USER="postgres"
POSTGRES_PASSWORD="$1"
ENV_FILE="$HOME/Recommandation_Project/.env"

docker volume create Data

cp ~/Recommandation_Project/application/fichiers/csv/db_sql.csv /var/lib/docker/volumes/Data/_data/

if [ ! -f "$ENV_FILE" ]; then
    echo "POSTGRES_USER=$POSTGRES_USER" > "$ENV_FILE"
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> "$ENV_FILE"
fi

sed -i "s/username = \"xxx\"/username = \"$POSTGRES_USER\"/g" "$HOME/Recommandation_Project/application/.streamlit/secrets.toml"
sed -i "s/password = \"xxx\"/password = \"$POSTGRES_PASSWORD\"/g" "$HOME/Recommandation_Project/application/.streamlit/secrets.toml"

cd ~/Recommandation_Project/
docker-compose up -d

docker cp ./postgresql/init-script.sql recommandation_project_postgres_1:/tmp/ 
docker exec -it recommandation_project_postgres_1 psql -U postgres -d recommandations -a -f /tmp/init-script.sql

