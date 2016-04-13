import urllib
import cStringIO
from PIL import Image
from functools import partial

# given an object called 'link'


def get_image_size(http_site_url, image_src):
  try:
      URL = http_site_url + image_src
      file = cStringIO.StringIO(urllib.urlopen(URL).read())
      im = Image.open(file)
      width, height = im.size
      return width, height
  except Exception as e:
      print e
      return "Pciture Unvalid", "Picture Unvalid"

MAILI_URL = 'http://121.40.158.110/media/'
get_image_from_maili = partial(get_image_size, MAILI_URL)


def get_image_from_maili_by_img_list(images):
    images_size = {}
    map(lambda url: images_size.setdefault(url, get_image_from_maili(url)), images)
    return images_size


if __name__ == '__main__':
    images = [
          "origin/377743001"
    ]

    print(get_image_from_maili_by_img_list(images))
