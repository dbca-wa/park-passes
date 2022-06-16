#!/bin/bash
## first parameter is DBCA branch name

set -e
if [[ $# -lt 1 ]]; then
    echo "ERROR: DBCA branch must be specified"
    echo "$0 1"
    exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
#REPO=$(basename -s .git `git config --get remote.origin.url` | sed 's/-//g')
REPO_NO_DASH=$(awk '{split($0, arr, "\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/-//g'|sed 's/....$//'))
REPO=$(awk '{split($0, arr, "\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/....$//'))
BUILD_TAG=oakdbca/$REPO:$1_v$(date +%Y.%m.%d.%H.%M%S)
DBCA_ORIGIN_HASH=$(echo "$REPO" | md5sum -t | cut -c1-32)
DBCA_BRANCH=$DBCA_ORIGIN_HASH"_"$1
EXISTING_REMOTES=$(git remote)

{
    if (( ! $(grep -c "$EXISTING_REMOTES" <<< "$DBCA_ORIGIN_HASH") )); then
        echo "Attempt to create branch"
        echo $REPO
        echo "git remote add $DBCA_ORIGIN_HASH git@github.com:dbca-wa/$REPO.git"
        git remote add $DBCA_ORIGIN_HASH git@github.com:dbca-wa/$REPO.git &&
        git fetch $DBCA_ORIGIN_HASH &&
        git remote set-url --push $DBCA_ORIGIN_HASH no_push &&
        git checkout -b $DBCA_ORIGIN_HASH"_"$1 $DBCA_ORIGIN_HASH"/"$1
    fi
    echo "DBCA branch already exists"
} ||
{
    echo "ERROR: Failed to create dbca branch"
    echo "$0 1"
    exit 1
}

{
    git checkout $DBCA_BRANCH
    echo $(git status)
} ||
{
    echo "ERROR: Failed to checkout dbca branch"
    echo "$0 1"
    exit 1
}
{
    git pull &&
    cd $REPO_NO_DASH/frontend/$REPO_NO_DASH/ &&
    npm run build &&
    cd ../../../ &&
    poetry run python manage.py collectstatic --no-input &&
    git log --pretty=medium -30 > ./git_history_recent &&
    docker image build --no-cache --tag $BUILD_TAG . &&
    git checkout $CURRENT_BRANCH
    echo $BUILD_TAG
} ||
{
    git checkout $CURRENT_BRANCH
    echo "ERROR: Docker build failed"
    echo "$0 1"
    exit 1
}
{
    docker push $BUILD_TAG
} || {
    git checkout $CURRENT_BRANCH
    echo "ERROR: Docker push failed"
    echo "$0 1"
    exit 1
}
