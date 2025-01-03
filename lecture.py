import os

def get_files_in_subject(folder_path, subject):
    # Initialize an empty list to store file names
    files = []
    
    # Walk through all directories in the folder path
    for root, dirs, filenames in os.walk(folder_path):
        # Check if any directory name matches the subject
        if subject.lower() == os.path.basename(root).lower():
            # If match found, add file names to the list
            files = [os.path.splitext(filename)[0] for filename in filenames]
    
    return files


