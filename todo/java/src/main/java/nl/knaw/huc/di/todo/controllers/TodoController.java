package nl.knaw.huc.di.todo.controllers;

import io.javalin.http.BadRequestResponse;
import io.javalin.http.Context;
import io.javalin.http.InternalServerErrorResponse;
import nl.knaw.huc.di.todo.dataclasses.CreateTodoRequest;
import org.json.JSONArray;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class TodoController
{
    static final Logger LOG = LoggerFactory.getLogger(TodoController.class);

    /**
     * Get the to do list of the currently logged-in user.
     * @param ctx The Javalin context
     */
    public void getTodoList(Context ctx)
    {
        String eppn = ctx.attribute("eppn");
        LOG.info("getTodolist - eppn: {}", eppn);
        JSONArray todos = new JSONArray();

        // read the todofiles/{eppn}.todo file
        String fileName = "todofiles/" + eppn + ".todo";
        try {
           todos.putAll(Files.readAllLines(Paths.get(fileName)));
        } catch (Exception e) {
            LOG.info("No todo file, nothing to do!");
            // do nothing
        }

        if (todos.isEmpty()) {
            todos.put("No todo file. Enjoy your day!");
        }

        JSONObject returnObject = new JSONObject();
        returnObject.put("tasks", todos);
        returnObject.put("user", eppn);

        ctx.result(returnObject.toString());
        ctx.contentType("application/json");
    }

    /**
     * Create a new to do
     * @param ctx The Javalin context
     */
    public void addTodo(Context ctx)
    {
        CreateTodoRequest request;
        String eppn = ctx.attribute("eppn");
        try {
            request = ctx.bodyAsClass(CreateTodoRequest.class);
        } catch (Exception e) {
            LOG.info("Invalid request");
            throw new BadRequestResponse();
        }
        LOG.info("Add todo: {}", request.task);

        String fileName = "todofiles/" + eppn + ".todo";
        String todo = request.task + "\n";

        // Write it to the file
        try {
            Files.writeString(Paths.get(fileName), todo, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException e) {
            LOG.info("error", e);
            throw new InternalServerErrorResponse();
        }

        JSONObject returnObject = new JSONObject();
        returnObject.put("task", request.task);
        returnObject.put("message", "added task");
        ctx.result(returnObject.toString());
        ctx.contentType("application/json");
        ctx.status(201);
    }
}
