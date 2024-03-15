package nl.knaw.huc.di.todo;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;

public class RootHandler implements HttpHandler {

    @Override

    public void handle(HttpExchange he) throws IOException {
        String response = "<b>Server start success if you see this message</b><br/><b>Port: " + "9000" + "</b>";
        he.sendResponseHeaders(200, response.length());
        OutputStream os = he.getResponseBody();
        os.write(response.getBytes());
        os.close();
    }
}