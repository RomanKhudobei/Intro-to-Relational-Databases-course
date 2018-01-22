# "Database code" for the DB Forum.

import datetime

import psycopg2
import bleach


DBNAME = 'forum'

def get_posts():
  """Return all posts from the 'database', most recent first."""
  database = psycopg2.connect(dbname=DBNAME)
  cursor = database.cursor()

  query = 'SELECT content, time FROM posts ORDER BY time DESC;'

  cursor.execute(query)
  posts = cursor.fetchall()

  return posts

def add_post(content):
  """Add a post to the 'database' with the current timestamp."""
  database = psycopg2.connect(dbname=DBNAME)
  cursor = database.cursor()

  content = bleach.clean(content)

  query = "INSERT INTO posts VALUES (%s);"

  try:
    cursor.execute(query, (content,))
  except:
    database.rollback()
    raise
  else:
    database.commit()

  cursor.close()
  database.close()