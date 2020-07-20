import requests, json, os, logging
from configparser import ConfigParser
from datetime import datetime

logging.basicConfig(filename='fb_pull.log',level=logging.DEBUG)

config = ConfigParser()
config.read('config.ini')

base_uri = "https://graph.facebook.com/v7.0/"
api_call = "me?fields=name,photos{album,link,created_time,name}"
access_token = config['DEFAULT']['access_token']
nphotos = 0

request_uri = base_uri + api_call + "&access_token=" + access_token
r = requests.get(request_uri)
j = json.loads(r.text)
fb_name = j['name']

try:
    os.mkdir(fb_name)
except FileExistsError:
    pass
except OSError:
    print ("Creation of the directory %s failed" % fb_name)
    exit(1)

photos = j['photos']
while True:
    logging.info(photos.keys())
    logging.info(photos)
    for photo in photos['data']:
        album = photo['album']
        album_name = album['name']
        album_ctime = datetime.strptime(album['created_time'], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y%m%d%H%M%S')
        album_dir = fb_name + '/' + album_ctime + '_' + album_name
        try:
            os.mkdir(album_dir)
        except FileExistsError:
            pass
        except OSError:
            print ("Creation of the directory %s failed" % album_dir)
            exit(1)
        link = photo['link']
        with open(album_dir + '/links.txt', 'a') as f:
            f.write(link + '\n')
            nphotos += 1
    try:
        request_uri = photos['paging']['next']
    except KeyError:
        break
    r = requests.get(request_uri)
    logging.info(r)
    j = json.loads(r.text)
    photos = j

print('dumped %d links' % links)
