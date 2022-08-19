#!/bin/bash
## first parameter is DBCA branch name

set -e
if [[ $# -lt 1 ]]; then
    echo "ERROR: DBCA branch must be specified"
    echo "$0 1"
    exit 1
fi

REPO_NO_DASH=$(awk '{split($0, arr, "\\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/-//g'|sed 's/....$//'))
REPO=$(awk '{split($0, arr, "\\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/....$//'))
BUILD_TAG=oakdbca/$REPO:$1_v$(date +%Y.%m.%d.%H.%M%S)

{
    docker image build --build-arg REPO_ARG=$REPO --build-arg REPO_NO_DASH_ARG=$REPO_NO_DASH --build-arg BRANCH_ARG=$1 --no-cache --tag $BUILD_TAG . &&
    echo $BUILD_TAG
} ||
{
    echo "ERROR: Docker build failed"
    echo "$0 1"
    exit 1
}
{
    docker push $BUILD_TAG
} || {
    echo "ERROR: Docker push failed"
    echo "$0 1"
    exit 1
}
