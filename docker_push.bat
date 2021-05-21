docker build -t image-storage .
docker image tag image-storage:latest jdefolter/image-storage:latest
docker push jdefolter/image-storage:latest