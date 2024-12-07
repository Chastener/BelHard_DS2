import telebot
import os
import yolov5master.detect
import time

if __name__ == '__main__':
    bot = telebot.TeleBot()
    folder = os.path.join(os.getcwd(), "receivedPhotos")
    res_folder = os.path.join(os.getcwd(), "yolov5master")
    res_folder = os.path.join(res_folder, "runs")
    res_folder = os.path.join(res_folder, "detect")
    res_folder = os.path.join(res_folder, "exp")

    def downloadFile(file_id):
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        return downloaded_file

    def saveFile(byteArray, file_name):
        with open(os.path.join(folder, file_name), 'wb') as new_file:
            new_file.write(byteArray)

    def processImage(file_name):
        file_path = os.path.join(folder, file_name)
        yolov5master.detect.run(source=file_path)
        result_file_path = os.path.join(res_folder, file_name)
        if os.path.isfile(result_file_path):
            with open(result_file_path, 'rb') as file:
                byteArray = file.read()
            os.remove(result_file_path)
            os.rmdir(res_folder)
            return byteArray

    @bot.message_handler(content_types=["photo"])
    def get_text_messages(message):
        chat_id = message.chat.id
        send = bot.send_message(message.from_user.id, 'Your photo is in work.')
        file_name = message.photo[-1].file_unique_id + ".jpg"
        saveFile(downloadFile(message.photo[-1].file_id), file_name)
        photo = processImage(file_name)
        bot.send_photo(chat_id, photo)


    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        pass


    bot.infinity_polling()
