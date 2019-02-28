from flask import Flask, render_template, redirect, request
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

app = Flask(__name__)
#setup PyMongo connection

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars"

# setup mongo connection
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# connect to mongo db and collection
db = client.mars
collection = db.resources

@app.route("/scrape")
def scrape():
    #mars = PyMongo(app).db
    scraps = scrape_mars.scrape()
    db.collection.insert_one(scraps)
    #mars.update({}, scraps, upsert=True)
    return redirect("", code=302)

@app.route("/")
def index():
    # write a statement that finds all the items in the db and sets it to a variable
    mars = list(db.collection.find())

    # render an index.html template and pass it the data you retrieved from the database
    return render_template("index.html", mars=mars)


# In[39]:

@app.route('/shutdown')
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Shutting down Flask server...'


if __name__ == "__main__":
    app.run(debug=True, port=5001)

    