schema="""
CREATE TABLE IF NOT EXISTS `user` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `name`                  VARCHAR(12) UNIQUE,
    `email`                 VARCHAR(100),
    `password`              VARCHAR(200) NOT NULL,
    `salt`                  VARCHAR(20) NOT NULL,
    `user_type`             INT(3) DEFAULT 2,
    `login_counting`        INT(5) DEFAULT 0,
    `create_datetime`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime`       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
);

CREATE TABLE IF NOT EXISTS `session` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `user_id`               INT(11) NOT NULL,
    `session`                 VARCHAR(100) NOT NULL,
    `last_call_datetime`    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`,`user_id`,`session`),
    CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `learn_english`.`user` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);
"""


# CREATE TABLE IF NOT EXISTS `idiom` (
#     `id`                    INT(11) NOT NULL AUTO_INCREMENT,
#     `expression`            VARCHAR(100),
#     `level`                 INT(3),
#     `search_count`          INT(11) DEFAULT 0,
# );

# CREATE TABLE IF NOT EXISTS `sentence` (
#     `id`                    INT(11) NOT NULL AUTO_INCREMENT,
#     `text`                  VARCHAR(1000),
# );

# CREATE TABLE IF NOT EXISTS `definition` (
#     `id`                    INT(11) NOT NULL AUTO_INCREMENT,
#     `text`                  VARCHAR(1000),
# );
