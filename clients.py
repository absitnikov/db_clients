import psycopg2


def create_db(conn):
    user_db = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL
        );
    """

    phone_db = """
        CREATE TABLE IF NOT EXISTS phone (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            phone VARCHAR(100) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """

    with conn.cursor() as cursor:
        cursor.execute(user_db)
        cursor.execute(phone_db)

        conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
               INSERT INTO users (first_name, last_name, email)
               VALUES (%s, %s, %s)
           """, (first_name, last_name, email))

        conn.commit()

        if phones:
            cur.execute("""
                   SELECT id
                   FROM users
                   WHERE first_name = %s AND last_name = %s AND email = %s
               """, (first_name, last_name, email))

            user_id = cur.fetchone()[0]

            for phone in phones:
                cur.execute("""
                       INSERT INTO phone (user_id, phone)
                       VALUES (%s, %s)
                   """, (user_id, phone))

        conn.commit()
        print(f'client info added: {first_name} {last_name}, {email} {phone}')

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phone (user_id, phone)
            VALUES (%s, %s)
        """, (client_id, phone))

        conn.commit()
        print(f'new phone for {client_id} added: {phone}')

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        user_change = []

        if first_name:
            user_change.append(f"first_name = '{first_name}'")
        if last_name:
            user_change.append(f"last_name = '{last_name}'")
        if email:
            user_change.append(f"email = '{email}'")

        cur.execute(f"""
            UPDATE users
            SET {','.join(user_change)}
            WHERE id = {client_id}
        """)

        if phones:
            cur.execute("""
                DELETE FROM phone
                WHERE user_id = %s
            """, (client_id,))

            for phone in phones:
                cur.execute("""
                    INSERT INTO phone (user_id, phone)
                    VALUES (%s, %s)
                """, (client_id, phones))

        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone
            WHERE user_id = %s AND phone = %s
        """, (client_id, phone))

        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone
            WHERE user_id = %s
        """, (client_id,))

        cur.execute("""
            DELETE FROM users
            WHERE id = %s
        """, (client_id,))

        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        find = []

        if first_name:
            find.append(f"first_name='{first_name}'")
        if last_name:
            find.append(f"last_name='{last_name}'")
        if email:
            find.append(f"email='{email}'")
        if phone:
            find.append(f"phone='{phone}'")

        sql = 'AND '.join(find)

        cur.execute(f"""
            SELECT users.id, first_name, last_name, email
            FROM users
            JOIN phone p ON users.id = p.user_id
            WHERE {sql}
        """)

        return cur.fetchone()[0]


with psycopg2.connect(database="clients", user="postgres", password="postgres") as conn:
    create_db(conn)
    add_client(conn, 'Ivan', 'Sidorov', 'not@mail.ru', ['+7343355'])
    add_client(conn, 'Andrey', 'Petrov', 'not@mail.ru', ['+72525'])
    user_find = find_client(conn, last_name='Petrov')
    print(user_find)
    add_phone(conn, '1', '+12345')
    change_client(conn, 2, 'Ivan', 'Ivanov', 'yes@mail.ru', '4516')
    delete_phone(conn, 2, '4516')
    delete_client(conn, 1)