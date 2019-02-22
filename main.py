import requests
import urllib2

proxies = {'http': 'http://127.0.0.1:1080', 'https': 'https://127.0.0.1:1080'}
# res = requests.get("http://www.google.com", timeout=1, proxies=proxies)
# print res

proxy_support = urllib2.ProxyHandler(proxies)
opener = urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

res = urllib2.urlopen("http://www.google.com", timeout=1)

print res.code
