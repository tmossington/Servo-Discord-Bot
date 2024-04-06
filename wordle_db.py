# wordle_db.py
import mysql.connector
from mysql.connector import Error
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Get environmental variables
host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
database = os.getenv('database')

def connect_to_db():
    # Connect to the MySQL database
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connect  to MySQL Server version ", db_info)

            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS wordle_stats")
            cursor.execute("USE wordle_stats")
            cursor.execute("CREATE TABLE IF NOT EXISTS user_stats (user_id VARCHAR(255), games_played INT DEFAULT 0, total_guesses INT DEFAULT 0, games_won INT DEFAULT 0, games_lost INT DEFAULT 0, PRIMARY KEY (user_id))")
    except Error as e:
        print("Error while connecting to MySQL", e)

    return connection, cursor


def update_user_stats(connection, cursor, user_id, game_won, num_guesses):
    # Update the user stats in the database
    cursor.execute('SELECT games_played, games_won, games_lost, total_guesses FROM user_stats WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()

    # If the user has no stats yet, insert a new row
    if row is None:
        cursor.execute('INSERT INTO user_stats (user_id, games_played, games_won, games_lost, total_guesses) VALUES (%s, 1, %s, %s, %s)', (user_id, int(game_won), int(not game_won), num_guesses))
    else:
     # Otherwise, update the existing row
        games_played, games_won, games_lost, total_guesses = row
        games_played = 0 if games_played is None else games_played
        games_won = 0 if games_won is None else games_won
        games_lost = 0 if games_lost is None else games_lost
        total_guesses = 0 if total_guesses is None else total_guesses
        cursor.execute('UPDATE user_stats SET games_played = %s, games_won = %s, games_lost = %s, total_guesses = %s WHERE user_id = %s', (games_played + 1, games_won + int(game_won), games_lost + int(not game_won), total_guesses + num_guesses, user_id))

    # Commit the changes
    connection.commit()

def get_user_stats(cursor, user_id):
    cursor.execute('SELECT * FROM user_stats WHERE user_id = %s', (user_id,))
    return cursor.fetchall()

def reset_database(connection, cursor):
    # Drop existing tables and recreate them
    cursor.execute("DROP TABLE IF EXISTS user_stats")

    # Recreate the table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user_stats (
                   user_id VARCHAR(255) PRIMARY KEY,
                   games_played INT DEFAULT 0,
                   games_won INT DEFAULT 0,
                   games_lost INT DEFAULT 0,
                   total_guesses INT DEFAULT 0
                     )
                     ''')
    
    # Commit the changes
    connection.commit()

connection, cursor = connect_to_db()

reset_database(connection, cursor)



    


