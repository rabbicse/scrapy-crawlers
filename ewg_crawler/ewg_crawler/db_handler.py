from sqlalchemy.orm import sessionmaker

from ewg_crawler.models import db_connect, create_tables
engine = db_connect()
create_tables(engine)
Session = sessionmaker(bind=engine)
