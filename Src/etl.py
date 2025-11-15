import datetime
import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

CL = "postgresql+psycopg2://{USERNPASSWORD}@127.0.0.1/postgres"
engine = create_engine(CL, echo=False)

def main():
    df = pd.read_csv("https://gist.githubusercontent.com/netj/8836201/raw/6f9306ad21398ea43cba4f7d537619d0e07d5ae3/iris.csv")

    df["timestamp"]=[datetime.datetime.now()] * len(df.index)

    print(df)

    df.to_sql(name='iris', con=engine, if_exists='append')

if __name__ == "__main__":
    main()
