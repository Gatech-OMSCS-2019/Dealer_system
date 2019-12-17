LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Users.csv' 
			INTO TABLE user 
			FIELDS TERMINATED BY ','
			OPTIONALLY ENCLOSED BY '"'
			LINES TERMINATED BY '\n'
			IGNORE 1 LINES (username, password,first_name, last_name);

-- JOB -----------------------------------------------------------------------------------
 LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Users.csv'
 INTO TABLE JOB
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\r\n'
 IGNORE 1 LINES (@DUMMY, @DUMMY, @DUMMY, @DUMMY, @job_title)
 SET job_title = TRIM(@job_title); -- make job_tile in Job UNIQUE
 
 DELETE FROM job
 WHERE LENGTH(job_title) - LENGTH(REPLACE(job_title, ',', '')) > 0;

-- USERJOB------------------------------------------------------------------------------
            
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Users.csv'
 INTO TABLE userjob
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\r\n'
 IGNORE 1 LINES (@username, @dummy, @dummy, @dummy, @job_title)
 SET user_id = (SELECT user_id FROM User 
					WHERE User.username = @username),
		job_id = (SELECT job_id FROM Job
					WHERE Job.job_title = TRIM(@job_title));
UPDATE job
SET job_title = 'Manager' WHERE job_title = 'Manager';
UPDATE job
SET job_title = 'Inventory Clerk' WHERE job_title = 'Clerk';
UPDATE job
SET job_title = 'Sales People' WHERE job_title = 'Sales Person';

INSERT INTO userjob 
VALUES(1, (SELECT job_id FROM job WHERE job_title = 'Manager')),
(1, (SELECT job_id FROM job WHERE job_title = 'Sales People')),
(1, (SELECT job_id FROM job WHERE job_title = 'Inventory Clerk'));                    

-- MANUFACTURER ------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE manufacturer
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @x, @x, @x, mfg_name);


-- TYPE -------------------------------------------------------------------------
 LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
INTO TABLE `type`
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES (@x, @x, @x, @x, @x, @x, @x, @x, @x,  type_name);

-- CUSTOMER ----------------------------------------------------------------------------
 LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE customer
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, email, phone, customer_id, street, city, state, zip_code );

-- INDIVIDUAL ------------------------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE individual
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, customer_id, @x, @x, @x, @x, dl_num, first_name, last_name );
 DELETE FROM individual
 where dl_num = '';

-- BUSINESS ----------------------------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE business
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, customer_id, @x, @x, @x, @x, @x, @x, @x, tax_id, business_name, first_name, last_name, title );
 DELETE FROM business
 where tax_id = '';


-- VEHICLE TABLE ----------------------------------------------------------------------------------------------
CREATE TABLE Vehicle_temp(
                                VIN VARCHAR(20),
                                original_price DECIMAL NOT NULL,
                                model_year varchar(50) NOT NULL,
                                model_name varchar(50) NOT NULL,
                                owner_id INT NOT NULL,
                                type_id INT NOT NULL,
                                mfg_id INT NOT NULL, 
                                mileage VARCHAR(10) NOT NULL,
                                car_condition VARCHAR(20) NOT NULL,
                                description TEXT,
                                add_by INT  DEFAULT NULL,
                                purchased_by INT DEFAULT NULL,
                                sold_by INT DEFAULT NULL,
                                add_at DATE ,
                                sold_at DATE 
                                );
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE vehicle_temp
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\r\n'
 IGNORE 1 LINES (@purchaseorsell, @date1, original_price, VIN, model_name, model_year, description, @mfg_name, car_condition, @type_name, mileage, @colors, @username, @x, @x, @customer_id  )
 SET  	owner_id = if ( TRIM(@purchaseorsell) = 'Purchase', @customer_id, NULL),
		add_by = if ( TRIM(@purchaseorsell) = 'Purchase', (SELECT user_id FROM user WHERE username = @username), NULL),
		add_at = if ( TRIM(@purchaseorsell) = 'Purchase', STR_TO_DATE(@date1,'%m/%d/%y)'), null),
        sold_by = if ( TRIM(@purchaseorsell) = 'Sale', (SELECT user_id FROM user WHERE username = @username), NULL),
        sold_at = if ( TRIM(@purchaseorsell) = 'Sale', STR_TO_DATE(@date1,'%m/%d/%y)'),null),
        purchased_by = if ( TRIM(@purchaseorsell) = 'Sale', @customer_id, NULL),
        type_id = (SELECT type_id FROM `Type`
					WHERE `Type`.type_name = @type_name),
		mfg_id = (SELECT mfg_id FROM `manufacturer`
					WHERE `manufacturer`.mfg_name = @mfg_name);
INSERT INTO vehicle
SELECT S.VIN, S.original_price, S.model_year, S.model_name, S.owner_id, S.type_id,
		S.mfg_id, S.mileage, S.car_condition, S.description, S.add_by, 
        T.purchased_by, T.sold_by, S.add_at,  T.sold_at 
FROM (SELECT * FROM vehicle_temp AS v1 
			WHERE v1.add_by IS NOT NULL) AS S
LEFT JOIN (SELECT * FROM vehicle_temp AS v2
			WHERE v2.add_by IS NULL) AS T
ON S.VIN = T.VIN;
DROP TABLE Vehicle_temp;

-- COLORS -----------------------------------------------------------------------------------

LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE Color
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, color);
Delete from color
WHERE color LIKE '%;%';


-- vehiclecolor

CREATE TABLE vehiclecolor_temp(
	VIN VARCHAR(50) PRIMARY KEY,
    COLOR VARCHAR(100)
);

LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE vehiclecolor_temp
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES(@x, @x, @x, VIN, @x, @x, @x, @x, @x, @x, @x, @color)
 SET color = @color;
 
call split_values(';');
INSERT INTO vehiclecolor
SELECT VIN, c.color_id  FROM table2
LEFT JOIN Color AS c ON c.color = table2.color;
Drop TABLE vehiclecolor_temp;
DROP TABLE table2;

-- LOAN -----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Transactions.csv'
 INTO TABLE Loan
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, VIN, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, @x, term, rate, down_payment, payment);
 
 DELETE FROM Loan
 WHERE term = 0;

-- VENDOR --------------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Parts.csv'
 INTO TABLE Vendor
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @x, vendor_name, phone_num, street, city, state, zip_code);
 
-- PART ORDER  ---------------------------------------------------------------------
 LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Parts.csv'
 INTO TABLE partorder
 FIELDS TERMINATED BY ','
 OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (@x, @x, @x, @x, @order_id, @vendor_name)
 SET VIN = substring_index(@order_id, '-', 1),
	vendor_id = (SELECT vendor_id FROM Vendor
					WHERE vendor_name = @vendor_name),
	order_index = substring_index(@order_id, '-', -1);
    
    -- PART ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Parts.csv'
 INTO TABLE Part
 FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES (part_num, description);
 
 
 -- POPART ----------------------------------------------------------------------
 LOAD DATA LOCAL INFILE 'C:\\Users\\yluo\\Downloads\\Sample Data\\Parts.csv'
 INTO TABLE popart
 FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
 LINES TERMINATED BY '\n'
 IGNORE 1 LINES(part_num, @x, price, status, @order_id)
 SET VIN = substring_index(@order_id, '-', 1),
	order_index = substring_index(@order_id, '-', -1);
 
    
                    
  
 
                    
                    
			