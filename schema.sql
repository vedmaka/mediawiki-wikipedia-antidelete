CREATE TABLE wikipedia_antidelete (
  id int NOT NULL AUTO_INCREMENT,
  page_title varchar(1024) DEFAULT NULL,
  page_namespace int(1) DEFAULT NULL,
  page_id_remote int DEFAULT NULL,
  page_id_local int DEFAULT NULL,
  page_revision_remote int(11) DEFAULT NULL,
  page_revision_local int(11) DEFAULT NULL,
  created_at int(11) DEFAULT NULL,
  updated_at int(11) DEFAULT NULL,
  status varchar(255) DEFAULT NULL,
  PRIMARY KEY (id)
)
ENGINE = INNODB;

CREATE TABLE wikipedia_antidelete_log (
  id INT NOT NULL AUTO_INCREMENT,
  touched INT(11) DEFAULT NULL,
  created_at INT(11) DEFAULT NULL,
  status VARCHAR(255) DEFAULT NULL,
  flag VARCHAR(512) DEFAULT NULL,
  PRIMARY KEY (id)
)
ENGINE = INNODB;