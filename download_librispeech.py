import requests
from tqdm import tqdm
import os
import tarfile


def download_file(url, destination_folder, retries=3, timeout=30):
    local_filename = url.split('/')[-1]
    final_path = os.path.join(destination_folder, local_filename)
    tmp_path = final_path + ".part"

    # Get total size and range support
    try:
        head = requests.head(url, allow_redirects=True, timeout=timeout)
        head.raise_for_status()
        total_size = int(head.headers.get('content-length', 0))
        accept_ranges = head.headers.get('accept-ranges', '').lower() == 'bytes'
    except Exception:
        total_size = 0
        accept_ranges = True  # try resume anyway

    # If already fully downloaded, skip
    if os.path.exists(final_path) and total_size and os.path.getsize(final_path) == total_size:
        print(f"File: {local_filename} already exists. Skipping.")
        return final_path

    existing_size = os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0
    headers = {}
    mode = 'wb'

    if existing_size > 0 and accept_ranges:
        headers['Range'] = f"bytes={existing_size}-"
        mode = 'ab'
    elif existing_size > 0 and not accept_ranges:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass
        existing_size = 0

    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
                r.raise_for_status()

                # Fix total size with Content-Range if present
                if 'content-range' in r.headers:
                    total_size = int(r.headers['content-range'].split('/')[-1])
                else:
                    if total_size == 0:
                        total_size = int(r.headers.get('content-length', 0))
                    if 'Range' in headers and r.status_code != 206:
                        headers.pop('Range', None)
                        mode = 'wb'
                        existing_size = 0

                with open(tmp_path, mode) as f, tqdm(
                    total=total_size if total_size else None,
                    initial=existing_size,
                    unit='iB',
                    unit_scale=True,
                    desc=local_filename
                ) as progress_bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        progress_bar.update(len(chunk))

            # Validate and atomically move
            final_size = os.path.getsize(tmp_path)
            if total_size and final_size != total_size:
                raise IOError(f"Incomplete download: {final_size}/{total_size} bytes.")
            os.replace(tmp_path, final_path)
            print(f"File: {local_filename} Downloaded")
            return final_path

        except Exception as e:
            print(f"Attempt {attempt}/{retries} failed for {local_filename}: {e}")
            if attempt >= retries:
                raise

def extract_tar_file(tar_path, extract_path):
    with tarfile.open(tar_path) as tar:
        tar.extractall(path=extract_path)
    os.remove(tar_path)
    print(f"Extraction completed. Files are extracted to {extract_path}")

# Define the URL of the dataset part you want to download
BASE_URL="http://www.openslr.org/resources/12/"
urls = ["test-clean.tar.gz", "train-clean-360.tar.gz", "train-other-500.tar.gz", "dev-clean.tar.gz", "dev-other.tar.gz"]
#"train-clean-100.tar.gz" >> already downloaded

# Define where you want to save the dataset (make sure this directory exists)
destination_folder = "./corpus/"

if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)

downloaded_files=[]
# Download all files
for url in urls:
    filename = download_file(BASE_URL+url, destination_folder)
    downloaded_files.append(filename)

# Untar files
for filename in downloaded_files:
    extract_tar_file(filename, destination_folder)
