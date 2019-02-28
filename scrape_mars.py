#!/usr/bin/env python
# coding: utf-8

# In[40]:
from flask import Flask, render_template
import pymongo
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser
import time

app = Flask(__name__)

executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', **executable_path, headless=False)

@app.route("/scrape")
def scrape():
    data = {}
    consolidated = mars_news()
    data["mars_title"] = consolidated["news_title"]
    data["mars_p"] = consolidated["news_p"]
    data["mars_f_image"] = mars_f_image()
    data["mars_weather"] = mars_weather()
    data["mars_table"] = mars_facts()
    data["mars_hemis"] = mars_hemis()
    return data
    
def mars_news():
    consolidated = {}
    news_url = "https://mars.nasa.gov/news/"
# Retrieve page with the requests module
    response = requests.get(news_url)
# Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')

# Retrieve the parent divs for all articles
    result = soup.find('div', class_="image_and_description_container")
#print(result)
    news_p = result.find('div', class_='rollover_description_inner').text
    news_title = result.find_all('img')[1]['alt']
    consolidated["news_p"] = news_p
    consolidated["news_title"] = news_title
# In[76]:
    return consolidated

def mars_f_image():
    f_i_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(f_i_url)

    browser.click_link_by_partial_text('FULL IMAGE')
#find featured image
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    img_container = soup.find('article', class_="carousel_item")
    img_url_long = img_container['style']
    img_url = img_url_long.split("'")[1]
    featured_image_url = f'https://www.jpl.nasa.gov/{img_url}'
    return featured_image_url

# In[79]:


#Find Mars Weather
def mars_weather():
    mars_w_url = "https://twitter.com/marswxreport?lang=en"
# Retrieve page with the requests module
    response = requests.get(mars_w_url)
# Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')
    mars_weather = soup.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    return mars_weather

# In[92]:

#Find Mars Facts
def mars_facts():
    mars_f_url = "https://space-facts.com/mars/"
    tables = pd.read_html(mars_f_url)
    mars_table = tables[0]
#    mars_table.columns = []
    mars_facts = mars_table.to_html()
    return mars_facts

# In[ ]:

#find mars hemisphere images
def mars_hemis():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    mars_hemis=[]
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    for i in range (4):
        time.sleep(5)
        images = browser.find_by_tag('h3')
        images[i].click()
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        partial = soup.find("img", class_="wide-image")["src"]
        img_title = soup.find("h2",class_="title").text
        img_url = 'https://astrogeology.usgs.gov'+ partial
        img_dictionary={"title":img_title,"img_url":img_url}
        mars_hemis.append(img_dictionary)
        browser.back()

    
    return mars_hemis

# =============================================================================
# 
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
# =============================================================================
