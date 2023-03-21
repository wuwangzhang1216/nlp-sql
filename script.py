from add_csv import main as add_csv
from add_question import main as add_question
from annotate_ws import main as annotate_ws
from predict import main as predict
import os
import json
import contextlib
import sys
import os
import optparse
import openai
import pymysql
from prettytable import PrettyTable

DESCRIPTION = "%prog is a tool to use natural language to do query from MySQL"

USAGE = "1. General input is the query in database in natural language;\n" \
        "2. Enter '?' to show the last executed SQL statement;\n" \
        "3. If start with '!', then your input would be executed as normal SQL statement\n" \
        "4. Enter 'switch' to switch to another table\n" \
        "5. Enter 'current' to show the current table\n" \
        "6. Enter 'exit' to exit the program\n"
KEYWORD_SELECT = "SELECT"

# f = open(os.devnull,"w")

# print("Weclome to use sql generation tool")

# print("Please input the table name")
# table_name = input()
# print("Please input the table path, onle csv file is supported")
# table_path = input()

# #  create table
# add_csv(table_name, table_path)

# # add question
# print("Please input the question")
# question = input()
# print("Adding question...")
# with contextlib.redirect_stdout(None):
#    add_question(table_name, table_name, question)

# # annotate
# print("Annotating...")
# with contextlib.redirect_stdout(None):
#    annotate_ws('./data_and_model', './data_and_model', table_name)


# # predict
# print("Predicting...")
# with contextlib.redirect_stdout(None):
#    predict("model_best.pt", "model_bert_best.pt", "param", "./data_and_model", table_name, "result")



# print result

# dir_path = "result"
# directory = os.fsencode(dir_path)
# for file in os.listdir(directory):
#      filename = os.fsdecode(file)
#      if filename.endswith(".jsonl"): 
#          json_file = open(dir_path + '/' + filename, 'r')
#          json_list = list(json_file)
#          for json_str in json_list:
#             result = json.loads(json_str)
#             print(f"sql: {result['sql']}")
#      else:
#          continue

# function to parse the arguments
def parse_arg():
   parser = optparse.OptionParser(
      description = DESCRIPTION,
      usage = USAGE,
      prog = "sqlx"
   )

   # add options
   parser.add_option("-H", "--host", action="store", type="string", dest="host",
                     help="MySQL server hostname. Default: 'localhost'.")
   parser.add_option("-p", "--port", action="store", type="int", dest="port",
                     help="MySQL server port. Default: 3306.")
   parser.add_option("-u", "--user", action="store", type="string", dest="user",
                     help="MySQL server user. Default: ''.")
   parser.add_option("-P", "--password", action="store", type="string", dest="password",
                     help="MySQL server password. Default: ''.")
   parser.add_option("-d", "--database", action="store", type="string", dest="database",
                     help="The MySQL database to use.")

   # parse arguments
   opt, args = parser.parse_args()
   if opt.host is None:
      opt.host = 'localhost'
   if opt.port is None:
      opt.port = 3306
   if opt.user is None:
      opt.user = "root"
   if opt.password is None:
      opt.password = "12345678"
   if opt.database is None:
      opt.database = "test"
   #   print("--database is required")
   #   sys.exit(1)

   return opt


def generate_column_desc(db, table_name):
   # create a csv file to store the table basic information
   f = open(f'data_and_model/{table_name}.csv', 'w', encoding='UTF8')
   desc = "("
   column_cursor = db.cursor()
   column_cursor.execute("DESC " + table_name)
   column_result = column_cursor.fetchall()
   column_names = []
   is_first_column = True
   for column in column_result:
      if not is_first_column:
         desc += ","
      else:
         is_first_column = False
      column_names.append(column[0])
      column_name = column[0]
      desc += column_name
   column_cursor.close()
   desc += ")\n"
   # write the header to csv
   f.write(','.join([str(item) for item in column_names]) + '\n')
   # select the first row of the table
   select_cursor = db.cursor()
   select_cursor.execute("SELECT * FROM " + table_name + " LIMIT 1")
   select_result = select_cursor.fetchall()
   # write the first row to csv
   f.write(','.join([str(item) for item in select_result[0]]))
   f.close()
   # generate table info
   add_csv(table_name, f'{table_name}.csv')
   return desc



def generate_table_desc(db, db_name):
    desc = "### MySQL tables, with their properties:\n"
    desc += "#\n"
    table_cursor = db.cursor()
    table_cursor.execute("SHOW TABLES")
    table_result = table_cursor.fetchall()
    for table in table_result:
        table_name = table[0]
        desc += "# " + table_name
        desc += generate_column_desc(db, table_name)
    table_cursor.close()
    desc += "#\n"

    return desc



def make_prediction(table_name, question):
   # add question
   print("Adding question...")
   with contextlib.redirect_stdout(None):
      add_question('./data_and_model', table_name, table_name, question)

   # annotate
   print("Annotating...")
   with contextlib.redirect_stdout(None):
      annotate_ws('./data_and_model', './data_and_model', table_name)


   # predict
   print("Predicting...")
   with contextlib.redirect_stdout(None):
      response = predict("model_best.pt", "model_bert_best.pt", "param", "./data_and_model", table_name, "result")

   return response



def print_query_result(db, sql):
    cursor = db.cursor()
    cursor.execute(sql)
    fields = cursor.description
    field_names = []
    for field in fields:
        field_names.append(field[0])
    table = PrettyTable(field_names)
    result = cursor.fetchall()
    for data in result:
        table.add_row(data)
    print(table)
    cursor.close()



def main():
    opt = parse_arg()
    db = pymysql.connect(host=opt.host, port=opt.port,
                         user=opt.user, password=opt.password,
                         database=opt.database, charset='utf8')


    sql = ""
    current_table = ""
    response = None
    table_desc = generate_table_desc(db, opt.database)

    print(table_desc)
    print("Welcome to SQLx!\n")
    while current_table == "":
         print("Please choose a table to start:")
         current_table = input("sqlx> ")
         # check if the current_table is valid
         if current_table not in table_desc:
            print("Invalid table name")
            current_table = ""
    print("You are now working on table: " + current_table + "\n")
    while True:
        try:
            user_input = input("sqlx> ")
            if user_input == "":
                continue
            elif user_input == "quit":
                break
            elif user_input == "?":
                print(sql)
                continue
            elif user_input == "current":
                print("You are now working on table: " + current_table + "\n")
                continue
            elif user_input == "switch":
                print("Please choose a new table to start:")
                current_table = input("sqlx> ")
                # check if the current_table is valid
                if current_table not in table_desc:
                    print("Invalid table name")
                    current_table = ""
                continue
            elif user_input.startswith("!"):
                sql = user_input[1:]
            else:
                response = make_prediction(current_table, user_input)
                sql = response[0]['sql']
            print_query_result(db, sql)

        except Exception as e:
            print(e)

    db.close()

    return 0

if __name__ == '__main__':
    rc = main()
    sys.exit(rc)