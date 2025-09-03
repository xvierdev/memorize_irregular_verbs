import sqlite3
import logging
from rich.console import Console

logging.basicConfig(level=logging.DEBUG, encoding='utf-8')
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
            logging.debug('Tabela criada com sucesso.')
        return True
    except sqlite3.Error as e:
        logging.error(e)
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
                logging.info(f'{data} inserido com sucesso.')
                return True
            else:
                cursor.close()
                return False
    except sqlite3.Error as e:
        logging.error(f'Erro ao inserir dados: {e}')
        return False


def insert_from_file(file):
    # obter dados a partir do arquivo de texto
    lines = []
    try:
        with open(file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            insert_into_table(tuple(line.split()))
        logging.info('Dados inseridos com sucesso na database.')
    except FileNotFoundError as e:
        logging.error(f'Erro ao abrir arquivo: {e}')


def get_random_data(dificulty: int, statistics) -> tuple:
    # obter uma linha aleatória na tabela
    next_key = 0
    if len(statistics.keys()) > 0:
        if len(set(statistics.values())) > 1:
            next_key = min(statistics.keys(), key=statistics.get)
            logging.debug(f'{next_key=}')
            logging.debug(f'{statistics=}')

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
            logging.debug(f'{data=}')
            return data[0], data[1:]
    except sqlite3.Error as e:
        logging.error(f'Erro ao obter dados: {e}')
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
    name = ''
    points = 0              # pontuação do jogador
    increment = 0           # contrele de update de nível
    dificulty = 3           # numero de palavras iniciais
    answers = 0             # contagem total de respostas
    corrects = 0            # contagem de acertos
    errors = 0              # contagem de erros
    statistics = dict()     # controle de repetição dos erros
    try:
        console.print("Welcome to the English tournament :skull:")
        name = input('Enter your name: ')
        dificulty = int(input('Chosse difficulty level (1~54): '))

        while True:
            id, result = get_random_data(dificulty, statistics)
            if result is None:
                logging.error('No data found in tables, please insert it.')
                break
            else:
                level = get_level(result)
                if game(result, level - 1):
                    points += level
                    increment += 1
                    corrects += 1
                    if increment % 5 == 0:
                        dificulty += 3
                        increment = 0
                    if statistics.get(id):
                        statistics[id] += 1
                    else:
                        statistics[id] = 1
                    console.print(f'✅ Correct - {dificulty=} - {points=}')
                else:
                    errors += 1
                    console.print('❌ Incorrect 📜', *result)
                    if id in statistics.keys():
                        statistics[id] -= 1
                    else:
                        statistics[id] = -1
                answers += 1
    except KeyboardInterrupt:
        console.print(f'\n{points=}')
        with open('records.txt', '+a', encoding='utf-8') as file:
            file.write(f'record of player {name} = {points}\n')


if __name__ == '__main__':
    create_database()
    insert_from_file('src/list.txt')
    main_menu()
