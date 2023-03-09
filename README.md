# frp-update-center

frp-update-center is a Python-based update center for frp, a fast reverse proxy written in Python. This update center provides the latest version of frp and its components for different platforms and architectures, and allows users to download them easily.

## Installation

To install frp-update-center, clone this repository to your local machine:

```shell
git clone https://github.com/yourusername/frp-update-center.git
cd frp-update-center
```

Then, install the dependencies using pip:

```
pip install -r requirements.txt
```

## Usage

To start the update center, run the main.py script:

```
python3 main.py
```

This will start a Flask web server at <http://localhost:65527>, which serves the following endpoints:

`/frpc/info`: Returns the latest version of frpc and its download URL for a given operating system and architecture.  
`/frpc/download`: Downloads the latest version of frpc for a given operating system and architecture.
To use the update center, you can send HTTP requests to these endpoints using a web browser or a command-line tool like curl. For example, to get the latest version of frpc for Linux AMD64, you can send a GET request to `http://localhost:65527/frpc/info?os_type=linux&arch=amd64`, which will return a JSON object like this:

```json
{
    "version": "0.37.1",
    "download_url": "https://github.com/fatedier/frp/releases/download/v0.37.1/frpc_linux_amd64.tar.gz"
}
```

To download the latest version of frpc for Linux AMD64, you can send a GET request to `http://localhost:65527/frpc/download?os_type=linux&arch=amd64`, which will download the file to your local machine.

The production environment is recommended to use pm2: `pm2 start main.py --interpreter=python3 --name frp-update-center`.

## License

frp-update-center is licensed under the [MIT License](LICENSE).
