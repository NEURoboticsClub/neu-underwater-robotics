## request package
import requests
from  bs4 import BeautifulSoup as bs

r = requests.get("https://bluerobotics.com/wp-content/uploads/2020/01/BlueRobotics-Logo-Blue-Black.png")


if r.status_code == 200:

    with open("C:/surface/video/br_test.jpg",'wb') as f:
        f.write(r.content)
## seleniuum
