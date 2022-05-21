#!/bin/bash

tag () {

PREV_VERSION=$(git describe --tags --abbrev=0)

read -p "Previous version is ${PREV_VERSION} please give new version: " NEW_VERSION

git tag -a $NEW_VERSION -m "new version"


}

version() {
CUR_VERSION=$(git describe --tags --abbrev=0)

echo $CUR_VERSION > VERSION

}

clean() {
    rm -f VERSION
    rm -rf ./dist/
}

package() {

version

FINADDR_BUILD_VERSION=$CUR_VERSION python3 setup.py sdist

}


publish() {

package
twine upload dist/*

}

$@
