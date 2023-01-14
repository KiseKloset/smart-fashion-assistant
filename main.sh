docker build -t retrieval-api ./retrieval_api
docker build -t tryon-api ./tryon_api   

docker run -d -p 8081:8081 --name retrieval-api retrieval-api
docker run -d -p 8082:8082 --name tryon-api tryon-api

python main_entry/src/main.py