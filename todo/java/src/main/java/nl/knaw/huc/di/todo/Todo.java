package nl.knaw.huc.di.todo;

import io.javalin.Javalin;
import nl.knaw.huc.di.openidconnect.LoginEndPoint;
import nl.knaw.huc.di.openidconnect.OpenIdClient;
import nl.knaw.huc.di.openidconnect.OpenIdConnectException;
import nl.knaw.huc.di.sleutelkast.SleutelkastClient;
import nl.knaw.huc.di.todo.controllers.TodoController;
import nl.knaw.huc.di.todo.middleware.Authentication;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class Todo {
    static final Logger LOG = LoggerFactory.getLogger(Todo.class);

    OpenIdClient openIdClient;

    public Todo() throws OpenIdConnectException, URISyntaxException
    {
        openIdClient = getOpenIdClient();
        SleutelkastClient sleutelkastClient = new SleutelkastClient(
                "https://sleutelkast.sd.di.huc.knaw.nl",
                "todo",
                "ookgeheim"
        );
        Authentication auth = new Authentication(openIdClient, sleutelkastClient);
        LoginEndPoint lep = new LoginEndPoint(openIdClient);
        TodoController todo = new TodoController();

        var app = Javalin.create()
                .before("/todo", auth::handleAuthentication)
                .get("/", ctx -> ctx.result("Hello World"))
                .get("/login", lep::login)
                .get("/callback", lep::callback)
                .get("/todo", todo::getTodoList)
                .post("/todo", todo::addTodo)
                .start(8000);
    }

    private OpenIdClient getOpenIdClient() throws OpenIdConnectException {
        String discoveryUrl = System.getenv("OIDC_SERVER");
        String clientId = System.getenv("OIDC_CLIENT_ID");
        String clientSecret = System.getenv("OIDC_CLIENT_SECRET");
        String scope = "openid email profile";
        String claims = "{\"userinfo\":{\"edupersontargetedid\":null,\"schac_home_organisation\":null," +
                "\"nickname\":null,\"email\":null,\"eppn\":null,\"idp\":null}}";
        String baseUri = System.getenv("APP_DOMAIN");
        return new OpenIdClient(discoveryUrl, clientId, clientSecret, scope, claims, baseUri);
    }

    public static void main(String[] args) throws IOException, OpenIdConnectException, URISyntaxException
    {
        LOG.info("Hello world!");
        Path path = Paths.get("./todofiles");
        Files.createDirectories(path);
        new Todo();
    }
}
