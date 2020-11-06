#!/usr/bin/env python3

import socket
import ssl
from urllib.parse import urlparse
import re


def get_valid_hosts():
    """
    Return a set of valid hosts

    :return: valid host
    """
    return ['cs5700.ccs.neu.edu']


def form_GET_msg(hostname, uri, cookie=None):
    """
    Weaves the HTTP/1.1 message for a GET request

    :param hostname: hostname or the domain name
    :param uri: endpoint to which the call is made
    :param cookie: cookie needed to be sent to the server
    :return:  HTTP/1.1 GET message
    """
    return "GET {} HTTP/1.1\r\n".format(uri) + \
           "User-Agent: Mozilla/5.0\r\n" + \
           "Host: {}\r\n".format(hostname) + \
           "Cookie: {}\r\n".format(cookie) + \
           "Connection: keep-alive\r\n" + \
           "Accept: */*;\r\n" + \
           "\r\n\r\n"


def form_POST_msg(hostname, uri, data=None, cookie=None):
    """
    Weaves the HTTP/1.1 message for a POST request

    :param hostname: hostname or the domain name
    :param uri: endpoint to which the call is made
    :param data: body of the post request
    :param cookie: cookie needed to be sent to the server
    :return:
    """
    if not data:
        raise RuntimeError("Post data does not have content")

    return "POST {} HTTP/1.1\r\n".format(uri) + \
           "Host: {}\r\n".format(hostname) + \
           "Cookie: {}\r\n".format(cookie) + \
           "Content-Type: application/x-www-form-urlencoded\r\n" + \
           "Content-Length: {}\r\n".format(len(data)) + \
           "\r\n" + "{}".format(data)


def get_hostname(url):
    """
    Generate domain name, uri and port(80 or 443) from the url

    :param url: url
    :return:  domain name, uri, port, ssl_flag
    """
    scheme = re.findall(r'^(http|https)://', url)[0]
    hostname = re.findall(r"://(.*?)/", url)[0]
    uri = re.findall(r"://.*?(/.*)", url)[0]
    if '?' in uri:
        uri = uri.split('?')[0]

    port = 443 if scheme == 'https' else 80
    ssl_flag = True if port is 443 else False
    return hostname, uri, port, ssl_flag


def get_connection(hostname, port, ssl_flag):
    """
    Creates a socket connection to the hostname over a given port

    :param hostname: hostname of the server to which a connection is required
    :param port: port of the server which is accepting the connection
    :param ssl_flag: True if connection is needed over HTTPS False otherwise
    :return: socket object
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ssl_flag:
            s = ssl.create_default_context().wrap_socket(s, server_hostname=hostname)
            s.connect((hostname, port))
        else:
            s.connect((hostname, port))
        return s
    except ValueError:
        raise ValueError("Connection refused")



def get_data(username, password, token):
    """
    Set the credentials of Fakebook in form data format

    :param password: username to login to Fakebook.com
    :param username: password of Fakebook.com
    :param token: csrftoken needed to connect to Fakebook.com
    :return: the credentials in form-data format
    """
    return "username={}".format(username) + \
           "&password={}".format(password) + \
           "&csrfmiddlewaretoken={}".format(token)


def build_cookie_string(session):
    """
    Generate a cookie string in the following format
     "csrftoken=<TOKEN>; sessionid=<SESSION_ID>"

    :param session: session object
    :return: cookie
    """
    csrftoken = session['csrftoken']['value']
    session_id = session['sessionid']['value']
    cookie = "csrftoken={}; sessionid={}".format(csrftoken, session_id)
    return cookie


def get_session_obj(set_cookie_val):
    """
    Creates a session object in the following format
    {
    sessionid :{
            value: XXXX
            date : XXX
        }
    csrftoken :{
        value: XXXX
        date : XXX
        }
    }
    :param set_cookie_val:
    :return:
    """
    temp_dic = {}
    key, value = set_cookie_val.split('=', 1)
    value_list = value.split(';')
    temp_dic[key] = {
        'value': value_list[0]
    }
    for values in value_list[1:]:
        k, val = values.split('=', 1)
        temp_dic[key].update({
            k: val
        })
    return {key: temp_dic[key]}
