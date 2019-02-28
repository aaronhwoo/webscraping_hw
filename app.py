from flask import Flask, render_template
import pymongo
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser
app = Flask(__name__)

# setup mongo connection
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# connect to mongo db and collection
db = client.mars
collection = db.resources

@app.route("/scrape")
def scrape():
    scraps = scraped()
    db.resources.insert_one(scraps)
    return "scraped"

@app.route("/")
def index():
    # write a statement that finds all the items in the db and sets it to a variable
    mars = list(db.collection.find())

    # render an index.html template and pass it the data you retrieved from the database
    return render_template("index.html", mars=mars)


# In[40]:



def scraped():
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
    import time
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
        dictionary={"title":img_title,"img_url":img_url}
        mars_hemis.append(dictionary)
        browser.back()

        scraps["hemisphere_image_urls"] = mars_hemis
    
    return scraps


if __name__ == "__main__":
    app.run(debug=True, port=5001)

    