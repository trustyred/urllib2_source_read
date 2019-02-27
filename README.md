# urllib2源代码阅读
## 阅读一个库的源码，首先你要了解这个库的使用方式，这是大前提，之后写一段使用这个库的代码，然后用Pycharm开始一步步调试
## urllib2这个库的代码还比较好理解，再阅读的时候注意几个概念，比如handlers,handler,OpenerDirector,Request等概念还有像handler_open,handler_error,process_response,process_request等数据结构

# 从基础流程入手
## example
```python
# main.py
import urllib2

res = urllib2.urlopen("http://www.baidu.com")
print res.code
```
## example背后的调用流程
### 
```
main.py --> 
    进入系统库目录 -> 
        urllib2.py -> 
            进入urlopen函数 -> 
                调用build_opener()全局的_opener,_opener是一切调用的入口，全局唯一单例 ->
                    进入build_opener函数 -> 
                        创建OpenerDirector实例openr，将默认的Handler加入到opener中，如果你在代码中主动继承了某个默认Handler并进行改写后，那么会将你自己编写的Handler加入到opener中，返回opener ->
            回到urlopen函数 ->
                调用opener.open函数 ->
                    生成Request对象，将请求的各种信息添加入Request对象中->
                    从process_request字典中找到特定请求的处理函数,将刚才生成的Request传入,并根据协议类型进行特定的修饰
                    调用OpenerDirector的_open方法去进行真正的请求并返回响应 ->
                    进入_open方法 ->
                        _open方法的实现很有意思，handler_open是一个字典结构为{"<kind1>":[meth1,meth2...],"<kind2>":[meth1,meth2]}_open中_call_chain方法按照default,protocol,unknown的顺序遍历调用handler_open中的方法，任意一个有结果就返回 ->
                    现在我们获得了响应的返回，对于http的请求来说，响应是由httplib.HTTPConnection的getresponse得到的，再经过urllib的addinfourl加工成一个file_like对象(一般来说实现了read,write等方法的对象就是file_like对象,不是很准确但是易于理解)->
                    继续遍历process_response字典，根据协议的不同，去处理不同的响应。比如对于http请求的响应，当返回302,304的时候要继续重新请求等操作,这也就是响应处理的作用,处理结束后返回最终的响应
            urlopen函数执行结束返回
返回到main.py中

```

