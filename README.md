# How to use

## Quick start
```
docker build -t smart-fashion .

docker run -d --name smart-fashion-container -p 8080:8080 smart-fashion
```

Website: `127.0.0.1:8080`
## Check Docker status
```
docker logs smart-fashion-container
```

## Remove
### 1. Container
```
docker stop smart-fashion-container
docker rm smart-fashion-container
```

### 2. Image
```
docker rmi smart-fashion
```
