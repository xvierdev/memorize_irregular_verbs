import sqlite3
from rich.console import Console

console = Console()


def create_database():
    # incializa a table principal
    schema = 'CREATE TABLE IF NOT EXISTS english (' \
        'word VARCHAR(50) UNIQUE NOT NULL,' \
        'translation VARCHAR(50) NOT NULL,' \
        'past VARCHAR(50) NOT NULL,' \
        'past_participle VARCHAR(50) NOT NULL)'
    try:
        with sqlite3.Connection('english.db') as conn:
            conn.execute(schema)
            conn.commit()
        return True
    except sqlite3.Error as e:
        console.print('Erro de sql:', e)
        return False


def insert_into_table(data: tuple):
    # inserir dados na tabela
    try:
        with sqlite3.Connection('english.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO english (word, translation, past, past_participle) VALUES (?, ?, ?, ?)', data)
            if cursor.rowcount > 0:
                cursor.close()
                return True
            else:
                cursor.close()
                return False
    except sqlite3.Error as e:
        console.print('Erro ao inserir dados:', e)
        return False


def insert_menu():
    # inserir dados manualmente
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
    # obter dados a partir do arquivo de texto
    lines = []
    with open(file, 'r') as file:
        lines = file.readlines()
    for line in lines:
        insert_into_table(tuple(line.split()))


def get_random_data() -> tuple:
    # obter uma linha aleatória na tabela
    try:
        with sqlite3.Connection('english.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT word, translation, past, past_participle FROM english ORDER BY RANDOM() LIMIT 1')
            return cursor.fetchone()
    except sqlite3.Error as e:
        console.print('Erro ao obter dados:', e)
        return ()


def game(result: tuple, level: int):
    # exibe e formata o resultado obtivo e verifica o acerto ou erro
    color = ['green', 'yellow', 'red']
    console.print(result[0], style=str(color[level]))
    translate = input('Translate: ').strip()
    past = input('Past: ').strip()
    past_participle = input('Past participle: ').strip()
    if (result[0], translate, past, past_participle) == result:
        return True
    else:
        return False


def get_level(result: tuple):
    # obtém o nível de dificuldade da palavra
    return len(set(result)) - 1


def main_menu():
    # menu principal da aplicação
    points = 0
    try:
        console.print("Welcome to the English tournament :skull:")
        name = input('Enter your name: ')

        while True:
            result = get_random_data()
            if result is None:
                console.print('No data found in table, please insert it')
                break
            if len(result if result is not None else '') > 0:
                level = get_level(result)
                if game(result, level - 1):
                    console.print('✅ Correct')
                    points += level
                else:
                    console.print('❌ Incorrect 📜', *result)
    except KeyboardInterrupt:
        console.print(f'\n{points=}')


if __name__ == '__main__':
    create_database()
    insert_from_file('src/list.txt')
    main_menu()
