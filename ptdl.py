print("-------- Deleting --------")
import sys
import os
if len(sys.argv) < 2:
    print("Nothing to be deleted!")
    sys.exit()
import cloudinary
cloudinary.config(
  cloud_name = os.environ['CLOUD_NAME'],
  api_key = os.environ['API_KEY'],
  api_secret = os.environ['API_SECRET']
)

import cloudinary.uploader
a = sys.argv[1:]
for dl in a:
    try:
        cloudinary.uploader.destroy(''.join(dl.split('.')[:-1]), invalidate=True)
    except:
        print(dl+" -- Not an asset on cloud! Skipped")
        continue
    print(dl+" deleted")
    pass

print("Delete Done!")