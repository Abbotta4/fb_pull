import requests, json, piexif, os, logging
from PIL import Image as image
from configparser import ConfigParser
from datetime import datetime

logging.basicConfig(filename='fb_pull.log',level=logging.DEBUG)

config = ConfigParser()
config.read('config.ini')

BASE_URI = "https://graph.facebook.com/v10.0/" # Graph API version 10.0
#api_call = "me/photos"
#api_call = "me?fields=name,photos{album,link,created_time,name}"
ACCESS_TOKEN = config['DEFAULT']['access_token']

def get_request_uri(api_call):
    return BASE_URI + api_call + "&access_token=" + ACCESS_TOKEN

def setup_dirs():
    r = requests.get(get_request_uri("me?fields=name"))
    j = json.loads(r.text)
    fb_name = j['name']

    try:
        os.mkdir(fb_name)
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
    #images = j['data']['images']
    while 'foo' not in j:
        #logging.info(photos.keys())
        #logging.info(photos)
        for photo in photos:
            photo_uri = photo['images'][0]['source'] # assumes first image in 'images' is the highest res
            time = photo['created_time'] if 'backdated_time' not in photo else photo['backdated_time']
            time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y%m%d%H%M%S')
            photographer = photo['from']['name']
            description = photo['name']
            #album = photo['album']
            #album_name = album['name']
            #album_ctime = datetime.strptime(album['created_time'], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y%m%d%H%M%S')
            #album_dir = fb_name + '/' + album_ctime + '_' + album_name
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
