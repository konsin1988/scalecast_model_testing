import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Init:
    def __init__(self):
        pass

    def __get_environ(self):
        load_dotenv()
        return {"user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
                "database": os.getenv("DB_NAME")}

    def set_engine(self):
        EV = self.__get_environ()
        self.__engine = create_engine(f"postgresql+psycopg2://{EV['user']}:{EV['password']}@{EV['host']}:{EV['port']}/{EV['database']}")

    def __get_list_files(self):
        return os.listdir('/data/')

    def load_data(self):
        with self.__engine.begin() as con:
            for file in self.__get_list_files():
                (
                    pd.read_csv(f"/data/{file}", parse_dates=['date'])
                    .set_index('date')
                    .to_sql(file.split(".")[0], con, if_exists='replace')
                )

    def __get_list_databases(self):
        query = "SELECT datname FROM pg_database;"
        return pd.read_sql_query(query, self.__engine)['datname'].to_list()

    def create_mlflow(self):
        if "mlflow" not in self.__get_list_databases():
            query = text('Create database mlflow')
            with self.__engine.connect() as con:
                con.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                con.execute(query)
        

def main():
    init = Init()
    init.set_engine()
    init.load_data()
    init.create_mlflow()

if __name__ == "__main__":
    main()