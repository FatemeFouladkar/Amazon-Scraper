import random
import logging

class CustomMiddleware(object):

    proxy_pool = ['212.112.113.178:3128',  '144.217.7.157:9300', '163.116.248.46:808']

    def process_request(self, request, spider):

        request.meta['proxy'] = "http://" + random.choice(self.proxy_pool)


    def process_response(self, request, response, spider):

        if response.status in [503]:
            logging.error("%s found for %s so retrying"%(response.status, response.url))
            req = request.copy()
            req.dont_filter = True
            req.meta['proxy'] =  "http://" + random.choice(self.proxy_pool)
            return req
        else:
            return response