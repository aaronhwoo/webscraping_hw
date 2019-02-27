#!/usr/bin/env python
# coding: utf-8

# In[40]:


from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser
import pymongo

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    # executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    scraps = {}
    url = "https://mars.nasa.gov/news/"
# Retrieve page with the requests module
    response = requests.get(url)
# Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')


# In[39]:


# Retrieve the parent divs for all articles
    result = soup.find('div', class_="image_and_description_container")
#print(result)
    news_p = result.find('div', class_='rollover_description_inner').text
    news_title = result.find_all('img')[1]['alt']
    scraps["news_p"] = news_p
    scraps["news_title"] = news_title
# In[76]:


#splinter stuff
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    browser.click_link_by_partial_text('FULL IMAGE')
#find featured image
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    img_container = soup.find('article', class_="carousel_item")
    img_url_long = img_container['style']
    img_url = img_url_long.split("'")[1]
    featured_image_url = f'https://www.jpl.nasa.gov/{img_url}'
    scraps["featured_image_url"] = featured_image_url

# In[79]:


#Find Mars Weather
    url = "https://twitter.com/marswxreport?lang=en"
# Retrieve page with the requests module
    response = requests.get(url)
# Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')
    mars_weather = soup.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    scraps["mars_weather"] = mars_weather

# In[92]:

#Find Mars Facts
    url = "https://space-facts.com/mars/"
    tables = pd.read_html(url)
    mars_table = tables[0]
    mars_facts = mars_table.to_html()
    scraps["mars_facts"] = mars_facts

# In[ ]:


#find mars hemisphere images
    hemisphere_image_urls = [
        {"title": "Valles Marineris Hemisphere", "img_url": "http://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg"},
        {"title": "Cerberus Hemisphere", "img_url": "http://astropedia.astrogeology.usgs.gov/download/Mars/Viking/cerberus_enhanced.tif/full.jpg"},
        {"title": "Schiaparelli Hemisphere", "img_url": "http://astropedia.astrogeology.usgs.gov/download/Mars/Viking/schiaparelli_enhanced.tif/full.jpg"},
        {"title": "Syrtis Major Hemisphere", "img_url": "http://astropedia.astrogeology.usgs.gov/download/Mars/Viking/syrtis_major_enhanced.tif/full.jpg"}    
]
    scraps["hemisphere_image_urls"] = hemisphere_image_urls
# Initialize PyMongo to work with MongoDBs
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
# Define database and collection
    db = client.mars
    collection = db.resources
    collection.insert_one(scraps)

@app.route("/")
def index():
    # write a statement that finds all the items in the db and sets it to a variable
    scraps = list(db.collection.find())
    print(scraps)

    # render an index.html template and pass it the data you retrieved from the database
    return render_template("index.html", scraps=scraps)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
