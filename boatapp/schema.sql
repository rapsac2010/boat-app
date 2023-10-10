DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS boat;
DROP TABLE IF EXISTS boat_transmissions;
DROP TABLE IF EXISTS boat_control;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS discount_codes;
DROP TABLE IF EXISTS register_codes;

-- User table contains user data (username, password, class, credits)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    registration_code TEXT NOT NULL,
    class TEXT NOT NULL DEFAULT 'user', -- 'user', 'family', 'admin'
    credits INTEGER NOT NULL DEFAULT 0,
    profile_fname TEXT DEFAULT NULL
);

-- Boat table contains boat data transmissions (time, coordinates, voltage, speed, amperage)
CREATE TABLE boat_transmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boat_id INTEGER NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    speed REAL NOT NULL,
    voltage REAL NOT NULL,
    amperage REAL NOT NULL,
    renter_id INTEGER,
    FOREIGN KEY (renter_id) REFERENCES user (id)
);

CREATE TABLE boat_control (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boat_id INTEGER NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    boat_on_lk INTEGER NOT NULL DEFAULT 1,
    boat_on_desired INTEGER NOT NULL DEFAULT 1,
    motor_lk INTEGER NOT NULL DEFAULT 0,
    motor_desired INTEGER NOT NULL DEFAULT 0,
    inverter_lk INTEGER NOT NULL DEFAULT 0,
    inverter_desired INTEGER NOT NULL DEFAULT 0,
    horn_lk INTEGER NOT NULL DEFAULT 0,
    horn_desired INTEGER NOT NULL DEFAULT 0,
    lights_fun_lk INTEGER NOT NULL DEFAULT 0,
    lights_fun_desired INTEGER NOT NULL DEFAULT 0,
    light_nav_lk INTEGER NOT NULL DEFAULT 0,
    light_nav_desired INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (boat_id) REFERENCES boat (id)
);


CREATE TABLE boat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seats INTEGER NOT NULL,
    length REAL NOT NULL,
    width REAL NOT NULL,
    battery_capacity REAL NOT NULL
);

-- Reservation table contains reservation data (boat_id, renter_id, start_time, end_time)
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boat_id INTEGER NOT NULL,
    renter_id INTEGER NOT NULL,
    price REAL NOT NULL DEFAULT 49,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'paid', 'cancelled'
    mollie_payment_id TEXT DEFAULT NULL,
    discount_code_id INTEGER,
    FOREIGN KEY (discount_code_id) REFERENCES discount_codes (id),
    FOREIGN KEY (boat_id) REFERENCES boat (id),
    FOREIGN KEY (renter_id) REFERENCES user (id)
);

CREATE TABLE discount_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    discount_percent INTEGER NOT NULL DEFAULT 0,
    max_uses INTEGER NOT NULL DEFAULT 1,
    current_uses INTEGER NOT NULL DEFAULT 0
);

-- Register codes table contains registration codes (id, code, class, credits, number_of_uses)
CREATE TABLE register_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    class TEXT NOT NULL DEFAULT 'user', -- 'user', 'family', 'admin'
    credits INTEGER NOT NULL DEFAULT 0,
    max_uses INTEGER NOT NULL DEFAULT 1,
    current_uses INTEGER NOT NULL DEFAULT 0
);



-- TODO: remove before deployment
INSERT INTO user (username, password, first_name, last_name, email, registration_code, class, credits, profile_fname)
VALUES ('test', 'scrypt:32768:8:1$mclLcw9Bu5DgMX3K$28ef855a6ca1041b9fc7714a700be215ba57544553974105c2636c5144009380eb36d89591bedbd81dc92d19112de876efab4ba091c52d0250b6b184cc7384ba',
        'Caspar', 'Hentenaar', 'caspar28subaru@live.nl', 'dev', 'user', 0, '73af437c-00e4-4cf0-94bf-ea39804aa4c5.jpg');

INSERT INTO register_codes (code, class, max_uses, current_uses) VALUES ('dev', 'user', 999, 0);

INSERT INTO boat (id, seats, length, width, battery_capacity)
VALUES (1, 12, 5.5, 2, 2400);

INSERT INTO boat_control (boat_id, boat_on_lk, boat_on_desired, motor_lk, motor_desired, inverter_lk, inverter_desired, horn_lk, horn_desired, lights_fun_lk, lights_fun_desired, light_nav_lk, light_nav_desired)
VALUES (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

INSERT INTO boat_transmissions (boat_id, longitude, latitude, speed, voltage, amperage, renter_id)
VALUES (1, 4.873, 52.385538, 0.0, 27, 34, NULL);

INSERT INTO reservations (boat_id, renter_id, start_time, end_time, payment_status)
VALUES (1, 1, '2023-10-12 8:00:00', '2023-10-12 22:00:00', 'payed');

INSERT INTO discount_codes (code, discount_percent, max_uses, current_uses)
VALUES ('test', 10, 1, 0);