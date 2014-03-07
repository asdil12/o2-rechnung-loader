#!/usr/bin/python2

import requests
from lxml import etree
import os
import sys

appid = "2FC6CE8BA2C6C9A9E3FF6E726B29826A52A3EE17772D8DD9A766BD6DC8DEA3DF"

if len(sys.argv) < 3:
	print "Usage: ./get.py RUFNUMMER PASSWORT"
	sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]

rechnung_dir = "rechnungen"

s = requests.Session()

r = s.post("https://m.o2online.de/applogin/requestsession", data={"appid": appid})
tree = etree.XML( r.text.encode() )
key = tree.xpath("/serviceResult/key")[0].text

r = s.post("https://m.o2online.de/applogin/login", data={
	"appid": appid,
	"key": key,
	"username": username,
	"password": password
})

r = s.get("https://apps.o2online.de/apps2mce/services/billings")

for rechnung in r.json():
	filename = "%s-%s.pdf" % tuple(rechnung["date"].split("-")[:2])
	docid = rechnung["billDocPart"][0]["billDocID"]
	filepath = os.path.join(rechnung_dir, filename)
	if not os.path.exists(filepath):
		print "Loading %s " % filename,
		r = s.get("https://apps.o2online.de/apps2mce/services/billings/%s/BILL_PDF" % docid, stream=True)
		with open(filepath, "wb") as f:
			for chunk in r.iter_content(1024):
				sys.stdout.write(".")
				sys.stdout.flush()
				f.write(chunk)
		sys.stdout.write("\n")
