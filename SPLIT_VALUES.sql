DELIMITER $$

DROP PROCEDURE IF EXISTS split_values $$
CREATE PROCEDURE split_values(s VARCHAR(255))

BEGIN

DECLARE VIN VARCHAR(50) DEFAULT '';
DECLARE color TEXT;
DECLARE occurance INT DEFAULT 0;
DECLARE i INT DEFAULT 0;
DECLARE splitted_value VARCHAR(100);
DECLARE done INT DEFAULT 0;
DECLARE cur1 CURSOR FOR SELECT table1.VIN, table1.color
                                     FROM cs6400team21.vehiclecolor_temp AS table1
                                     WHERE table1.color <> '';
DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

DROP TABLE IF EXISTS table2;
CREATE TABLE table2(
`VIN` VARCHAR(50) NOT NULL,
`color` VARCHAR(255) NOT NULL
) ENGINE=Memory;

OPEN cur1;
  read_loop: LOOP
    FETCH cur1 INTO VIN, color;
    IF done THEN
      LEAVE read_loop;
    END IF;

    SET occurance = (SELECT LENGTH(color) - LENGTH(REPLACE(color, s, '')) + 1);

    SET i=1;
    WHILE i <= occurance DO
      SET splitted_value =
      (SELECT REPLACE(SUBSTRING(SUBSTRING_INDEX(color, s, i),
      LENGTH(SUBSTRING_INDEX(color, s, i - 1))+ 1), s, ''));

      INSERT INTO table2 VALUES (VIN, splitted_value);
      SET i = i + 1;

    END WHILE;
  END LOOP;

  SELECT * FROM TABLE2;
 CLOSE cur1;
 END; $$