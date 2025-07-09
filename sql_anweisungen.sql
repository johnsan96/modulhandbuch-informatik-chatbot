CREATE TABLE module (
  id INT AUTO_INCREMENT PRIMARY KEY,
  modulnummer VARCHAR(10),
  titel VARCHAR(100),
  cp INT,
  sws INT,
  pflichtmodul BOOLEAN,
  turnus VARCHAR(50),
  verantwortlich VARCHAR(100)
);

CREATE TABLE modul_kompetenzen (
  id INT AUTO_INCREMENT PRIMARY KEY,
  modul_id INT,
  typ VARCHAR(20),  -- z. B. "generisch" oder "fachlich"
  kompetenztext TEXT,
  FOREIGN KEY (modul_id) REFERENCES module(id)
);

CREATE TABLE modul_inhalte (
  id INT AUTO_INCREMENT PRIMARY KEY,
  modul_id INT,
  inhalt TEXT,
  FOREIGN KEY (modul_id) REFERENCES module(id)
);

CREATE TABLE modul_medien (
  id INT AUTO_INCREMENT PRIMARY KEY,
  modul_id INT,
  medium VARCHAR(255),
  FOREIGN KEY (modul_id) REFERENCES module(id)
);

CREATE TABLE modul_literatur (
  id INT AUTO_INCREMENT PRIMARY KEY,
  modul_id INT,
  autor VARCHAR(255),
  titel TEXT,
  isbn VARCHAR(20),
  verlag VARCHAR(100),
  jahr INT,
  FOREIGN KEY (modul_id) REFERENCES module(id)
);

