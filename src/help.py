import sqlite3
import logging
from rich.console import Console
from sound import play

logging.basicConfig(level=logging.INFO, encoding='utf-8', filename='debug.log')
console = Console()


_INCORPORED_LIST = """be ser was/were been
become tornar-se became become
begin começar began begun
break quebrar broke broken
bring trazer brought brought
build construir built built
buy comprar bought bought
read ler read read
catch pegar caught caught
run correr ran run
choose escolher chose chosen
say dizer said said
come vir came come
cut cortar cut cut
see ver saw seen
do fazer did done
sell vender sold sold
draw desenhar drew drawn
send enviar sent sent
dream sonhar dreamt dreamt
shut fechar shut shut
drive dirigir drove driven
sing cantar sang sung
drink beber drank drunk
sit sentar sat sat
eat comer ate eaten
sleep dormir slept slept
fall cair fell fallen
speak falar spoke spoken
feel sentir felt felt
spend gastar spent spent
fight lutar fought fought
swim nadar swam swum
find encontrar found found
take pegar took taken
fly voar flew flown
teach ensinar taught taught
forget esquecer forgot forgotten
tell contar told told
forgive perdoar forgave forgiven
think pensar thought thought
get pegar got got
throw lançar threw thrown
give dar gave given
understand entender understood understood
go ir went gone
wake acordar woke woken
have ter had had
wear vestir wore worn
know saber knew known
win ganhar won won
write escrever wrote written
"""


def create_database():
    # inicializa a table principal
    schema = 'CREATE TABLE IF NOT EXISTS english (' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'word VARCHAR(50) UNIQUE NOT NULL,' \
        'translation VARCHAR(50) NOT NULL,' \
        'past VARCHAR(50) NOT NULL,' \
        'past_participle VARCHAR(50) NOT NULL);' \
        'CREATE TABLE IF NOT EXISTS records (' \
        'name VARCHAR(50) DEFAULT \'player1\',' \
        'record INTEGER DEFAULT 0,' \
        'corrects INTEGER DEFAULT 0,' \
        'errors INTEGER DEFAULT 0);'
    try:
        with sqlite3.Connection('english.db') as conn:
            conn.executescript(schema)
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


def insert_from_string(lines):
    # obter dados a partir do arquivo de texto
    try:
        for line in lines:
            if len(line.split()) == 4:
                insert_into_table(tuple(line.split()))
        logging.info('Dados inseridos com sucesso na database.')
    except FileNotFoundError as e:
        logging.error(f'Erro ao abrir arquivo: {e}')


def get_random_data(dificulty: int, statistics) -> tuple:
    # obter uma linha aleatória na tabela
    next_key = 0
    if len(statistics.keys()) > 0:
        if len(set(statistics.values())) > 2:  # diferença de frequencia
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
    # exibe e formata o resultado obtido e verifica o acerto ou erro
    color = ['green', 'yellow', 'red']
    console.print(result[0], style=str(color[level]))
    play(result[0])
    translate = input('Translate: ').strip()
    play(translate, 'pt-br')
    past = input('Past: ').strip()
    play(past)
    past_participle = input('Past participle: ').strip()
    play(past_participle)
    if (result[0], translate, past, past_participle) == result:
        return True
    else:
        return False


def get_level(result: tuple):
    # obtém o nível de dificuldade da palavra
    return len(set(result)) - 1


def write_records(data: tuple):
    try:
        with sqlite3.connect('english.db') as conn:
            conn.execute('INSERT INTO records VALUES (?,?,?,?)', data)
            conn.commit()
            logging.info('Score gravado com sucesso.')
    except sqlite3.Error as e:
        logging.error(f'Ocorreu um erro ao gravar scores: {e}')


def read_records():
    try:
        with sqlite3.connect('english.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM records ORDER BY record DESC LIMIT 3')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f'Erro ao obter records: {e}')


def main_menu():
    # menu principal da aplicação
    name = ''
    points = 0              # pontuação do jogador
    increment = 0           # contrele de update de nível
    difficulty = 3          # numero de palavras iniciais
    answers = 0             # contagem total de respostas
    corrects = 0            # contagem de acertos
    errors = 0              # contagem de erros
    statistics = dict()     # controle de repetição dos erros
    try:
        console.print("Welcome to the English tournament :skull:")
        records = read_records()
        if records is not None:
            console.print('Records 🏁')
            for i, record in enumerate(records):
                print(f'{i + 1}:{record[0]} points = {record[1]}')
        name = input('Enter your name: ')
        difficulty = int(input('Choose difficulty level (1~54): '))

        while True:
            id, result = get_random_data(difficulty, statistics)
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
                        difficulty += 3
                        increment = 0
                    if statistics.get(id):
                        statistics[id] += 1
                    else:
                        statistics[id] = 1
                    console.print(f'✅ Correct - {difficulty=} - {points=}')
                else:
                    errors += 1
                    console.print('❌ Incorrect 📜', *result)
                    play(','.join((result[0], result[2], result[3])))
                    if id in statistics.keys():
                        statistics[id] -= 1
                    else:
                        statistics[id] = -1
                answers += 1
    except KeyboardInterrupt:
        if points > 0:
            write_records((name if name != '' else 'AnyPlayer',
                           answers, corrects, errors))
        logging.debug('Encerrado pelo usuário.')
        console.print('Bye 💤')


if __name__ == '__main__':
    create_database()
    insert_from_string(_INCORPORED_LIST.split('\n'))
    main_menu()
