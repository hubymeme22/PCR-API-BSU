# Performance Commitment Review System
A simple system designed to facilitate and streamline the process of evaluating and managing employee performance within the Batangas State University. Its primary purpose is to enhance the performance management process by providing a centralized and efficient platform for conducting performance reviews, setting goals, giving feedback, and tracking progress.

## Proxy Setup
Apply the api endpoints for your web app by changing the http server on `Location /` reverse proxy part. (See example below for applying api endpoints for http://example.com/):
```
server {
    location /api {
        proxy_pass http://localhost:5000/;
    }

    location / {
        proxy_pass http://example.com/;
    }
}
```


Backup nginx default configuration, apply the customed one, and restart the nginx proxy server to access the site on port 80:
```
$ sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
$ sudo cp /configs/default /etc/nginx/sites-available/default
$ sudo systemctl restart nginx
```

## Web application Setup

- mongodb connection credential in `.env` file at project root directory

  ```bash
  MONGODB_USER=<username>
  MONGODB_PW=<password>
  MONGODB_HOST=<host>
  MONGODB_DB=<database>
  ```

- Install extra dependencies

  `pip install -r requirements.txt`