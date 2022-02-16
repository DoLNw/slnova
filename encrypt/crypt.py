# import base64
#
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# # from md5util import md5
#
# class AESCipher(object):
#     def __init__(self, key, mode, **kwargs):
#         """ :param key: 16 (AES-128) 24 (AES-192) 32 (AES-256) :
#         param mode: 模式 :param kwargs: iv 初始向量 MODE_CBC 模式使用 必须是16字节 """
#         self.key = key
#         self.mode = mode
#         self.kwargs = kwargs
#
#     def _get_aes(self):
#         """TypeError: decrypt() cannot be called after encrypt()"""
#         return AES.new(self.key.encode('utf-8'), self.mode, **self.kwargs)
#
#     def encrypt(self, plain_text):
#         # 选择pkcs7补全
#         pad_pkcs7 = pad(plain_text.encode('utf-8'), AES.block_size)
#         encrypt_data = self._get_aes().encrypt(pad_pkcs7)
#         return str(base64.b64encode(encrypt_data), encoding='utf-8')
#
#     def decrypt(self, cipher_text):
#         padded_data = self._get_aes().decrypt(base64.b64decode(cipher_text.encode('utf-8')))
#         return str(unpad(padded_data, AES.block_size), encoding='utf-8')
#
#
# def main():
#     key = "123456"
#     # md5_key = md5(key)
#     md5_key = '9999999999999999'
#     aes_str = "123456789"
#
#     # ECB 模式
#     ecb_cipher = AESCipher(md5_key, mode=AES.MODE_ECB)
#     cipher_text = ecb_cipher.encrypt(aes_str)
#     print(cipher_text)
#     # 7J0VfbEYF0XdLnLuA1b4Fw== print(ecb_cipher.decrypt(cipher_text))
#     # CBC 模式
#     cbc_cipher = AESCipher(md5_key, mode=AES.MODE_CBC, IV=md5_key[0:16].encode())
#     cipher_text = cbc_cipher.encrypt(aes_str)
#     print(cipher_text)
#     print(cbc_cipher.decrypt(cipher_text))
#
#
# if __name__ == '__main__':
#     main()
#



# https://help.aliyun.com/document_detail/131058.html
# https://help.aliyun.com/document_detail/201599.html

#!/usr/bin/env python
#coding=utf-8

import json
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from aliyunsdkcore import client
from aliyunsdkkms.request.v20160120 import DecryptRequest
from aliyunsdkkms.request.v20160120 import GenerateDataKeyRequest


def KmsGenerateDataKey(client, key_alias):
    request = GenerateDataKeyRequest.GenerateDataKeyRequest()  # 根据创建的密钥别名，创建加密密钥，目前只是一个请求
    request.set_accept_format('JSON')
    request.set_KeyId(key_alias)
    request.set_NumberOfBytes(32)
    response = json.loads(client.do_action(request))

    datakey_encrypted = response["CiphertextBlob"]
    datakey_plaintext = response["Plaintext"]
    print("print(datakey_plaintext) " + datakey_plaintext)
    # 第一个是明文密钥，第二个是加密的，需要保存下来，等到解密的时候使用
    # 加密的这个，等到解密的时候进行计算，然后再得到与第一个相同的明文密钥，再使用的
    return (datakey_plaintext, datakey_encrypted)


# [python打开zip文件_如何从Python中的zip文件中读取？](https://blog.csdn.net/weixin_39597318/article/details/110502906)
def enReadTextFile(in_file):
    # file = open(in_file, 'r', encoding='gbk') # 出现中文的时候可以用这个
    file = open(in_file, 'r', encoding='utf-8')
    content = file.read()
    file.close()
    return content

def enWriteTextFile(out_file, lines):
    file = open(out_file, 'w')
    for ln in lines:
        # print(type(ln))
        file.write(ln)
        file.write('\n')
    file.close()

# Out file format (text)
# Line 1: b64 encoded data key
# Line 2: b64 encoded IV
# Line 3: b64 encoded ciphertext
# Line 4: b64 encoded authentication tag
def LocalEncrypt(datakey_plaintext, datakey_encrypted, in_file, out_file):
    data_key_binary = base64.b64decode(datakey_plaintext)
    cipher = AES.new(data_key_binary, AES.MODE_EAX)

    in_content = enReadTextFile(in_file)

    pad_pkcs7 = pad(in_content.encode('utf-8'), AES.block_size)
    ciphertext, tag = cipher.encrypt_and_digest(pad_pkcs7)

    print(datakey_encrypted)
    lines = [datakey_encrypted, base64.b64encode(cipher.nonce).decode("utf-8"), base64.b64encode(ciphertext).decode("utf-8"), base64.b64encode(tag).decode("utf-8")]

    enWriteTextFile(out_file, lines)

def KmsDecrypt(client, ciphertext):
    request = DecryptRequest.DecryptRequest()
    request.set_accept_format('JSON')
    request.set_CiphertextBlob(ciphertext)
    response = json.loads(client.do_action(request))
    return response.get("Plaintext")

def deReadTextFile1(in_file):
    file = open(in_file, 'r')
    lines = []
    for ln in file:
        lines.append(ln)
    file.close()
    return lines

def deWriteTextFile1(out_file, content):
    file = open(out_file, 'w')
    file.write(content)
    file.close()

def LocalDecrypt(datakey, iv, ciphertext, tag, out_file):
    cipher = AES.new(datakey, AES.MODE_EAX, iv)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    data = str(unpad(data, AES.block_size), encoding='utf-8')
    deWriteTextFile1(out_file, data)


if __name__ == "__main__":

    clt = client.AcsClient('LTAIbE2A27BOEdAG', 'kXfaggVavdrnfot93c87fxMmm46iRH', 'cn-hangzhou')

    key_alias = 'alias/slnova_test1'

    en_in_file = './credentials.csv'
    en_out_file = './en_credentials.csv'

    # de_in_file = './en_credentials.csv'
    de_in_file = en_out_file
    de_out_file = './de_credentials.csv'

    # Generate Data Key
    datakey = KmsGenerateDataKey(clt, key_alias)

    # Locally Encrypt the sales record
    LocalEncrypt(datakey[0], datakey[1], en_in_file, en_out_file)


    # Read encrypted file
    in_lines = deReadTextFile1(de_in_file)

    # Decrypt data key
    # 这个lines[0]存储的是加密密钥，用阿里云的kms来解开它
    datakey = KmsDecrypt(clt, in_lines[0])

    # Locally decrypt the sales record
    LocalDecrypt(
      base64.b64decode(datakey),
      base64.b64decode(in_lines[1]),  # IV, 向量
      base64.b64decode(in_lines[2]),  # Ciphertext
      base64.b64decode(in_lines[3]),  # Authentication tag，来验证对不对
      de_out_file
      )