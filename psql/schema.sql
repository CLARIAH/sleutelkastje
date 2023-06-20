        DROP TABLE IF EXISTS application CASCADE;
        CREATE TABLE application (
            _id SERIAL PRIMARY KEY,
            mnemonic TEXT NOT NULL,
            credentials TEXT NOT NULL,
            redirect TEXT NOT NULL,
            funcPerson TEXT
        );
        DROP TABLE IF EXISTS invitation CASCADE;
        CREATE TABLE invitation (
                _id SERIAL PRIMARY KEY,
                uuid TEXT NOT NULL,
                app int REFERENCES application (_id),
                usr int REFERENCES users (_id)
        );
        DROP TABLE IF EXISTS users CASCADE;
        CREATE TABLE users (
                _id SERIAL PRIMARY KEY,
                user_info JSON,
                keys JSON
        );
        DROP TABLE IF EXISTS key CASCADE;
        CREATE TABLE key (
                _id SERIAL NOT NULL,
                uuid TEXT,
                usr int REFERENCES users (_id)
        );
