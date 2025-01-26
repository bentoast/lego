import psycopg2 as db


class DatabaseService:

    def __init__(self, configuration) -> None:
        self.configuration = configuration

    def executeQuery(self, statement, params):
        con = db.connect(
          host=self.configuration.host,
          user=self.configuration.user,
          password=self.configuration.password,
          database=self.configuration.database)
        cur = con.cursor()

        cur.execute(statement, params)
        fields = [desc[0].lower() for desc in cur.description]
        return [dict(zip(fields, row)) for row in cur.fetchall()]

    def executeNonQuery(self, statement, params):
        con = db.connect(
          host=self.configuration.host,
          user=self.configuration.user,
          password=self.configuration.password,
          database=self.configuration.database)
        cur = con.cursor()

        cur.execute(statement, params)
        con.commit()
        return True
