docker build -t myapp:dev .

docker pull mongo:latest

docker network create container-network

docker rm -f myapp || true
docker rm -f mongo-db || true

docker run -d \
  --name mongo-db \
  --network container-network \
  --network-alias db \
  mongo:latest

#-p exposes real 8080 port and maps to the 8080 container
docker run -it \
  --name myapp \
  --network container-network \
  -p 8080:8080 \
  myapp:dev


