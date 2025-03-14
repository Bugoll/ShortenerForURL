CREATE TABLE IF NOT EXISTS User (
    id integer primary key autoincrement,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL 
);

CREATE TABLE IF NOT EXISTS Link (
    id integer primary key autoincrement,
    user_id INTEGER,
    long TEXT NOT NULL,
    FOREIGN KEY (user_id) 
        REFERENCES User (id) 
            ON DELETE CASCADE 
            ON UPDATE NO ACTION
);