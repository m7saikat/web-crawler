#!/usr/bin/env python3

from CustomRequestUtils import *


class Response:
    """
    Creates a response object with the following attributes:
    session: sessionid of a request
    headers: key value pairs of header fields
    text: texts of the response if any
    status: status code of the response
    """

    def __init__(self, headers=None, text=None):
        self.session = {}
        self.headers = {} if not headers else headers
        self.status = 0 if not headers else int(headers['status_code'])
        self.text = '' if not text else text
        self.session = {} if not headers['session'] else headers['session']


class CustomRequests:
    """
    Implements GET, POST requests using sockets. Also implements a login method which returns the updated cookie
    """

    def __init__(self, username, password):
        """
        Initialize the class variables
        """
        self.ROOT = "http://cs5700.ccs.neu.edu/fakebook/"
        self.LOGIN = "http://cs5700.ccs.neu.edu/accounts/login/?next=/fakebook/"
        self.csrftoken = ''
        self.sessionid = ''
        self.username = username
        self.password = password

    def read_header(self, header):
        """
        Reads the header string and returns a dictionary of the fields in key value pairs

        :param header: header in string format
        :return: dictionary of the fields in the header
        """
        headers_dic = {}
        header_list = header.split('\r\n')
        headers_dic['status_code'] = header_list[0].split()[1]
        headers_dic['session'] = {}
        for heads in header_list[1:]:
            key, val = heads.split(":", 1)
            key = key.strip()
            val = val.strip()

            if key == 'Set-Cookie':
                sess = get_session_obj(val)
                if 'csrftoken' in sess.keys():
                    headers_dic['session'].update(sess)
                    self.csrftoken = headers_dic['session']['csrftoken']
                if 'sessionid' in sess.keys():
                    headers_dic['session'].update(sess)
                    self.sessionid = headers_dic['session']['sessionid']

            headers_dic[key] = val
        return headers_dic

    def process_response(self, response):
        """
        Process the response of a request and handle redirects

        :param response: response of a REST call
        :return: response of the API from the redirected endpoint, if any
        """
        header_str, html = response.split('\r\n\r\n', 1)
        header_dic = self.read_header(header_str)

        if header_dic['status_code'] in ('301', '302'):
            new_url = header_dic['Location']
            hostname, _, _, _ = get_hostname(new_url)
            if hostname not in get_valid_hosts():
                raise RuntimeError
            res = self.GET(new_url)
            header_dic = res.headers
            if 'sessionid' not in header_dic['session'].keys() and self.sessionid:
                header_dic['session'].update({'sessionid': self.sessionid})
            if 'csrftoken' not in header_dic['session'].keys() and self.csrftoken:
                header_dic['session'].update({'csrftoken': self.csrftoken})

            html = res.text
        return header_dic, html

    def send_request(self, url, req_type, data=None, cookie=None):
        """
        This method executes the following actions in the given order:-
        1. Fetch a socket connection to the CCS server,
        2. Form the HTTP/1.1 message(either POST or GET),
        3. Send a request over the socket,
        4. Fetch the response,
        5. Process the response,
        6. Create a response object
        7. Return the response object

        :param url: REST endpoint
        :param req_type: 'POST' or 'GET'. Creates the HTTP message based on these values
        :param data: body of a POST request
        :param cookie: cookie to be sent with the request
        :return: response from the received over the socket
        """

        # 1. Fetch a socket connection to the CCS server,
        hostname, uri, port, ssl_flag = get_hostname(url)
        sock = get_connection(hostname, port, ssl_flag)

        # 2. Form the HTTP/1.1 message(either POST or GET),
        if req_type == 'GET':
            msg = form_GET_msg(hostname, uri).encode('utf-8') if not cookie \
                else form_GET_msg(hostname, uri, cookie).encode('utf-8')
        elif req_type == 'POST' and data:
            msg = form_POST_msg(hostname, uri, data).encode('utf-8') if not cookie \
                else form_POST_msg(hostname, uri, data, cookie).encode('utf-8')
        else:
            raise ValueError("POST request without data")

        #  3. Send a request over the socket,
        sock.sendall(msg)
        res = sock.recv(4096)

        # 5. Process the response,
        header_dic, html = self.process_response(res.decode('utf-8'))

        # 6. Create a response object
        resp_obj = Response(header_dic, html)

        # 7. Return the response object
        return resp_obj

    def GET(self, url, **kwargs):
        """
        Performs a GET Request to a given url

        :param url: endpoint url
        :param kwargs: associated fields of a GET request such as params and cookie
        :return: response of the GET request
        """
        cookie = None
        for key, value in kwargs.items():
            if key == 'params':
                params = value
                str_params = '?'
                for k in params.keys():
                    str_params += "{}={}&".format(k, params[k])
                str_params = str_params[:-1]
                if url[-1] == '/':
                    url = url[:-1]
                url += str_params
            if key == 'cookie':
                cookie = value
        return self.send_request(url, 'GET', None, cookie)

    def POST(self, url, data, cookie=None):
        """
        Performs a POST Request to a given url

        :param url: endpoint url
        :param data: body of the post request
        :param cookie: cookie needed for persisting session while crawling
        :return:  response of the POST request
        """
        return self.send_request(url, 'POST', data) if not cookie else self.send_request(url, 'POST', data, cookie)
        pass

    def login(self):
        """
        Fetches the updated cookie after logging in to Fakebook.

        :return: updated cookie after logging in
        """
        res = self.GET(self.ROOT)
        csrftoken = res.session['csrftoken']['value']

        cookie = build_cookie_string(res.session)
        data = get_data(self.username, self.password, csrftoken)
        post_response = self.POST(self.LOGIN, data, cookie)

        new_cookie = build_cookie_string(post_response.session)

        return new_cookie
