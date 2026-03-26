import yaml
from sqlalchemy import create_engine, text

with open("config/config.yaml") as f:
    cfg = yaml.safe_load(f)

db = cfg["database"]
url = f"mysql+pymysql://{db['user']}:{db['password']}@{db['host']}:{db.get('port', 3306)}/{db['name']}"
engine = create_engine(url, pool_pre_ping=True)

with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES;"))
    print("Tables in database:", [row[0] for row in result])
