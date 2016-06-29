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
	print 'extractAds.py username password size from\n'
        sys.exit(0)

username = sys.argv[1]
password = sys.argv[2]
size = sys.argv[3]
start = sys.argv[4]

url = "https://els.istresearch.com:19200/memex-domains/escorts/_search?size=" + size + "&from=" + start + "&pretty=true"
output, status = query(url, username, password)

if status == 200:
	jout = json.loads(output)
        
	for akey in jout['hits']['hits']:
            print '_id:', akey['_id']
            if 'userlocation' in akey['_source']['extractions']:
 	       print 'location:', akey['_source']['extractions']['userlocation']['results'][0]
            if 'posttime' in akey['_source']['extractions']:
	       print 'post time:', akey['_source']['extractions']['posttime']['results'][0]    
            if 'region' in akey['_source']['extractions']:	    
	       print 'Post ID:', akey['_source']['url'].split('/')[-1], akey['_source']['extractions']['region']['results'][0]
	    print 'Time to extract:', akey['_source']['crawl_data']['context']['timestamp']
 
