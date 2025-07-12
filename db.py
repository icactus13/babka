"""
This module contains functions for working with the database
"""
import sqlite3
from typing import Union, Optional


def handle_error(text: str, e: Exception) -> None:
    """
    Handle a database error, print a message and re-raise the exception

    Args:
        text (str): A message to print
        e (Exception): The exception to handle

    Raises:
        e: The exception
    """
    print('=' * 80)
    print('DAMN, GOD, YOU CRASHED THE GAME!')
    print(text)
    print(f'Error: {e}')
    print('=' * 80)
    raise e


def insert_db(query: str, var: Union[str, tuple] = "") -> None:
    """Execute a query in the database

    Args:
        query (str): SQL query
        var (str or tuple): Values to substitute into the query

    Returns:
        None
    """
    conn = sqlite3.connect('saves.db')
    cur = conn.cursor()
    cur.execute(query, var)
    conn.commit()


def select_db(query: str) -> list:
    """
    Return rows from DB

    Args:
        query (string): Database query

    Returns:
        [list]: rows from DB
    """
    conn = sqlite3.connect('saves.db')
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


def create_table() -> None:
    """
    Create the 'babkas' table in the database if it does not exist
    """
    insert_db("""CREATE TABLE IF NOT EXISTS babkas(
                    userid INT PRIMARY KEY,
                    name TEXT,
                    level INT,
                    inventory BLOB,
                    damage INT,
                    defence INT,
                    luck INT,
                    exp INT,
                    location INT,
                    maxhp INT,
                    hp INT,
                    dexterity INT,
                    strength INT);
                    """)


def save_babka(
    name: str,
    level: int,
    hp: int,
    strength: int,
    dexterity: int,
    luck: int,
    inventory: list,
    damage: int,
    defence: int,
    exp: int,
    location: int,
    maxhp: int
) -> None:
    """
    Save babka to the database.

    Args:
        name (str): Babka's name
        level (int): Babka's level
        hp (int): Babka's health points
        strength (int): Babka's strength
        dexterity (int): Babka's dexterity
        luck (int): Babka's luck
        inventory (list): Babka's inventory
        damage (int): Babka's damage
        defence (int): Babka's defence
        exp (int): Babka's experience
        location (int): Babka's location
        maxhp (int): Babka's maximum health points

    Returns:
        None
    """
    try:
        create_table()
    except sqlite3.Error as e:
        handle_error('Error creating table', e)
    try:
        check = select_db(
            "Select * from babkas Where name = '" + name + "';")
    except sqlite3.Error as e:
        handle_error('Error selecting values from table', e)
    else:
        inv = '-'
        for i in inventory:
            inv += str(i) + '-'
        print(inv)
        if len(check) == 0:
            try:
                result = select_db("Select * from babkas;")
            except sqlite3.Error as e:
                handle_error('Error selecting values from table', e)
            save = (
                len(result)+1,
                str(name),
                level,
                inv,
                damage,
                defence,
                luck,
                exp,
                location,
                maxhp,
                hp,
                dexterity,
                strength,
            )
            try:
                insert_db(
                    'INSERT INTO babkas VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', save
                )
            except sqlite3.Error as e:
                handle_error('Error inserting values in table', e)
        else:
            update_save = (
                level,
                inv,
                damage,
                defence,
                luck,
                exp,
                location,
                maxhp,
                hp,
                dexterity,
                strength,
                check[0][0]
            )
            try:
                insert_db(
                    "UPDATE babkas SET level=?, inventory=?, \
                        damage=?, defence=?, luck=?, exp=?, \
                        location=?, maxhp=?, hp=?, dexterity=?, \
                        strength=? where userid = ?", update_save
                )
            except sqlite3.Error as e:
                handle_error('Error updating values in table', e)


def init_db():
    """
    Initialize the database and create the 'babkas' table if it does not exist.
    """
    try:
        create_table()
    except sqlite3.Error as e:
        handle_error('Error initializing database', e)


def get_saves() -> list:
    """[summary]

    Returns:
        [list]: List of saved babkas
    """
    try:
        create_table()
        result = select_db("Select * from babkas;")
    except sqlite3.Error as e:
        handle_error('Error selecting values from table', e)
    names = []
    for name in result:
        names.append(name[1])
    return names


def get_babka_from_db(babka_number: int) -> Optional[dict]:
    """
    Get babka from db

    Args:
        babka_number (int): Babka number in the database

    Returns:
        dict: Babka data
    """
    try:
        create_table()
        params = select_db(
            "Select * from babkas Where userid = " + str(babka_number) + ";")
    except sqlite3.Error as e:
        handle_error('Error selecting values from table', e)
    if not params:
        return None
    inv = []
    for i in params[0][3]:
        if i != '-':
            inv.append(int(i))
    babka = {
        'name': params[0][1],  # name
        'gender': "female",
        'level': params[0][2],  # level
        'inventory': inv,
        'damage': params[0][4],  # damage
        'defence': params[0][5],  # defence
        'luck': params[0][6],  # luck
        'stats': None,
        'exp': params[0][7],  # exp
        'location': params[0][8],  # location
        'maxhp': params[0][9],  # maxhp
        'hp': params[0][10],  # hp
        'dexterity': params[0][11],  # dexterity
        'strength': params[0][12],  # strength
    }
    return babka
