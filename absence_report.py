import pandas as pd
import sqlite3

def generate_absence_report(db_path='school_system.db', output_path='تقرير_الغياب.xlsx'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM absence_log", conn)
    df.to_excel(output_path, index=False)
    conn.close()
    return output_path
