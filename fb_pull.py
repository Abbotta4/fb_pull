import requests, json, piexif, os, logging
from configparser import ConfigParser
from datetime import datetime

logging.basicConfig(filename='fb_pull.log',level=logging.DEBUG)

config = ConfigParser()
config.read('config.ini')

BASE_URI = "https://graph.facebook.com/v10.0/" # Graph API version 10.0
ACCESS_TOKEN = config['DEFAULT']['access_token']

def get_request_uri(api_call):
    return BASE_URI + api_call + "&access_token=" + ACCESS_TOKEN

def setup_dir():
    r = requests.get(get_request_uri("me?fields=name"))
    j = json.loads(r.text)
    fb_name = j['name']
    dirname = "photos of " + fb_name

    try:
        os.mkdir(dirname)
        os.chdir(dirname)
    except FileExistsError:
        pass
    except OSError:
        print ("Creation of the directory %s failed" % fb_name)
        return 1
    return 0

def get_photos():
    r = requests.get(get_request_uri("me/photos?type=tagged&fields=images,backdated_time,created_time,from,name,name_tags,place")) #adding album eliminates photos?
    j = json.loads(r.text)
    photos = j['data']
    nphotos = 0
    while True:
        logging.info(photos)
        for photo in photos:
            photo_uri = photo['images'][0]['source'] # assumes first image in 'images' is the highest res
            time = photo['created_time'] if 'backdated_time' not in photo else photo['backdated_time']
            time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y%m%d%H%M%S')
            photographer = photo['from']['name']
            description = False if 'name' not in photo else photo['name']
            try:
                os.mkdir(photographer)
            except FileExistsError:
                pass
            except OSError:
                print ("Creation of the directory {} failed".format(album_dir))
                return -1
            with open(photographer + '/' + time, 'wb') as f:
                r = requests.get(photo_uri)
                f.write(r.content)
                nphotos += 1
        try:
            request_uri = j['paging']['next']
        except KeyError:
            return nphotos
        r = requests.get(request_uri)
        logging.info("getting 'next': " + str(r))
        j = json.loads(r.text)
        photos = j['data']

if __name__ == "__main__":
    print("dumped {} photos".format(get_photos()))
