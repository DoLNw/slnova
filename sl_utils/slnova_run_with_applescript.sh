#!/bin/bash

# 当前是第几个窗口数，就是第几个主机
read -p "请输入主机个数：" host_num

while [[ ! "${host_num}" =~ ^[0-9]+$ ]] || [[ -z "${host_num}" ]]
do
	read -p "请重新输入主机个数：" host_num
done

# # case:aaa 总的第一个，总是要压缩并重新上传更新代码，然后远程登录解压缩，然后运行；
# # case:bbb 每一个网盘区域的第一个，不需要给本地代码再压缩了，但是也是需要上传解压再运行的
# # case:ccc 其他的，只需要远程登录然后运行即可

# for ((i=0;i<${host_num};i+=1))
# 	do
# 	   case ${i} in
# 	    0)
# 		ssh_cmd="ssh -p 28371 root@region-11.autodl.com "
# 		password="MxKJm3QZ1U"
# 		config_filename="config/PEMS04/individual_3layer_12T.json"

# 		port=`echo $ssh_cmd | awk '{print $3}'`
# 		user=`echo $ssh_cmd | awk '{print $4}'`

# 		#'' 如果压缩包存在，则删除
# 		if [ -f '/Users/jc/jcall/研究实验代码/slnova.zip' ]; then
# 			rm -f '/Users/jc/jcall/研究实验代码/slnova.zip'
# 		fi

# 		# 将新的代码重新压缩成zip文件
# 		cd '/Users/jc/jcall/研究实验代码'
# 		zip -r 'slnova.zip' 'slnova'


# 		read -p "请输入回车以启动第一个主机："
# 		echo "host number 0"
# 		# case:aaa 本地压缩上面搞定了，下面这一句需要上传解压，然后执行
# 		osascript <<EOF
# 		tell application "Terminal"
# 			display notification "主机No.${i}开始启动" with title ""
# 			do script "expect /Users/jc/jcall/研究实验代码/slnova/sl_utils/slnova_expect_upload_and_run.sh ${port} ${user} ${password} ${config_filename}"
# 			activate
# 			end tell
# EOF
		
# 		# expect /Users/jc/jcall/研究实验代码/slnova/sl_utils/slnova_expect_upload_and_run.sh ${port} ${user} ${password} ${config_filename}
# 	    ;;

# 	    1)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		echo "host number 1"

# 		ssh_cmd="ssh -p 16893 root@region-11.autodl.com "
# 		password="V0vJwfMtZM"
# 		config_filename="config/PEMS08/individual_3layer_12T.json"

# 		port=`echo $ssh_cmd | awk '{print $3}'`
# 		user=`echo $ssh_cmd | awk '{print $4}'`

# 		# case:ccc 只需要远程登录然后执行就好
# 		osascript <<EOF
# 		tell application "Terminal"
# 			display notification "主机No.${i}开始启动" with title ""
# 			do script "expect /Users/jc/jcall/研究实验代码/slnova/sl_utils/slnova_expect_run.sh ${port} ${user} ${password} ${config_filename}"
# 			activate
# 			end tell
# EOF

# 		# expect /Users/jc/jcall/研究实验代码/slnova/sl_utils/slnova_expect_run.sh ${port} ${user} ${password} ${config_filename}
# 	    ;;

# 	    2)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		read -p "请输入主机个数："
# 		echo "host number 2"
# 	    ;;

# 	    3)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		echo "host number 3"
# 	    ;;

# 	    4)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		echo "host number 4"
# 	    ;;

# 	    5)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		echo "host number 5"
# 	    ;;

# 	    6)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		echo "host number 6"
# 	    ;;

# 	    7)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 		echo "host number 7"
# 	    ;;

# 	    *)
# 		read -p "请等待前一个主机配置完成后输入回车："
# 	    echo "number of hosts reaches to maximum"
# 	    ;;
# 	esac
# done


