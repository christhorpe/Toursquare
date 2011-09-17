#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from django.utils import simplejson as json


api_base_url = "https://api.foursquare.com/v2"


class ListHandler(webapp.RequestHandler):
	def get(self, listid):
		listid = "4e74ffa97d8b917602deab9b"
		method = "/lists/"
		oauth_token = "2I0PMFAZOSOGFX5FAPAAKLK0XKEKR4MPUMNW23XJTM3ZP05Z"
		list_url = api_base_url + method + listid + "?oauth_token="+ oauth_token +"&v=20110917"
		result = urlfetch.fetch(list_url)
		if result.status_code == 200:
			items = json.loads(result.content)["response"]["list"]["listItems"]["items"]
			for item in items:
				
			self.response.out.write(items)


class AddPictureHandler(webapp.RequestHandler):
	def get(self, itemid):
		self.response.out.write("hello")
	def post(self, itemid):
		self.response.out.write("hello")


class AddAudioHandler(webapp.RequestHandler):
	def get(self, itemid):
		self.response.out.write("hello")
	def post(self, itemid):
		self.response.out.write("hello")


def main():
    application = webapp.WSGIApplication([
		('/manage/list/(.*)', ListHandler),
		('/manage/picture/(.*)', AddPictureHandler),
		('/manage/audio/(.*)', AddAudioHandler)
	], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
