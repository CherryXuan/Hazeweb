drop database if exists hazeserver;

create database hazeserver;

use hazeserver;

grant select,insert,update,delete on hazeserver.* to 'haze'@'127.0.0.1' identified by 'hazepasswd';

CREATE TABLE messages(
`id` VARCHAR(50) not null,
`addr` VARCHAR(50) not null,
`data` VARCHAR(50) not null,
`pm25` VARCHAR(20) not null,
`pm10` VARCHAR(20) not null,
PRIMARY KEY (`id`)
)engine=innodb default charset=utf8;

