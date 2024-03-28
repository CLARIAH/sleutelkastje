package nl.knaw.huc.di.todo;

import io.javalin.Javalin;
import nl.knaw.huc.di.openidconnect.OpenIdClient;
import nl.knaw.huc.di.openidconnect.OpenIdConnectException;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.Set;

public class Todo {

    public Todo() throws OpenIdConnectException {
        var app = Javalin.create(/*config*/)
                         .get("/", ctx -> ctx.result("Hello World"))
                         .start(9000);
        // app.get("/todo", ctx -> { // the {} syntax does not allow slashes ('/') as part of the parameter
        //     if(login()) {
        //         ctx.result(getTodoList());
        //     }
        // });
        // LoginEndPoint endpoint = new LoginEndPoint(getOpenIdClient());
        // app.get(String.valueOf((endpoint.login("/login"))));
    }
    //
    // private boolean login() throws OpenIdConnectException {
    //     boolean result = false;
    //     String discoveryUrl = "";
    //     String clientId = "";
    //     String clientSecret = "";
    //     String scope = "";
    //     String claims = "";
    //     String baseUri = "";
    //     Set properties = Collections.singleton("");
    //     OpenIdClient openIdClient =
    //         new OpenIdClient(discoveryUrl, clientId, clientSecret, scope, claims, properties, baseUri);
    //     Response login_result = new LoginEndPoint(openIdClient).login("");
    //     if(!login_result.equals(null))
    //         return true;
    //     else
    //         return result;
    // }

    private OpenIdClient getOpenIdClient() throws OpenIdConnectException {
        boolean result = false;
        String discoveryUrl = "";
        String clientId = "";
        String clientSecret = "";
        String scope = "";
        String claims = "";
        String baseUri = "";
        Set properties = Collections.singleton("");
        return new OpenIdClient(discoveryUrl, clientId, clientSecret, scope, claims, properties, baseUri);
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

    public static void main(String[] args) throws IOException, OpenIdConnectException {
        System.out.println("Hello world!");
        Path path = Paths.get("./todofiles");
        Files.createDirectories(path);
        new Todo();
    }
}