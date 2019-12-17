import pymysql
from .models import *


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DbHelper(metaclass=Singleton):
    CREATE_DB = "CREATE DATABASE CS6400Team21"
    USE_DB = "USE CS6400Team21"
    CREATE_DJANGO_SESSION = '''
                            CREATE TABLE django_session (
                            session_key VARCHAR(40) PRIMARY KEY NOT NULL,
                            session_data LONGTEXT,
                            expire_date DATETIME
                            )
        '''
    CREATE_TABLE_USER = '''CREATE TABLE User (
                            user_id INT PRIMARY KEY AUTO_INCREMENT,
                            first_name VARCHAR(45) NOT NULL,
                            last_name VARCHAR(45) NOT NULL,
                            username VARCHAR(20) NOT NULL,
                            password VARCHAR(100) NOT NULL);
        '''

    CREATE_TABLE_JOB = '''
                            CREATE TABLE Job (
                            job_id INT PRIMARY KEY AUTO_INCREMENT,
                            job_title VARCHAR(45) NOT NULL,
                            UNIQUE (job_title)
);
                            
    '''

    CREATE_TABLE_USER_JOB = '''
                            CREATE TABLE UserJob (
                            user_id INT NOT NULL,
                            job_id INT NOT NULL,
                            PRIMARY KEY (user_id, job_id),
                            CONSTRAINT fk_user_job_user FOREIGN KEY (user_id) REFERENCES User (user_id),
                            CONSTRAINT fk_user_job_job FOREIGN KEY (job_id) REFERENCES Job (job_id)
                            
);
    '''

    CREATE_TABLE_MANUFACTURER = '''
                             CREATE TABLE Manufacturer(
                             mfg_id INT PRIMARY KEY AUTO_INCREMENT,
                             mfg_name VARCHAR(50) NOT NULL ,
                             UNIQUE (mfg_name)
                             )
         '''


    CREATE_TABLE_TYPE = '''
                            CREATE TABLE Type (                          
                            type_id INT PRIMARY KEY AUTO_INCREMENT,
                            type_name VARCHAR(50) NOT NULL ,
                            UNIQUE (type_name)
                            )
        '''

    CREATE_TABLE_CUSTOMER = '''
                            CREATE TABLE Customer (
                            customer_id INT PRIMARY KEY AUTO_INCREMENT,
                            phone VARCHAR(20) NOT NULL,
                            street VARCHAR(100) NOT NULL,
                            city VARCHAR(100) NOT NULL,
                            state VARCHAR(100) NOT NULL,
                            zip_code VARCHAR(20) NOT NULL,
                            email VARCHAR(100) 
                             )
          '''
    CREATE_TABLE_INDIVIDUAL = '''
                           CREATE TABLE Individual(
                           dl_num VARCHAR(20)  NOT NULL,
                           customer_id INT NOT NULL,
                            first_name VARCHAR(20) NOT NULL,
                            last_name VARCHAR(20) NOT NULL,
                            PRIMARY KEY (dl_num),
                           CONSTRAINT fk_individual_customer FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
                               )
           '''

    CREATE_TABLE_BUSINESS = '''
                                    CREATE TABLE Business(
                                    tax_id VARCHAR(20) PRIMARY KEY,	
                                    business_name VARCHAR(100) NOT NULL,
                                    title VARCHAR(25) NOT NULL,
                                    first_name VARCHAR(20) NOT NULL,
                                    last_name VARCHAR(20) NOT NULL,
                                    customer_id INT NOT NULL,
                                    CONSTRAINT fk_business_customer FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
                                    )
                '''

    CREATE_TABLE_COLOR = '''
                                   CREATE TABLE Color(
                                   color_id INT PRIMARY KEY AUTO_INCREMENT ,
                                   color VARCHAR(50) NOT NULL,
                                   UNIQUE (color)
                                   )


       '''

    CREATE_TABLE_VEHICLE = '''CREATE TABLE Vehicle(
                                VIN VARCHAR(20) PRIMARY Key,
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
                                )'''

    CREATE_TABLE_VEHICLE_COLOR = '''
                                   CREATE TABLE VehicleColor(
                                   VIN VARCHAR(20) NOT NULL,
                                   color_id INT NOT NULL,
                                   PRIMARY KEY (VIN, color_id),
                                   CONSTRAINT fk_colo_vin FOREIGN KEY (VIN) REFERENCES Vehicle (VIN),
                                   CONSTRAINT fk_color_name FOREIGN KEY (color_id) REFERENCES color(color_id)
                                   )
       '''

    CREATE_TABLE_VENDOR = '''
                                   CREATE TABLE Vendor (
                                   vendor_id INT PRIMARY KEY AUTO_INCREMENT,
                                   vendor_name VARCHAR(50) NOT NULL,
                                    street VARCHAR(100) NOT NULL,
                                   city VARCHAR(100) NOT NULL,
                                   state VARCHAR(100) NOT NULL,
                                   zip_code VARCHAR(100) NOT NULL,
                                   phone_num VARCHAR(15) NOT NULL, 
                                   UNIQUE (vendor_name)
			);
               '''


    CREATE_TABLE_PARTORDER = '''
                            CREATE TABLE PartOrder (
                            VIN VARCHAR(20) NOT NULL,
                            order_index VARCHAR(20) NOT NULL,
                            PRIMARY KEY (VIN, order_index),
                            vendor_id INT NOT NULL,
                            CONSTRAINT fk_part_order_vehicle FOREIGN KEY (VIN) REFERENCES Vehicle (VIN),
                            CONSTRAINT fk_po_vendor FOREIGN KEY (vendor_id) REFERENCES Vendor (vendor_id)
                            )
        '''

    CREATE_TABLE_PART = '''
                            CREATE TABLE Part (
                            part_num VARCHAR(20) PRIMARY KEY,
                            description TEXT
                            )
        '''


    CREATE_TABLE_PO_PART = '''
                                CREATE TABLE POPart (
                                id  INT PRIMARY KEY AUTO_INCREMENT,
                                VIN VARCHAR(20) NOT NULL,
                                order_index VARCHAR(20) NOT NULL,
                                part_num VARCHAR(20) NOT NULL,
                                status VARCHAR(20) DEFAULT 'ordered' NOT NULL,
                                price DECIMAL(8,2) NOT NULL,
                                CONSTRAINT fk_part_po FOREIGN KEY (VIN, order_index) REFERENCES PartOrder (VIN, order_index),
                                CONSTRAINT fk_po_part FOREIGN KEY (part_num) REFERENCES Part (part_num)
                                )
        '''


    CREATE_TABLE_LOAN = '''
                                CREATE TABLE Loan(
                                VIN VARCHAR(50) NOT NULL ,
                                rate VARCHAR(10) NOT NULL,
                                payment DECIMAL(10,2) NOT NULL ,
                                down_payment DECIMAL (15,2) NOT NULL,
                                term INT NOT NULL,
                                CONSTRAINT fk_loan_vehicle FOREIGN KEY (VIN) REFERENCES Vehicle (VIN)
    );
        '''



    def __init__(self, host, user, port, ):
        print("I am initiate dbhelper")
        self.connector = pymysql.connect(host=host, user=user, port=port, password="root", charset="utf8")
        self.cursor = self.connector.cursor(pymysql.cursors.DictCursor)
        ## to be commented if debug or import data by "CS6400Team21.sql"
        # self.cursor.execute("DROP DATABASE IF EXISTS CS6400Team21")
        # self.cursor.execute(self.CREATE_DB)
        ################################
        self.cursor.execute(self.USE_DB)
        ## to be commented if debug or import data by "CS6400Team21.sql"
        # self.cursor.execute("DROP TABLE IF EXISTS UserJob")
        # self.cursor.execute("DROP TABLE IF EXISTS User")
        # self.cursor.execute("DROP TABLE IF EXISTS Job")
        # self.cursor.execute("DROP TABLE IF EXISTS Manufacturer")
        # self.cursor.execute("DROP TABLE IF EXISTS Type")
        # self.cursor.execute("DROP TABLE IF EXISTS Individual")
        # self.cursor.execute("DROP TABLE IF EXISTS Business")
        # self.cursor.execute("DROP TABLE IF EXISTS Customers")
        # self.cursor.execute("DROP TABLE IF EXISTS django_session")
        # self.cursor.execute("DROP TABLE IF EXISTS PartOrder")
        # self.cursor.execute("DROP TABLE IF EXISTS POPart")
        # self.cursor.execute("DROP TABLE IF EXISTS Part")
        # self.cursor.execute("DROP TABLE IF EXISTS VehicleColor")
        # self.cursor.execute("DROP TABLE IF EXISTS Vehicle")
        # self.cursor.execute("DROP TABLE IF EXISTS Vendor")
        # self.cursor.execute("DROP TABLE IF EXISTS Color")
        # self.cursor.execute(self.CREATE_TABLE_USER)
        # self.cursor.execute(self.CREATE_TABLE_JOB)
        # self.cursor.execute(self.CREATE_TABLE_USER_JOB)
        # self.cursor.execute(self.CREATE_TABLE_MANUFACTURER)
        # self.cursor.execute(self.CREATE_TABLE_TYPE)
        # self.cursor.execute(self.CREATE_TABLE_CUSTOMER)
        # self.cursor.execute(self.CREATE_TABLE_INDIVIDUAL)
        # self.cursor.execute(self.CREATE_TABLE_BUSINESS)
        # self.cursor.execute(self.CREATE_TABLE_COLOR)
        # self.cursor.execute(self.CREATE_TABLE_VEHICLE)
        # self.cursor.execute(self.CREATE_DJANGO_SESSION)
        # self.cursor.execute(self.CREATE_TABLE_VEHICLE_COLOR)
        # self.cursor.execute(self.CREATE_TABLE_VENDOR)
        # self.cursor.execute(self.CREATE_TABLE_PARTORDER)
        # self.cursor.execute(self.CREATE_TABLE_PART)
        # self.cursor.execute(self.CREATE_TABLE_PO_PART)
        # self.cursor.execute(self.CREATE_TABLE_LOAN)
        # self.connector.commit()
        #################################################


    def close(self):
        self.cursor.close()


