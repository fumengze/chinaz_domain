# chinaz_domain
站长之家同IP网站查询脚本

# 工作流程
把需要查询的域名或链接放入inj.txt内，会开始解析域名的IP，并添加到set中去重，最后写入ip.txt，然后从ip.txt内获取ip查询这个IP下的所有网站，存储进数据库后最后做一次去重。
# 使用方法：
创建mysql或MariaDB数据库，导入url_all.sql
在脚本中更改数据库的IP地址，用户名，密码，端口等信息。
