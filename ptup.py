import sys
import os
import requests

print("-------- Uploading --------")
if len(sys.argv) < 2:
    print("Nothing to be added")
    sys.exit()

import cloudinary
cloudinary.config(
  cloud_name = os.environ['CLOUD_NAME'],
  api_key = os.environ['API_KEY'],
  api_secret = os.environ['API_SECRET']
)
import cloudinary.uploader
u = cloudinary.uploader.upload
files = sys.argv[1:]
for file in files:
    f = os.path.split(file)
    folder = f[0]
    name = f[1]
    try:
        u(file,
        folder = folder,
        public_id=''.join(name.split('.')[:-1]))
    except:
        print(file + " -- Not an image file! Skipped")
        continue
    print(file + ' uploaded')
    r = requests.get("https://purge.jsdelivr.net/gh/onlya/blog_resources/" + file)
    if r.status_code == 200:
        print(file + ' purged')
    pass

print("DONE uploading!")