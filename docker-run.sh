#!/usr/bin/env bash

function generate_sha256()
{
    read -p "Enter a value to generate token: " value
    hash=$(echo "$value" | shasum -a 256 | awk '{print $1}')
    export API_AUTH=$hash
    echo "API_AUTH: $hash"
}

if [ "$1" = "start" ]; then
    generate_sha256
    docker compose up
elif [ "$1" = "stop" ]; then
    docker compose down
fi

