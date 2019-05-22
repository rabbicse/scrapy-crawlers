from sqlalchemy.orm import sessionmaker

from arzt_crawler.models import db_connect, create_tables
engine = db_connect()
create_tables(engine)
Session = sessionmaker(bind=engine)
