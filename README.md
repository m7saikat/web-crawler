# Project 2: Web Crawler

The project has been implemented in two parts:
* Custom Requests: Implementation of GET, POST HTTP methods using sockets
    -Implemented by Saikat Mukhopadhyay
* Webcrawler: A web crawler to crawl Fakebook to search for secret_flags
    -Implemented by Ryan Newell

## Custom Requests

The custom request is an implementation of the GET and POST HTTP method along with a login method in a `CustomRequests` class. The HTTP methods returns a response object in the following format
```
{
    session: {
    <csrftoken and sessionid information>
    },
    headers: {
    <key value pairs of header fields>
    },
    text: "<texts of the response if any>",
    status: "<status code of the response>"
}
```

The HTTP methods behave as they should normally. The login method logs into the Fakebook with a given credential and returns the updates sessionid. This sessionid is needed with every API call for persisting the login

## Webcrawler

The web crawler logs into fakebook, goes to the fakebook homepage, then adds all non-duplicate links to the frontier and goes to the first entry in the frontier queue. It uses a loop that continues until it has found all 5 flags or the frontier is empty.The crawler can take some time, as it has to check every valid link it sees to find out if it is a duplicate.

The web crawler initially used a stack as its frontier, but that caused it to search a person's friends list pages before it moved on to other people. The friends list pages come after the friends, so they were added last and taken last. Since all flags are in people, the stack was changed to a queue to for search people before going to friends list pages.

One issue faced was filtering the response text into usable links or flags. We ended up using re to find patterns, such as how the flag is always surrounded by FLAG: and >.
# web-crawler
