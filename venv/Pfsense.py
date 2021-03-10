import requests
import os.path
import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET
import re


class Connect:
    def checkconn(self, url):
        try:
            ssl = True
            r = requests.get(url + "index.php", verify=ssl)
            if r.status_code == 200:
                print('Success connect!')
                if r.text.find('pfSense') < 0:
                    print('Это не pfSense')
                    return [ssl, 'negood', r.status_code]
                else:
                    return [ssl, 'good', r.status_code]
            else:
                print('Error. Status code not 200. It is: ' + str(r.status_code))
                return [ssl, 'bad200', r.status_code]

        except requests.exceptions.SSLError:
            print('Сертификат ssl недействителен, отключаем проверку')
            ssl = False
            r = requests.get(url + "index.php", verify=ssl)
            if r.status_code == 200:
                print('Success connect!')

                if r.text.find('pfSense') < 0:
                    print('Это не pfSense')
                    return [ssl, 'negood', r.status_code]
                else:
                    return [ssl, 'good', r.status_code]

            else:
                print('Error. Status code not 200. It is: ' + str(r.status_code))
                return [ssl, 'bad', r.status_code]

        except Exception as e:
            print('Ошибка ' + e)
            return [ssl, 'ex', e]

        # извлекаем токен

    def token(self, text):
        s1 = text.find('csrfMagicToken') + 18
        s2 = text.find('csrfMagicName') - 6
        token = text[s1:s2]
        print(token)
        return token

        # авторизируемся и получаем куки и токен

    def auth(self, url, ssl, pwd, user):
        status = self.checkconn(url)
        if status[1] == 'good':
            try:
                kek = requests.get(url + "index.php", verify=ssl)
                kek = requests.post(url + 'index.php', {
                    '__csrf_magic': self.token(kek.text),
                    'usernamefld': user,
                    'passwordfld': pwd,
                    'login': 'Sign+In',
                }, verify=ssl)

                state = 'no'
                if kek.text.find('Sign In') < 0:
                    state = 'success'
                data = [kek.cookies, self.token(kek.text), state]
                return data

            except Exception as e:
                print(e)
        else:
            data = ['bad', 'bad', 'bad']
            print('Ошибка подключения')
            return data


class CreateConfig(Connect):
    def __init__(self, url, user, pwd, path, ssl):
        self.url = url
        self.user = user
        self.pwd = pwd
        self.path = path
        self.ssl = False

        if ssl == "True":
            self.sll = True
        elif ssl == "False":
            self.ssl = False

    # скачиваем конфиг
    def getcfg(self):

        try:
            data = Connect().auth(self.url, self.ssl, self.pwd, self.user)
            cookies = data[0]
            token = data[1]

            kek = requests.post(self.url + 'diag_backup.php', {
                '__csrf_magic': token,
                'backuparea': '',
                'donotbackuprrd': 'yes',
                'encrypt_password': '',
                'download': 'Download configuration as XML',
                'restorearea': '',
                'conffile': '(binary)',
                'decrypt_password': '',
            }, verify=self.ssl, cookies=cookies)
        except Exception as e:
            print(e)
        return kek.content

    def savecfg(self, cfg):
        file = open(self.path + '.xml', 'wb')
        file.write(cfg)
        file.close

    def go(self):  # функция сохраннеия бэкапа
        try:
            r = requests.get(self.url + "index.php", verify=self.ssl)
            if r.status_code == 200:
                print('Success!')
                cfg = self.getcfg()
                self.savecfg(cfg)
            else:
                print('Error.')
        except Exception as e:
            print(e)

