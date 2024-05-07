import telebot
import sqlite3
import validators
import pandas as pd
from scholarly import scholarly
from scholarly import ProxyGenerator

# Telegram API token
token = '6900920415:AAGYm-HmKmZWv3-g22SgUCCAwLToVdneYKc'

# ScraperAPI token for Scholarly proxy
API_key = '0f9ebc275950b6fa94b7b2439712a0ce'

# Generate proxy to bypass Google Scholar antibot
pg = ProxyGenerator()
pg.ScraperAPI(API_key)
scholarly.use_proxy(pg)

# Evaluate tg bot
bot = telebot.TeleBot(token)

# CCreate sqlite db if not created before
db_name = 'database.db'
connection = sqlite3.connect(db_name)
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Articles (id INTEGER PRIMARY KEY,
                                                       link TEXT NOT NULL,
                                                       title TEXT NOT NULL,
                                                       author TEXT NOT NULL,
                                                       year TEXT NOT NULL,
                                                       Journal TEXT NOT NULL)''')
connection.commit()
connection.close()


def search_in_scholar(query: str) -> dict:
    """
    This function use scholarly module to find information about article by query
    Information to find if : title, author, year, year, Journal
    If information is not found or API is unavailable params will remains empty
    in: query - query to find in Google Scholar. This is expected to be a url.
    out: outdict - vocabular with extracted data
    """
    try:
        search_query = scholarly.search_pubs(query)
        result = next(search_query)['bib']
        outdict = {"link": query, "title": result["title"], 'author': result["author"][0], 'year': result["pub_year"],
                   'Journal': result['venue']}
    except:
        outdict = {"link": query, "title": '', 'author': '', 'year': '', 'Journal': ''}
    return outdict


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
    loc_cursor.execute('SELECT id,link, title,author,year,Journal FROM Articles WHERE ROWID = ?', (rowid,))
    result = loc_cursor.fetchall()
    loc_connection.commit()
    loc_connection.close()
    out_mes = output_formatter(result)
    return out_mes


def show_last() -> str:
    """
    This function create output message with last article data
    out: out_mes - output message
    """
    loc_connection = sqlite3.connect(db_name)
    loc_cursor = loc_connection.cursor()
    loc_cursor.execute('SELECT id,link, title,author,year,Journal FROM Articles ORDER BY id DESC LIMIT 1')
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
    loc_cursor.execute('SELECT id,link, title,author,year,Journal FROM Articles')
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
    loc_cursor.execute('DELETE FROM Articles where id = ?', (rowid,))
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
def start_message(message):
    welcome_message = 'Привет!\n Article_bot - Бот для организации хранения ссылок на научные статьи!' \
                      ' \n Вызовите /help чтобы получить подробности'
    bot.send_message(message.chat.id, welcome_message)


@bot.message_handler(commands=['help'])
def start_message(message):
    help_vocabular = {"/add + URL": "Укажите URL адрес статьи, которую хотите добавить",
                      "/show_id": "Вывести информацию о статье по id",
                      "/show_all": "Вывести информацию о всех сохраненных статьях",
                      "/export + format": "Укажите формат (Поддерживается format=xlsx/csv) для экспорта сохраненных статей",
                      "/delete_id": "Удалить статью из сохраненных по id",
                      "/clear": "Удалить все сохраненные статьи",
                      }
    help_message = "Article_bot - Бот для организации хранения ссылок на научные статьи! \n"
    for key in help_vocabular.keys():
        help_message = help_message + key + " - " + help_vocabular[key] + "\n"
    bot.send_message(message.chat.id, help_message)


@bot.message_handler(commands=['add'])
def add_command(message):
    # query expected to be url
    query = message.text.replace('/add', '').strip().replace(" ", "")
    # check url is valid
    if validators.url(query):
        # find data in Google Scholar
        scholar_voc = search_in_scholar(query)
        # If data is empy then search in scholar is failed
        if scholar_voc['title'] == "":
            bot.send_message(message.chat.id, "Не удалось найти статью в Google Schoolar")
        # Add article to database
        add_article(scholar_voc)
        # Show added article
        result = show_last()
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Некорректная ссылка")


@bot.message_handler(commands=['show_id'])
def show_id_command(message):
    # retrieve id to show
    id_to_show = message.text.replace('/show_id', '').strip().replace(" ", "")
    # id check
    try:
        id_to_show = int(id_to_show)
        result = show_article(id_to_show)
        bot.send_message(message.chat.id, result)
    except:
        bot.send_message(message.chat.id, "Некорректный id")


@bot.message_handler(commands=['show_all'])
def show_all_command(message):
    result = show_all()
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['clear'])
def clear_command(message):
    clear()


@bot.message_handler(commands=['delete_id'])
def delete_id_command(message):
    id_to_delete = message.text.replace('/delete_id', '').strip().replace(" ", "")
    # id check
    try:
        id_to_delete = int(id_to_delete)
        delete_id(id_to_delete)
        bot.send_message(message.chat.id, "Удалено")
    except:
        bot.send_message(message.chat.id, "Некорректный id")


@bot.message_handler(commands=['export'])
def export_command(message):
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
