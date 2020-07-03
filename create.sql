create table books (
    book_id serial primary key,
    isbn varchar not null,
    title VARCHAR not NULL,
    author varchar not null,
    year integer 

);

create table Users (
    user_id serial PRIMARY key,
    username varchar unique,
    password varchar not null,
    name varchar not null,
    r_written Integer REFERENCES books
);

create table review(
    b_id integer REFERENCES books,
    r varchar ,
    id_user integer references users
);
