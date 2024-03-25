package nl.knaw.huc.di.todo;

import io.javalin.Javalin;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class Todo {

    public Todo() {
        var app = Javalin.create(/*config*/)
                         .get("/", ctx -> ctx.result("Hello World"))
                         .start(9000);
        app.get("/todo", ctx -> { // the {} syntax does not allow slashes ('/') as part of the parameter
            ctx.result(getTodoList());
        });
    }

    private String getTodoList() {
        // get the epid
        String result = "No todo file. Enjoy your day!";
        String epid = "";
        // read the todofiles/{epid}.todo file
        String fileName = "todofiles/" + epid;
        try {
            result = new String(Files.readAllBytes(Paths.get(fileName)));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        // return the content
        return result;
    }

    public static void main(String[] args) throws IOException {
        System.out.println("Hello world!");
        Path path = Paths.get("./todofiles");
        Files.createDirectories(path);
        new Todo();
    }
}