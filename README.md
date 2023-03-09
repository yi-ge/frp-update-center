# frp-update-center

Frp update center

编写python3的API，监听65527端口，每隔5分钟检查一次<https://github.com/fatedier/frp>是否发布了新版本，如果发布则下载最新版releases中的各个文件保存到/data/frp/\<version>/文件夹中（如果不存在则创建）。实现/frpc/info接口，根据URL参数中的操作系统和架构返回/data/frp/中最新的version的版本号以及github中对应版本的下载地址，实现/frpc/download接口，根据URL参数中的操作系统和架构再根据/data/frp/中最新的version的版本号代理github中对应版本的下载地址返回文件数据流。

请你给上面的代码增加功能但不得重构代码。需要增加：
1、如果下载成功后，根据文件夹中的“frp_sha256_checksums.txt”检查文件的sha256是否匹配并对不匹配的文件重新下载。
2、每次启动程序后遍历/data/frp目录下的文件，找出最新版本号并赋值给全局变量version

pm2 start main.py --interpreter=python3 --name frp
