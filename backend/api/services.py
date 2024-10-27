# services.py
import os
import whisper
import numpy as np
import pymorphy2
from pydub import AudioSegment
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from .models import Intent, Subintent, Phrase  # Импортируйте ваши модели Django

# Путь к папке с моделями
MODEL_DIR = "models"
# Создание папки, если она не существует
os.makedirs(MODEL_DIR, exist_ok=True)  

# Указание пути к ffmpeg для работы с библиотекой pydub
ffmpeg_path = r'C:\vs_code\Hack_dgtu\intents\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe'
# Добавление пути к ffmpeg в переменную окружения
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# Инициализация морфологического анализатора для обработки русского языка
morph = pymorphy2.MorphAnalyzer()

# Функция для конвертации аудиофайлов формата .ogg в .wav
def convert_to_wav(audio_path):
    if audio_path.endswith(".ogg"):
        audio = AudioSegment.from_ogg(audio_path)  # Загружаем .ogg файл
        wav_path = audio_path.replace(".ogg", ".wav")  # Задаем путь для .wav
        audio.export(wav_path, format="wav")  # Экспортируем в формате .wav
        return wav_path
    return audio_path  # Возвращаем оригинальный путь, если не .ogg

# Функция для лемматизации текста
def lemmatize_text(text):
    words = text.split()  # Разделение текста на слова
    # Возвращаем лемматизированные слова, объединенные в строку
    return ' '.join(morph.parse(word)[0].normal_form for word in words)

# Проверка функции get_response
def get_response(intent_name, subintent_name=None):
    # Проверка получения ответа поднамерения
    if subintent_name:
        response = Subintent.objects.filter(name=subintent_name, intent__name=intent_name).values_list('answer', flat=True).first()
    else:
        # Получение ответа намерения
        response = Intent.objects.filter(name=intent_name).values_list('answer', flat=True).first()
    
    return response if response else "Ответ не найден."

# Функция для загрузки данных намерений и поднамерений из базы данных
def load_data():
    intent_data = {}  # Словарь для хранения намерений
    subintent_data = {}  # Словарь для хранения поднамерений

    intents = Intent.objects.all()  # Запрос на получение всех намерений

    for intent in intents:
        # Получение фраз, связанных с намерением
        intent_phrases = Phrase.objects.filter(intent=intent).values_list('text', flat=True)
        intent_data[intent.name] = list(intent_phrases)  # Сохраняем фразы в словарь

        # Получение поднамерений для текущего намерения
        subintents = Subintent.objects.filter(intent=intent)
        for subintent in subintents:
            subintent_phrases = Phrase.objects.filter(subintent=subintent).values_list('text', flat=True)
            # Сохраняем поднамерения и их фразы в словаре
            if intent.name not in subintent_data:
                subintent_data[intent.name] = {}
            subintent_data[intent.name][subintent.name] = list(subintent_phrases)

    return intent_data, subintent_data  # Возвращаем данные намерений и поднамерений

# Лемматизация данных и создание маппинга {лемматизированное: исходное}
def create_lemmatized_mapping(data):
    lemmatized_data = {}  # Словарь для хранения лемматизированных данных
    lemmatized_to_original = {}  # Словарь для маппинга лемматизированных форм к оригинальным
    for key, phrases in data.items():
        lemmatized_key = lemmatize_text(key)  # Лемматизация ключа
        lemmatized_phrases = [lemmatize_text(phrase) for phrase in phrases]  # Лемматизация фраз
        lemmatized_data[lemmatized_key] = lemmatized_phrases  # Сохраняем в словарь
        lemmatized_to_original[lemmatized_key] = key  # Сохраняем маппинг
    return lemmatized_data, lemmatized_to_original  # Возвращаем лемматизированные данные и маппинг

