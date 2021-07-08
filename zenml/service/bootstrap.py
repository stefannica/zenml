import logging
import os
import time

from alembic import config
from app.db.init_db import init_db
from app.db.session import db_session, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init(connection_retries=5):
    for i in range(0, connection_retries):
        try:
            logger.info(
                "Create session to check if DB is awake,"
                " {}/{}".format(
                    i + 1,
                    connection_retries + 1)
            )
            db_session.execute("SELECT 1")
            logger.info("Connection established")
            break
        except Exception as e:
            logger.info("Connection to db failed to establish.")
            logger.info(e)
            if i >= (connection_retries - 1):
                raise e
            else:
                time.sleep(i)

    try:
        # if no alembic versions are installed...
        if not engine.has_table("alembic_version"):
            logger.info("No alembic versions present, bootstrapping")
            # ..create a revision
            create_revision = ['revision', '--autogenerate']
            config.main(argv=create_revision)

            # inject app into revision code, to resolve dependencies
            for i in os.listdir('alembic/versions'):
                if i.endswith(".py"):
                    with open(os.path.join('alembic/versions', i), 'r') as f:
                        lines = f.readlines()
                    with open(os.path.join('alembic/versions', i), 'w') as f:
                        lines.insert(8, '\nimport app\n')
                        f.writelines(lines)

                        # upgrade the head
            upgrade = ['upgrade', 'head']
            config.main(argv=upgrade)

            # seed data the db with data
            await init_db(db_session)

            logger.info("Database bootstrapped with initial data")
        else:
            logger.info("Table exists, skipping bootstrap")
    except Exception as e:
        logger.error(e)
        raise e


async def main():
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    import asyncio

    asyncio.get_event_loop().run_until_complete(main())
