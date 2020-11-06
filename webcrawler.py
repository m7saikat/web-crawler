#!/usr/bin/env python3

import argparse
import re

from custom_requests import *
from collections import deque

# The frontier is the queue of links to be visited. added_links is the list of links added to the frontier to ensure
# the crawler does not revisit any links.
frontier = deque()
added_links = deque()


def check_for_flags(text):
    """
    Checks the response text for the presence of a flag. Prints the flag if it is present

    :param text: the text of a response call
    :return: 1 if a flag exists, 0 if not. Used to increment flag counter
    """
    flag = re.findall(r"FLAG: \w+", text)
    if len(flag) > 0:
        print(flag[0][6:])
        return 1
    return 0


def add_sanitized_links(text):
    """
    Takes all links from a response text, and adds them to the frontier and the added links to prevent duplicates.
    Ensures that all links are fakebook links and no duplicate links are added to the frontier

    :param text: the text of a response call
    """
    links = re.findall(r'"([^"]*)"', text)
    for link in links:
        if link[0:9] == '/fakebook' and link not in added_links:
            frontier.append(link)
            added_links.append(link)


def handle_arguments():
    """
    Fetch the credentials for logging in Fakebook.com via arguments..
    :return: arguments containing username and password
    """
    parser = argparse.ArgumentParser(description='Start crawling www.fakebok.com with the provided credentials')
    parser.add_argument('username',
                        metavar=str("Username provided by the Instructors"),
                        type=str,
                        help="Username for the portal www.fakebook.com")

    parser.add_argument('password',
                        metavar=str("Password provided by the Instructors"),
                        type=str,
                        help="Password to log into the portal www.fakebook.com")


    args = parser.parse_args()
    username = args.username
    password = args.password
    if not username or not password:
        raise ValueError("Username or password cannot be None")
    else:
        return args


def webcrawler():
    """
    Logs into the site and crawls through fakebook to search for the flags.
    Handles 500, 403 and 404 errors. 301 errors are handled in the custom requests process_response function
    The crawler continues until the queue is empty, or until all 5 flags have been found.
    """
    sitename = "http://cs5700.ccs.neu.edu"
    args = handle_arguments()
    login = CustomRequests(args.username, args.password)
    login_cookie = login.login()

    frontier.append('/fakebook/')
    flag_counter = 0
    while len(frontier) > 0:
        # peeks at the queue
        suffix = frontier[0]
        response = login.GET(sitename + suffix, cookie=login_cookie)
        # Checks for 500 error and repeats GET request until a 500 error is no longer received
        if response.status == 500:
            while response.status == 500:
                response = login.GET(sitename + suffix, cookie=login_cookie)
        # Ignores a link and removes it if a 403 or 404 error is received
        if response.status == 403 or response.status == 404:
            frontier.popleft()
        # Searches the text for flags and new links to add to the queue if a valid 200 response code is received
        if response.status == 200:
            frontier.popleft()
            add_sanitized_links(response.text)
            flag_counter += check_for_flags(response.text)
        # If another response call is received, it will ignore the link
        else:
            frontier.popleft()

        # Checks if all 5 flags have been found
        if flag_counter >= 5:
            break


webcrawler()
