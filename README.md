# Flask Movie API

This is a Flask-based RESTful API for managing movies and user authentication.

## Features

- **Movie Management:** Allows CRUD operations on movies (Create, Read, Update, Delete).
- **User Authentication:** Supports user authentication with role-based access control.

## Prerequisites

- Python 3.x
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Bcrypt

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/flask-movie-api.git
   ```

## Endpoints

### Movies

- `GET /movies`: Retrieves all movies.
- `POST /movies`: Adds a new movie (Requires authentication).
- `GET /movies/<movie_id>`: Retrieves a specific movie.
- `PUT /movies/<movie_id>`: Updates a specific movie (Requires authentication).
- `DELETE /movies/<movie_id>`: Deletes a specific movie (Requires authentication).

### Users

- `GET /user`: Retrieves all users (Accessible only for admins).
- `POST /user`: Adds a new user (Accessible only for admins).
- `GET /user/<user_id>`: Retrieves a specific user (Requires authentication).
- `PUT /user/<user_id>`: Updates a specific user (Accessible only for admins).
- `DELETE /user/<user_id>`: Deletes a specific user (Accessible only for admins).

### Authentication

- `POST /auth`: Authenticates a user.

## Installation (continued)

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
    ```
