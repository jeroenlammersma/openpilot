#!/bin/bash

while read hash submodule ref; do
  branch=$([ "$submodule" = "cereal" ] && echo "driving-coach" || echo "master")
  git -C $submodule fetch --depth 100 origin $branch
  git -C $submodule branch -r --contains $hash | grep "origin/$branch"
  if [ "$?" -eq 0 ]; then
    echo "$submodule ok"
  else
    echo "$submodule: $hash is not on $branch"
    exit 1
  fi
done <<< $(git submodule status --recursive)
