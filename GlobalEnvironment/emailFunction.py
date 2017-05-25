import imaplib

class GlobalEmail(object):
    def emailValidation(self,username,password):
        try:
            SMTP_SERVER = "smtp.gmail.com"
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            login = mail.login(username, password)
            if login[0] == 'OK':
                return 1
            else:
                return False
        except:
            pass