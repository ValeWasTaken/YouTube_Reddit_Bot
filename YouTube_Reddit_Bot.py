# Python 3.4
from __future__ import unicode_literals # Support unicode in video titles.
import youtube_dl   # Grab YouTube video information.
import re           # Parse data
import requests     # Handle exceptions
import time         # Enable timed looping
import praw         # Reddit interaction


r = praw.Reddit(
    user_agent='YouTube Reddit Bot - Version 1.1.0'
               'Created by /u/Valestrum AKA /u/Killmail_Bot'
               'Designed to find comments with YouTube links and '
               'reply to the links with the title and length of the video.')
username, password = [line.rstrip('\n') for line in open('user_info.txt')]
r.login(username, password)
subreddit = r.get_subreddit('all')
loop_count = 0


# Catch debug, warnings, and errors for youtube_dl.
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


# Scrape YouTube details for each YouTube link found.
def scrape_info(links):
    output = []
    ydl_opts = {'logger': MyLogger()}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for link in links:
            info = ydl.extract_info(link, download=False)
            title = "[{0}]({1})".format(info['title'], link)
            seconds = info['duration']
            duration = time.strftime('%H:%M:%S', time.gmtime(seconds))
            reply = '>"{0}" - Length: {1}'.format(title, duration)
            output.append(reply)
    return '\n\n'.join(output)


def run_bot():
    # Check existing comment ids.
    with open('cache.txt','r') as cache:
        existing = cache.read().splitlines()
        
    comments = subreddit.get_comments(limit=200)

    with open('cache.txt', 'a+') as cache:
        for comment in comments:
            comment_text = comment.body

            links = [
                item for item in comment_text.split()
                if re.match(r'https://www\.youtube\.com/watch\?v=.*', item)]

            # Check that comment hasn't been seen before and that
            # it meets the desired critera.
            if links and comment.id not in existing:
                    existing.append(comment.id)
                    cache.write(comment.id + '\n')
                    response = scrape_info(links)
                    comment.reply(response)
                    print('New comment found - ID: {0}'.format(comment.id))


while True:
    try:
        run_bot()
    except Exception as e:
        print(e)
    loop_count += 1
    print("Program loop #{0} completed successfully.".format(loop_count))
    time.sleep(140) # Loop once every 140 seconds.
