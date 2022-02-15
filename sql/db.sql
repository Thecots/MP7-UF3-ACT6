DROP DATABASE IF EXISTS ahorcado;
CREATE DATABASE ahorcado;
USE ahorcado;

CREATE TABLE partides(
  id_partida INT PRIMARY KEY AUTO_INCREMENT,
  data VARCHAR(100),
  host VARCHAR(100),
  guest VARCHAR(100),
  hostWord VARCHAR(10),
  guestWord VARCHAR(10),
  hostLetters VARCHAR(100),
  guestLetters VARCHAR(100),
  torn VARCHAR(10),
);
