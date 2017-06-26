Hazeweb
==================================================================================================================
- 实现功能 ： 以linux服务器为后端，搭建web服务和mysql数据库服务。
------------------------------------------------------------------------------------------------------------------
	mysql数据库：负责存放远程雾霾监测机器发送而来的实时雾霾数据。
	web服务：以Python语言开发的aiohttp为web框架，来对接微信服务接口，来实现提取mysql数据库数据传送给微信公众号服务。

关于aiohttp的web框架：
--------------------------------------------------------------------------------------------------------------------
	app.py 是web服务运行主体程序。
	orm.py 数据库操作底层程序，数据库对象映射程序。
	models.py 定义你将会用到哪些数据库表单，并定义数据库表单中元素有哪些，数据类型是什么。
	coroweb.py 对与aiohttp的web框架进行再封装。主要是对请求url的方法和参数进行判断和提取的一些类方法，并结合handler.py调用，来实现对与不同请求，进行对处理。
	handler.py web 请求处理函数，定义了不同请求，用对应方法处理，并返还给用用户请求结果。
	static 目录是存放你未来搭建网页所需前端部分的框架（css,js）,此处未用未创建

关于微信部分程序
---------------------------------------------------------------------------------------------------------------------
	微信公众号大概原理:微信公众号是当用户发送给公众号请求时，微信公众号会把用户请求包装，给web服务器发送一个对应的http请求，web会处理此请求，并把结果返还给公众号，公众号再把结果进行对应解析，发送给用户。	
	handler.py 就是把公众号发送来的请求进行处理，再返还给公众号，定义了一系列处理方法。
	recevie.py 对于公众号发来的请求进行解析的一些处理函数。
	reply.py   服务器返还公众号数据的格式（将返还数据格式转换为公众号能处理的格式）

[微信效果图](https://github.com/msun1996/Hazeweb/blob/master/image/Screenshot_2017-06-24-10-34-35.png)

