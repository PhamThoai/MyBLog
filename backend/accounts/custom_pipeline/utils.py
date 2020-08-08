import requests

def download(url):
    try:
        r = requests.get(url)
        if not r.status_code == 200:
            raise Exception('file request failed with status code: ' + str(r.status_code))
        return (r.content)
    except Exception as ex:
        return None