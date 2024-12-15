import telebot
import os
import yolov5master.detect
import time
import yaml
import shutil

if __name__ == '__main__':
    bot = telebot.TeleBot("")
    data_folder = os.path.join(os.getcwd(), "data")
    waiting_new_marks = {}

    def downloadFile(file_id):
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        return downloaded_file

    def saveFile(byteArray, user_id, file_id):
        user_folder = os.path.join(data_folder, user_id)
        input_folder = os.path.join(user_folder, "images")
        file_path = os.path.join(input_folder, file_id + ".jpg")
        if os.path.isfile(file_path):
            os.remove(file_path)
            labels_folder = os.path.join(user_folder, "labels")
            labels_path = os.path.join(labels_folder, file_id + ".txt")
            if os.path.isfile(labels_path):
                os.remove(labels_path)
        with open(file_path, 'wb') as new_file:
            new_file.write(byteArray)

    def processImage(user_id, file_name):
        user_folder = os.path.join(data_folder, user_id)
        file_path = os.path.join(user_folder, "images")
        file_path = os.path.join(file_path, file_name)

        weights = os.path.join(user_folder, user_id + ".pt")
        yolov5master.detect.run(source=file_path,
                                weights=weights,
                                project=data_folder,
                                name=user_id,
                                save_txt=True,
                                exist_ok=True)
        
        result_file_path = os.path.join(user_folder, file_name)
        if os.path.isfile(result_file_path):
            with open(result_file_path, 'rb') as file:
                byteArray = file.read()
            os.remove(result_file_path)
            return byteArray

    def registry_new_worker(user_id):
        user_folder = os.path.join(data_folder, user_id)
        os.makedirs(user_folder)
        os.makedirs(os.path.join(user_folder, "images"))

        weights_path = os.path.join(os.getcwd(), "yolov5s.pt")
        shutil.copyfile(weights_path, os.path.join(user_folder, user_id + ".pt"))

        yolo_folder = os.path.join(os.getcwd(), "yolov5master")
        yolo_data_folder = os.path.join(yolo_folder, "data")
        data_path = os.path.join(yolo_data_folder, "coco128.yaml")
        with open(data_path, errors="ignore") as file:
            data_yaml = yaml.safe_load(file)
        data_yaml["train"] = "images"
        data_yaml["val"] = "images"
        data_yaml["path"] = f"../data/{user_id}"
        with open( os.path.join(user_folder, user_id + ".yaml"), 'w') as outfile:
            yaml.dump(data_yaml, outfile)


    def get_text_messages(self, message):
        self._create_menu(message)
        self._bot.send_message(message.from_user.id,
                               text="Выбери в какую категорию внести затраты\U0001F60A",
                               reply_markup=self._more_keyboard)

    def create_image_menu(image_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="Изменить метки",
                                                        callback_data="change_for_" + image_id))
        return keyboard

    @bot.message_handler(content_types=["photo"])
    def get_text_messages(message):
        chat_id = message.chat.id
        user_id = str(chat_id)
        user_folder = os.path.join(data_folder, user_id)
        if not os.path.exists(user_folder):
            registry_new_worker(user_id)
        bot.send_message(chat_id, 'Фото принято в обработку.')
        file_id = message.photo[-1].file_unique_id
        saveFile(downloadFile(message.photo[-1].file_id), user_id, file_id)
        file_name = file_id + ".jpg"
        photo = processImage(user_id, file_name)
        bot.send_photo(chat_id, photo, reply_markup=create_image_menu(file_id))

    def get_user_labels(user_id):
        user_folder = os.path.join(data_folder, user_id)
        file_path = os.path.join(user_folder, user_id + ".yaml")
        with open(file_path, errors="ignore") as file:
            labels = yaml.safe_load(file)["names"]
            return labels

    def get_image_labels(user_id, file_id):
        user_folder = os.path.join(data_folder, user_id)
        labels_folder = os.path.join(user_folder, "labels")
        labels_path = os.path.join(labels_folder, file_id + ".txt")
        if os.path.isfile(labels_path):
            with open(labels_path, 'r') as new_file:
                full_labels = new_file.readlines()
                user_labels = get_user_labels(user_id)
                labels = []
                classesNum = {}
                for label in full_labels:
                    label = int(label.split()[0])
                    if label not in classesNum:
                        classesNum[label] = 1
                    labels.append(f"{user_labels[label]}-{classesNum[label]}")
                    classesNum[label] += 1
                return labels
        return []
    
    def create_image_labels_menu(labels, file_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        for label in labels:
            keyboard.add(telebot.types.InlineKeyboardButton(text=label,
                                                        callback_data=f"change_label_{label}_for_{file_id}"))
        return keyboard


    def create_user_labels_menu(user_id, file_id, label):
        keyboard = telebot.types.InlineKeyboardMarkup()
        labels = get_user_labels(user_id)
        for key in labels.keys():
            if key < 80:
                continue
            keyboard.add(telebot.types.InlineKeyboardButton(text=labels[key],
                                                        callback_data=f"change_to_{labels[key]}_label_{label}_for_{file_id}"))    
        keyboard.add(telebot.types.InlineKeyboardButton(text="Добавить новую метку",
                                                        callback_data=f"change_to_new_label_{label}_for_{file_id}"))
        return keyboard

    def add_user_label(user_id, to_label):
        user_folder = os.path.join(data_folder, user_id)
        file_path = os.path.join(user_folder, user_id + ".yaml")
        with open(file_path, errors="ignore") as file:
            data_yaml = yaml.safe_load(file)
        max_key = 0
        for key in data_yaml["names"].keys():
            max_key = max(max_key, key)
        data_yaml["names"][max_key + 1] = to_label
        with open(file_path, 'w') as outfile:
            yaml.dump(data_yaml, outfile)

    def change_label(user_id, file_id, from_label, to_label):
        if to_label not in get_user_labels(user_id).values():
            add_user_label(user_id, to_label)
        user_labels = get_user_labels(user_id)
        to_label_key = -1
        for key in user_labels.keys():
            if to_label == user_labels[key]:
                to_label_key = key
        labels = get_image_labels(user_id, file_id)
        from_label_idx = labels.index(from_label)

        user_folder = os.path.join(data_folder, user_id)
        labels_folder = os.path.join(user_folder, "labels")
        labels_path = os.path.join(labels_folder, file_id + ".txt")
        if os.path.isfile(labels_path):
            with open(labels_path, 'r') as new_file:
                full_labels = new_file.readlines()
            label_to_change = full_labels[from_label_idx]
            label_to_change = label_to_change.split()
            label_to_change[0] = str(to_label_key)
            full_labels[from_label_idx] = " ".join(label_to_change) + "\n"
            with open(labels_path, 'w') as new_file:
                new_file.writelines(full_labels)

    def send_done(chat_id):
        bot.send_message(chat_id, "Метка для изображения изменена")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        chat_id = call.from_user.id
        user_id = str(chat_id)
        if call.data.startswith("change_for_"):
            img_id = call.data[11:]
            labels = get_image_labels(user_id, img_id)
            if labels:
                bot.send_message( chat_id, "Какую метку вы хотите заменить?", 
                                reply_markup=create_image_labels_menu(labels, img_id) )
            else:
                bot.send_message( chat_id, "На данном изображении ничего не найдено" )
        elif call.data.startswith("change_label_"):
            splited_call = call.data.split("_for_")
            file_id = splited_call[-1]
            label = splited_call[0][13:]
            bot.send_message(chat_id, "На какую метку заменять?",
                             reply_markup=create_user_labels_menu(user_id, file_id, label))
        elif call.data.startswith("change_to_"):
            splitted = call.data.split("_for_")
            file_id = splitted[-1]
            splitted = splitted[0].split("_label_")
            from_label = splitted[-1]
            if splitted[0].endswith("new"):
                bot.send_message(chat_id, "Введите новую метку")
                waiting_new_marks[user_id] = (file_id, from_label)
            else:
                to_label = splitted[0].split("_to_")[-1]
                change_label(user_id, file_id, from_label, to_label)
                send_done(chat_id)

    @bot.message_handler(content_types=["text"])
    def get_text_messages(message):
        chat_id = message.chat.id
        user_id = str(chat_id)
        if user_id in waiting_new_marks:
            file_id, from_label = waiting_new_marks.pop(user_id)
            change_label(user_id, file_id, from_label, message.text)
            send_done(chat_id)
        else:
            bot.send_message(chat_id, "Отправьте картинку")

#python .\yolov5master\train.py --data .\data\450976890\450976890.yaml --weights .\data\450976890\450976890.pt --img 640 --epochs 3
    bot.infinity_polling()
