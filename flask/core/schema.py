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
"""