Идея состоит в том, чтобы использовать yolo для распознавания грабителей в доме
Данный репозиторий является вспомогательным для создания подходящего датасета и обучения моделей
Постепенно пользователь разметит всех членов семьи и следящее око перестанет их распознавать

Репозиторий состоит из репозитория yolov5 и телеграм бота, а так же папки результатов тренировки
Телеграмм бот для каждого нового пользователя создает свою копию модели йоло и папку для хранения данных
Каждый пользователь может добавлять свои фото в бота и он сохраняет их и лейблы + выдает назад в телеграм размеченные фото
По каждому результату можно заменить класс разметки на пользовательскую
Таким образом формируется датасет по пользователю
Далее вручную запускается тренировка модели на размеченных пользователем данных
И обновленная модель копируется из результатов тренировки в данные пользователя

Смысл в том, чтобы научить модель определять членов семьи, в том числе домашних животных
Тестирование проводилось на жене и коте
По результатам работы в первый раз все определялось как жена
Поэтому в датасет были искусственно добавлены фото со случайными людьми и котами из pinterest
После этого жену начало определять с приемлемой точностью(из 10 тестов где-то 1-2 ошибается)
Кот остался неопознанным и требует добавления большего количества своих фото в датасет

Тем не менее на данном можно сделать вывод, что способ рабочий и следующим этапом прикрутить его к системе умного дома для поиска незнакомых людей или котов

# TODO
# 1) Сделать или скачать обширный датасет людей или котов для добавления их на этапе обучения
# 2) Сделать анализ датасета для отслеживания накопления размеченных членов семьи
# 3) Сделать автоматический запуск дообучения по накоплению определенного количества данных
# 4) Используя функции из __main__.py подсоединить камеру, и сделать функцию автоматической отправки пользователю кадров с попавшими туда людьми\животными для разметки в случае ошибок