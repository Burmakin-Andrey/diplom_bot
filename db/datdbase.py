import sqlite3

db = sqlite3.connect('bot.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS photo ( id INTEGER PRIMARY KEY, photo BLOB NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS questions ( id INTEGER PRIMARY KEY, text TEXT NOT NULL, answers TEXT NOT NULL, photoid INTEGER, FOREIGN KEY (photoid) REFERENCES photo(id))")
    cur.execute("CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY, user_id INTEGER, q_id INTEGER, answer TEXT, FOREIGN KEY (q_id) REFERENCES questions(id), FOREIGN KEY (user_id) REFERENCES users(id))")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tg_id INTEGER)")
    print("db start")
    db.commit()


async def check_user(id: int):
    user = cur.execute(f"SELECT * FROM users WHERE tg_id=={id}").fetchone()
    if not user:
        cur.execute(f"INSERT INTO users(tg_id) VALUES({id})")
        db.commit()


async def set_answers(user_id, q_id, answer):
    cur.execute(f"INSERT INTO answers(user_id, q_id, answer) VALUES({user_id}, {q_id}, '{answer}')")
    db.commit()


async def set_questions(text, answers, photoid):
    cur.execute(f"INSERT INTO questions(text, answers, photoid) VALUES('{text}', '{answers}', {photoid})")
    db.commit()


async def set_photo(photo):
    with open(photo, "rb") as ph:
        binar_photo = ph.read()
        cur.execute("INSERT INTO photo(photo) VALUES(?)", (binar_photo,))
        db.commit()
        ph.close()


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
    photo_data = cur.execute(f"SELECT photo FROM photo WHERE id={id}").fetchone()
    return photo_data


async def questions_count():
    count = cur.execute(f"SELECT COUNT(*) FROM questions")
    return count.fetchone()[0]


async def test_data():
    await set_photo("cat1.jpg")
    await set_photo("car1.jpg")
    await set_questions("Это кот или собака?", "Кот,Собака", 1)
    await set_questions("Это машина или самолет?", "Машина,Самолет", 2)
