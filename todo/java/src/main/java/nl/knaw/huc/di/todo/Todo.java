package nl.knaw.huc.di.todo;

import io.javalin.Javalin;
import nl.knaw.huc.di.openidconnect.LoginEndPoint;
import nl.knaw.huc.di.openidconnect.OpenIdClient;
import nl.knaw.huc.di.openidconnect.OpenIdConnectException;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class Todo {

    public Todo() throws OpenIdConnectException {
        OpenIdClient client = getClient();
        LoginEndPoint lep = new LoginEndPoint(client);
        var app = Javalin.create(/*config*/)
                         .get("/", ctx -> ctx.result("Hello World"))
                         .get("/login", lep::login)
                         .get("/callback", lep::callback)
                         .start(8000);
        // app.get("/todo", ctx -> { // the {} syntax does not allow slashes ('/') as part of the parameter
        //     if(login()) {
        //         ctx.result(getTodoList());
        //     }
        // });
        // LoginEndPoint endpoint = new LoginEndPoint(getOpenIdClient());
        // app.get(String.valueOf((endpoint.login("/login"))));
    }

    private OpenIdClient getClient() throws OpenIdConnectException {
        String discoveryUrl = System.getenv("OIDC_SERVER");
        String clientId = System.getenv("OIDC_CLIENT_ID");
        String clientSecret = System.getenv("OIDC_CLIENT_SECRET");
        String scope = "openid email profile";
        String claims = "{\"userinfo\":{\"edupersontargetedid\":null,\"schac_home_organisation\":null," +
            "\"nickname\":null,\"email\":null,\"eppn\":null,\"idp\":null}}";
        String baseUri = System.getenv("APP_DOMAIN");
        OpenIdClient openIdClient =
            new OpenIdClient(discoveryUrl, clientId, clientSecret, scope, claims, baseUri);
        return openIdClient;
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