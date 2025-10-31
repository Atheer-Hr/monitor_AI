import pandas as pd
import sqlite3

def generate_excel_report(db_path='student_log.db', output_path='تقرير_الطلاب.xlsx'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM logs", conn)
    df.to_excel(output_path, index=False)
    conn.close()
    return output_path