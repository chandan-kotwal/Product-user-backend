CREATE DATABASE IF NOT EXISTS productuser;
USE productuser;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO user (username, password) VALUES ('admin', 'password');
