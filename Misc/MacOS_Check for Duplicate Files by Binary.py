import os
import hashlib
import send2trash
import easygui

def get_hash(file_path):
    print(f"Getting hash for file: {file_path}")
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def scan_for_duplicates(directory):
    print(f"Scanning directory: {directory}")
    hashes = {}
    duplicates = []

    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_hash = get_hash(file_path)

            if file_hash in hashes:
                duplicates.append((file_path, hashes[file_hash]))
            else:
                hashes[file_hash] = file_path

    return duplicates

def main():
    directory = easygui.diropenbox(title="Select directory to scan for duplicate files")
    print(f"Selected directory: {directory}")

    if not os.path.isdir(directory):
        print("Directory does not exist. Please try again.")
        return

    print("Scanning for duplicate files...")
    duplicates = scan_for_duplicates(directory)

    if not duplicates:
        print("No duplicate files found.")
        return

    print("The following duplicate files were found:")
    for dup, orig in duplicates:
        print(f"Duplicate: {dup} \nOriginal: {orig}\n")

    response = easygui.ynbox("Do you want to move these duplicate files to the trash?", choices=('Yes', 'No'))

    if response:
        for dup, _ in duplicates:
            send2trash.send2trash(dup)
        print("Duplicates moved to trash.")
    else:
        print("Not moving duplicates to trash.")

if __name__ == "__main__":
    print("Starting script...")
    main()