# Функция для обучения моделей для намерений и поднамерений
def train_models(intent_data, subintent_data):
    models = {}  # Словарь для хранения обученных моделей

    # Обучение основной модели намерений
    intent_lemmatized, intent_map = create_lemmatized_mapping(intent_data)  # Лемматизация намерений
    intent_model = Pipeline([('tfidf', TfidfVectorizer()), ('classifier', LogisticRegression())])  # Создаем пайплайн
    intent_model.fit(
        [q for phrases in intent_lemmatized.values() for q in phrases],  # Входные данные для обучения
        [key for key, phrases in intent_lemmatized.items() for _ in phrases]  # Метки для обучения
    )
    models['intent'] = {'model': intent_model, 'map': intent_map}  # Сохраняем модель намерений

    # Обучение моделей для поднамерений
    for intent_name, subintents in subintent_data.items():
        subintent_lemmatized, subintent_map = create_lemmatized_mapping(subintents)  # Лемматизация поднамерений
        if len(subintent_map) > 1:  # Обучаем модель только если есть несколько классов
            subintent_model = Pipeline([('tfidf', TfidfVectorizer()), ('classifier', LogisticRegression())])  # Создаем пайплайн для поднамерений
            subintent_model.fit(
                [q for phrases in subintent_lemmatized.values() for q in phrases],  # Входные данные
                [key for key, phrases in subintent_lemmatized.items() for _ in phrases]  # Метки
            )
            models[intent_name] = {'model': subintent_model, 'map': subintent_map}  # Сохраняем модель поднамерений

    return models  # Возвращаем все обученные модели
 
# Функция для загрузки модели Whisper
def load_model(model_name):
    model_path = os.path.join(MODEL_DIR, model_name)  # Определяем путь к модели
    # Если модель не существует, загружаем и сохраняем её
    if not os.path.exists(os.path.join(MODEL_DIR, model_name + ".pt")):
        model = whisper.load_model(model_name)  # Загрузка модели
        model.save_pretrained(MODEL_DIR)  # Сохранение модели
    return whisper.load_model(model_name)  # Возвращаем загруженную модель

# Функция для транскрипции аудио
def transcribe_audio(audio_path):
    model = load_model("medium")  # Загружаем модель Whisper
    audio_path = convert_to_wav(audio_path)  # Конвертируем аудио в .wav
    result = model.transcribe(audio_path, verbose=True, language="ru")  # Транскрибируем аудио
    return result['text'].strip()  # Возвращаем текст транскрипции

# Функция для обнаружения намерения и поднамерения
def detect_intent_and_subintent(user_message, models):
    lemmatized_message = lemmatize_text(user_message)  # Лемматизируем пользовательское сообщение
    
    # Получаем модель и маппинг намерений
    intent_model = models['intent']['model']
    intent_map = models['intent']['map']
    
    # Предсказание намерения с вероятностями
    intent_probas = intent_model.predict_proba([lemmatized_message])[0]
    intent_prediction_index = intent_probas.argmax()
    intent_prediction = intent_model.classes_[intent_prediction_index]
    intent_name = intent_map.get(intent_prediction, intent_prediction)
    intent_confidence = intent_probas[intent_prediction_index]
    
    # Получаем минимальный коэффициент уверенности для намерения
    min_confidence = Intent.objects.get(name=intent_name).min_confidence
    
    if intent_confidence < min_confidence:  # Если уверенность ниже минимального порога
        return intent_name, None  # Возвращаем только намерение, поднамерение не определяем

    # Получаем модель поднамерений для предсказанного намерения
    if intent_name in models:
        subintent_model = models[intent_name]['model']
        subintent_map = models[intent_name]['map']
        
        # Предсказание поднамерения
        subintent_probas = subintent_model.predict_proba([lemmatized_message])[0]
        subintent_prediction_index = subintent_probas.argmax()
        subintent_prediction = subintent_model.classes_[subintent_prediction_index]
        subintent_name = subintent_map.get(subintent_prediction, subintent_prediction)
        subintent_confidence = subintent_probas[subintent_prediction_index]

        print(subintent_prediction)
        print(subintent_confidence)
        
        min_subintent_confidence = Subintent.objects.get(name=subintent_name, intent__name=intent_name).min_confidence
        
        if subintent_confidence >= min_subintent_confidence:  # Если уверенность поднамерения достаточна
            return intent_name, subintent_name  # Возвращаем намерение и поднамерение
        
    return intent_name, None  # Возвращаем только намерение, если поднамерение не определено



# import whisper
# import os
# import numpy as np
# import pymorphy2
# from pydub import AudioSegment
# from sklearn.pipeline import Pipeline
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from .models import Intent, Subintent, Phrase  # Импортируйте ваши модели Django


# # Путь к папке с моделями
# MODEL_DIR = "models"
# # Создание папки, если она не существует
# os.makedirs(MODEL_DIR, exist_ok=True)  

# # Указание пути к ffmpeg для работы с библиотекой pydub
# ffmpeg_path = r'C:\vs_code\Hack_dgtu\intents\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe'
# # Добавление пути к ffmpeg в переменную окружения
# os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# # Инициализация морфологического анализатора для обработки русского языка
# morph = pymorphy2.MorphAnalyzer()

