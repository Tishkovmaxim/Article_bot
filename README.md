# Сведения о программе
В данном репозитории располагается исходный код для телеграмм бота Article_bot @sci_article_bot.\
Article_bot - Бот для организации хранения ссылок на научные статьи!\
Функционал бота позволяет сохранять ссылки на научные статьи, производить поиск метаданных статьи в Google Scholar (Название, автор, год и т.д.), а также экспортировать полученный список литературы.

Т.к. Google Scholar не обладает официальным API, поиск производится с помощью модуля Scholarly и сервиса ScraperAPI.
Поэтому работоспособность бота зависит от статуса ScraperAPI.

# Установка 

1. Установите интерпретатор [python]([openweather](https://openweathermap.org/)) версии 3.11.7 или выше
2. Клонируйте репозиторий, или скачайте файлы из него
3. Создайте виртуальное окружение в директории проекта с помощью команды:\
`python -m venv {venv name}`

4. Активируйте виртуальное окружение с помощью команд:\
(Windows) при использовании командной строки:\
`venv\Scripts\activate.bat`\
(Windows) при использовании PowerShell (например при запуске через IDE PyCharm):\
`venv\Scripts\Activate.ps1`\
(MacOs) через консоль с помощью команды:\
`source venv/bin/activate`
6. Установите необходимые библиотеки из файла requirements.txt с помощью команды:\
`pip install -r requirements.txt`
7. Зарегистрируйтесь на сайте [ScraperAPI](https://www.scraperapi.com/scale-data-collection/) и получить API ключ.
8. Вставьте API ключ как значение переменной API_key в файле main.py в директории программы\
*ВНИМАНИЕ: по умолчанию в программе задан API ключ автора программы. Из-за ограничения количества запросов бесплатного функционала сервиса [ScraperAPI](https://www.scraperapi.com/scale-data-collection/) могут возникать ошибки.*\
*Также в работе сервиса на территории РФ могут возникать неполадки. При ошибках подключения рекомендуется использовать VPN.*

# Инструкция к использованию
Активация бота производится стандартной командой /start, после чего высветится стартовое сообщение:

```
Привет!
Article_bot - Бот для организации хранения ссылок на научные статьи!'
Вызовите /help чтобы получить подробности
```

По команде /help появляется подсказка:
```
Article_bot - Бот для организации хранения ссылок на научные статьи! 
 Знак "+" писть не нужно.
/add + URL - Введите команду /add и укажите URL адрес статьи, которую хотите добавить
/show_id + id - Введите команду /show_id и укажите id статьи, информацию о которой хотите вывести
/show_all - Введите команду /show_all, чтобы вывести информацию о всех сохраненных статьях
/export + format - Введите команду /export и укажите формат (Поддерживается format=xlsx/csv) для экспорта сохраненных статей
/delete_id + id - Введите команду /delete_id и укажите id статьи, которую хотите удалить из списка
/clear - Введите команду /clear, чтобы удалить все сохраненные статьи
```

# Пример использования
Возьмем научную [статью](https://link.springer.com/chapter/10.1007/978-3-030-66948-5_9) и добавим её в наш список:
```
/add https://link.springer.com/chapter/10.1007/978-3-030-66948-5_9
```
Статья будет успешно добавлена, что подтвердится ответным сообщением:
```
Id : 1 
Link : https://link.springer.com/chapter/10.1007/978-3-030-66948-5_9 
Title : Influence of linear elastic stresses on hydrogen diffusion into metals 
Author : PM Grigoreva 
Year : 2021 
Journal : Advances in Hydrogen …
```

Теперь добавим еще [две](https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-c4e4e4d9-5e69-4819-886d-34042135a434) [статьи](https://www.sciencedirect.com/science/article/pii/S1875389215015321) и выведем весь имеющийся список:
```
/add https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-c4e4e4d9-5e69-4819-886d-34042135a434
/add https://www.sciencedirect.com/science/article/pii/S1875389215015321
/show_all
```

Получаем ответным сообщением:
```
Id : 1 
Link : https://link.springer.com/chapter/10.1007/978-3-030-66948-5_9 
Title : Influence of linear elastic stresses on hydrogen diffusion into metals 
Author : PM Grigoreva 
Year : 2021 
Journal : Advances in Hydrogen …

Id : 2 
Link : https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-c4e4e4d9-5e69-4819-886d-34042135a434 
Title : Improper interpretation of dilatometric data for cooling transformation in steels 
Author : B Pawłowski 
Year : 2014 
Journal : Archives of Metallurgy and …

Id : 3 
Link : https://www.sciencedirect.com/science/article/pii/S1875389215015321 
Title : Laser welding process–a review of keyhole welding modelling 
Author : J Svenungsson 
Year : 2015 
Journal : Physics procedia
```

Полученный список можно экспортировать в xlsx/scv таблицу:
```
/export csv
/export xlsx
```
