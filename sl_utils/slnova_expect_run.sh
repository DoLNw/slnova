#!/usr/local/bin/expect

# 上面这个路径可以使用 which expect 命令查看

# Expect是一个用来处理交互的命令。借助Expect，我们可以将交互过程写在一个脚本上，
# 使之自动化完成。形象的说，ssh登录，ftp登录等都符合交互的定义。下文我们首先提出一个问题，
# 然后介绍基础知四个命令，最后提出解决方法。

set timeout -1

# 设置变量
set user "root"
set host "192.160.149.100"

# 得到登录密码，用户名和远程IP
set loginpass [lindex $argv 2]
set port [lindex $argv 0]
set user [lindex $argv 1]
if {$argc >= 4} {
	set config_filename [lindex $argv 3]
}

# 执行ssh
spawn ssh -p ${port} ${user}

# -re 匹配正则表达式
expect {
	-re "Are you sure you want lo continue connecting (yes/no)?" {
		send "yes\r"
	}
	-re "password:" {
		send "${loginpass}\r"
	}
	-re "Permission deled, please try again." {
		exit
	}
}

expect "*#"                    # 定义命令的开始，就是匹配到了root@container-836911b1ac-c9909245:~#，最后不是有一个#嘛，前面的*表示任何
send "cd autodl-nas\r"

# 若slnova.zip没有解压，那么解压
expect "*#"
# [ ! -d "/root/autodl-nas/slnova" ] | echo $?
send "if \[ ! -d '/root/autodl-nas/slnova' \]; then\r unzip /root/autodl-nas/slnova.zip\r fi\r"

# 若存在这个文件，将这个文件删除
expect "*#"
send "if \[ -d '/root/autodl-nas/__MACOSX' \]; then\r rm -rf '/root/autodl-nas/__MACOSX'\r fi\r"

expect "*#"
send "cd slnova/main\r"

expect "*#"


if {$argc >= 4} {
	send "python main.py ${config_filename}\r"
} else {
	send "python main.py\r"
}



# # 这个命令表示停留在上面的执行完之后，停留在该界面，可以让用户进行交互
interact  #用exact这个指令是为了把控制权交给用户，代替send "logout\r"    终端不会断开)