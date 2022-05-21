#!/bin/bash

tag () {

PREV_VERSION=$(git describe --tags --abbrev=0)

read -p "Previous version is ${PREV_VERSION} please give new version: " NEW_VERSION

git tag -a $NEW_VERSION -m "new version"


}

package() {

CUR_VERSION=$(git describe --tags --abbrev=0)

echo $CUR_VERSION > VERSION

FINADDR_BUILD_VERSION=$CUR_VERSION python3 setup.py sdist

rm -f VERSION

}


publish() {

package
twine upload dist/*

}

$@
