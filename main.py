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
from google.appengine.ext import db
from google.appengine.api import memcache

from django.utils import simplejson as json

import helpers

class List(db.Model):
	listid = db.StringProperty()
	name = db.StringProperty()
	url = db.StringProperty()
	image = db.BlobProperty()
	icon = db.BlobProperty()
	created = db.StringProperty()
	owner = db.StringProperty()
	ownericon = db.BlobProperty()
	ownericonurl = db.StringProperty()



class ListItem(db.Model):
	itemkey = db.StringProperty()
	list = db.ReferenceProperty(List)
	itemid = db.StringProperty()
	name = db.StringProperty()
	audio = db.BlobProperty()
	image = db.BlobProperty()
	icon = db.BlobProperty()



api_base_url = "https://api.foursquare.com/v2"

lists = ["4e74ffa97d8b917602deab9b"]

def get_list(listid):
	method = "/lists/"
	oauth_token = "2I0PMFAZOSOGFX5FAPAAKLK0XKEKR4MPUMNW23XJTM3ZP05Z"
	list_url = api_base_url + method + listid + "?oauth_token="+ oauth_token +"&v=20110917"
	data = memcache.get(listid)
	if not data:		
		result = urlfetch.fetch(list_url)
		if result.status_code == 200:
			data = json.loads(result.content)["response"]["list"]
			memcache.add(listid, data, 3600)
	return data


class AppHandler(webapp.RequestHandler):
	def get(self):
		listset = []
		for listid in lists:
			data = get_list(listid)
			listset.append(data)
		template_values = {
			"listset": listset
		}
#		self.response.out.write(listset)
		helpers.render_template(self, "app.html", template_values)





class ListHandler(webapp.RequestHandler):
	def get(self, listid):
		data = get_list(listid)
		list = List.get_or_insert(listid)
		list.listid = data["id"]
		list.name = data["name"]
		list.url = data["url"]
		list.ownericonurl = data["user"]["photo"]
		list.created = str(data["createdAt"])
		list.owner = data["user"]["firstName"] + " " + data["user"]["lastName"]
		list.put()
		self.response.out.write(data["name"])
		self.response.out.write(" | <a href=\"/manage/listpicture/" + data["id"] + "\">add picture</a>")
		self.response.out.write(" | <a href=\"/manage/listicon/" + data["id"] + "\">add icon</a>")
		self.response.out.write("<br />")
		self.response.out.write(data["url"])
		self.response.out.write("<br />")
		self.response.out.write(data["description"])
		self.response.out.write("<br />")
		self.response.out.write(data["createdAt"])
		self.response.out.write("<br />")
		self.response.out.write("<br />")
		items = data["listItems"]["items"]
		for item in items:
			itemkey = data["id"] + "_" + item["venue"]["id"]
			listitem = ListItem.get_or_insert(itemkey, itemkey=itemkey, list=list, name=item["venue"]["name"])
			self.response.out.write(item["venue"]["name"])
			self.response.out.write(" | <a href=\"/manage/itempicture/" + itemkey + "\">add picture</a>")
			self.response.out.write(" | <a href=\"/manage/itemicon/" + itemkey + "\">add icon</a>")
			self.response.out.write(" | <a href=\"/manage/audio/" + itemkey + "\">add audio</a>")
			self.response.out.write(item["venue"])
			self.response.out.write("<br />")
			self.response.out.write("<br />")
		self.response.out.write(data)



class AddPictureHandler(webapp.RequestHandler):
	def get(self, itemid):
		item = ListItem.get_by_key_name(itemid)
		template_values = {
			"media": "picture",
			"url": "/manage/itempicture/",
			"item": item,
			"id": itemid
		}
		helpers.render_template(self, "addmediaform.html", template_values)
	def post(self, itemid):
		item = ListItem.get_by_key_name(itemid)
		item.image = self.request.get("media")
		item.put()
		self.response.out.write("<a href=\"/manage/list/"+ item.list.listid +"\">back</a>")


class AddIconHandler(webapp.RequestHandler):
	def get(self, itemid):
		item = ListItem.get_by_key_name(itemid)
		template_values = {
			"media": "icon",
			"url": "/manage/itemicon/",
			"id": itemid,
			"item": item
		}
		helpers.render_template(self, "addmediaform.html", template_values)
	def post(self, itemid):
		item = ListItem.get_by_key_name(itemid)
		item.icon = self.request.get("media")
		item.put()
		self.response.out.write("<a href=\"/manage/list/"+ item.list.listid +"\">back</a>")


class AddAudioHandler(webapp.RequestHandler):
	def get(self, itemid):
		item = ListItem.get_by_key_name(itemid)
		template_values = {
			"media": "audio",
			"url": "/manage/audio/",
			"item": item,
			"id": itemid
		}
		helpers.render_template(self, "addmediaform.html", template_values)
	def post(self, itemid):
		item = ListItem.get_by_key_name(itemid)
		item.audio = self.request.get("media")
		item.put()
		self.response.out.write("<a href=\"/manage/list/"+ item.list.listid +"\">back</a>")


class AddListPictureHandler(webapp.RequestHandler):
	def get(self, listid):
		item = List.get_by_key_name(listid)
		template_values = {
			"media": "picture",
			"url": "/manage/listpicture/",
			"item": item,
			"id": listid
		}
		helpers.render_template(self, "addmediaform.html", template_values)
	def post(self, listid):
		list = List.get_by_key_name(listid)
		list.image = self.request.get("media")
		list.put()
		self.response.out.write("<a href=\"/manage/list/"+ listid +"\">back</a>")


class AddListIconHandler(webapp.RequestHandler):
	def get(self, listid):
		item = List.get_by_key_name(listid)
		template_values = {
			"media": "icon",
			"url": "/manage/listicon/",
			"item": item,
			"id": listid
		}
		helpers.render_template(self, "addmediaform.html", template_values)
	def post(self, listid):
		list = List.get_by_key_name(listid)
		list.icon = self.request.get("media")
		list.put()
		self.response.out.write("<a href=\"/manage/list/"+ listid +"\">back</a>")
		



class ListAssetHandler(webapp.RequestHandler):
	def get(self, asset_type, listid):
		list = List.get_by_key_name(listid)
		self.response.headers['Content-Type'] = "image/jpeg"
		if asset_type == "icon":
			self.response.out.write(list.icon)
		else:
			self.response.out.write(list.image)


class ItemAssetHandler(webapp.RequestHandler):
	def get(self, asset_type, itemid):
		itemid = itemid.replace("_v", "_")
		item = ListItem.get_by_key_name(itemid)
		if asset_type == "audio":
			self.response.headers['Content-Type'] = "image/jpeg"
			self.response.out.write(item.audio)
		else:
			self.response.headers['Content-Type'] = "image/jpeg"
			if asset_type == "icon":
				self.response.out.write(item.icon)
			else:
				self.response.out.write(item.image)


def main():
    application = webapp.WSGIApplication([
		('/app', AppHandler),
		('/manage/list/(.*)', ListHandler),
		('/manage/listpicture/(.*)', AddListPictureHandler),
		('/manage/listicon/(.*)', AddListIconHandler),
		('/manage/itempicture/(.*)', AddPictureHandler),
		('/manage/itemicon/(.*)', AddIconHandler),
		('/manage/audio/(.*)', AddAudioHandler),
		('/asset/list/(.*)/(.*)', ListAssetHandler),
		('/asset/item/(.*)/(.*)', ItemAssetHandler)
	], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
