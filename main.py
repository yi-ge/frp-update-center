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
download_urls_by_version = manager.dict()


# Check for a new version of frp and update the download URLs if a new version
# is found. Returns True if a new version is found and False otherwise.
def check_for_updates():
    global download_urls_by_version
    r = requests.get(
        'https://api.github.com/repos/fatedier/frp/releases/latest')
    if r.status_code != 200:
        return
    latest_version = r.json()['tag_name'][1:]  # remove the 'v' prefix
    download_urls = {}
    for asset in r.json()['assets']:
        download_urls[asset['name']] = asset['browser_download_url']
    if latest_version in download_urls_by_version:
        return False
    download_urls_by_version[latest_version] = download_urls
    print(
        f"Found new version {latest_version} with download URLs: {download_urls}"
    )
    return True


# Download the latest files from the github
def download_files(version):
    global download_urls_by_version
    if version not in download_urls_by_version:
        return False
    base_dir = os.path.join('/data/frp', version)
    os.makedirs(base_dir, exist_ok=True)
    for filename, url in download_urls_by_version[version].items():
        file_path = os.path.join(base_dir, filename)
        print(f"Downloading {url} to {file_path}...")

        r = requests.get(url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # Calculates sha256 values and compares them to the values in the checksum file
    for filename, url in download_urls_by_version[version].items():
        file_path = os.path.join(base_dir, filename)
        with open(file_path, 'rb') as f:
            sha256_value = hashlib.sha256(f.read()).hexdigest()
        expected_sha256_value = None
        with open(os.path.join(base_dir, 'frp_sha256_checksums.txt'),
                  'r') as c:
            for line in c.readlines():
                parts = line.strip().split('  ')
                if len(parts) == 2 and parts[1] == filename:
                    expected_sha256_value = parts[0]
                    if expected_sha256_value != sha256_value:
                        print(
                            f"SHA256 hash mismatch: {expected_sha256_value} (expected) vs {sha256_value}"
                        )
                        os.remove(file_path)
                        return False
                    print(f'{filename} SHA256 hash mismatch: ok')
                    break
    return True


@app.route('/frp/info')
def frp_info():
    os_type = request.args.get('os_type')
    arch = request.args.get('arch')
    version = request.args.get('version')
    if not os_type or not arch:
        return "Missing os_type or arch parameter", 400
    if not version:
        version = max(download_urls_by_version.keys())
    if version not in download_urls_by_version:
        r = requests.get(
            f'https://api.github.com/repos/fatedier/frp/releases/tags/v{version}'
        )
        if r.status_code != 200:
            return f"No information found for version {version}", 404
        download_urls = {}
        for asset in r.json()['assets']:
            download_urls[asset['name']] = asset['browser_download_url']
        download_urls_by_version[version] = download_urls

    for key in download_urls_by_version[version].keys():
        if key.startswith(f"frp_{version}_{os_type}_{arch}"):
            return {
                "version": version,
                "download_url": download_urls_by_version[version].get(key),
            }
    return f"No download URL found for version {version}", 404


@app.route('/frp/download')
def frp_download():
    os_type = request.args.get('os_type')
    arch = request.args.get('arch')
    version = request.args.get('version')
    if not os_type or not arch:
        return "Missing os_type or arch parameter", 400
    if not version:
        version = max(download_urls_by_version.keys())
    if version not in download_urls_by_version:
        r = requests.get(
            f'https://api.github.com/repos/fatedier/frp/releases/tags/v{version}'
        )
        if r.status_code != 200:
            return f"No downloadavailable for version {version}", 404
        download_urls = {}
        for asset in r.json()['assets']:
            download_urls[asset['name']] = asset['browser_download_url']
        download_urls_by_version[version] = download_urls

    for key in download_urls_by_version[version].keys():
        if key.startswith(f"frp_{version}_{os_type}_{arch}"):
            file_path = os.path.join('/data/frp', version, key)
            if not os.path.isfile(file_path):
                if not download_files(version):
                    return f"File {key} not found for version {version} and failed to download it.", 404
            return send_file(file_path, as_attachment=True)
    return f"No download available for version {version}", 404


def check_and_download_files():
    while True:
        if check_for_updates():
            latest_version = max(download_urls_by_version.keys())
            download_files(latest_version)
        time.sleep(5 * 60)


if __name__ == '__main__':
    thread = threading.Thread(target=check_and_download_files)
    thread.start()

    server = pywsgi.WSGIServer(('0.0.0.0', 65527), app)
    server.serve_forever()