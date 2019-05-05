import json
import re

from flask import Flask, jsonify

import tweepy

from twython import Twython, TwythonError
from tweepy import OAuthHandler 
from textblob import TextBlob 
import re
import requests, json
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

consumer_key = 'iSaIm4vG1kI2wGkaiuWYD5vN9'
consumer_secret = '5zBcyyMS20926lWyXNnJq2vjnQNiHMNNHElD7Ymnbc5n5zACJ3'
access_token = '1050518240974258179-9Gpi9dZA77Ivs1hhFy8JThC6iCqY6l'
access_token_secret = 'jy6jeQsdyp9Q2ySlPtrgyckadzYfddmxitvl9cB7uhnAy'

auth = OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret) 
api = tweepy.API(auth) 
twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)

client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017')
db = client.saugs

@app.route('/twitter/<query>')
def get_tweets(query):
    count = 100

    users_with_geodata = {
        "data": []
    }
    all_users = []
    total_tweets = 0
    geo_tweets  = 0

    countries = get_countries_list()
    fetched_tweets = api.search(q = query, count = count) 
    for tweet in fetched_tweets:
        tweet_text = tweet.text
        sentiment_analysis = get_tweet_sentiment(tweet_text)
        if tweet.user.id:
            total_tweets += 1 
            user_id = tweet.user.id
            if user_id not in all_users:
                all_users.append(user_id)
                user_data = {
                    "user_id" : tweet.user.id,
                    "result" : {
                        "name" : tweet.user.name,
                        "id": tweet.user.id,
                        "screen_name": tweet.user.screen_name,
                        "tweets" : 1,
                        "location": tweet.user.location,
                    }
                }
                if tweet.coordinates:
                    user_data["result"]["primary_geo"] = 'US' # str(tweet.coordinates[tweet.coordinates.keys()[1]][1]) + ", " + str(tweet.coordinates[tweet.coordinates.keys()[1]][0])
                    user_data["result"]["geo_type"] = "Tweet coordinates"
                elif tweet.place:
                    user_data["result"]["primary_geo"] = tweet.place.full_name + ", " + tweet.place.country
                    user_data["result"]["geo_type"] = "Tweet place"
                else:
                    user_data["result"]["primary_geo"] = tweet.user.location
                    user_data["result"]["geo_type"] = "User location"
                
                if user_data["result"]["primary_geo"]: 
                    user_data["result"]["analysis_result"] = sentiment_analysis
                    user_data["result"]["country"] = get_country(user_data["result"]["primary_geo"])
                    print(user_data["result"]["country"])
                    if user_data["result"]["country"] is not None:
                        if user_data["result"]["country"] in countries:
                            countries[user_data["result"]["country"]]["total_tweets"] =  countries[user_data["result"]["country"]]["total_tweets"] + 1
                            if sentiment_analysis.sentiment.polarity > 0:
                                countries[user_data["result"]["country"]]["positive"] =  countries[user_data["result"]["country"]]["positive"] + 1
                            elif sentiment_analysis.sentiment.polarity < 0:
                                countries[user_data["result"]["country"]]["negative"] =  countries[user_data["result"]["country"]]["negative"] + 1
                            else:
                                countries[user_data["result"]["country"]]["neutral"] =  countries[user_data["result"]["country"]]["neutral"] + 1
                            
                            total_polarity = countries[user_data["result"]["country"]]["total_polarity"]
                            total_polarity = total_polarity + sentiment_analysis.sentiment.polarity
                            mean = total_polarity / countries[user_data["result"]["country"]]["total_tweets"]
                            countries[user_data["result"]["country"]]["total_polarity"] =  total_polarity
                            countries[user_data["result"]["country"]]["total"] =  mean * 100
                    users_with_geodata['data'].append(user_data)
                    geo_tweets += 1

                elif user_id in all_users:
                    for user in users_with_geodata["data"]:
                        if user_id == user["user_id"]:
                             user["result"]["tweets"] += 1
            for user in users_with_geodata["data"]:
                geo_tweets = geo_tweets + user["result"]["tweets"]
            
    print("The file included " + str(len(all_users)) + " unique users who tweeted with or without geo data")
    print("The file included " + str(len(users_with_geodata['data'])) + " unique users who tweeted with geo data, including 'location'")
    print("The users with geo data tweeted " + str(geo_tweets) + " out of the total " + str(total_tweets) + " of tweets.")
    return jsonify(countries), {'Access-Control-Allow-Origin': '*'}

def get_tweet_sentiment(tweet): 
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet))
    return analysis 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'

def clean_tweet(tweet): 
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

