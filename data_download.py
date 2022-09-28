import numpy as np
import os
from io import BytesIO
import numpy as np
import matplotlib.pylab as plt
import boto3
import glob
import matplotlib.patches as mpatches
#downloading
downloading = False
if downloading:
    aws_access_key_id="<YOUR_ACCESS_KEY_ID>"
    aws_secret_access_key="<YOUR_SECRET_ACCESS_KEY>"
    aws_session_token="<YOUR_SESSION_TOKEN>"
    session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    s3 = session.resource('s3')
    s34 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    my_bucket = s3.Bucket("<NAME_OF_S3_BUCKET>")
    classified_imgs = []
    rgb_images = []
    for i,my_bucket_object in enumerate(my_bucket.objects.all()):
        if i % 2 == 0:
            classified_imgs.append(my_bucket_object.key)
        else:
            rgb_images.append(my_bucket_object.key)
        s34.download_file("landsat-classification-results", f"{my_bucket_object.key}", f"{my_bucket_object.key}")

#opening files
images = []
classified_imgs = glob.glob("classified/*.txt")
rgb_images = glob.glob("rgb/*.txt")

for i, img in enumerate(classified_imgs):
    with open(f"{img}", "rb") as f:
        np_bytes = BytesIO(f.read())
        classified = np.load(np_bytes, allow_pickle=True)
    
    with open(f"{rgb_images[i]}", "rb") as x:
        np_bytesy = BytesIO(x.read())
        rgb = np.load(np_bytesy, allow_pickle=True)

    
    images.append((classified, rgb))

#displaying an image
x = images[1]
fig, axarr = plt.subplots(1, 2)
axarr[0].set_title('Result image')
axarr[1].set_title('RGB image')
axarr[0].set_xlabel('Latitude')
axarr[0].set_ylabel('Longitude')
axarr[1].set_xlabel('Latitude')
axarr[1].set_ylabel('Longitude')

number_pic = 0

axarr[0].imshow(x[0])
axarr[1].imshow(x[1])

colors = ["r", "g", "b", "y", "black"]
texts = ["Urban", "Forest", "Water", "Desert", "Unknown"]
patches = [mpatches.Patch(color=colors[i], label="{:s}".format(texts[i]) ) for i in range(len(texts))]

plt.rcParams['figure.figsize'] = [20, 10]
plt.rcParams['figure.dpi'] = 200 
plt.show()
