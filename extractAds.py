from io import BytesIO 
import certifi 
import pycurl
import json
import sys

#Uses pycurl to fetch a site

def query(url, username, password):
  
  output = BytesIO()

  q = pycurl.Curl()
  q.setopt(q.SSL_VERIFYPEER, 0)
  q.setopt(pycurl.POSTFIELDS, '{ "query": { "filtered": { "filter": { "term": { "url.domain": "backpage.com" } } } } }')
  q.setopt(pycurl.USERPWD, "%s:%s" % (str(username), str(password)))
  q.setopt(pycurl.URL, url)
  q.setopt(pycurl.WRITEFUNCTION, output.write)
  
  try:
    q.perform()
    status = q.getinfo(pycurl.HTTP_CODE)

    return output.getvalue(), status
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc), '', ''


if len(sys.argv) < 3:
	print 'extractAds.py username password\n'
        sys.exit(0)

username = sys.argv[1]
password = sys.argv[2]

url = "https://els.istresearch.com:19200/memex-domains/escorts/_search?size=1&from=27057019&pretty=true"
output, status = query(url, username, password)

if status == 200:
	jout = json.loads(output)
        
	for akey in jout['hits']['hits']:
            print '_id', akey['_id']
 	    print 'location', akey['_source']['extractions']['userlocation']['results']
            print 'post time', akey['_source']['extractions']['posttime']['results']    
	    print 'Post ID', akey['_source']['url'].split('/')[-1]
 
