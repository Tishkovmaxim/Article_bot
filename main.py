rimport telebot
import sqlite3
import validators
import pandas as pd
from scholarly import scholarly
from scholarly import ProxyGenerator
from scholarly import _proxy_generator

# Telegram API token
token = 'insert_here'

# ScraperAPI token for Scholarly proxy
API_key = 'insert_here'

# Generate proxy to bypass Google Scholar antibot
pg = ProxyGenerator()
# pg.FreeProxies()
pg.ScraperAPI(API_key)

scholarly.use_proxy(pg)

# Evaluate tg bot
bot = telebot.TeleBot(token)

# CCreate sqlite db if not created before
db_name = 'database.db'
connection = sqlite3.connect(db_name)
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Articles (link TEXT NOT NULL UNIQUE,
                                                       title TEXT,
                                                       author TEXT,
                                                       year TEXT,
                                                       Journal TEXT)''')
connection.commit()
connection.close()


def search_in_scholar(query: str) -> list:
    """
    This function use scholarly module to find information about article by query
    Information to find is : title, author, year, Journal
    If information is not found  params will remains empty
    If API is unavailable Exception will be raised and no information will be returned.
    in: query - query to find in Google Scholar. This is expected to be an url.
    out: outdict - vocabulary with extracted data
    out: status - status of request to Scholar.
         Notice: not found in scholar is status = True (bc. request was successful)
    out: message - output message if error occurs
    """
    try:
        search_query = scholarly.search_pubs(query)
        result = next(search_query)['bib']
        outdict = {"link": query, "title": result["title"], 'author': result["author"][0], 'year': result["pub_year"],
                   'Journal': result['venue']}
        status = True  # status of request
        message = ''  # output message
    except Exception as e:
        status = False
        message = e
        outdict = {"link": query, "title": '', 'author': '', 'year': '', 'Journal': ''}
        if type(e) == _proxy_generator.MaxTriesExceededException:  # API problem happen here
            message = "Не удалось подключиться к Google Scholar: " + repr(e)
        if type(e) == StopIteration:  # This means empty result from request
            message = "По вашему запросу ничего не найдено в Google Scholar!\nДобавлена только ссылка."
            outdict = {"link": query, "title": '', 'author': '', 'year': '', 'Journal': ''}
            status = True
    return [outdict, status, message]


def output_formatter(result: list) -> str:
    """
    This function process list with article data to output message string
    in: result - list with extracted data
    out: output - output message string
    """
    output = ''
    for row in result:
        output = output + "\n" + "\n" + f"Id : {row[0]} \nLink : {row[1]} \nTitle : {row[2]} \nAuthor : {row[3]}" \
                                        f" \nYear : {row[4]} \nJournal : {row[5]}"
    return output


def add_article(scholar_voc: dict) -> None:
    """
    This function add article data in the sqlite database
    in: scholar_voc - vocabulary with extracted data
    """
    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('INSERT INTO Articles (link, title,author,year,Journal) VALUES (?, ?, ?, ?, ?)',
                       (scholar_voc['link'], scholar_voc['title'], scholar_voc['author'], scholar_voc['year'],
                        scholar_voc['Journal']))
    loc_connection.commit()
    loc_connection.close()


def show_article(rowid: int) -> str:
    """
    This function create output message with article data by id
    in: rowid - article id
    out: out_mes - output message
    """
    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('SELECT * FROM Articles where rowid = ?', (rowid,))
    # check is rowid belongs to existing articles
    row = loc_cursor.fetchone()
    if row is None:
        loc_connection.commit()
        loc_connection.close()
        raise Exception('Такого id нет!')
    loc_connection.commit()
    loc_cursor.execute('SELECT rowid,link, title,author,year,Journal FROM Articles WHERE ROWID = ?', (rowid,))
    result = loc_cursor.fetchall()
    loc_connection.commit()
    loc_connection.close()
    out_mes = output_formatter(result)
    return out_mes


def show_last() -> str:
    """
    This function create output message with last added article data
    out: out_mes - output message
    """
    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('SELECT rowid,link, title,author,year,Journal FROM Articles ORDER BY rowid DESC LIMIT 1')
    result = loc_cursor.fetchall()
    loc_connection.commit()
    loc_connection.close()
    out_mes = output_formatter(result)
    return out_mes


def show_all() -> str:
    """
    This function create output message with all existing articles data
    out: out_mes - output message
    """

    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('SELECT rowid ,link, title,author,year,Journal FROM Articles')
    result = loc_cursor.fetchall()
    loc_connection.commit()
    loc_connection.close()
    # if table is empty result will be []
    if not result == []:
        out_mes = output_formatter(result)
    else:
        out_mes = "Пока ничего нет"
    return out_mes


def delete_id(rowid: int) -> None:
    """
    This function delete article from database by id
    in: rowid - article id
    """
    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('SELECT * FROM Articles where rowid = ?', (rowid,))
    # check is rowid belongs to existing articles
    row = loc_cursor.fetchone()
    if row is None:
        loc_connection.commit()
        loc_connection.close()
        raise Exception('Такого id нет!')
    loc_connection.commit()
    # deletion
    loc_cursor.execute('DELETE FROM Articles where rowid = ?', (rowid,))
    loc_connection.commit()
    # renumeration id after deleting
    loc_cursor.execute('UPDATE Articles set rowid=rowid-1 where rowid > ?', (rowid,))
    loc_connection.commit()
    loc_connection.close()


def clear() -> None:
    """
    This function delete all articles from database
    """
    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('DELETE FROM Articles')
    loc_connection.commit()
    loc_connection.close()


@bot.message_handler(commands=['start'])
def start_command(message):
    """
    This function operate on /start command from user
    welcome message will appear
    """
    welcome_message = 'Привет!\n Article_bot - Бот для организации хранения ссылок на научные статьи!' \
                      ' \n Вызовите /help чтобы получить подробности'
    bot.send_message(message.chat.id, welcome_message)


@bot.message_handler(commands=['help'])
def help_command(message):
    """
    This function operate on /help command from user
    Show help
    """
    help_vocabular = {"/add + URL": "Введите команду /add и укажите URL адрес статьи, которую хотите добавить",
                      "/show_id + id": "Введите команду /show_id и укажите id статьи, информацию о которой хотите вывести",
                      "/show_all": "Введите команду /show_all, чтобы вывести информацию о всех сохраненных статьях",
                      "/export + format": "Введите команду /export и укажите формат (Поддерживается format=xlsx/csv) для экспорта сохраненных статей",
                      "/delete_id + id": "Введите команду /delete_id и укажите id статьи, которую хотите удалить из списка",
                      "/clear": "Введите команду /clear, чтобы удалить все сохраненные статьи",
                      }
    help_message = "Article_bot - Бот для организации хранения ссылок на научные статьи!" \
                   " \n Знак \"+\" писть не нужно.\n"
    for key in help_vocabular.keys():
        help_message = help_message + key + " - " + help_vocabular[key] + "\n"
    bot.send_message(message.chat.id, help_message)


@bot.message_handler(commands=['add'])
def add_command(message):
    """
    This function operate on /add command from user
    add article in the sqlite database by syntax: "/add link"
    """
    # query expected to be url
    query = message.text.replace('/add', '').strip().replace(" ", "")
    # check url is valid
    if validators.url(query):
        bot.send_message(message.chat.id, "Пытаюсь найти статью в Scholar...")
        # find data in Google Scholar
        [scholar_voc, status, out_message] = search_in_scholar(query)
        # If data is empy then search in scholar is failed
        if out_message != "":
            bot.send_message(message.chat.id, out_message)
        if status:
            # Add article to database
            try:
                add_article(scholar_voc)
                # Show added article
                result = show_last()
                bot.send_message(message.chat.id, result)
            except sqlite3.IntegrityError:
                bot.send_message(message.chat.id, "Статья уже добавлена!")
    else:
        bot.send_message(message.chat.id, "Некорректная ссылка")


@bot.message_handler(commands=['show_id'])
def show_id_command(message):
    """
    This function operate on /show_id command from user
    Show information about article by id, syntax: "/show_id id"
    """
    # retrieve id to show
    id_to_show = message.text.replace('/show_id', '').strip().replace(" ", "")
    # id check
    try:
        id_to_show = int(id_to_show)
        if id_to_show <= 0:
            raise Exception('Id должен быть положителен')
        result = show_article(id_to_show)
        bot.send_message(message.chat.id, result)
    except Exception as e:
        if type(e) == Exception:
            bot.send_message(message.chat.id, e)
        else:
            bot.send_message(message.chat.id, "Некорректный id")


@bot.message_handler(commands=['show_all'])
def show_all_command(message):
    """
    This function operate on /show_all command from user
    Show information about all articles
    """
    result = show_all()
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['clear'])
def clear_command(message):
    """
    This function operate on /clear command from user
    Show information delete all articles
    """
    clear()
    bot.send_message(message.chat.id, "Все статьи удалены")


@bot.message_handler(commands=['delete_id'])
def delete_id_command(message):
    """
    This function operate on /delete_id command from user
    delete article from the sqlite database by id, syntax: "/delete id"
    """
    id_to_delete = message.text.replace('/delete_id', '').strip().replace(" ", "")
    # id check
    try:
        id_to_delete = int(id_to_delete)
        if id_to_delete <= 0:
            raise Exception('Id должен быть положителен')
        delete_id(id_to_delete)
        bot.send_message(message.chat.id, "Удалено")
    except Exception as e:
        if type(e) == Exception:
            bot.send_message(message.chat.id, e)
        else:
            bot.send_message(message.chat.id, "Некорректный id")


@bot.message_handler(commands=['export'])
def export_command(message):
    """
    This function operate on /export command from user
    Export all articles to format=xlsx/csv, syntax : "/export format"
    """
    supported_types = ['csv', 'xlsx']
    outtype = message.text.replace('/export', '').strip().replace(" ", "")
    # check outtype is supported
    if outtype not in supported_types:
        bot.send_message(message.chat.id, "Неподдерживаемый тип " + outtype)
        return

    loc_connection = sqlite3.connect(db_name)
    # create pandas dataframe to easy export
    df = pd.read_sql_query("select * from Articles", loc_connection)
    loc_connection.close()

    if outtype == 'csv':
        df.to_csv(r'Articles.csv')

    if outtype == 'xlsx':
        df.to_excel(r'Articles.xlsx')

    # send to user
    doc = open('Articles.' + outtype, 'rb')
    bot.send_document(message.chat.id, doc)


bot.infinity_polling(none_stop=True, interval=0)
