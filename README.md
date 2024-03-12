# minichat

A REST API chat application utilizing Python, Django, DRF, PostgreSQL, Channels.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. Clone the repository into a folder of your choice:

   ```shell
   git clone https://github.com/jayjaychukwu/minichat.git
   ```

2. Spin up the project using Docker Compose:

   Either you use

    ```shell
    docker-compose up --build
    ```

   and spin up another terminal to run the next set of commands or you run it in the background using

   ```shell
   docker-compose up -d --build
   ```

3. Make migrations for the dx app and migrate

   ```shell
   docker-compose run web python manage.py makemigrations accounts chat
   docker-compose run web python manage.py migrate
   ```

- To create a superuser for the admin dashboard, run the following command:
  
    ```shell
    docker-compose run web python manage.py createsuperuser
    ```

    Follow the prompts to create a superuser account.
    Access the admin dashboard at `http://localhost:8000/admin/` and log in using your superuser credentials.

## API Documentation

- Swagger Docs: `http://localhost:8000/`
- ReDoc: `http://localhost:8000/redoc/`

## Architecture

The project follows a Django architecture and utilizes the Django REST Framework for building the API. Docker is used for containerization, providing an isolated and consistent environment for development and deployment.

## Caching

Caching has been implemented in the project using Django's caching mechanisms. Decorators such as cache_page have been applied to specific endpoints, such as list and retrieve operations, to improve performance by storing the response data in memory. This helps reduce the need for executing the same expensive database queries or computations repeatedly, resulting in faster response times for subsequent requests.

## Transaction Atomicity

The project leverages the transaction.atomic() method provided by Django's database API to ensure atomicity and improve performance. By encapsulating a block of code for uploading CSV files within transaction.atomic(), all database operations within that block are executed as a single transaction. This approach reduces the number of round trips between the application and the database server, leading to improved performance and efficiency. Additionally, it helps maintain data consistency and integrity by rolling back the entire transaction if any operation within the block fails, preventing partial updates and keeping the database in a consistent state.

By employing caching and utilizing transaction atomicity, the project optimizes performance, reduces database round trips, and ensures the reliability and integrity of data operations.

## Support and Feedback

- Remember to always spin down your docker containers after you are done because they can consume a lot of memory.

Please feel free to reach out to me or raise an Issue if you run into any problems running this project.
