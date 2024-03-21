package nl.knaw.huc.di.todo;

import io.javalin.Javalin;

import java.io.IOException;

public class Todo {

    public Todo() {
        var app = Javalin.create(/*config*/)
                         .get("/", ctx -> ctx.result("Hello World"))
                         .start(9000);
    }

    public static void main(String[] args) throws IOException {
        System.out.println("Hello world!");
        new Todo();
    }
}