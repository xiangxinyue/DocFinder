import os
import gdown

def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        print(f"Downloading {output_path} from Google Drive")
        gdown.download(id=file_id, output=output_path, quiet=False)
    else:
        print(f"{output_path} already exists, skipping download.")

def setup_database():
    os.makedirs("Database", exist_ok=True)

    #hardcoded fileIDs
    # These are the file IDs for the index and metadata files on Google Drive
    index_file_id = "1OJe2t4SZRNzUAUYWoVtTyXtUSFzXDyL6"
    metadata_file_id = "1Op06GqoKs24YgH_phckH5w4R4H7bz4eX"

    download_file(index_file_id, "Database/wiki_index.faiss")
    download_file(metadata_file_id, "Database/wiki_metadata.pkl")

