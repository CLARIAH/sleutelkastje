package nl.knaw.huc.di.todo;

import com.sun.net.httpserver.HttpServer;
import org.apache.commons.lang3.StringUtils;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.QueryParam;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Path("/openid-connect")
public class Todo {
  private final Map<UUID, LoginSessionData> loginSessions;
  private final OpenIdClient openIdClient;

  public static void main(String[] args) throws IOException {
    System.out.println("Hello world!");
    int port = 9000;
    HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
    System.out.println("server started at " + port);
    // server.createContext("/", new RootHandler());
    // server.createContext("/echoHeader", new EchoHeaderHandler());
    // server.createContext("/echoGet", new EchoGetHandler());
    // server.createContext("/echoPost", new EchoPostHandler());
    server.setExecutor(null);
    server.start();
  }

  public Todo(OpenIdClient openIdClient) {
    this.openIdClient = openIdClient;
    loginSessions = new ConcurrentHashMap<>();
  }

  @GET
  @Path("/login")
  public String login(@QueryParam("redirect-uri") String clientRedirectUri) {
    if (StringUtils.isBlank(clientRedirectUri)) {
      return "status(400) - expected a query param redirect-uri";
    }

    UUID sessionId = UUID.randomUUID();
    UUID nonce = UUID.randomUUID();

    loginSessions.put(sessionId,null);
    return openIdClient.createRedirectResponse(sessionId, nonce);
  }

  // @GET
  // @Path("/callback")
  // public Response callback(@QueryParam("state") UUID loginSession, @QueryParam("code") String code) {
  //   if (!loginSessions.containsKey(loginSession)) {
  //     return Response.status(417).entity("Login session unknown").build();
  //   }
  //   return null;
  // }
    private record LoginSessionData(String userRedirectUri, String nonce) {
    }

}