# # Функция для конвертации аудиофайлов формата .ogg в .wav
# def convert_to_wav(audio_path):
#     if audio_path.endswith(".ogg"):
#         audio = AudioSegment.from_ogg(audio_path)  # Загружаем .ogg файл
#         wav_path = audio_path.replace(".ogg", ".wav")  # Задаем путь для .wav
#         audio.export(wav_path, format="wav")  # Экспортируем в формате .wav
#         return wav_path
#     return audio_path  # Возвращаем оригинальный путь, если не .ogg

# # Функция для лемматизации текста
# def lemmatize_text(text):
#     words = text.split()  # Разделение текста на слова
#     # Возвращаем лемматизированные слова, объединенные в строку
#     return ' '.join(morph.parse(word)[0].normal_form for word in words)

# # Проверка функции get_response
# def get_response(intent_name, subintent_name=None):
#     # Проверка получения ответа поднамерения
#     if subintent_name:
#         response = Subintent.objects.filter(name=subintent_name, intent__name=intent_name).values_list('answer', flat=True).first()
#     else:
#         # Получение ответа намерения
#         response = Intent.objects.filter(name=intent_name).values_list('answer', flat=True).first()
    
#     return response if response else "Ответ не найден."


# # Функция для загрузки данных намерений и поднамерений из базы данных
# def load_data():
#     intent_data = {}  # Словарь для хранения намерений
#     subintent_data = {}  # Словарь для хранения поднамерений

#     intents = Intent.objects.all()  # Запрос на получение всех намерений

#     for intent in intents:
#         # Получение фраз, связанных с намерением
#         intent_phrases = Phrase.objects.filter(intent=intent).values_list('text', flat=True)
#         intent_data[intent.name] = list(intent_phrases)  # Сохраняем фразы в словарь

#         # Получение поднамерений для текущего намерения
#         subintents = Subintent.objects.filter(intent=intent)
#         for subintent in subintents:
#             subintent_phrases = Phrase.objects.filter(subintent=subintent).values_list('text', flat=True)
#             # Сохраняем поднамерения и их фразы в словаре
#             if intent.name not in subintent_data:
#                 subintent_data[intent.name] = {}
#             subintent_data[intent.name][subintent.name] = list(subintent_phrases)

#     return intent_data, subintent_data  # Возвращаем данные намерений и поднамерений

# # Лемматизация данных и создание маппинга {лемматизированное: исходное}
# def create_lemmatized_mapping(data):
#     lemmatized_data = {}  # Словарь для хранения лемматизированных данных
#     lemmatized_to_original = {}  # Словарь для маппинга лемматизированных форм к оригинальным
#     for key, phrases in data.items():
#         lemmatized_key = lemmatize_text(key)  # Лемматизация ключа
#         lemmatized_phrases = [lemmatize_text(phrase) for phrase in phrases]  # Лемматизация фраз
#         lemmatized_data[lemmatized_key] = lemmatized_phrases  # Сохраняем в словарь
#         lemmatized_to_original[lemmatized_key] = key  # Сохраняем маппинг
#     return lemmatized_data, lemmatized_to_original  # Возвращаем лемматизированные данные и маппинг

# # Функция для обучения моделей для намерений и поднамерений
# def train_models(intent_data, subintent_data):
#     models = {}  # Словарь для хранения обученных моделей

#     # Обучение основной модели намерений
#     intent_lemmatized, intent_map = create_lemmatized_mapping(intent_data)  # Лемматизация намерений
#     intent_model = Pipeline([('tfidf', TfidfVectorizer()), ('classifier', LogisticRegression())])  # Создаем пайплайн
#     intent_model.fit(
#         [q for phrases in intent_lemmatized.values() for q in phrases],  # Входные данные для обучения
#         [key for key, phrases in intent_lemmatized.items() for _ in phrases]  # Метки для обучения
#     )
#     models['intent'] = {'model': intent_model, 'map': intent_map}  # Сохраняем модель намерений

#     # Обучение моделей для поднамерений
#     for intent_name, subintents in subintent_data.items():
#         subintent_lemmatized, subintent_map = create_lemmatized_mapping(subintents)  # Лемматизация поднамерений
#         if len(subintent_map) > 1:  # Обучаем модель только если есть несколько классов
#             subintent_model = Pipeline([('tfidf', TfidfVectorizer()), ('classifier', LogisticRegression())])  # Создаем пайплайн для поднамерений
#             subintent_model.fit(
#                 [q for phrases in subintent_lemmatized.values() for q in phrases],  # Входные данные
#                 [key for key, phrases in subintent_lemmatized.items() for _ in phrases]  # Метки
#             )
#             models[intent_name] = {'model': subintent_model, 'map': subintent_map}  # Сохраняем модель поднамерений

