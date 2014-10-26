import urllib2


for i in range(10):
    url = 'http://54.172.148.221:5000/sub/0/' + str(i)
    response = urllib2.urlopen(url)
    html = response.read()
    print html 
