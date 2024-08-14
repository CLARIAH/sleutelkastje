package nl.knaw.huc.di.todo.controllers;

import io.javalin.http.Context;
import nl.knaw.huc.di.todo.Todo;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Paths;

public class TodoController {

    static final Logger LOG = LoggerFactory.getLogger(Todo.class);

    public void getTodoList(Context ctx) {
        String eppn = ctx.attribute("eppn");
        LOG.info("getTodolist - eppn: {}", eppn);
        String result = "No todo file. Enjoy your day!";
        // read the todofiles/{eppn}.todo file
        String fileName = "todofiles/" + eppn + ".todo";
        try {
            result = new String(Files.readAllBytes(Paths.get(fileName)));
        } catch (Exception e) {
            // throw new RuntimeException(e);
            // do nothing
        }
        // return the content
        LOG.info(result);

        JSONObject returnObject = new JSONObject();
        returnObject.put("tasks", result);
        returnObject.put("eppn", eppn);

        ctx.result(returnObject.toString());
        ctx.contentType("application/json");
        return;
    }
}
