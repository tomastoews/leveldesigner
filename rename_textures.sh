#!/bin/bash

if [ -z $1 ]; then
	echo "The folder name is required"
	exit 1
fi

folder=./resources/textures/$1

if [ ! -d $folder ]; then
	echo "Folder does not exist"
	exit 1
fi

for file in $(ls $folder);
do
	number="$(echo $file | grep --only-matching '[0-9][0-9]*')"
	[ -n $number ] && mv $folder/$file "$folder/$number.png"
done
