import os
import psycopg2 as pg
import logging
from sqlalchemy import create_engine

os.environ["DATABASE_USERNAME"]='postgres'
os.environ["DATABASE_HOST"]='edgar-dev.cziomxrz0xjc.ap-northeast-1.rds.amazonaws.com'
os.environ["DATABASE_PASSWORD"]='edgar-dev'
os.environ["DATABASE_PORT"]='5432'
os.environ["DATABASE_NAME"]='postgres'

class DBUtil():
    @staticmethod
    def conn():
        conn = pg.connect(
            user=os.environ["DATABASE_USERNAME"],
            host=os.environ["DATABASE_HOST"],
            password=os.environ["DATABASE_PASSWORD"],
            port=os.environ["DATABASE_PORT"],
            dbname=os.environ["DATABASE_NAME"]
        )
        conn.set_client_encoding('utf-8')
        logging.info(conn)
        return conn

    @staticmethod
    def engine():
        engine = create_engine(
            "postgresql://" +
            os.environ["DATABASE_USERNAME"] +
            ":" +
            os.environ["DATABASE_PASSWORD"] +
            "@" +
            os.environ["DATABASE_HOST"] +
            ":" +
            os.environ["DATABASE_PORT"] +
            "/" +
            os.environ["DATABASE_NAME"] + "")
        return engine

    @staticmethod
    def insertDf(df, table_name, if_exists="append", index=False):
        """
        dfをinsertするメソッド

        Arguments:
        ----------
        df: dataframe
            DBにインサートしたいdataframe
        table_name: string
         dataframeを格納したいテーブル名
        if_exists: string
            データベースにデータが存在しているとき、appendするかreplaceするか選ぶ
            defaultはappend
        index: boolean
            dataframeのindexを格納するかどうか。
            defaultはFalse
        """
        try:
            engine = DBUtil.engine()
        except:
            sleep(5)
            engine = DBUtil.engine()
        df.to_sql(table_name, engine, if_exists=if_exists, index=index)

    @staticmethod
    def cursor(conn):
        return conn.cursor()

    @staticmethod
    def execute(cur, query):
        return cur.execute(query)

    @staticmethod
    def commit(conn):
        return conn.commit()

    @staticmethod
    def cur_close(cur):
        return cur.close()

    @staticmethod
    def conn_close(conn):
        return conn.close()

    @staticmethod
    def fetch_one(query):
        with DBUtil.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchone()

    @staticmethod
    def fetch_many(query):
        with DBUtil.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchmany()

