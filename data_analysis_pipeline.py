
import csv
import sqlite3
import pandas as pd
import google.generativeai as genai
import os

# --- Configuration ---
CSV_FILE_PATH = "C:\\Users\\703401801\\Desktop\\Cigna\\synthetic_patient_data_with_distances.csv"
DB_FILE_PATH = "C:\\Users\\703401801\\Desktop\\Cigna\\patient_data.db"
TABLE_NAME = "patient_data"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # <<< IMPORTANT: Replace with your actual Gemini API Key

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- Part 1: CSV to SQLite ---
def csv_to_sqlite(csv_file_path, db_file_path, table_name):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Read CSV to infer schema and get column names
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader) # Get header row

    # Create CREATE TABLE statement
    # For simplicity, initially assume all columns are TEXT.
    # In a more robust solution, you'd infer types more carefully.
    columns_with_types = [f'"{col}" TEXT' for col in headers]
    create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({ ", ".join(columns_with_types) })"
    cursor.execute(create_table_sql)
    conn.commit()

    # Use pandas to read CSV in chunks and insert into SQLite
    # This is more efficient for large files than row-by-row insertion
    chunk_size = 10000
    for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size, encoding='utf-8'):
        # Rename columns to match the SQL table (pandas might alter names)
        chunk.columns = headers 
        chunk.to_sql(table_name, conn, if_exists='append', index=False)
    
    conn.close()
    print(f"Data from {csv_file_path} successfully loaded into {db_file_path} table {table_name}.")

# --- Part 2: Get SQLite Table Schema ---
def get_sqlite_schema(db_file_path, table_name):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema_info = cursor.fetchall()
    conn.close()
    
    schema_str = f"Table: {table_name}\nColumns:\n"
    for col_info in schema_info:
        cid, name, ctype, notnull, dflt_value, pk = col_info
        schema_str += f"- {name} ({ctype})\n"
    return schema_str

# --- Part 3: NLQ to SQL using Gemini ---
def nlq_to_sql(natural_language_query, db_schema, gemini_api_key):
    prompt = f"""
    You are a helpful assistant that translates natural language queries into SQL queries.
    You are working with a SQLite database.
    Here is the schema of the table you need to query:

    {db_schema}

    Please provide only the SQL query as your response, without any additional text or explanations.
    Ensure the SQL query is valid for SQLite. 
    
    Natural Language Query: {natural_language_query}
    SQL Query:
    """
    
    response = model.generate_content(prompt)
    sql_query = response.text.strip()
    return sql_query

# --- Part 4: Execute SQL Query ---
def execute_sql_query(db_file_path, sql_query):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return column_names, results
    except sqlite3.Error as e:
        return None, f"SQL Error: {e}"
    finally:
        conn.close()

# --- Part 5: Get Insights from Queried Data using Gemini ---
def get_insights_from_data(queried_data_columns, queried_data_rows, natural_language_query, gemini_api_key):
    if not queried_data_rows:
        return "No data returned from the SQL query to generate insights."

    # Summarize data if it's too large for the LLM context window
    # For simplicity, we'll take a sample of rows and include column names
    max_rows_for_llm = 100
    data_summary = f"Data from query (first {min(len(queried_data_rows), max_rows_for_llm)} rows):\n"
    data_summary += f"Columns: {queried_data_columns}\n"
    for i, row in enumerate(queried_data_rows):
        if i >= max_rows_for_llm:
            break
        data_summary += f"Row {i+1}: {row}\n"
    if len(queried_data_rows) > max_rows_for_llm:
        data_summary += f"... (truncated, {len(queried_data_rows) - max_rows_for_llm} more rows)\n"

    prompt = f"""
    You are a helpful assistant that provides insights from data.
    The original natural language query was: "{natural_language_query}"
    Here is the data returned from the SQL query:

    {data_summary}

    Please provide key descriptive and prescriptive insights from this data.
    Focus on trends, anomalies, and actionable recommendations.
    """
    
    response = model.generate_content(prompt)
    insights = response.text.strip()
    return insights

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure Gemini API Key is set
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("ERROR: Please replace 'YOUR_GEMINI_API_KEY' in the script with your actual Gemini API Key.")
        exit()

    # 1. Store CSV to SQLite
    print(f"Loading data from {CSV_FILE_PATH} into SQLite...")
    csv_to_sqlite(CSV_FILE_PATH, DB_FILE_PATH, TABLE_NAME)
    print("Data loading complete.")

    # 2. Get SQLite Table Schema
    db_schema = get_sqlite_schema(DB_FILE_PATH, TABLE_NAME)
    print("\nDatabase Schema:")
    print(db_schema)

    while True:
        natural_language_query = input("\nEnter your natural language query about the patient data (or 'exit' to quit):\n> ")
        if natural_language_query.lower() == 'exit':
            break

        # 3. Convert NLQ to SQL
        print("\nConverting natural language query to SQL using Gemini...")
        sql_query = nlq_to_sql(natural_language_query, db_schema, GEMINI_API_KEY)
        print(f"Generated SQL Query: {sql_query}")

        # 4. Execute SQL Query
        print("\nExecuting SQL query...")
        columns, results = execute_sql_query(DB_FILE_PATH, sql_query)

        if columns is None:
            print(f"Error executing SQL query: {results}")
        else:
            print(f"Query returned {len(results)} rows.")
            # 5. Get Insights from Queried Data
            print("\nGenerating insights from queried data using Gemini...")
            insights = get_insights_from_data(columns, results, natural_language_query, GEMINI_API_KEY)
            print("\n--- Insights from Gemini ---")
            print(insights)
            print("----------------------------")

    print("\nExiting data analysis pipeline.")
    # Clean up: Optionally remove the DB file
    # os.remove(DB_FILE_PATH)
    # print(f"Removed database file: {DB_FILE_PATH}")