def get_country(location):
    countries_collection = db.countries
    splitted_data = location.split(',')
    country = ''
    if len(splitted_data) > 0:
        city = splitted_data[0]
        splitted_cities = city.split(' ')
        for city in splitted_cities:
            for x in countries_collection.find({ "name" : {"$regex": city, '$options': 'i'} } ):
                country = x["country"]
                break
        if country == "":
            for city in splitted_cities:
                for x in countries_collection.find({ "subcountry" : {"$regex": city, '$options': 'i'} } ):
                    country = x["country"]
                    break
    else:
        for x in countries_collection.find({ "name" : {"$regex": location, '$options': 'i'} } ):
            country = x["country"]
    return country

def get_countries_list():

    countries = {
        "Afghanistan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Albania": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Algeria": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Angola": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Anguilla": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Antigua and Barbuda": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Argentina": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Armenia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Aruba": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Australia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Austria": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Azerbaijan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bahamas, The": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bahrain": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bangladesh": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Barbados": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Belarus": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Belgium": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Belize": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Benin": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bermuda": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bhutan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bolivia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bosnia and Herz.": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Botswana": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Brazil": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "British Virgin Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Brunei": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Bulgaria": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Burkina Faso": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Burundi": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cambodia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cameroon": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Canada": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cape Verde": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cayman Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Central African Rep.": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Chad": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Chile": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "China": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Colombia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Comoros": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Dem. Rep. Congo": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Congo": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cook Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Costa Rica": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Ivory Coast": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Croatia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cuba": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Curacao": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Cyprus": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Czech Rep.": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Denmark": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Djibouti": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Dominica": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Dominican Rep.": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Ecuador": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Egypt": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "El Salvador": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Equatorial Guinea": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Eritrea": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Estonia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Ethiopia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "European Union": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Falkland Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Faroe Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Fiji": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Finland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "France": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "French Polynesia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Gabon": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Gambia, The": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Georgia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Germany": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Ghana": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Gibraltar": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Greece": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Greenland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Grenada": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Guatemala": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Guernsey": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Guinea": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Guinea-Bissau": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Guyana": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Haiti": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Honduras": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Hong Kong": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Hungary": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Iceland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "India": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Indonesia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Iran": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Iraq": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Ireland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Isle of Man": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Israel": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Italy": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Jamaica": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Japan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Jersey": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Jordan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Kazakhstan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Kenya": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Kiribati": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Dem. Rep. Korea": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Korea": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Kosovo": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Kuwait": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Kyrgyzstan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Lao PDR": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Latvia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Lebanon": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Lesotho": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Liberia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Libya": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Liechtenstein": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Lithuania": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Luxembourg": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Macau": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Macedonia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Madagascar": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Malawi": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Malaysia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Maldives": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Mali": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Malta": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Marshall Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Mauritania": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Mauritius": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Mexico": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Micronesia, Federated States of": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Moldova": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Monaco": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Mongolia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Montenegro": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Montserrat": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Morocco": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Mozambique": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Myanmar": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Namibia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Nepal": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Netherlands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "New Caledonia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "New Zealand": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Nicaragua": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Niger": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Nigeria": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Niue": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Norway": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Oman": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Pakistan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Palau": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Panama": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Papua New Guinea": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Paraguay": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Peru": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Philippines": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Poland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Portugal": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Puerto Rico": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Qatar": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Romania": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Russia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Rwanda": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Saint Kitts and Nevis": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Saint Lucia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Saint Martin": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Saint Vincent and the Grenadines": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Samoa": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "San Marino": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Sao Tome and Principe": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Saudi Arabia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Senegal": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Serbia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Seychelles": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Sierra Leone": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Singapore": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Sint Maarten": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Slovakia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Slovenia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Solomon Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Somalia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },        
        "Somaliland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "South Africa": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Spain": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Sri Lanka": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Sudan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "S. Sudan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Suriname": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Swaziland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Sweden": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Switzerland": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Syria": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Taiwan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Tajikistan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Tanzania": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Thailand": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Timor-Leste": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Togo": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Tonga": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Trinidad and Tobago": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Tunisia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Turkey": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Turkmenistan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Turks and Caicos Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Tuvalu": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Uganda": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Ukraine": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "United Arab Emirates": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "United Kingdom": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "United States": {
            "positive": 10, "neutral": 10, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Uruguay": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Uzbekistan": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Vanuatu": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Venezuela": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Vietnam": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "U.S. Virgin Islands": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "West Bank and Gaza": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Western Sahara": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Yemen": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Zambia": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        },
        "Zimbabwe": {
            "positive": 0, "neutral": 0, "negative": 0, "total": 200, "total_tweets": 0, "total_polarity": 0 
        }
    }
    return countries

@app.route('/trends')
def get_trends():
    trends = api.trends_place(id = 1)
    return jsonify({'trends' : trends}), {'Access-Control-Allow-Origin': '*'}

if __name__ == '__main__':
    app.run()
