#!/bin/bash

# config
DESIRED_LANGUAGE="Java"
REPO_LIST_FILE_NAME="repolist.txt"

# workdir
RESULT_FOLDER="result_repo_list_$(date +"%s")"
mkdir "$RESULT_FOLDER"
mv "$REPO_LIST_FILE_NAME" "$RESULT_FOLDER"
cd "$RESULT_FOLDER"

# script for analyzing repo language structure
LANGUAGE_ANALYZER="
require 'rugged'
require 'linguist'
repo = Rugged::Repository.new('.')
project = Linguist::Repository.new(repo, repo.head.target_id)
puts project.language
"

# use both username & repo to avoid duplicate repo names
REPO_NAMES=$(awk -F '/' '{print $4 "/" $5}' "$REPO_LIST_FILE_NAME")
for REPO_NAME in $REPO_NAMES; do
  git clone --recurse-submodules "https://github.com/$REPO_NAME.git" "$REPO_NAME"
  cd "$REPO_NAME"
  # analyze the repo language structure
  LANGUAGE_ANALYZER_SCRIPT="language_analyzer_script_$(date +"%s")"
  echo $LANGUAGE_ANALYZER >> "$LANGUAGE_ANALYZER_SCRIPT"
  RESULT=$(ruby "$LANGUAGE_ANALYZER_SCRIPT" | grep "$DESIRED_LANGUAGE" | wc -l)
  cd ..
  # remove this repo if the main language isn't the desired language
  if [ $RESULT -eq 0 ]; then
    rm -rf "$REPO_NAME"
  fi
done
