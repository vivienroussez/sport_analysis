#/bin/zsh

docker run -p 5432:5432 -d \
-e POSTGRES_PASSWORD="test_pg" \
-v ~/Documents/pg_data:/var/lib/postgresql/data \
--name pg_container \
postgres    