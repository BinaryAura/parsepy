#!/usr/bin/env bash

git clone "git@github.com:$1/parsepy.git"
cd parsepy
git remote add upstream git@github.com:BinaryAura/parsepy.git
git fetch upstream
git pull upstream master
git push
cd ..
rm -rf parsepy
pip install "git+ssh://git@github.com/$1/parsepy.git"