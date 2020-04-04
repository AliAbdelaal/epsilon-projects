from twitterscraper.query import query_tweets, query_tweets_once_generator

STOP_FLAG = False
SCRAPER_RUNNING = False

def get_tweets_generator(query, limit=None, lang='en'):
    """get a generator to scrape tweets one by one
    
    Arguments:
        query {str} -- the query you want to search with
    
    Keyword Arguments:
        limit {int} -- how much tweets you want at least (default: {None})
        lang {str} -- the language of the tweets you want (default: {'en'})
    
    Yields:
        twitterscraper.tweet.Tweet -- the tweet object with all of it's data
        you can access the following from the Tweet object
        # user name & id
        screen_name
        username
        user_id
        # tweet basic data
        tweet_id
        tweet_url
        timestamp
        timestamp_epochs
        # tweet text
        text
        text_html
        links
        hashtags
        # tweet media
        has_media
        img_urls
        video_url
        # tweet actions numbers
        likes
        retweets
        replies
        is_replied
        # detail of reply to others
        is_reply_to
        parent_tweet_id
        reply_to_users
    """
    for tweet, pos in query_tweets_once_generator(query, lang=lang):
        yield tweet

def scraper_job(query, queue):
    """this function runs in a thread with a thread-safe queue as input to put scraped tweets in it
    
    Arguments:
        query {str} -- the query string
        queue {Queue.queue} -- thread-safe queue to put data in
    """
    global SCRAPER_RUNNING
    SCRAPER_RUNNING = True
    total_tweets = 0
    for tweet in get_tweets_generator(query):
        global STOP_FLAG
        if STOP_FLAG:
            print(f"Scrapper {query} was flagged to stop ....")
            SCRAPER_RUNNING = False
            return
        total_tweets += 1
        if total_tweets %100 == 0:
            print("$"*100)
            print(f"Scrapped total of {total_tweets}...")
            print("$"*100)
        queue.put(tweet)


def update_flag(flag):
    global STOP_FLAG
    STOP_FLAG = flag

def get_scraper_running_status():
    global SCRAPER_RUNNING
    return SCRAPER_RUNNING



if __name__ == "__main__":
    query = "python"
    for tweet in get_tweets_generator(query):
        print(" -- "*50)
        print(tweet.text)
        print(" -- "*50)