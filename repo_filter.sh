#!/bin/bash
set -eux
# This script filter and downloads the repos based on the desired language

# Config
# desired language to look for
DESIRED_LANGUAGE="Java"
# a text file contains a list of repo link (e.g. https://github.com/WillCZhang/ScriptsToolbox) to check, 
REPO_LIST_FILE_NAME="repolist.txt"
# should the desired language be the main language in this repo?
# false (or everything else): this repo contains the desired language
# true: the desired language should be the main language used in this repo
IS_MAJORITY=true
OUTPUT="result.txt"

# Setup workdir
RESULT_FOLDER="result_repo_list_$(date +"%s")"
mkdir "$RESULT_FOLDER"
cp "$REPO_LIST_FILE_NAME" "$RESULT_FOLDER"
cd "$RESULT_FOLDER"

# Setup the language analyzer script
LANGUAGE_ANALYZER_SCRIPT="language_analyzer_script_$(date +"%s")"
echo "require 'rugged'"                                               >> "$LANGUAGE_ANALYZER_SCRIPT"
echo "require 'linguist'"                                             >> "$LANGUAGE_ANALYZER_SCRIPT"
echo "repo = Rugged::Repository.new('.')"                             >> "$LANGUAGE_ANALYZER_SCRIPT"
echo "project = Linguist::Repository.new(repo, repo.head.target_id)"  >> "$LANGUAGE_ANALYZER_SCRIPT"
if [ "$IS_MAJORITY" = true ]; then
  echo "puts project.language"                                        >> "$LANGUAGE_ANALYZER_SCRIPT"
else
  echo "puts project.languages"                                       >> "$LANGUAGE_ANALYZER_SCRIPT"
fi

# use both username & repo to avoid duplicate repo names
REPO_NAMES=$(awk -F '/' '{print $4 "-" $5}' "$REPO_LIST_FILE_NAME")
for REPO_NAME in $REPO_NAMES; do
  git clone --recurse-submodules "https://github.com/$REPO_NAME.git" "$REPO_NAME"
  cp "$LANGUAGE_ANALYZER_SCRIPT" "$REPO_NAME"
  cd "$REPO_NAME"
  # Analyze the repo language structure
  RESULT=$(ruby "$LANGUAGE_ANALYZER_SCRIPT" | grep "$DESIRED_LANGUAGE" | wc -l)
  cd ../
  # Remove the repo the save space
  rm -rf "$REPO_NAME"
  if [ ! $RESULT -eq 0 ]; then
    echo "$REPO_NAME" >> "$OUTPUT"
  fi
done
