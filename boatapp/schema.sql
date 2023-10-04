DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS boat;
DROP TABLE IF EXISTS reservations;

-- User table contains user data (username, password, class, credits)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    class TEXT NOT NULL DEFAULT 'user', -- 'user', 'family', 'admin'
    credits INTEGER NOT NULL DEFAULT 0
);

-- Boat table contains boat data transmissions (time, coordinates, voltage, speed, amperage)
CREATE TABLE boat (
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

-- Reservation table contains reservation data (boat_id, renter_id, start_time, end_time)
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boat_id INTEGER NOT NULL,
    renter_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    FOREIGN KEY (boat_id) REFERENCES boat (id),
    FOREIGN KEY (renter_id) REFERENCES user (id)
);