#     return models  # Возвращаем все обученные модели
 
# # Функция для загрузки модели Whisper
# def load_model(model_name):
#     model_path = os.path.join(MODEL_DIR, model_name)  # Определяем путь к модели
#     # Если модель не существует, загружаем и сохраняем её
#     if not os.path.exists(os.path.join(MODEL_DIR, model_name + ".pt")):
#         model = whisper.load_model(model_name)  # Загрузка модели
#         model.save_pretrained(MODEL_DIR)  # Сохранение модели
#     return whisper.load_model(model_name)  # Возвращаем загруженную модель

# # Функция для транскрипции аудио
# def transcribe_audio(audio_path):
#     model = load_model("medium")  # Загружаем модель Whisper
#     audio_path = convert_to_wav(audio_path)  # Конвертируем аудио в .wav
#     result = model.transcribe(audio_path, verbose=True, language="ru")  # Транскрибируем аудио
#     return result['text'].strip()  # Возвращаем текст транскрипции

# # Функция для обнаружения намерения и поднамерения
# def detect_intent_and_subintent(user_message, models):
#     lemmatized_message = lemmatize_text(user_message)  # Лемматизируем пользовательское сообщение
    
#     # Получаем модель и маппинг намерений
#     intent_model = models['intent']['model']
#     intent_map = models['intent']['map']
    
#     # Предсказание намерения с вероятностями
#     intent_probas = intent_model.predict_proba([lemmatized_message])[0]
#     intent_prediction_index = intent_probas.argmax()
#     intent_prediction = intent_model.classes_[intent_prediction_index]
#     intent_name = intent_map.get(intent_prediction, intent_prediction)
#     intent_confidence = intent_probas[intent_prediction_index]
    
#     # Получаем минимальный коэффициент уверенности для намерения
#     min_intent_confidence = Intent.objects.get(name=intent_name).min_confidence
    
#     if intent_confidence >= min_intent_confidence:  # Проверка уверенности намерения
#         # Если у намерения есть поднамерения, проверяем их
#         if intent_name in models:
#             subintent_model = models[intent_name]['model']
#             subintent_map = models[intent_name]['map']
#             subintent_probas = subintent_model.predict_proba([lemmatized_message])[0]
#             subintent_prediction_index = subintent_probas.argmax()
#             subintent_prediction = subintent_model.classes_[subintent_prediction_index]
#             subintent_name = subintent_map.get(subintent_prediction, subintent_prediction)
#             subintent_confidence = subintent_probas[subintent_prediction_index]
            
#             # Получаем минимальный коэффициент уверенности для поднамерения
#             min_subintent_confidence = Subintent.objects.get(name=subintent_name, intent__name=intent_name).min_confidence

#             # Проверка уверенности поднамерения
#             if subintent_confidence >= min_subintent_confidence:
#                 return intent_name, subintent_name  # Возвращаем намерение и поднамерение
#             else:
#                 return intent_name, None  # Возвращаем только намерение
#         else:
#             return intent_name, None  # Возвращаем намерение, если поднамерений нет
#     return None, None  # Если намерение не прошло по уверенности


# # Основная функция для обработки текста с использованием обученной модели
# def handle_message(user_message, models):
#     intent, subintent = detect_intent_and_subintent(user_message, models)  # Обнаруживаем намерение и поднамерение
#     return get_response(intent, subintent)  # Получаем ответ на основе обнаруженных намерений и поднамерений


# # Функция для обработки аудиосообщения
# def handle_audio_intent(audio_path, models):
#     transcribed_text = transcribe_audio(audio_path)  # Транскрибируем аудио
#     return handle_message(transcribed_text, models)  # Обрабатываем транскрибированный текст

# if __name__ == "__main__":
#     # Загружаем данные намерений и поднамерений из базы данных
#     intent_data, subintent_data = load_data()

#     # Обучаем модели на основе загруженных данных
#     models = train_models(intent_data, subintent_data)

#     # Обработка примера: путь к аудиофайлу
#     audio_file_path = "ogg/ip.ogg"
#     detected_intent = handle_audio_intent(audio_file_path, models)  # Обрабатываем аудиосообщение
#     print("Намерение:", detected_intent)  # Выводим обнаруженное намерение
