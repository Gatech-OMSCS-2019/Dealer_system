from decimal import Decimal

from .dbhelper import DbHelper
from .models import *


class DbManager:
    HOST = "localhost"
    PORT = 3306
    USER = "root"
    PASSWD = "root"
    DB = "Test_DB"

    def __init__(self):
        self.__db_helper = DbHelper(self.HOST, self.USER, self.PORT)
        self.cursor = self.__db_helper.cursor

    #   utility functions
    def dict_to_tuple(self, dict):
        return tuple(list(dict.values()))

    def add_user_entry(self, first_name, last_name, job_title, gender):
        sql = "INSERT INTO User (first_name, last_name, job_title, gender)VALUES (%s,%s,%s,%s)"
        self.cursor.execute(sql, (first_name, last_name, job_title, gender))
        self.change_commit()

    # def cursor2dict(self, mycursor, is_cursor):
    #     if is_cursor:
    #         return mycursor
    #     else:
    #         return mycursor.fetchall()

    ########################################## Search ######################################
    def search(self, manufacturer, type, model_year, keywords, colors, job_title=None, vin=None, status=None):
        sql = '''SELECT V.VIN, T.type_name, V.model_year, V.model_name, M.mfg_name, V.mileage, TT.colors,TT.color_ids,
         IF(sum(price) IS NOT NULL, (original_price*1.25 + SUM(price) *1.1) , original_price*1.25 )  AS sales_price FROM Vehicle AS V
                JOIN Manufacturer AS M ON V.mfg_id = M.mfg_id
                JOIN Type AS T ON V.type_id = T.type_id
                LEFT JOIN PoPart AS po ON po.VIN = V.VIN
                LEFT JOIN (SELECT VIN, GROUP_CONCAT(color order by color SEPARATOR ';') AS colors, GROUP_CONCAT(vc.color_id SEPARATOR ';') AS color_ids FROM vehiclecolor AS vc
                JOIN Color AS c ON c.color_id = vc.color_id
                GROUP BY VIN) AS TT ON TT.VIN = V.VIN
                WHERE 1 = 1
        '''
        if manufacturer:
            sql = sql + f" AND V.mfg_id = '{manufacturer}'"
        if type:
            sql = sql + f" AND V.type_id = '{type}'"
        if model_year:
            sql = sql + f" AND V.model_year = {model_year}"
        if vin:
            sql = sql + f" AND V.VIN = '{vin}'"
        if status == 'Sold':
            sql = sql + f" AND V.purchased_by IS NOT NULL"
        elif status == 'Unsold':
            sql = sql + f" AND V.purchased_by IS NULL"
        if keywords:
            sql += '''
                    AND (
                        V.VIN LIKE '%{0}%'
                        OR original_price LIKE '%{0}%'
                        OR model_year LIKE '%{0}%'
                        OR model_name LIKE '%{0}%'
                        OR mfg_name LIKE '%{0}%'
                        OR type_name LIKE '%{0}%'
                    
                    )
            '''.format(keywords)
        if colors:
            str_colors = self.color_to_string(colors)
            sql += '''AND (TT.color_ids = '{0}'
			OR TT.color_ids LIKE '{0};%'
            OR TT.color_ids LIKE '%;{0};%'
            OR TT.color_ids LIKE '%;{0}'
        )'''.format(str_colors)

        if 'Inventory Clerk' not in job_title and 'Manager' not in job_title:
            sql = sql + '''
                AND  purchased_by IS NULL AND V.VIN NOT IN 
                (SELECT DISTINCT VIN FROM PoPart
                WHERE status <> 'INSTALLED')	
            '''
        elif 'Inventory Clerk' in job_title and 'Manager' not in job_title:
            sql += " AND V.purchased_by IS NULL"
        sql += ' GROUP BY V.VIN'
        sql += ' ORDER BY V.VIN'
        print(sql)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def color_to_string(self, colors):
        count = 0
        str = ""
        for c in colors:
            str += c
            if count != len(colors) - 1:
                str += ";"
            count += 1
        return str

    def has_pending(self, vin):
        sql = '''
                SELECT * FROM Po_part
                WHERE CONTAINS (po_num, %s) 
        '''
        self.cursor.execute(sql, (vin,))

    ########################## User Query #######################################################

    def list_user(self):
        sql = '''
                SELECT * from user
        '''
        self.cursor.execute(sql)
        return self.cursor

    def instantiate_user(self, cursor):
        if cursor.rowcount == 1:

            result = cursor.fetchone()
            self.change_commit()
            user = User(result['username'], result['password'], result['first_name'], result['last_name'],
                        result['job_title'])
        else:
            result = cursor.fetchall()
            self.change_commit()
            job_titles = []
            for r in result:
                job_titles.append(r['job_title'])
            user = User(result[0]['username'], result[0]['password'], result[0]['first_name'], result[0]['last_name'],
                        job_titles)
        return user

    def get_user_by_job(self, job_title):
        sql = "SELECT * FROM User WHERE job_title = %s"
        self.cursor.execute(sql, (job_title,))
        result = self.cursor.fetchall()
        return result

    def get_user_by_username(self, username):
        # print(f"inside get user by username {username}")
        sql = '''
                    SELECT * FROM User AS u
                    JOIN UserJob uj ON uj.user_id = u.user_id
                    JOIN Job AS j ON j.job_id = uj.job_id 
                    WHERE username = %s
                '''
        self.cursor.execute(sql, (username,))

        try:
            user = self.instantiate_user(self.cursor)
        except:
            user = None
        return user

    def get_user_by_id(self, user_id):
        sql = '''
                    SELECT * FROM User
                    WHERE user_id = %s
                '''
        self.cursor.execute(sql, (user_id,))
        user = self.instantiate_user(self.cursor)
        return user

    def get_user_id(self, username):
        sql = '''
                SELECT user_id FROM User
                WHERE username = %s
        '''
        self.cursor.execute(sql, (username,))
        return self.cursor.fetchone()['user_id']

    def info_4_manager(self, vin):
        sql = ''' SELECT CONCAT(u.first_name, ' ' ,u.last_name) AS inven, CONCAT(s.first_name, ' ', s.last_name) AS sales, v.add_at, v.sold_by, v.sold_at, 
                    CONCAT(year(v.sold_at),'-', month(v.sold_at)) as `starting_month`,rate, down_payment, payment term 
                    FROM Vehicle AS v
                    LEFT JOIN User AS u ON u.user_id = v.add_by
                    LEFT JOIN User AS s ON s.user_id = v.sold_by
                    LEFT JOIN Loan AS l ON l.VIN = V.VIN
                    WHERE v.VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchone()
        return result

    ################################## VEHICLE Query #############################

    def list_vehicle(self):
        sql = '''
                SELECT * FROM Vehicle
        '''
        self.cursor.execute(sql)
        return self.cursor

    def if_sold(self, vin):
        sql = '''
                SELECT purchased_by FROM Vehicle
                WHERE VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchone()
        self.change_commit()
        if result['purchased_by'] is None:
            return False
        else:
            return True

    def get_mfg(self, vin):
        sql = '''
                SELECT mfg_name FROM Manufacturer AS m
                JOIN Vehicle AS v ON v.mfg_id = m.mfg_id
                WHERE v.VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchone()
        return result

    def get_type(self, vin):
        sql = '''
                SELECT type_name FROM Type AS t
                JOIN Vehicle AS v ON v.type_id = t.type_id
                WHERE v.VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchone()
        return result

    def instantiate_vehicle(self, result):
        self.change_commit()
        # print(f"{result} ------------------ instantiate_vehicle")
        vehicle = Vehicle(result['VIN'], result['mileage'], result['car_condition'], result['original_price'],
                          result['model_year'],
                          result['model_name'], result['mfg_id'], result['type_id'],
                          result['description'])
        return vehicle

    def get_vehicle_by_vin(self, vin):
        sql = '''
                SELECT * FROM Vehicle AS v
                JOIN Manufacturer AS m
                ON v.mfg_id = m.mfg_id
                JOIN Type AS t
                ON v.type_id = t.type_id
                WHERE v.VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchone()
        self.change_commit()
        try:
            return self.instantiate_vehicle(result)
        except:
            return None

    def get_vehicle_by_type(self, type):
        sql = "SELECT * FROM Vehicle WHERE type = %s"
        self.cursor.execute(sql, (type,))
        result = self.cursor.fetchall()
        return result

    def get_avail_vehicle(self):
        sql = '''
                SELECT VIN FROM Vehicle
                WHERE purchased_by IS NULL AND VIN NOT IN 
                (SELECT DISTINCT VIN FROM PoPart
                WHERE status <> 'INSTALLED')
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def pending_num(self):
        sql = '''
               SELECT COUNT(DISTINCT v.VIN) AS pending_num from Vehicle AS v
                JOIN popart AS pp ON pp.VIN = v.VIN
                WHERE v.purchased_by IS NULL AND pp.status <> 'INSTALLED'
            '''
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def list_vehicles_by_owner(self, owner):
        sql = '''
             SELECT Vehicle.VIN, Vehicle.type, Vehicle.price, User.first_name
            FROM Vehicle
            JOIN User ON  User.user_id = Vehicle.owner_id 
            WHERE Vehicle.type = 'Convertible' AND User.first_name= %s
        '''
        self.cursor.execute(sql, (owner,))
        return self.cursor

    def generate_order_index(self, vin):
        # print(f"vin is {vin}, {type(vin)}")
        sql = '''
                SELECT VIN, order_index FROM PartOrder
                WHERE VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        num = self.cursor.rowcount

        order_index = ("00" + str(num + 1))[-3:]
        return order_index

    def update_status(self, vin):
        sql = '''
                UPDATE Vehicle
                SET status  = %s
                WHERE vin = %s
        '''
        self.cursor.execute(sql, ('SOLD', vin,))
        self.change_commit()

    def check_part_status(self, arg):
        for e in arg:
            if e['status'] != 'INSTALLED':
                return False
        # print('status is true ---- check part status')
        return True

    # def update_availability(self, vin):
    #     sql_1 = '''
    #             SELECT * FROM POPart
    #             WHERE VIN = %s;
    #     '''
    #
    #     sql_2 = '''
    #                 SELECT status FROM Vehicle
    #                 WHERE VIN = %s;
    #         '''
    #     sql_3 = '''
    #                 UPDATE Vehicle
    #                 SET availability = %s
    #                 WHERE  VIN = %s;
    #         '''
    #     self.cursor.execute(sql_1, (vin,))
    #     dict_1 = self.cursor.fetchall()
    #     self.cursor.execute(sql_2, (vin,))
    #     dict_2 = self.cursor.fetchone()
    #     status = self.check_part_status(dict_1)
    #     if status and dict_2['status'] == 'UNSOLD':
    #         availability = 'YES'
    #     else:
    #         availability = 'NO'
    #     self.cursor.execute(sql_3, (availability, vin,))
    #     self.change_commit()

    def add_vehicle(self, vehicle, seller_id, user_id, colors):
        # get seller id

        sql_1 = '''
                INSERT INTO Vehicle
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                DEFAULT, DEFAULT, DEFAULT, DEFAULT )
        '''

        self.cursor.execute(sql_1, (vehicle.vin, float(vehicle.original_price), vehicle.model_year, vehicle.model_name,
                                    seller_id, int(vehicle.type_id), int(vehicle.mfg_id), vehicle.mileage,
                                    vehicle.car_condition,
                                    vehicle.description, user_id,))

        # add color

        sql_2 = '''
                INSERT INTO VehicleColor
                VALUES (%s, %s)
        '''
        for c in colors:
            self.cursor.execute(sql_2, (vehicle.vin, c,))
        self.change_commit()

    def get_sales_price(self, vehicle):
        parts = self.get_parts_vehicle(vehicle.vin)
        part_cost = 0
        for p in parts:
            part_cost += p['price']
        sales_price = round(Decimal(vehicle.original_price) * Decimal(1.25) + part_cost * Decimal(1.1), 2)
        # print(f"{vehicle.vin} --- {sales_price}")
        return sales_price

    def list_colors(self):
        sql = '''
                Select * from Color
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def get_color_by_vehicle(self, vin):
        sql = '''
                SELECT color FROM Color AS c
                JOIN VehicleColor AS vc ON vc.color_id = c.color_id
                JOIN Vehicle AS v ON v.VIN = vc.VIN
                WHERE v.VIN = %s
        '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    ###################################### PART Query #####################################

    def get_parts_vehicle(self, vin):
        sql = '''
                    SELECT po.VIN, po.order_index, description,p.part_num, price, pop.status, v.vendor_name FROM PartOrder AS po
                    JOIN POPart as pop ON po.VIN = pop.VIN AND po.order_index = pop.order_index
                    JOIN Part as p ON pop.part_num = p.part_num
                    LEFT JOIN Vendor as v ON v.vendor_id = po.vendor_id
                    WHERE po.VIN = %s;
            '''
        self.cursor.execute(sql, (vin,))
        result = self.cursor.fetchall()
        return result

    def list_all_parts(self):
        sql = '''
                    SELECT part_num FROM Part
            '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def update_part_status(self, new_status, part_num, vin, order_index):
        sql = '''
                UPDATE POPart
                SET status = %s
                WHERE VIN = %s AND part_num = %s AND order_index = %s
            '''
        self.cursor.execute(sql, (new_status, vin, part_num, order_index,))
        self.change_commit()

    def add_part(self, part):
        sql = '''
                         INSERT INTO Part
                         VALUES (%s, %s)
              '''
        self.cursor.execute(sql, (part.part_num, part.description))
        self.change_commit()

    ##################################### PART_ORDER Query ####################################

    def add_part_order(self, vin, order_index, vendor_id):
        sql = '''
                    INSERT INTO PartOrder
                    VALUES (%s, %s, %s)
            '''
        self.cursor.execute(sql, (vin, order_index, vendor_id,))
        self.change_commit()

    def add_po_parts(self, vin, order_index, part_num, price):
        sql = '''
                INSERT INTO POPart
                VALUES (NULL, %s, %s, %s, DEFAULT, %s)
            '''
        self.cursor.execute(sql, (vin, order_index, part_num, price))
        self.change_commit()

    def get_part(self, type, param):
        if type == 'part_num':
            sql = '''
                    SELECT * FROM Part
                    WHERE part_num = %s
                '''
        self.cursor.execute(sql, (param,))
        return self.cursor.fetchone()

    def po_total_cost(self, vin, order_index):
        sql = '''
                SELECT  SUM(price) AS total_cost FROM POPart
                JOIN Part ON POPart.part_num = Part.part_num
                WHERE VIN = %s AND order_index= %s;
            '''
        self.cursor.execute(sql, (vin, order_index,))
        result = self.cursor.fetchone()
        total_cost = result['total_cost']
        # print(f"total cost is {total_cost}")
        update_sql = '''
                    UPDATE PartOrder
                    SET total_cost = %s
                    WHERE VIN = %s AND order_index= %s;
            '''
        self.cursor.execute(update_sql, (total_cost, vin, order_index))
        self.change_commit()
        return self.cursor.fetchone()

    ######################################## VENDOR Query ################################
    def list_vendor(self):
        sql = '''
                    SELECT * FROM Vendor
            '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_vendor_id(self, vendor_name):
        sql = '''
                SELECT * FROM Vendor
                WHERE vendor_name = %s
            '''
        self.cursor.execute(sql, (vendor_name,))
        return self.cursor.fetchone()

    ######################################  MANUFACTURER Query ################################

    def list_manufacturers(self):
        sql = '''
                SELECT * FROM Manufacturer
            '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    ######################################  TYPE Query ####################################
    def list_types(self):
        sql = '''
                       SELECT * FROM Type
                   '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def search_seller(self, keyword):
        sql = '''
                SELECT * FROM User
                WHERE first_name LIKE %s
            '''
        self.cursor.execute(sql, ('%' + keyword + '%',))
        result = self.cursor.fetchall()
        return result

    def add_customer(self, new_customer):
        sql = '''
                                    INSERT INTO Customer
                                    VALUES (NULL, %s, %s, %s, %s, %s, %s)
                                '''
        self.cursor.execute(sql, (new_customer.phone,
                                  new_customer.street, new_customer.city, new_customer.state, new_customer.zip_code,
                                  new_customer.email,))
        self.change_commit()
        customer_id = self.cursor.lastrowid
        # print(f" customer type {new_customer.category}, {new_customer.dl_num}, {new_customer.first_name}")
        if new_customer.category:

            sql_individual = '''
                            INSERT INTO Individual
                            VALUES (%s, %s, %s, %s)
                    '''

            self.cursor.execute(sql_individual,
                                (new_customer.dl_num, customer_id, new_customer.first_name, new_customer.last_name))
        else:
            sql_business = '''
                                       INSERT INTO Business
                                       VALUES (%s, %s, %s, %s, %s, %s)
                               '''
            self.cursor.execute(sql_business,
                                (new_customer.tax_id, new_customer.business_name, new_customer.title,
                                 new_customer.first_name, new_customer.last_name, customer_id))

        self.change_commit()

    def change_commit(self):
        self.__db_helper.connector.commit()

    ########################## CUSTOMER  Query ####################################
    def get_customer(self, input, type):

        if type:
            sql = '''
                            SELECT * from Individual
                            WHERE dl_num = %s
                    '''
        else:
            sql = '''
                            SELECT * from Business
                            WHERE tax_id = %s
                    '''
        self.cursor.execute(sql, (input,))
        return self.cursor.fetchone()

    def list_individual(self):

        sql = '''
                            SELECT * from Customer AS c
                            JOIN Individual AS i ON c.customer_id = i.customer_id

                    '''

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def list_business(self):
        sql = '''
                                SELECT * from Customer AS c
                                JOIN Business AS b ON c.customer_id = b.customer_id

                        '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_seller(self, vehicle):
        sql = '''
            SELECT c.street, c.city, c.state, c.zip_code, c.phone,
            c.email, IF(i.first_name IS NOT NULL, i.first_name, b.first_name) AS first_name,
            IF(i.last_name IS NOT NULL, i.last_name, b.last_name) As las_name, i.dl_num, b.tax_id, b.business_name, b.title FROM Customer AS c
            JOIN Vehicle AS v ON v.owner_id = c.customer_id
            LEFT  JOIN Individual AS i ON i.customer_id = c.customer_id
            LEFT JOIN Business AS b ON b.customer_id = c.customer_id
            WHERE VIN = %s
        '''

        self.cursor.execute(sql, (vehicle.vin,))
        result = self.cursor.fetchone()
        return result

    def get_buyer(self, vehicle):
        sql = '''
                    SELECT c.street, c.city, c.state, c.zip_code, c.phone,
                    c.email, IF(i.first_name IS NOT NULL, i.first_name, b.first_name) AS first_name,
                    IF(i.last_name IS NOT NULL, i.last_name, b.last_name) As las_name, i.dl_num, b.tax_id, b.business_name, b.title FROM Customer AS c
                    JOIN Vehicle AS v ON v.purchased_by = c.customer_id
                    LEFT  JOIN Individual AS i ON i.customer_id = c.customer_id
                    LEFT JOIN Business AS b ON b.customer_id = c.customer_id
                    WHERE VIN = %s
                '''

        self.cursor.execute(sql, (vehicle.vin,))
        result = self.cursor.fetchone()
        return result

    ########################### LOAN Query ###########################

    def add_loan(self, vin, rate, payment, down_payment, term):
        sql = '''
                INSERT INTO Loan
                VALUES (%s , %s, %s, %s, %s)
        
        '''
        self.cursor.execute(sql, (vin, rate, payment, down_payment, term))
        self.change_commit()

    ############################# TRANSACTION Query ##############################

    def add_transaction(self, vin, customer_id, user_id):
        sql = '''
                UPDATE Vehicle
                SET purchased_by = %s, sold_by = %s
                WHERE VIN = %s;
        '''
        self.cursor.execute(sql, (customer_id, user_id, vin,))
        self.change_commit()

    ############################ Reprots #####################################
    def seller_history(self):
        sql = '''
                SELECT  CONCAT(IF(b.first_name IS NULL, i.first_name, b.business_name), ' ' , 
                IF(b.last_name IS NULL, i.last_name, '')) AS 'seller_name', COUNT(DISTINCT v.VIN) AS 'vehicle_num', 
                ROUND(AVG(v.original_price),2) AS 'avg_price', COUNT(pp.part_num) AS 'parts_ordered', 
                SUM(pp.price) AS 'parts_cost', ROUND(COUNT(pp.part_num)/COUNT(DISTINCT v.VIN),2) AS 'avg_part', 
                ROUND(SUM(pp.price)/ COUNT(DISTINCT v.VIN),0) AS 'avg_part_cost'  FROM  Vehicle AS v
                LEFT JOIN Customer AS c ON c.customer_id = v.owner_id
                LEFT JOIN Individual AS i ON i.customer_id = c.customer_id
                LEFT JOIN Business AS b ON b.customer_id = c.customer_id
                LEFT JOIN POPart AS pp ON v.VIN = pp.VIN
                GROUP BY seller_name
                ORDER BY vehicle_num DESC, avg_price ASC
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def average_time(self):
        sql = '''
                SELECT type_name,  ROUND(avg(datediff(sold_at, add_at)),1) AS 'instock_day' FROM Vehicle AS v
                LEFT JOIN Type AS t ON t.type_id = v.type_id
                WHERE type_name IN (SELECT DISTINCT type_name AS r FROM Vehicle AS v
                LEFT JOIN Type AS t ON t.type_id = v.type_id
                WHERE v.purchased_by IS NOT NULL)
                GROUP BY type_name
                
                UNION
                
                SELECT   type_name,'N/A' AS 'instock_day' FROM Vehicle AS v
                LEFT JOIN Type AS t ON t.type_id = v.type_id
                WHERE v.purchased_by IS NULL AND type_name NOT IN 
                (SELECT DISTINCT type_name AS r FROM Vehicle AS v
                LEFT JOIN Type AS t ON t.type_id = v.type_id
                WHERE v.purchased_by IS NOT NULL)
                GROUP BY type_name
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def price_per_condition(self):
        sql = '''
                SELECT t.type_name, CONCAT('$', COALESCE(ROUND(excellent.avg_price,2),'0')) AS 'excellent',CONCAT('$', COALESCE(ROUND(very_good.avg_price,2), '0')) AS 'very_good',
                CONCAT('$', COALESCE(ROUND(good.avg_price,2),'0')) AS 'good', CONCAT('$', COALESCE(ROUND(fair.avg_price,2),'0')) AS 'fair' FROM Type AS t
                LEFT JOIN (SELECT type_name, AVG(v.original_price) AS 'avg_price' FROM Vehicle AS v
                JOIN Type ON v.type_id = Type.type_id
                WHERE v.car_condition = 'EXCELLENT'
                GROUP BY type_name) AS excellent ON excellent.type_name = t.type_name
                
                LEFT JOIN (SELECT type_name, AVG(v.original_price) AS 'avg_price' FROM Vehicle AS v
                JOIN Type ON v.type_id = Type.type_id
                WHERE v.car_condition = 'GOOD'
                GROUP BY type_name) AS good ON good.type_name = t.type_name
                
                LEFT JOIN (SELECT type_name, AVG(v.original_price) AS 'avg_price' FROM Vehicle AS v
                JOIN Type ON v.type_id = Type.type_id
                WHERE v.car_condition = 'VERY GOOD'
                GROUP BY type_name) AS very_good ON very_good.type_name = t.type_name
                
                LEFT JOIN (SELECT type_name, AVG(v.original_price) AS 'avg_price' FROM Vehicle AS v
                JOIN Type ON v.type_id = Type.type_id
                WHERE v.car_condition = 'FAIR'
                GROUP BY type_name) AS fair ON fair.type_name = t.type_name;
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def parts_stats(self):
        sql = '''
                SELECT vendor_name, COUNT(p.part_num) AS 'part_quan', SUM(price) AS 'cost' FROM Vendor AS v
                LEFT JOIN PartOrder AS po ON po.vendor_id = v.vendor_id
                JOIN POPart AS pp ON pp.VIN = po.VIN AND pp.order_index = po.order_index
                JOIN Part AS p ON p.part_num = pp.part_num
                GROUP BY vendor_name
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def monthly_sales(self):
        sql = '''
            SELECT COUNT(T.vin) AS vehicle_num, SUM(T.sales_price) AS sales_income, (SUM(T.sales_price) - SUM(T.original_price)) AS net_income, T.year, T.month FROM
            (
            Select v.VIN AS vin , original_price, price, YEAR(sold_at) AS year, Month(sold_at) AS month , 
            IF(sum(price) IS NOT NULL, original_price*1.25 + SUM(price) *1.1,  original_price*1.25 )  AS sales_price FROM Vehicle AS v
            LEFT JOIN POPart AS pp ON pp.VIN =  v. VIN
            Where v.purchased_by IS NOT NULL
            GROUP BY v.VIN
            ) AS T
            GROUP BY T.year, T.month
            ORDER BY T.year DESC, T.month DESC
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def best_sales(self, year, month):
        sql = '''
            SELECT CONCAT(u.first_name, ' ', u.last_name) AS sales_people, count(T.vin)AS vehicle_num, 
            SUM(T.sales_price) AS sales, year(sold_at) AS year, month(sold_at) AS Month FROM vehicle AS v
            
            JOIN user AS u ON u.user_id = v.sold_by
            
            JOIN (Select v.VIN AS vin , v.original_price,
            IF(sum(price) IS NOT NULL, original_price*1.25 + SUM(price) *1.1,  original_price*1.25 )  AS sales_price FROM Vehicle AS v
            LEFT JOIN POPart AS pp ON pp.VIN =  v. VIN
            Where v.purchased_by IS NOT NULL
            GROUP BY v.VIN) AS T ON T.vin = v.VIN
            WHERE v.purchased_by IS NOT NULL AND year(sold_at)  = %s AND month(sold_at) =%s
            GROUP BY CONCAT(u.first_name, ' ', u.last_name)
            ORDER BY vehicle_num DESC, T.sales_price DESC
        '''
        self.cursor.execute(sql, (year, month,))
        result = self.cursor.fetchall()
        self.change_commit()
        return result

    def loan_income(self, month):
        sql = '''
            SELECT SUM(payment*0.01) AS earned_share, SUM(payment) AS monthly_payment, payment, year(date_add(curdate() , INTERVAL -%s MONTH)) AS year, 
            month (date_add(curdate() , INTERVAL -%s MONTH)) AS month,YEAR(v.sold_at), month(v.sold_at)   ,
            YEAR(DATE_ADD(v.sold_at, INTERVAL l.term MONTH)) AS end_year, MONTH(DATE_ADD(v.sold_at, INTERVAL l.term MONTH)) AS end_month FROM Loan AS l
            JOIN Vehicle AS v ON v.VIN = l.VIN
            WHERE CASE
									WHEN YEAR(v.sold_at)  < YEAR(date_add(curdate() , INTERVAL -%s MONTH)) THEN YEAR(v.sold_at)  < YEAR(date_add(curdate() , INTERVAL -%s MONTH)) 
                                    WHEN YEAR(v.sold_at)  = YEAR(date_add(curdate() , INTERVAL -%s MONTH)) THEN MONTH(v.sold_at)  < MONTH(date_add(curdate() , INTERVAL -%s MONTH)) 
                                    ELSE 1=2
							END
                            AND
                            CASE
									WHEN YEAR(DATE_ADD(v.sold_at, INTERVAL l.term MONTH)) < YEAR(date_add(curdate() , INTERVAL -%s MONTH)) THEN FALSE
                                    WHEN YEAR(DATE_ADD(v.sold_at, INTERVAL l.term MONTH)) = YEAR(date_add(curdate() , INTERVAL -%s MONTH)) THEN MONTH (DATE_ADD(v.sold_at, INTERVAL l.term MONTH)) >= MONTH(date_add(curdate() , INTERVAL -%s MONTH)) 
                                    ELSE TRUE
							END
            

        '''
        self.cursor.execute(sql, (month, month, month, month, month, month, month, month, month))
        result = self.cursor.fetchone()
        return result
