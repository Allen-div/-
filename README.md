# dailyfresh

天天生鲜是一个电商类的生鲜项目。

本版本是一个简洁版本没有用到分布式，数据库中存的是图片的静态链接。

天天生鲜一共有四个模块goods,cart,order,user

1.下载本项目，创建虚拟环境，之后安装requirements.txt

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

2.创建相关数据库：

3.创建迁移文件，执行迁移

python manage.py makemigrations

python manage.py migrate

4.启动项目

python manage.py runserver
