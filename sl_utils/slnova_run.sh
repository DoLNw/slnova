


# ssh_cmd="ssh -p 16893 root@region-11.autodl.com"
# password="V0vJwfMtZM"

ssh_cmd=$1
password=$2

echo ${ssh_cmd}
echo ${password}

port=`echo $ssh_cmd | awk '{print $3}'`
user=`echo $ssh_cmd | awk '{print $4}'`

#'' 如果压缩包存在，则删除
if [ -f '/Users/jc/jcall/研究实验代码/slnova.zip' ]; then
	rm -f '/Users/jc/jcall/研究实验代码/slnova.zip'
fi

# 将新的代码重新压缩成zip文件
cd '/Users/jc/jcall/研究实验代码'
zip -r 'slnova.zip' 'slnova'

# expect /Users/jc/jcall/研究实验代码/slnova/sl_utils/slnova_expect.sh ${port} ${user} ${password}

open -a Terminal `expect /Users/jc/jcall/研究实验代码/slnova/sl_utils/slnova_expect_upload_and_run.sh ${port} ${user} ${password}`