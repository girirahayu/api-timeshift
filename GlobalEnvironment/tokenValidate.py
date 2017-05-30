from GlobalEnvironment.emailFunction import GlobalEmail
from GlobalEnvironment.db import DB
from Crypto.Cipher import AES
from datetime import datetime, timedelta
import base64
import falcon
import jwt
import json
import os
import uuid

JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

getEmail = GlobalEmail()
conn = DB()

def encryption(privateInfo):
    # 32 bytes = 256 bits
    # 16 = 128 bits
    # the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
    BLOCK_SIZE = 32
    # the character used for padding
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING = '{'
    # function to pad the functions. Lambda
    # is used for abstraction of functions.
    # basically, its a function, and you define it, followed by the param
    # followed by a colon,
    # ex = lambda x: x+5
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    # encrypt with AES, encode with base64
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    # generate a randomized secret key with urandom
    secret = uuid.uuid4().hex
    # creates the cipher obj using the key
    cipher = AES.new(secret)
    # encodes you private info!
    encoded = EncodeAES(cipher, privateInfo)
    return encoded , secret

def decryption(encryptedString,secret):
	PADDING = '{'
	DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
	#Key is FROM the printout of 'secret' in encryption
	#below is the encryption.
	encryption = encryptedString
	key = secret
	cipher = AES.new(key)
	decoded = DecodeAES(cipher, encryption)
	return decoded


class getToken(object):
    def on_post(self,req, resp):
        username = req.get_param('username')
        password = req.get_param('password')

        if getEmail.emailValidation(username, password) == 1:


            enco , secre = encryption(password)
            fil = "select count(username) as count from members where username =%s"
            filter = conn.query("select", fil,username)
            dict = filter[0]
            if dict.get('count') == 0:
                query = "insert into members (username,password,secret) values(%s,%s,%s)"
                conn.query("insert",query,(username,enco,secre))
                payload = {
                    'username': username,
                    'password': enco
                    #'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
            else:
                query = "select password from members where username=%s"
                dataq = conn.query("select", query,username)
                dict = dataq[0]
                payload = {
                    'username': username,
                    'password': dict.get('password')
                    #'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }

            conn.close_cur()
            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
            data = {"token": jwt_token.decode('utf-8')}
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            data = {"status": "Can't validate Email address!"}
            resp.status = falcon.HTTP_401
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))