#!/bin/bash

SOURCE="<INSERT SOURCE LOCATION HERE>"
DESTINATION="$SOURCE/_Organized"

# Function to handle duplicates and append a number to the filename
handle_duplicate() {
    local file=$1
    local dir=$(dirname "$file")
    local base=$(basename "$file" ."$2")
    local ext=$2
    local counter=1
    while [[ -f "$dir/$base($counter).$ext" ]]; do
        ((counter++))
    done
    echo "$dir/$base($counter).$ext"
}

# Find and move files by year and then by file type
find "$SOURCE" -type f -print0 | while IFS= read -r -d '' file; do
    year=$(stat -f "%Sm" -t "%Y" "$file")
    extension="${file##*.}"
    year_folder="$DESTINATION/$year"
    type_folder="$year_folder/$extension"
    
    mkdir -p "$type_folder"

    # Handling file renaming in case of duplicates
    filename=$(basename -- "$file")
    destination_file="$type_folder/$filename"
    if [[ -f "$destination_file" ]]; then
        destination_file=$(handle_duplicate "$destination_file" "$extension")
    fi

    # Moving the file and logging
    echo "Moving '$file' to '$destination_file'"
    mv "$file" "$destination_file"
done

# Remove empty directories in the source folder
find "$SOURCE" -mindepth 1 -type d -empty -delete

echo "Organization complete."
