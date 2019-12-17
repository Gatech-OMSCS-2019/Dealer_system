CREATE USER IF NOT EXISTS root@localhost IDENTIFIED BY 'root';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH privileges;
DROP DATABASE IF EXISTS cs6400_fall19_team21;
CREATE DATABASE cs6400_fall19_team21;
USE cs6400_fall19_team21;

 CREATE TABLE django_session (
			session_key VARCHAR(40) PRIMARY KEY NOT NULL,
			session_data LONGTEXT,
			expire_date DATETIME
			);

CREATE TABLE User (
			user_id INT PRIMARY KEY AUTO_INCREMENT,
			first_name VARCHAR(45) NOT NULL,
			last_name VARCHAR(45) NOT NULL,
			username VARCHAR(20) NOT NULL,
            password VARCHAR(100) NOT NULL
			);

CREATE TABLE Job (
			job_id INT PRIMARY KEY AUTO_INCREMENT,
			job_title VARCHAR(45) NOT NULL
);

CREATE TABLE UserJob (
			user_id INT NOT NULL,
            job_id INT NOT NULL,
            PRIMARY KEY (user_id, job_id),
            CONSTRAINT fk_user_job_user FOREIGN KEY (user_id) REFERENCES User (user_id),
            CONSTRAINT fk_user_job_job FOREIGN KEY (job_id) REFERENCES Job (job_id)

);

CREATE TABLE Manufacturer(
			mfg_id INT PRIMARY KEY AUTO_INCREMENT,
			mfg_name VARCHAR(50) NOT NULL
			);

 CREATE TABLE Type (
			type_id INT PRIMARY KEY AUTO_INCREMENT,
			type_name VARCHAR(50) NOT NULL
			);



CREATE TABLE Customer (
			customer_id INT PRIMARY KEY AUTO_INCREMENT,
			phone VARCHAR(20) NOT NULL,
			street VARCHAR(100) NOT NULL,
			city VARCHAR(100) NOT NULL,
			state VARCHAR(100) NOT NULL,
			zip_code VARCHAR(20) NOT NULL,
			email VARCHAR(100)
			);


CREATE TABLE Individual(
			dl_num VARCHAR(20)  PRIMARY KEY,
			customer_id INT NOT NULL,
            first_name VARCHAR(20) NOT NULL,
			last_name VARCHAR(20) NOT NULL,
			CONSTRAINT fk_individual_customer FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
			);


CREATE TABLE Business(
			tax_id VARCHAR(20) PRIMARY KEY,
			business_name VARCHAR(100) NOT NULL,
			title VARCHAR(20) NOT NULL,
            first_name VARCHAR(20) NOT NULL,
			last_name VARCHAR(20) NOT NULL,
			customer_id INT NOT NULL,
			CONSTRAINT fk_business_customer FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
			);

CREATE TABLE Color(
			color_id INT PRIMARY KEY AUTO_INCREMENT,
            color VARCHAR(50) NOT NULL
);


CREATE TABLE Vehicle(
			VIN VARCHAR(20) PRIMARY KEY,
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
			add_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL ,
			sold_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			CONSTRAINT fk_vehicle_owner FOREIGN KEY (owner_id) REFERENCES Customer (customer_id),
			CONSTRAINT fk_vehicle_purchase FOREIGN KEY (purchased_by) REFERENCES Customer (customer_id),
			CONSTRAINT fk_vehicle_type FOREIGN KEY (type_id) REFERENCES Type (type_id),
			CONSTRAINT fk_vehicle_mfg FOREIGN KEY (mfg_id) REFERENCES Manufacturer (mfg_id),
			CONSTRAINT fk_vehicle_user FOREIGN KEY (add_by) REFERENCES User (user_id),
			CONSTRAINT fk_vehicle_sell FOREIGN KEY (sold_by) REFERENCES User (user_id)
			);

CREATE TABLE VehicleColor(
			VIN VARCHAR(20) NOT NULL,
            color_id INT NOT NULL,
            PRIMARY KEY (VIN, color_id),
            CONSTRAINT fk_vehicle_color_vin FOREIGN KEY (VIN) REFERENCES Vehicle (VIN),
            CONSTRAINT fk_vehicle_color_color FOREIGN KEY (color_id) REFERENCES Color (color_id)
);

CREATE TABLE Vendor (
		   vendor_id INT PRIMARY KEY AUTO_INCREMENT,
		   vendor_name VARCHAR(50) NOT NULL,
			street VARCHAR(100) NOT NULL,
		   city VARCHAR(100) NOT NULL,
		   state VARCHAR(100) NOT NULL,
		   zip_code VARCHAR(100) NOT NULL,
		   phone_num VARCHAR(15) NOT NULL
			);



CREATE TABLE PartOrder (
			VIN VARCHAR(20) NOT NULL,
			order_index VARCHAR(20) NOT NULL,
			vendor_id INT NOT NULL,
            PRIMARY KEY (VIN, order_index),
			CONSTRAINT fk_po_vendor FOREIGN KEY (vendor_id) REFERENCES Vendor (vendor_id),
			CONSTRAINT fk_part_order_vehicle FOREIGN KEY (VIN) REFERENCES Vehicle (VIN)
			);





CREATE TABLE Part (
			part_num VARCHAR(10) PRIMARY KEY,
			description TEXT
			);



CREATE TABLE POPart (
			id  INT PRIMARY KEY AUTO_INCREMENT,
			VIN VARCHAR(20) NOT NULL,
			order_index VARCHAR(20) NOT NULL,
			part_num VARCHAR(10) NOT NULL,
			price DECIMAL(8,2) NOT NULL,
			status VARCHAR(20) DEFAULT 'ORDERED' NOT NULL,
			CONSTRAINT fk_part_po FOREIGN KEY (VIN, order_index) REFERENCES PartOrder (VIN, order_index),
			CONSTRAINT fk_po_part FOREIGN KEY (part_num) REFERENCES Part (part_num)
			);

CREATE TABLE Loan(
			VIN VARCHAR(50) NOT NULL ,
			rate VARCHAR(10) NOT NULL,
			payment DECIMAL(10,2) NOT NULL ,
			down_payment DECIMAL (15,2) NOT NULL,
			term INT NOT NULL,
			CONSTRAINT fk_loan_vehicle FOREIGN KEY (VIN) REFERENCES Vehicle (VIN)
			);