import re
from queue import Queue
import threading
from collections import Counter
import spacy
from Dashboard.scraper import scraper_job, update_flag, get_scraper_running_status

tweets_q = Queue()
analytics_dict = {
    "total_tweets": 0,
    "total_likes": 0,
    "total_retweets": 0,
    "hashtags": [],
    "mentions": [],
    "top_hashtags": [],
    "top_mentions": [],
    "countries": []
}


top_tweets = []
min_retweets = 0
ANALYTICS_THREAD_STATUS = False

nlp = spacy.load("en_core_web_sm")


def init_jobs(queries):
    """
    initialize scraper for each query and make them all append in the same queue, and start the analytics thread
    """
    global ANALYTICS_THREAD_STATUS, tweets_q, analytics_dict, top_tweets, min_retweets
    # clear all the meta data
    analytics_dict = {
        "total_tweets": 0,
        "total_likes": 0,
        "total_retweets": 0,
        "hashtags": [],
        "mentions": [],
        "top_hashtags": [],
        "top_mentions": [],
        "countries": []
    }
    tweets_q.queue.clear()
    top_tweets = []
    min_retweets = 0


    concat_query = " OR ".join(queries)
    # flag the scraping thread to stop
    update_flag(True) 
    # wait till the scraper stops
    while get_scraper_running_status():
        pass
    # release the flag for the new thread to run
    update_flag(False) 
    t = threading.Thread(target=scraper_job, args=(concat_query, tweets_q), name=f"{concat_query}-scrape-thread")
    t.start()
    print(f"started thread to scrap {concat_query}...")
    # check if the analytics job is already running, else start a new job
    if not ANALYTICS_THREAD_STATUS:
        t = threading.Thread(target=analytics_job, args=(tweets_q,), name=f"analytics-thread")
        t.start()
    print("all threads started")


def analytics_job(tweets_q):
    """get the scraped tweets and analyze it
    
    Arguments:
        tweets_q {Queue.queue} -- the tweets queue
    """
    global ANALYTICS_THREAD_STATUS
    ANALYTICS_THREAD_STATUS = True

    # get new tweets
    while True:
        # wait till new tweet is available
        global min_retweets, top_tweets, analytics_dict
        new_tweet = tweets_q.get(block=True, timeout=None)

        # get the tweet info
        likes = new_tweet.likes
        retweets = new_tweet.retweets
        
        tweet_text = str(new_tweet.text).lower()

        # get hashtags and mentions
        hashtags = re.findall(r"#(\w+)", tweet_text)
        mentions = re.findall(r"@(\w+)", tweet_text)
        
        countries = []
        for entity in nlp(new_tweet.text).ents:
            if entity.label_ == "GPE":
                countries.append(str(entity.text))
    
        #append the new data
        analytics_dict['total_tweets'] += 1
        analytics_dict['total_likes'] += likes
        analytics_dict['total_retweets'] += retweets
        analytics_dict['hashtags'] += hashtags
        analytics_dict['mentions'] += mentions
        analytics_dict['countries'] += countries

        # calculate the top hashtags and top mentions
        top_hashtags = Counter(analytics_dict['hashtags']).most_common()[:10]
        analytics_dict['top_hashtags'] = top_hashtags

        top_mentions = Counter(analytics_dict['mentions']).most_common()[:10]
        analytics_dict['top_mentions'] = top_mentions
        
        # top countries
        top_countries = Counter(analytics_dict['countries']).most_common()[:10]
        analytics_dict['top_countries'] = top_countries

        # analyze the tweet to see if it's a top tweet
        if new_tweet.retweets > min_retweets:
            if len(top_tweets)< 3:
                top_tweets.append(new_tweet)
            else:
                # remove the last tweet 
                top_tweets.pop()
                # append the new tweet
                top_tweets.append(new_tweet)
                # sort the tweets
                top_tweets.sort(key=lambda x: x.retweets, reverse=True)
                # update the min retweets
                min_retweets = top_tweets[-1].retweets



        
def get_analytics_dict():
    global analytics_dict
    total_tweets = analytics_dict['total_tweets']
    total_likes = analytics_dict['total_likes']
    total_retweets = analytics_dict['total_retweets']
    hashtags = analytics_dict['top_hashtags']
    mentions = analytics_dict['top_mentions']
    countries = analytics_dict.get('top_countries', [])
    return {
        'total_tweets':total_tweets, 
        'total_likes':total_likes, 
        'total_retweets':total_retweets, 
        'hashtags':hashtags, 
        'mentions':mentions, 
        "countries": countries,
    }
    


def get_top_tweets():
    global top_tweets
    return top_tweets