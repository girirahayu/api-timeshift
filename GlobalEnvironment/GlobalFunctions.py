import uuid
import base64
from Crypto.Cipher import AES
import jwt
import urllib2
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

def sendmail(efrom,to,cc,subject,body,password):
    if cc is None:
        cece = 'infra@codigo.id'
    else:
        cc = cc.replace('[','').replace(']','').replace("'", "")
        if "infra@codigo.id" in cc:
            cece = cc
        else:
            cece = cc + ',infra@codigo.id'

    toaddr = ', '.join([to])
    msg = MIMEMultipart()
    msg['From'] = efrom
    msg['To'] = toaddr
    msg['Cc'] = cece
    msg['Subject'] = subject
    toaddrs = [toaddr]+cece.split(',')
    msg.attach(MIMEText(body, 'html'))
    try :
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(efrom, password)
        text = msg.as_string()
        server.sendmail(efrom, toaddrs, text)
        #server.set_debuglevel(True)
        server.quit()
        return 200
    except Exception as e:
        print e

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


def jwtDecode(token):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload['username'], payload['password']

def sendTelegram(message):
    token = '211902458:AAGihnHsNG-slhhzEX_cTMNw45ZecGmRif0'
    chatid = '-171840403'
    msg = 'Hai Sayang!! ' + message + ' dong!!'

    req = urllib2.Request("https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + chatid + "&text=" + msg)
    opener = urllib2.build_opener()
    f = opener.open(req)
    js = json.loads(f.read())
    result = json.dumps(dict(js), ensure_ascii=False)
    return result

def sendToRabbit(message):
    data = {"properties":{},"routing_key":"","payload":message,"payload_encoding":"string"}
    req = urllib2.Request('http://rabbit.codigo.id/api/exchanges/infra/monitoring/publish')
    req.add_header("Authorization", "Basic XXXXXXXXXXX")
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))
    return response
