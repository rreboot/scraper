import sqlite3


def open_db():
    conn = sqlite3.connect('info.db')
    print("Database opened")
    return conn


def create_tables(conn):
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS articles (
             id integer PRIMARY KEY,
             url varchar,
             rating integer
        );
        CREATE TABLE IF NOT EXISTS tags (
             id integer PRIMARY KEY AUTOINCREMENT,
             name varchar
        );
        CREATE TABLE IF NOT EXISTS files (
            id integer PRIMARY KEY AUTOINCREMENT,
            name varchar,
            is_downloaded integer,
            is_published integer,
            article_id integer,
            FOREIGN KEY(article_id) REFERENCES articles(id)
        );
        CREATE TABLE IF NOT EXISTS articles_tags (
            id integer PRIMARY KEY AUTOINCREMENT,
            article_id integer,
            tag_id integer,
            FOREIGN KEY (article_id) REFERENCES articles(id)
            FOREIGN KEY (tag_id) REFERENCES Tags(id)
        );
    ''')
    print("Tables created")
    conn.close


def insert_article(conn, id, url, rating):
    try:
        conn.execute('''
            INSERT INTO articles VALUES (?, ?, ?);
        ''', (id, url, rating))
    except sqlite3.DatabaseError as err:
        print("Error: ", err)
    else:
        conn.commit()


# def insert_tags(conn, id, name, article_id):
#     try:
#         conn.execute('''
#             INSERT INTO tags VALUES (?, ?)
#         ''')