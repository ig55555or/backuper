import requests
import os.path
import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET
import re

class CreateConfig:
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


    # извлекаем токен
    def token(self, text):
        s1 = text.find('csrfMagicToken') + 18
        s2 = text.find('csrfMagicName') - 6
        token = text[s1:s2]
        print(token)
        return token

    # авторизируемся и получаем куки и токен
    def auth(self):
        try:
            kek = requests.get(self.url + "index.php", verify=self.ssl)
            kek = requests.post(self.url + 'index.php', {
                '__csrf_magic': self.token(kek.text),
                'usernamefld': self.user,
                'passwordfld': self.pwd,
                'login': 'Sign+In',
            }, verify=self.ssl)

            data = [kek.cookies, self.token(kek.text)]
        except Exception as e:
            print(e)

        return data

    #скачиваем конфиг
    def getcfg(self):

        try:
            data = self.auth()
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

    def go(self): #функция сохраннеия бэкапа
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




class Settings():
    ##################################################

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

            ##############################################

    def start(self):
        if (os.path.exists('settings.xml')):
            print('Конфигурационный файл найден ')
            self.startpars()
        else:
            print('Конфигурационный файл не найден, создание конфигурационного файла: ')
            self.crateConfXML()
            self.startpars()

    def startpars(self):
        conf = self.readConfXML()
        cfg = CreateConfig(conf[0].text, conf[2].text, conf[3].text, conf[4].text, conf[1].text)
        cfg.go()


    def checkurl(self): #Проверка url
        chckurl = 'https?://(?:www\.|)([\w.-]+).*'
        textc = input("Введите url ")
        while re.search(chckurl, textc) == None or textc.find('http') < 0:
            print('Неверный url')
            textc = input("Введите url ")
        url = re.search(chckurl, textc).string + '/'
        return url


    def crateConfXML(self):

        root = xml.Element("Config")
        url = xml.SubElement(root, "url")
        ssl = xml.SubElement(root, 'ssl')

        #Проверка Url
        textc = self.checkurl()
        print('Проверка подключения...')
        status = self.checkconn(textc)
        while status[1] != 'good':
            textc = self.checkurl()
            status = self.checkconn(textc)


        url.text = textc
        ssl.text = str(status[0])
        #


        user = xml.SubElement(root, "user")


        textc = input("Введите имя пользователя ")
        while len(textc) <= 0:
            print('Имя пользователя не может быть пустым')
            textc = input("Введите имя пользователя ")
        user.text = textc

        pwd = xml.SubElement(root, "pwd")
        textc = input("Введите пароль ")
        while len(textc) <= 0:
            print('Пароль не может быть пустым')
            textc = input("Введите пароль ")
        pwd.text = textc

        path = xml.SubElement(root, "path")
        path.text = input("Введите путь сохранения конфигов ")

        x = xml.ElementTree(root)
        with open("settings.xml", "wb") as fh:
            x.write(fh)


    def readConfXML(self):
        try:
            tree = ET.parse("settings.xml")
            root = tree.getroot()
        except Exception as e:
            print(e)
        return root












