#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    connection = connect()
    cursor = connection.cursor()

    query = '''
        UPDATE standings
        SET wins = 0, matches = 0;
    '''

    cursor.execute(query)

    connection.commit()

    cursor.close()
    connection.close()


def deletePlayers():
    """Remove all the player records from the database."""
    connection = connect()
    cursor = connection.cursor()

    query = '''
        DELETE FROM standings; DELETE FROM players;
    '''

    cursor.execute(query)

    query = '''
        SELECT setval('players_id_seq', 1, false);
        SELECT setval('standings_id_seq', 1, false);
    '''

    cursor.execute(query)

    connection.commit()

    cursor.close()
    connection.close()


def countPlayers():
    """Returns the number of players currently registered."""
    connection = connect()
    cursor = connection.cursor()

    query = '''
        SELECT count(*) as number_of_players FROM players;
    '''

    cursor.execute(query)

    result = cursor.fetchall()
    result = result[0][0]

    cursor.close()
    connection.close()

    return result


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    connection = connect()
    cursor = connection.cursor()

    insert2players = '''
        INSERT INTO players (name) VALUES (%s);
    '''

    insert2standings = '''
        INSERT INTO standings (name) VALUES (%s);
    '''

    try:
        cursor.execute(insert2players, (name,))
    except psycopg2.Error as e:
        print('An error occur during registration')
        print(e.pgerror)
        connection.rollback()
    else:
        connection.commit()

    try:
        cursor.execute(insert2standings, (name,))
    except  psycopg2.Error as e:
        print('An error occur during registration')
        print(e.pgerror)
        connection.rollback()
    else:
        connection.commit()

    cursor.close()
    connection.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    connection = connect()
    cursor = connection.cursor()

    query = '''
        SELECT * FROM standings ORDER BY wins DESC;
    '''

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    connection = connect()
    cursor = connection.cursor()

    query_winner = '''
        UPDATE standings
        SET wins = wins + 1, matches = matches + 1
        WHERE id = %s;
    '''

    query_loser = '''
        UPDATE standings
        SET matches = matches + 1
        WHERE id = %s;
    '''

    cursor.execute(query_winner, (winner,))
    cursor.execute(query_loser, (loser,))

    connection.commit()

    cursor.close()
    connection.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    connection = connect()
    cursor = connection.cursor()

    query = '''
        SELECT id, name FROM standings ORDER BY wins DESC;
    '''

    cursor.execute(query)
    data = cursor.fetchall()

    pairs = []

    is_even = False     # holds parity of iteration

    for i in range(len(data)):
        if is_even:
            id2, name2 = data[i]
            pairs.append( (id1, name1, id2, name2) )
            is_even = False
        else:
            id1, name1 = data[i]
            is_even = True

    cursor.close()
    connection.close()

    return pairs