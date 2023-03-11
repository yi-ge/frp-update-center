# frp-update-center

frp-update-center is a Python-based update center for [frp](https://github.com/fatedier/frp), a fast reverse proxy written in Go. This update center provides the latest version of frp and its components for different platforms and architectures, and allows users to download them easily.

## Installation

To install frp-update-center, clone this repository to your local machine:

```shell
git clone https://github.com/yi-ge/frp-update-center.git
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

`/frp/info`: Returns the latest version of frp and its download URL for a given operating system and architecture.  
`/frp/download`: Downloads the latest version of frp for a given operating system and architecture.

The `version` parameter in these endpoints is optional. If it is not specified, the latest version of frp will be used. To get information about a specific version of frp, you can include the version parameter in your request. For example, to get the latest version of frp for Linux AMD64 for version 0.37.1, you can send a GET request to <http://localhost:65527/frp/info?os_type=linux&arch=amd64&version=0.37.1>, which will return a JSON object like this:

```json
{
    "version": "0.37.1",
    "download_url": "https://github.com/fatedier/frp/releases/download/v0.37.1/frp_linux_amd64.tar.gz"
}
```

To download the latest version of frp for Linux AMD64 you can send a GET request to `http://localhost:65527/frp/download?os_type=linux&arch=amd64`, which will download the file to your local machine.

The production environment is recommended to use pm2: `pm2 start main.py --interpreter=python3 --name frp-update-center`.

## License

frp-update-center is licensed under the [MIT License](LICENSE).
