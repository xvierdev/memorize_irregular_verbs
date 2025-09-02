import sqlite3


def create_database():
    schema = 'CREATE TABLE IF NOT EXISTS english (' \
        'word VARCHAR(50) UNIQUE NOT NULL,' \
        'translation VARCHAR(50),' \
        'past,' \
        'past_participle)'
    try:
        with sqlite3.Connection('english.db') as conn:
            conn.execute(schema)
            conn.commit()
        return True
    except sqlite3.Error as e:
        print('Erro de sql:', e)
        return False


def insert_into_table(data: tuple):
    try:
        with sqlite3.Connection('english.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO english VALUES (?, ?, ?, ?)', data)
            if cursor.rowcount > 0:
                cursor.close()
                return True
            else:
                cursor.close()
                return False
    except sqlite3.Error as e:
        print('Erro ao inserir dados:', e)
        return False


def insert_menu():
    word = input('infinitive form: ')
    if word == '':
        return False
    translate = input('translate: ')
    if translate == '':
        return False
    past = input('past: ')
    if past == '':
        return False
    past_participle = input('past participle: ')
    if past_participle == '':
        return False
    if insert_into_table((word, translate, past, past_participle)):
        return True
    else:
        return False

def insert_from_file(file):
    lines = []
    with open(file, 'r') as file:
        lines = file.readlines()
    for line in lines:
        insert_into_table(tuple(line.split()))


def get_random_data() -> tuple:
    try:
        with sqlite3.Connection('english.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM english ORDER BY RANDOM() LIMIT 1')
            return cursor.fetchone()
    except sqlite3.Error as e:
        print('Erro ao obter dados:', e)
        return ()


def game(result: tuple):
    print(result[0])
    translate = input('Translate: ').strip()
    past = input('Past: ').strip()
    past_participle = input('Past participle: ').strip()
    if (result[0], translate, past, past_participle) == result:
        return True
    else:
        return False


def get_level(result: tuple):
    return len(set(result)) - 1


def main_menu():
    while True:
        print('choose your option: ')
        op = input().strip().lower()

        if op == '1':
            insert_menu()
        if op == '2':
            points = 0
            try:
                while True:
                    result = get_random_data()
                    if result is None:
                        print('No data found in table, please insert it')
                        break
                    if len(result if result is not None else '') > 0:
                        if game(result):
                            print('Correct')
                            points += get_level(result)
                        else:
                            print('Incorrect:', *result)
            except KeyboardInterrupt:
                print('Points =', points)
        if op in ('0', '', 'q'):
            print('bye.')
            exit()


if __name__ == '__main__':
    create_database()
    insert_from_file('src/list.txt')
    main_menu()
