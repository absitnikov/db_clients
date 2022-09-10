import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                        CREATE TABLE IF NOT EXISTS users(
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(60) NOT NULL,
                        last_name VARCHAR(60) NOT NULL,
                        email VARCHAR(60) NOT NULL
                        );
                    """)

        cur.execute("""
                        CREATE TABLE IF NOT EXISTS phone(
                        id SERIAL PRIMARY KEY,
                        phone VARCHAR(20),
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
                        );
                    """)
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
        client_change = []

        if first_name:
            client_change.append(f"first_name = '{first_name}'")
        if last_name:
            client_change.append(f"last_name = '{last_name}'")
        if email:
            client_change.append(f"email = '{email}'")

        cur.execute(f"""
            UPDATE users
            SET {','.join(client_change)}
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
                """, (client_id, phone))

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

        if phone is not None:
            phone = str(phone)
            cur.execute("""
                SELECT users_id FROM phone
                WHERE phone = %s;
                        """, (phone,))
            id_user = cur.fetchall()[0][0]
            print(f'user ID: {id_user}')

        else:
            cur.execute("""
                SELECT id FROM users 
                WHERE first_name = %s AND last_name = %s AND email = %s; 
                        """, (first_name, last_name, email))
            id_user = cur.fetchall()[0][0]
            print(f'user ID: {id_user}')


with psycopg2.connect(database="clients", user="postgres", password="postgres") as conn:
    create_db(conn)
    add_client(conn, 'Ivan', 'Sidorov', 'not@mail.ru', ['+7343566'])
    add_client(conn, 'Andrey', 'Petrov', 'yes@mail.ru', ['+72525'])
    add_client(conn, 'Alexander', 'Sidorov', 'data@mail.ru', ['12345'])
    add_phone(conn, '2', '+72345')
    change_client(conn, 3, 'Alexander', 'Belov', 'data2@mail.com', ['+712345'])
    delete_phone(conn, 2, '+72525')
    delete_client(conn, 3)
    find_client(conn, 'Ivan', 'Sidorov', 'not@mail.ru')

conn.close()
