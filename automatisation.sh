#!/bin/bash

POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
ENV_FILE="$HOME/Recommandation_Project/.env"

docker volume create Data

cp ~/Recommandation_Project/application/fichiers/csv/db_sql.csv /var/lib/docker/volumes/Data/_data/

if [ ! -f "$ENV_FILE" ]; then
    echo "POSTGRES_USER=$POSTGRES_USER" > "$ENV_FILE"
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> "$ENV_FILE"
fi

sed -i 's/username = "xxx"/username = "postgres"/g' "$HOME/Recommandation_Project/application/.streamlit/secrets.toml"
sed -i 's/password = "xxx"/password = "postgres"/g' "$HOME/Recommandation_Project/application/.streamlit/secrets.toml"

cd ~/Recommandation_Project/
docker-compose up -d

docker exec -it recommandation_project_postgres_1 psql -U postgres -d recommandations -a -f /docker-entrypoint-initdb.d/init-script.sql > /dev/null 2>&1

