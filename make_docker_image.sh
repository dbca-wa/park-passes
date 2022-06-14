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
REPO=$(awk '{split($0, arr, "\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/-//g'|sed 's/....$//'))
DBCA_BRANCH="dbca_"$1
BUILD_TAG=oakdbca/$REPO:$1_v$(date +%Y.%m.%d.%H.%M%S)
{
    git checkout $DBCA_BRANCH
} ||
{
    echo "ERROR: You must have your local code checked in and the DBCA branch set up on local with the 'dbca_' prefix.  Example Instructions:"
    echo "git remote add dbca git@github.com:dbca-wa/wildlifecompliance.git"
    echo "git checkout -b dbca_compliance_mgt_dev dbca/compliance_mgt_dev"
    echo "$0 1"
    exit 1
}
{
    git pull &&
    cd $REPO/frontend/$REPO/ &&
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
