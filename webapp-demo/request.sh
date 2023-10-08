#! /bin/bash

# host=$1
# data_folder=$2
# data_file=$3

function pull_request() {
    curl -X POST http://localhost:$1/predict -d @./$2/$3 -H "Content-Type: application/json"
}

pull_request $1 $2 $3