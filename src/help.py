import sqlite3
from rich.console import Console

console = Console()


def create_database():
    # incializa a table principal
    schema = 'CREATE TABLE IF NOT EXISTS english (' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
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
    with open(file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        insert_into_table(tuple(line.split()))


def get_random_data(dificulty: int, statistics: dict) -> tuple:
    # obter uma linha aleatória na tabela
    max_error = 0
    next_key = 0
    for key, value in statistics.items():
        if value > max_error:
            max_error = value
            next_key = key

    try:
        with sqlite3.Connection('english.db') as conn:
            cursor = conn.cursor()
            if next_key == 0:
                cursor.execute(
                    'SELECT id, word, translation, past, past_participle FROM english WHERE id <= ? ORDER BY RANDOM() LIMIT 1',
                    (dificulty,))
            else:
                cursor.execute(
                    'SELECT id, word, translation, past, past_participle FROM english WHERE id = ?',
                    (next_key,))
                next_key = 0
            data = cursor.fetchone()
            return data[0], data[1:]
    except sqlite3.Error as e:
        console.print('Erro ao obter dados:', e)
        return -1, ()


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
    points = 0              # pontuação do jogador
    increment = 0           # contrele de update de nível
    dificulty = 3           # numero de palavras iniciais
    statistics = dict()     # controle de repetição dos erros
    name = ''
    try:
        console.print("Welcome to the English tournament :skull:")
        name = input('Enter your name: ')
        dificulty = int(input('Chosse difficulty level (1~54): '))

        while True:
            id, result = get_random_data(dificulty, statistics)
            if result is None:
                console.print('No data found in table, please insert it')
                break
            if len(result if result is not None else '') > 0:
                level = get_level(result)
                if game(result, level - 1):
                    console.print(f'✅ Correct - {level=} - {points=}')
                    points += level
                    increment += 1
                    if increment % 10 == 0:
                        dificulty += 3
                        increment = 0
                    if statistics.get(id):
                        if statistics[id] > 0:
                            statistics[id] -= 1
                        else:
                            statistics.pop(id)
                else:
                    console.print('❌ Incorrect 📜', *result)
                    if id in statistics.keys():
                        statistics[id] += 1
                    else:
                        statistics[id] = 1
                    print(statistics)
    except KeyboardInterrupt:
        console.print(f'\n{points=}')
        with open('records.txt', '+a', encoding='utf-8') as file:
            file.write(f'record of player {name} = {points}')


if __name__ == '__main__':
    create_database()
    insert_from_file('src/list.txt')
    main_menu()
