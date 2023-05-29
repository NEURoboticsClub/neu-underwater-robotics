
import requests
import shutil
from bs4 import BeautifulSoup
#r = requests.get("http://localhost:5000//video_feed//5000",stream = True)
#r = requests.get("http://localhost:5000//video_feed",stream = True,headers = {'content-type':"image/jpg"})
r = requests.get("http://localhost:5000//video_feed")
print(r.iter_content())
print(r.text)
print(r.json)
if r.status_code == 200:

   # data = BeautifulSoup(r.text,'html.parser')
  #  images = data.find_all('img',src=True)

  #  images = [x['src'] for x in images]
  #  images = ['http://localhost:5000/video_feed/5600']
  #  print(images)

   # for image in images:
      with open("C:/surface/video/test.jpg",'wb') as f:
         # res = requests.get(image)
         # f.write(res.content)

         r.raw.decode_content = True
         shutil.copyfileobj(r.raw,f)
