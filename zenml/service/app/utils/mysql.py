from sqlalchemy import create_engine


def create_metadata_database(admin_username, admin_password, user_username,
                             user_password, host, port, database):
    db_uri = 'mysql+pymysql://{user}:{password}@{host}:{port}'.format(
        user=admin_username,
        password=admin_password,
        host=host,
        port=port,
    )
    engine = create_engine(db_uri)

    # create database
    with engine.connect() as con:
        query = f"CREATE DATABASE IF NOT EXISTS {database};"
        con.execute(query)

    # create user
    with engine.connect() as con:
        query = f"CREATE USER '{user_username}'@'cloudsqlproxy~%%' " \
                f"IDENTIFIED BY '{user_password}';"
        con.execute(query)

    # give access
    with engine.connect() as con:
        query = f"GRANT CREATE,DELETE,INSERT,SELECT,UPDATE ON {database}.* " \
                f"TO '{user_username}'@'cloudsqlproxy~%%';"
        con.execute(query)
