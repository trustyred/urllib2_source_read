# urllib2源代码阅读
## 阅读一个库的源码，首先你要了解这个库的使用方式，这是大前提，之后写一段使用这个库的代码，然后用Pycharm开始一步步调试
urllib2这个库的代码还比较好理解，再阅读的时候注意几个概念，比如handlers,handler,OpenerDirector,Request等概念还有像handler_open,handler_error,process_response,process_request等数据结构
# 关于urllib2的问题
- 当添加的data大于2147483647长度的时候会报错的问题,目前的解决方法如下,但具体原因在源码中并没有发现,估计还要再深入到httplib的源码中才能找到问题的答案
```python
# 上传字符大于2147483647会报错的代码
import urllib2

f = open('./test')
buf = f.read()
urllib2.urlopen('http://your_url',data=buf)
```

```python
# 解决上传字符串过长的代码
import mmap
import urllib2
f = open('./test')
mmapped_file_as_string = mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
urllib2.urlopen('http://your_url',data=mmapped_file_as_string)
```
## 问题解决
通过查看httplib库中真正进行http请求的函数，找到了解决这个问题的答案
```python
httplib库中HTTPConnetion类的send方法代码片段
def send(self, data):
        """Send `data' to the server."""
        if self.sock is None:
            if self.auto_open:
                self.connect()
            else:
                raise NotConnected()

        if self.debuglevel > 0:
            print "send:", repr(data)
        blocksize = 8192
        if hasattr(data,'read') and not isinstance(data, array):
            if self.debuglevel > 0: print "sendIng a read()able"
            datablock = data.read(blocksize)
            while datablock:
                self.sock.sendall(datablock)
                datablock = data.read(blocksize)
        else:
            self.sock.sendall(data)

```
上面代码中send传入的data，也就是我们传入的buf，一般来说我们都会将一个读好的字符串通过urlib2的urlopen传到HTTPConnection的send函数,这个字符串类型肯定是没有实现read方法的,所以直接将所有的data通过self.sock.sendall(data)方法发出,也就无法一块块的读取导致单次tcp请求传输了过多数据(这里有待查找rfc文档佐证),出现了报错,只要传入一个实现了read方法的对象，这个问题就很容易解决了
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

