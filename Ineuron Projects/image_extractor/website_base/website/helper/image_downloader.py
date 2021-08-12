from selenium import webdriver
import s3fs
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from flask import flash
import requests as rq
from website.helper.creds_helper import aws_creds_provider


def download_images(topic, n_images, user_dir):
    url_prefix = "https://www.istockphoto.com/search/2/image?mediatype=photography&page=2&phrase="
    url_postfix = "&sort=best"

    search_url = url_prefix + topic + url_postfix
    path = r'.\config\chromedriver.exe'

    key, secret = aws_creds_provider()

    fs = s3fs.S3FileSystem(anon=False, key=key, secret=secret)
    dest_path = 'image-extractor/'+user_dir+'/'+topic
    fs.makedirs(dest_path)

    driver = webdriver.Chrome(path)
    driver.get(search_url)
    counter = 1
    value = 0
    while True:
        driver.execute_script("scrollBy(" + str(value) + ",+10000);")
        value += 1000
        time.sleep(1)

        elem1 = driver.find_element_by_class_name('Gallery-module__columnContainer___qTlm6')
        sub = elem1.find_elements_by_tag_name('img')
        for i in sub:
            txt = i.get_attribute('src')

            x = re.search("https://media.istockphoto.com", str(txt))
            if x:
                if counter<=n_images:
                    img_data = rq.get(txt).content
                    with fs.open(dest_path + "/" + str(counter) + '.jpg', 'wb') as f:
                        f.write(img_data)
                    counter += 1
                else:
                    break
        next_button = driver.find_element_by_xpath("/ html / body / div[2] / section / div / main / div / div / div / div[2] / div[2] / section / a[2] / div")
        actions = ActionChains(driver)
        actions.move_to_element(next_button).click().perform()

        if counter>=n_images:
            break

    driver.close()
    flash("download completed for "+topic+" !", category="success")