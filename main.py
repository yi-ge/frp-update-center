#!/usr/bin/env python3
import os
import glob
import time
import hashlib
import requests
import threading
from flask import Flask, request, send_file
from gevent import pywsgi
import multiprocessing as mp

app = Flask(__name__)

# Creating global variables using shared memory
manager = mp.Manager()
version = manager.Value('i', None)
download_urls = manager.dict()


# Check for a new version of frp and update the download URLs if a new version
# is found. Returns True if a new version is found and False otherwise.
def check_for_updates():
    global version, download_urls
    r = requests.get(
        'https://api.github.com/repos/fatedier/frp/releases/latest')
    if r.status_code != 200:
        return
    latest_version = r.json()['tag_name'][1:]  # remove the 'v' prefix
    download_urls = {}
    for asset in r.json()['assets']:
        download_urls[asset['name']] = asset['browser_download_url']
    if latest_version == version.value:
        return False
    version.value = latest_version
    print(
        f"Found new version {version.value} with download URLs: {download_urls}")
    return True


# Download the latest files from the github
def download_latest_files():
    global version, download_urls
    if not version.value or not download_urls:
        return
    base_dir = os.path.join('/data/frp', version.value)
    os.makedirs(base_dir, exist_ok=True)
    for filename, url in download_urls.items():
        file_path = os.path.join(base_dir, filename)
        print(f"Downloading {url} to {file_path}...")

        r = requests.get(url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # Calculates sha256 values and compares them to the values in the checksum file
    for filename, url in download_urls.items():
        file_path = os.path.join(base_dir, filename)
        with open(file_path, 'rb') as f:
            sha256_value = hashlib.sha256(f.read()).hexdigest()
        expected_sha256_value = None
        with open(os.path.join(base_dir, 'frp_sha256_checksums.txt'), 'r') as c:
            for line in c.readlines():
                parts = line.strip().split('  ')
                if len(parts) == 2 and parts[1] == filename:
                    expected_sha256_value = parts[0]
                    if expected_sha256_value != sha256_value:
                        print(
                            f"SHA256 hash mismatch: {expected_sha256_value} (expected) vs {sha256_value}")
                        os.remove(file_path)
                        download_latest_files()
                        return
                    print(f'{filename} SHA256 hash mismatch: ok')
                    break


@app.route('/frpc/info')
def frpc_info():
    os_type = request.args.get('os_type')
    arch = request.args.get('arch')
    if not os_type or not arch:
        return "Missing os_type or arch parameter", 400
    if not version.value or not download_urls:
        return "No version or download URLs available", 404

    for key in download_urls.keys():
        if key.startswith(f"frp_{version.value}_{os_type}_{arch}"):
            return {
                "version": version.value,
                "download_url": download_urls.get(key),
            }
    return "Download URL not found", 404


@app.route('/frpc/download')
def frpc_download():
    os_type = request.args.get('os_type')
    arch = request.args.get('arch')
    if not os_type or not arch:
        return "Missing os_type or arch parameter", 400
    if not version.value or not download_urls:
        return "No version or download URLs available", 404

    for key in download_urls.keys():
        if key.startswith(f"frp_{version.value}_{os_type}_{arch}"):
            file_path = os.path.join('/data/frp', version.value, key)
            if not os.path.isfile(file_path):
                return f"File {key} not found for version {version.value}", 404
            return send_file(file_path, as_attachment=True)
    return "Download URL not found", 404


# @app.before_first_request
# def find_latest_version():
#     global version
#     all_versions = []
#     for path in glob.glob('/data/frp/*'):
#         if os.path.isdir(path):
#             version_number = os.path.basename(path)
#             try:
#                 version_parts = list(map(int, version_number.split('.')))
#                 if len(version_parts) == 3:
#                     all_versions.append((version_parts, version_number))
#             except ValueError:
#                 pass
#     if all_versions:
#         latest_version = max(all_versions)[1]
#         if latest_version != version:
#             version = latest_version
#             print(f"Found latest version {version}")


def check_and_download_files():
    while True:
        if check_for_updates():
            download_latest_files()
        time.sleep(5 * 60)


if __name__ == '__main__':
    thread = threading.Thread(target=check_and_download_files)
    thread.start()

    server = pywsgi.WSGIServer(('0.0.0.0', 65527), app)
    server.serve_forever()
