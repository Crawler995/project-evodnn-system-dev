docker images | awk '{print $1, $2, $3}' | grep '<none>' | awk '{print $3}' | xargs -I{} docker rmi -f {}