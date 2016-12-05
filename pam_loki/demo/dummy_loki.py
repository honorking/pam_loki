#!/usr/bin/env python

import tornado.ioloop
import tornado.web
from tornado.escape import json_decode

USERS_ALLOWED = ['wzyboy', 'wdj', 'doge', 'odin']


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        post_data = json_decode(self.request.body)
        try:
            username = post_data['username']
        #hostname = self.get_body_argument('hostname', None)
        #privilege_type = self.get_body_argument('privilege_type', None)
        #privilege_name = self.get_body_argument('privilege_name', None)
        except KeyError:
            raise tornado.web.HTTPError(400, reason='Missing username')

        if username in USERS_ALLOWED:
            self.write('Authenticated\n')
        else:
            raise tornado.web.HTTPError(403, reason='Permission denied')


if __name__ == '__main__':
    application = tornado.web.Application([
        (r'/api/privilege/authorize', MainHandler),
    ])
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()
