# https://core.telegram.org/bots#
# https://pytorch.org/get-started/locally/
# pip3 install opencv-python
# pip3 install PyTelegramBotAPI==2.2.3
import sys
import datetime
import sqlite3 as sq
import telebot
import traceback
import torch
from torchvision import transforms
import config
from handler import *

bot = telebot.TeleBot(config.TOKEN)
classes = ['пчела', 'другое насекомое', 'нет насекомых', 'оса']
model = torch.jit.load('Wasp_Bees_Insects.pt')
transform = transforms.Compose(
    [transforms.Resize(224),
     transforms.ToTensor(),
     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


def get_photo(message) :
    photo = message.photo[1].file_id
    file_info = bot.get_file(photo)
    file_content = bot.download_file(file_info.file_path)
    return file_content


@bot.message_handler(commands=['start'])
def start_message(message) :
    bot.send_message(message.chat.id,
                     'Ку-ку, друг! Пришли мне картинку, '
                     'чтобы определить наличие на ней пчел, ос или других насекомых :)')


@bot.message_handler(commands=['stop'])
def stop_message(message):
    bot.send_message(message.chat.id, 'До встречи!!!')

@bot.message_handler(commands=['sessions'])
def dbdbdbd(message) :
    with sq.connect("insects.db") as con :

        cur = con.cursor()
        cur.execute("""
               """)
        result = cur.fetchall()
        result = cur.execute('SELECT insect FROM insects')
        # cur.execute('SELECT * FROM insects')
        for result in cur.fetchall() :
            bot.send_message(message.chat.id, result)

@bot.message_handler(content_types=['photo'])
def repeat_all_messages(message) :
    try :
        file_content = get_photo(message)
        image = byte2image(file_content)
        image = transform(image)
        model.eval()
        image = torch.unsqueeze(image, 0)
        outputs = model(image)
        _, preds = torch.max(outputs, 1)
        bot.send_message(message.chat.id, text='На картинке {}'.format(classes[int(preds)]))
        now = datetime.datetime.now()
        print(now.strftime("%Y-%m-%d"))
        with sq.connect("insects.db") as con :
            cur = con.cursor()
            cur.execute("""
            """)
            cur.execute("INSERT INTO insects (date, insect) VALUES(?, ?)",
                        (now.strftime("%Y-%m-%d"), classes[int(preds)],))
            result = cur.fetchall()





    except Exception :
        traceback.print_exc()
        bot.send_message(message.chat.id, 'Давай еще разочек')


if __name__ == '__main__' :
    import time

    while True :
        try :
            bot.polling(none_stop=True)
        except Exception as e :
            time.sleep(15)
            print('Restart!')
