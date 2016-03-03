import urllib
import cStringIO
from PIL import Image
from functools import partial

# given an object called 'link'


def get_image_size(http_site_url, image_src):
    URL = http_site_url + image_src
    file = cStringIO.StringIO(urllib.urlopen(URL).read())
    im = Image.open(file)
    width, height = im.size
    return width, height

MAILI_URL = 'http://121.40.158.110'
get_image_from_maili = partial(get_image_size, MAILI_URL)


def get_image_from_maili_by_img_list(images):
    images_size = {}
    map(lambda url: images_size.setdefault(url, get_image_from_maili(url)), images)
    return images_size


if __name__ == '__main__':
    images = [
          "/media/origin/22674a8d4f9055ef_uYYJJPK.JPEG",
          "/media/origin/-41136f1eb1c62c15_zuwXuTa.JPEG",
          "/media/origin/-43d2394e4465ba5a_TrOb7lB.JPEG",
          "/media/origin/-2993ed61b26443bd_VcdY0vC.JPEG",
    ]

    print(get_image_from_maili_by_img_list(images))
