import io as systemIo
import asyncio
import json
import requests
import base64
import numpy as np
import matplotlib.pyplot as plt
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from PIL import Image
from matplotlib.patches import ConnectionPatch
from skimage import io, color, exposure, img_as_float
from skimage.measure import regionprops
from skimage.morphology import closing
from types import SimpleNamespace
URL = "https://api.arpa.veneto.it/REST/v1/radar_imgs_geo"


async def process_image(meteoimg, imageIndex):
    dist = await calculateDistance(imageIndex, await filter_image_color(await image_from_bas64(meteoimg)))
    imageIndex += 1
    return dist


async def image_from_bas64(meteoimg):
    return img_as_float(io.imread(systemIo.BytesIO(base64.b64decode(meteoimg.image))))


async def filter_image_color(floatimg):
    red = [1., 0, 0]
    yellow = [252, 251, 49]
    yellow_lab = color.rgb2lab(yellow)
    red_lab = color.rgb2lab(red)
    image_lab = color.rgb2lab(floatimg)
    distance_yellow = color.deltaE_cmc(
        yellow_lab, image_lab, kL=0.5, kC=0.5).squeeze()
    distance_red = color.deltaE_cmc(
        red_lab, image_lab, kL=0.5, kC=0.5).squeeze()
    distance = distance_yellow - distance_red
    distance = exposure.rescale_intensity(distance)
    image_yellow = floatimg.copy()
    image_yellow[distance < 0.9] = 0
    f, ax = plt.subplots()
    f.set_size_inches(10, 10)
    ax.set_axis_off()
    ax.imshow(image_yellow, aspect='auto')
    plt.plot(1450, 1400, "ro")
    f.canvas.draw()
    im = Image.frombytes('RGB', f.canvas.get_width_height(),
                         f.canvas.tostring_rgb())
    return np.array(im)


async def calculateDistance(imageIndex, img):
    imageFinalElaboration = f"finalElaboration{imageIndex}.png"
    yellow = [252, 251, 49]
    red = [255, 0, 0]
    threshold = 10
    dist_from_yellow = np.linalg.norm(img - yellow, axis=-1)
    dist_from_red = np.linalg.norm(img - red, axis=-1)
    yellow_blob = closing(dist_from_yellow < threshold)
    red_blob = closing(dist_from_red < threshold)
    labels = np.zeros(shape=img.shape[:2], dtype=np.ubyte)
    labels[yellow_blob] = 1
    labels[red_blob] = 2
    blobs = regionprops(labels)
    dist = 0
    if len(blobs) >= 2:
        center_0 = np.asarray(blobs[0].centroid[::-1])
        center_1 = np.asarray(blobs[1].centroid[::-1])
        dist = np.linalg.norm(center_0 - center_1)
        f, ax = plt.subplots()
        f.set_size_inches(10, 10)
        ax.set_axis_off()
        ax.imshow(img, aspect='auto')
        con = ConnectionPatch(xyA=center_0, xyB=center_1,
                              coordsA='data', arrowstyle="-|>", ec='yellow')
        ax.add_artist(con)
        plt.annotate('Distance = {:.2f}'.format(dist),
                     xy=(center_0 + center_1)/2, xycoords='data',
                     xytext=(0.5, 0.7), textcoords='figure fraction', color='blue',
                     arrowprops=dict(arrowstyle="->", color='blue'))
        plt.savefig(imageFinalElaboration)
    return dist


async def send_mail(send_to, text, files=None,
                    server="127.0.0.1"):
    assert isinstance(send_to, list)
    send_from = ""
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Meteo Alarm"

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


async def main():
    r = requests.get(url=URL)
    imageIndex = 0
    response = json.loads(json.dumps(r.json()),
                          object_hook=lambda d: SimpleNamespace(**d))
    response.data.sort(key=lambda x: x.date)
    distances = []
    orderedElement = 0

    for imageIndex, meteoimg in enumerate(response.data):
        d = await process_image(meteoimg, imageIndex)
        if d > 0:
            if (len(distances) != 0 and distances[-1] > d) or len(distances) == 0:
                orderedElement += 1
            distances.append(d)
    print(orderedElement)
    print(distances)
    if orderedElement > len(distances)/2:
        print("invio mail")
        # await send_mail()

if __name__ == '__main__':
    if __debug__:
        asyncio.run(main())

