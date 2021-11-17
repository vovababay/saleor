from django.core.mail import EmailMultiAlternatives
from django.conf import settings



"""
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = "student@webjox.ru"
EMAIL_HOST_PASSWORD = "lhztrnwksyglifgr"
"""

"""
EMAIL_FILE_PATH = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL = email_config["EMAIL_USE_SSL"]
"""

text_message_head = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Оповещение о регистрации на сайте shop.lighted.ru</title>
  <style>
    body{
       height: 700px;
       width: 700px;
    }
    h1, h2 {
       text-align: center;
    }
    p {
       text-align: center;
       text-decoration: none;
    }
    a{
      text-decoration: none;
      border: 1px solid black;
      border-radius: 3px;
      display: block;
      padding: 0px auto;
      margin: 0px auto;
      line-height: 30px;
      width: 300px;
      color: white;
      background-color: #484848
    }
    a:hover{
	background-color: #fff;
	color: black;
	transition: 0.3s linear;
    }

  </style>
 </head>
 """
text_message_body = """<body>
  <h1 style="">Вы успешно зарегестрировались на сайте shop.lighted.ru</h1>
  <h2>Данные которые вы указали при регистрации<h2>
  <p>Логин: {}</p>
  <p>Пароль: {}</p>
  <a href="https://shop.lighted.ru/">Перейти на сайт</a>
 </body>
</html>
"""
def send_registr_user_data(email, login, password):
    subject = 'Оповещение о регистрации на сайте shop.lighted.ru'
    text_content = "This is an important message."
    html_content = text_message_head + text_message_body.format(login, password)#"Вы успешно зарегестрировалась"

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print("*" * 50)
    print('ОТПРАВЛЕНО "Письмо с данными при регистрации"')
    print("*" * 50)
    return True
