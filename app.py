from flask import Flask, request,  render_template
import re

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html'), 200

#обработка запроса
@app.route('/', methods=['POST'])
def getrequest():
    #принимаем и декодируем xml строку
    xml_string = request.data.decode('UTF-8')
    
    #преобразование из xml в json с нужными ключами
    json_string = decoding_request(xml_string)

    #отправка запроса
    sendrequest(json_string, xml_string)

    return render_template('index.html', str = xml_string, data=json_string), 200

#отправка запроса
def sendrequest(json_string, xml_string):
    import requests
    from requests import Request, Session
    s = requests.Session()

    org = re.search(r'<b>Наименование организации</b>: ООО (.+?)<br>', xml_string)

    try:
        test=org.group(1)
    except AttributeError:
        org = re.search(r'<b>Наименование организации</b>: ООО (.+?)<br>', '<b>Наименование организации</b>: ООО "Автошкола "Драйв"<br>')
    
    if (org.group(1)=='"Автопремиум"'):
        s.headers.update({
        'content-type':'application/json',
        'x-requested-with':'XMLHttpRequest',
        'api_key':'9c67f03b57f647b58296e2750f9cf8dc'})

    elif (org.group(1)=='"Драйв"'):
        s.headers.update({
        'content-type':'application/json',
        'x-requested-with':'XMLHttpRequest',
        'api_key':'566c2315ed28482f823de14a3523f121'})

    elif (org.group(1)=='"Учебный центр "Драйв"'):
        s.headers.update({
        'content-type':'application/json',
        'x-requested-with':'XMLHttpRequest',
        'api_key':'fd0017e6dba44287ba57cd3c9d0d690c'})

    else:
        s.headers.update({
        'content-type':'application/json',
        'x-requested-with':'XMLHttpRequest',
        'api_key':'1d4329f0a61240bcb8a13c8a0c213c62'})

    r = s.post('https://app.dscontrol.ru/api/LeadExternalAdd' , json=json_string)
    print(r.status_code)
    print(r.text)
    

#преобразование из xml в json с нужными ключами
def decoding_request(text):
    #org = re.search(r'<b>Наименование организации</b>: ООО (.+?)<br>', text)
    surname = re.search(r'<b>Фамилия</b>: (.+?)<br>', text)
    name = re.search(r'<b>Имя</b>: (.+?)<br>', text)
    patronymic = re.search(r'<b>Отчество</b>: (.+?)<br>', text)
    owner = re.search(r'<b>Исполнитель</b>: (.+?)<br>', text)
    gender = re.search(r'<b>Пол</b>: (.+?)<br>', text)
    gear = re.search(r'<b>МКПП/АКПП</b>: (.+?)<br>', text)
    #channel = re.search(r'<b>Откуда пришел клиент</b>: (.+?)<br>', text)
    comment = re.search(r'<b>Комментарий</b>: (.+?)<br>', text)
    category = re.search(r'<b>Категория обучения</b>: (.+?)<br>', text)

    data = {}
    try:
        data['Name']=name.group(1)
    except AttributeError:
        data['Name']='Noname'
        
    try:
        data['Surname']=surname.group(1)
    except AttributeError:
        pass

    try:
        data['Patronymic']=patronymic.group(1)
    except AttributeError:
        pass
    
    try:
        data['Gernder']=get_gender(gender.group(1))#выбор пола
    except AttributeError:
        pass
    
    try:
        data['ChannelId']=get_channelid(text)#выбор соответствующего канала привлечения
    except AttributeError:
        data['ChannelId']=get_channelid('<b>Наименование организации</b>: ООО "Автошкола "Драйв"<br><b>Откуда пришел клиент</b>: Пришел сам<br>')#выбор соответствующего канала привлечения
    
    try:
        data['NeedAutomaticGear']=get_NeedAutomaticGear(gear.group(1))#выбор кпп
    except AttributeError:
        pass
    
    data['LogText']=''
    try:
        data['LogText']+='Исполнитель: '+ owner.group(1)
    except AttributeError:
        pass
    try:
        data['LogText']+=' Категория обучения: '+category.group(1)
    except AttributeError:
        pass
    try:
        data['LogText']+=' Комментарий: '+comment.group(1)
    except AttributeError:
        pass
    
    return data

#выбор пола
def get_gender(gender):
    if (gender == 'Мужской'):
        return 0
    else: return 1

#выбор кпп
def get_NeedAutomaticGear(gear):
    if (gear == 'АКПП'):
        return True
    else: return False

