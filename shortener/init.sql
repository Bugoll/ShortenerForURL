CREATE TABLE users (
    id integer primary key autoincrement,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL 
);

CREATE TABLE link (
    id integer primary key autoincrement,
    user_id INTEGER,
    long TEXT NOT NULL,
    FOREIGN KEY (user_id) 
        REFERENCES users (id) 
            ON DELETE CASCADE 
            ON UPDATE NO ACTION
);
