import sqlite3
import logging
import sys
from time import sleep
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format of the log messages
    handlers=[
        logging.StreamHandler(sys.stdout)  # Output to stdout
    ]
)

logger = logging.getLogger(__name__)

# Initialize the counter variable
db_connection_count = 0

class DatabaseConnection:
    def __init__(self) -> None:
        self.db_connection = self.get_db_connection()

    def __enter__(self) -> sqlite3.Connection:
        global db_connection_count
        db_connection_count += 1
        return self.db_connection

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        sleep(10)
        global db_connection_count
        db_connection_count -= 1
        self.db_connection.close()

    # Function to get a database connection.
    # This function connects to database with the name `database.db`
    def get_db_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        return connection


# Function to get a post using its ID
def get_post(post_id) -> sqlite3.Row:

    with DatabaseConnection() as connection:
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()

        return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    with DatabaseConnection() as connection:
        posts = connection.execute('SELECT * FROM posts').fetchall()
        return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.error(f"Post with id {post_id} does not exist")
        return render_template('404.html'), 404
    else:
        logger.info(f"Article {post['title']} retrieved!")
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info("About us page retrieved")
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            with DatabaseConnection() as connection:
                connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                            (title, content))
                connection.commit()

            logging.info(f"New article created: {title}")

            return redirect(url_for('index'))

    return render_template('create.html')


# Define the heath endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

    return response


# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    with DatabaseConnection() as connection:
        post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]

    response = app.response_class(
        response=json.dumps({
            "db_connection_count": db_connection_count,
            "post_count": post_count
        }),
        status=200,
        mimetype='application/json'
    )

    return response

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