#выбор соответствующего канала привлечения
def get_channelid(text):
    org = re.search(r'<b>Наименование организации</b>: ООО (.+?)<br>', text)
    channel = re.search(r'<b>Откуда пришел клиент</b>: (.+?)<br>', text)
    try:
        test=org.group(1)
    except AttributeError:
        org = re.search(r'<b>Наименование организации</b>: ООО (.+?)<br>', '<b>Наименование организации</b>: ООО "Автошкола "Драйв"<br>')

    try:
        test=channel.group(1)
    except AttributeError:
        channel = re.search(r'<b>Откуда пришел клиент</b>: (.+?)<br>', '<b>Откуда пришел клиент</b>: Пришел сам<br>')

    #во всем виновата автошкола-контроль
    if (org.group(1)=='"Автошкола "Драйв"'):
        if (channel.group(1)=='SMS- рассылка'):
            return 1709
        elif (channel.group(1)=='Вконтакте'):
            return 1711
        elif (channel.group(1)=='Группа ВК'):
            return 1283
        elif (channel.group(1)=='Друзья'):
            return 1090
        elif (channel.group(1)=='Из другой автошколы'):
            return 2339
        elif (channel.group(1)=='Инстаграм'):
            return 1721
        elif (channel.group(1)=='Наружная реклама'):
            return 1089
        elif (channel.group(1)=='Отдел продаж'):
            return 1720
        elif (channel.group(1)=='Печатная реклама (листовки)'):
            return 1088
        elif (channel.group(1)=='По обзвону холодной базы'):
            return 1710
        elif (channel.group(1)=='Поисковая система'):
            return 1087
        elif (channel.group(1)=='Ранее учились знакомые'):
            return 1091
        elif (channel.group(1)=='Рейтинг сдачи в ГИБДД'):
            return 1092
        elif (channel.group(1)=='Реклама в лифтах'):
            return 1282
        elif (channel.group(1)=='Сайт автошколы'):
            return 1086
        elif (channel.group(1)=='Пришел сам'):
            return 1707
        elif (channel.group(1)=='Не заполнено'):
            return 1707
        else: return 1707

    elif (org.group(1)=='"Автопремиум"'):
        if (channel.group(1)=='SMS- рассылка'):
            return 1789
        elif (channel.group(1)=='Вконтакте'):
            return 2366
        elif (channel.group(1)=='Группа ВК'):
            return 1844
        elif (channel.group(1)=='Друзья'):
            return 61
        elif (channel.group(1)=='Из другой автошколы'):
            return 2138
        elif (channel.group(1)=='Инстаграм'):
            return 2135
        elif (channel.group(1)=='Наружная реклама'):
            return 60
        elif (channel.group(1)=='Отдел продаж'):
            return 2138
        elif (channel.group(1)=='Печатная реклама (листовки)'):
            return 59
        elif (channel.group(1)=='По обзвону холодной базы'):
            return 1788
        elif (channel.group(1)=='Поисковая система'):
            return 58
        elif (channel.group(1)=='Ранее учились знакомые'):
            return 61
        elif (channel.group(1)=='Рейтинг сдачи в ГИБДД'):
            return 2134
        elif (channel.group(1)=='Реклама в лифтах'):
            return 60
        elif (channel.group(1)=='Сайт автошколы'):
            return 2134
        elif (channel.group(1)=='Пришел сам'):
            return 2340
        elif (channel.group(1)=='Не заполнено'):
            return 2134
        else: return 2134

    elif (org.group(1)=='"Учебный центр "Драйв"'):
        if (channel.group(1)=='SMS- рассылка'):
            return 1705
        elif (channel.group(1)=='Вконтакте'):
            return 1704
        elif (channel.group(1)=='Группа ВК'):
            return 1704
        elif (channel.group(1)=='Друзья'):
            return 1076
        elif (channel.group(1)=='Из другой автошколы'):
            return 2330
        elif (channel.group(1)=='Инстаграм'):
            return 1702
        elif (channel.group(1)=='Наружная реклама'):
            return 1075
        elif (channel.group(1)=='Отдел продаж'):
            return 1719
        elif (channel.group(1)=='Печатная реклама (листовки)'):
            return 1074
        elif (channel.group(1)=='По обзвону холодной базы'):
            return 1706
        elif (channel.group(1)=='Поисковая система'):
            return 1073
        elif (channel.group(1)=='Ранее учились знакомые'):
            return 1077
        elif (channel.group(1)=='Рейтинг сдачи в ГИБДД'):
            return 1078
        elif (channel.group(1)=='Реклама в лифтах'):
            return 1075
        elif (channel.group(1)=='Сайт автошколы'):
            return 1072
        elif (channel.group(1)=='Пришел сам'):
            return 1701
        elif (channel.group(1)=='Не заполнено'):
            return 1701
        else: return 1701
    
    elif (org.group(1)=='"Драйв"'):
        if (channel.group(1)=='SMS- рассылка'):
            return 1714
        elif (channel.group(1)=='Вконтакте'):
            return 1716
        elif (channel.group(1)=='Группа ВК'):
            return 1716
        elif (channel.group(1)=='Друзья'):
            return 1524
        elif (channel.group(1)=='Из другой автошколы'):
            return 1521
        elif (channel.group(1)=='Инстаграм'):
            return 1718
        elif (channel.group(1)=='Наружная реклама'):
            return 1523
        elif (channel.group(1)=='Отдел продаж'):
            return 1721
        elif (channel.group(1)=='Печатная реклама (листовки)'):
            return 1522
        elif (channel.group(1)=='По обзвону холодной базы'):
            return 1717
        elif (channel.group(1)=='Поисковая система'):
            return 1521
        elif (channel.group(1)=='Ранее учились знакомые'):
            return 1525
        elif (channel.group(1)=='Рейтинг сдачи в ГИБДД'):
            return 1526
        elif (channel.group(1)=='Реклама в лифтах'):
            return 1523
        elif (channel.group(1)=='Сайт автошколы'):
            return 1520
        elif (channel.group(1)=='Пришел сам'):
            return 1713
        elif (channel.group(1)=='Не заполнено'):
            return 1713
        else: return 1713
    else: return 1707


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


