package nl.knaw.huc.di.todo;

import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import com.sun.org.slf4j.internal.Logger;
import com.sun.org.slf4j.internal.LoggerFactory;
import nl.knaw.huc.di.openidconnect.LoginEndPoint;
import nl.knaw.huc.di.openidconnect.OpenIdClient;
import org.apache.commons.lang3.StringUtils;

import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Response;

public class EchoGetHandler implements HttpHandler {

    public static final Logger LOG = LoggerFactory.getLogger(LoginEndPoint.class);
    private final Map<UUID, LoginSessionData> loginSessions;
    private final OpenIdClient openIdClient;


    @Override
    @Path("/todo")
    public void handle(HttpExchange he) throws IOException {
        // parse request
        Map<String, Object> parameters = new HashMap<String, Object>();
        URI requestedUri = he.getRequestURI();
        String query = requestedUri.getRawQuery();
        parseQuery(query, parameters);

        // send response
        String response = "";
        for (String key : parameters.keySet())
            response += key + " = " + parameters.get(key) + "\n";
        he.sendResponseHeaders(200, response.length());
        OutputStream os = he.getResponseBody();
        os.write(response.toString().getBytes());
        os.close();
    }

    @Path("/login")
    public Response handle(@QueryParam("redirect-uri") String clientRedirectUri) {
        if (StringUtils.isBlank(clientRedirectUri)) {
            return Response.status(400).entity("expected a query param redirect-uri").build();
        }

        UUID sessionId = UUID.randomUUID();
        UUID nonce = UUID.randomUUID();

        loginSessions.put(sessionId, new LoginSessionData(clientRedirectUri, nonce.toString()));
        return openIdClient.createRedirectResponse(sessionId, nonce);
    }
    public static void parseQuery(String query, Map<String,
        Object> parameters) throws UnsupportedEncodingException {

        if (query != null) {
            String pairs[] = query.split("[&]");
            for (String pair : pairs) {
                String param[] = pair.split("[=]");
                String key = null;
                String value = null;
                if (param.length > 0) {
                    key = URLDecoder.decode(param[0],
                        System.getProperty("file.encoding"));
                }

                if (param.length > 1) {
                    value = URLDecoder.decode(param[1],
                        System.getProperty("file.encoding"));
                }

                if (parameters.containsKey(key)) {
                    Object obj = parameters.get(key);
                    if (obj instanceof List<?>) {
                        List<String> values = (List<String>) obj;
                        values.add(value);

                    } else if (obj instanceof String) {
                        List<String> values = new ArrayList<String>();
                        values.add((String) obj);
                        values.add(value);
                        parameters.put(key, values);
                    }
                } else {
                    parameters.put(key, value);
                }
            }
        }
    }
}
