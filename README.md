BusinessInfo-Crawler
====================

BusinessInfo-Crawler
v1.0 更新说明
中山采购 v1.0
这是一个为某个公司所做的外包项目，是我一个人承担的。
公司需要的是公司数据，而我是锻炼技术。

这是一个集合了 网络爬虫，指定地点与关键词，爬取针对的黄页上的所有公司信息。
以及能对Google的数据进行爬取。
还有涉及到网页文本摘要。
采用了多线程技术，BeautifulSoup，正则，浏览器伪装，cookie伪装等方式的爬虫
后来会再进行框架的开发。
其他的慢慢补充。。。

项目文件打包

请确保Python 的环境变量配置好了。
参考http://www.cnblogs.com/babykick/archive/2011/03/25/1995994.html 的第1、2步骤即可

然后双击运行 第一次使用初始化环境.bat 
文件对应什么模块请看：说明文件.txt
运行脚本方式：
右键 py文件， 选择 Edit With IDLE
然后 按F5 运行


findUrls.py 是模块1   寻找GOOGLE 特定URL
ContactFinder.py 是模块2  寻找页面内的公司信息，EMAIL,TEL,ADDRESS等等。。 还有文本提取
yellowPageDataming.py 是模块3 某个黄页的信息提取
FilterRegular.txt是过滤规则  过滤掉不要的页面
database.db是数据库文件 自己设计用来存储这些信息的数据库

以后的改动会写在更新说明里。