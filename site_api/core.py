from site_api.utils.api_handler import SiteApiInterface

url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/{ROVER}/photos?' \
      'sol={NUM}&camera={CAM}&api_key='

apod_url = 'https://api.nasa.gov/planetary/apod?api_key='   # URL для фото дня

site_api = SiteApiInterface

if __name__ == '__main__':
    site_api()
