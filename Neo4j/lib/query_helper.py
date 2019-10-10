import psycopg2 as db
import csv
import os

class comm_helper:
    def __init__(self, username, password, host, port):
        self.cursor = self.connect_to_db(username, password, host, port)

    def connect_to_db(self, username, password, host, port):

        conn = db.connect(user=username, password=username,
                          host=host, port=port)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        record = cursor.fetchone()
        print("Connected to -: ", record)
        return cursor

    def format_time_date(self, data, index):
        data = list(data)
        for i in range(len(data)):
            data[i] = list(data[i])
            if data[i][index] != None:
                data[i][index] = str(data[i][index]).replace(" ", "T")
        return data

    def query_and_write(self, filename, query, header, colAsDate=-1):
        print("Start querying table {}".format(filename))
        if os.path.isfile(filename):
            os.remove(filename)
        self.cursor.execute(query)
        # This only happens for documents

        print("Start writing table {}.".format(filename))
        if colAsDate != -1:
            data = self.cursor.fetchall()
            data = self.format_time_date(data, colAsDate)
            with open(filename, 'w') as csvfile:
                assert len(data[0]) == len(header)
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(header)
                csvwriter.writerows(data)

        # otherwise we do batching
        else:
            with open(filename, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(header)

                while True:
                    data = self.cursor.fetchmany(65536)
                    if not data:
                        break
                    csvwriter.writerows(data)

    def getCursor(self):
        return self.cursor

