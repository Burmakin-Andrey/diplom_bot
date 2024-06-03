import sqlite3

import xml.etree.ElementTree as ET

db = sqlite3.connect('bot.db')
cur = db.cursor()


async def db_start():
    cur.execute('''CREATE TABLE IF NOT EXISTS photo ( id INTEGER PRIMARY KEY, file_name TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS questions ( id INTEGER PRIMARY KEY, text TEXT NOT NULL, answers TEXT NOT NULL, photoid INTEGER, FOREIGN KEY (photoid) REFERENCES photo(id))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY, user_id INTEGER, q_id INTEGER, answer TEXT, FOREIGN KEY (q_id) REFERENCES questions(id), FOREIGN KEY (user_id) REFERENCES users(id))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tg_id INTEGER, name TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS password (id INTEGER PRIMARY KEY, user_pas TEXT)''')
    cur.execute('''INSERT OR IGNORE INTO password (id, user_pas) VALUES (1, 'user')''')
    print("db start")
    db.commit()


async def check_user(id: int, user_name="", valid=False):
    print(f'Name in bd:{user_name}')
    user = cur.execute(f"SELECT * FROM users WHERE tg_id=={id}").fetchone()
    if user:
        return True
    if not user and valid:
        cur.execute(f"INSERT INTO users(tg_id, name) VALUES({id}, '{user_name}')")
        db.commit()
        return True
    return False


async def set_answers(user_id, q_id, answers):
    answers_list = ""
    for answer in answers:
        answers_list += f"{answer},"
    answers_list = answers_list[:-1]
    cur.execute(f"INSERT INTO answers(user_id, q_id, answer) VALUES({user_id}, {q_id}, '{answers_list}')")
    db.commit()


async def set_questions(text, answers, photoid):
    cur.execute(f"INSERT INTO questions(text, answers, photoid) VALUES('{text}', '{answers}', {photoid})")
    db.commit()


async def set_photo(file_name):
    cur.execute(f"INSERT INTO photo(file_name) VALUES('{file_name}')")
    db.commit()
    return cur.lastrowid


async def set_password(pas):
    cur.execute(f'UPDATE password set user_pas=(?) WHERE id=1', (pas,))
    db.commit()


async def get_question(id):
    question = cur.execute(f"SELECT * FROM questions WHERE id={id}").fetchall()
    print(question[0][1])
    return question[0]


async def get_answer(id):
    answer = cur.execute(f"SELECT * FROM answers WHERE id={id}").fetchall()
    if not answer:
        return None
    else:
        return answer


async def get_photo(id):
    file = cur.execute(f"SELECT file_name FROM photo WHERE id={id}").fetchone()
    print(file)
    with open(f'img/{file[0]}', "rb") as photo:
        photo_data = photo
        return photo.read()


async def get_password():
    pas = cur.execute(f"SELECT user_pas FROM password WHERE id=1").fetchone()
    return pas[0]


async def questions_count():
    count = cur.execute(f"SELECT COUNT(*) FROM questions")
    return count.fetchone()[0]


async def get_passed_users():
    users = cur.execute(f"SELECT DISTINCT user_id FROM answers;").fetchall()
    print(users)
    print(users[0][0])
    return len(users), users


async def get_user_name(tg_id):
    name = cur.execute(f"SELECT name FROM users WHERE tg_id={tg_id};").fetchone()
    return name[0]


async def delete_users():
    cur.execute(f"DELETE FROM users")
    db.commit()

async def get_users_answers(question_id):
    data = cur.execute(f'SELECT answer FROM answers WHERE q_id = {question_id}').fetchall()
    return data


async def fill_db_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for question in root:
        text = question.find('text').text
        answers = question.find('answers').text
        image_file = question.find('image_file').text
        photoid = await set_photo(image_file)
        await set_questions(text, answers, photoid)
    db.commit()
