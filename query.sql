-- Creazione del DB
CREATE DATABASE


SHOW USERS;

-- Creazione dell'utente
CREATE USER 'lorenzo_adm'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON films.* TO 'lorenzo_adm'@'localhost';
FLUSH PRIVILEGES;

SELECT User, Host FROM mysql.user;
