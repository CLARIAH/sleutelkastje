package nl.knaw.huc.di.todo;

import io.javalin.Javalin;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import java.io.IOException;

@Path("/openid-connect")
public class Todo {
  // private final Map<UUID, LoginSessionData> loginSessions;
  // private final OpenIdClient openIdClient;

    public Todo() {
      // openIdClient = null;
      // loginSessions = null;
      var app = Javalin.create(/*config*/)
                       .get("/", ctx -> ctx.result("Hello World"))
                       .start(9000);
      // app.get("/todo", ctx -> { // runs on a different server than serverOneApp
      //   String string = ctx.cookieStore().get("string");
      //   int i = ctx.cookieStore().get("i");
      //   List<String> list = ctx.cookieStore().get("list");
      // });
    }

    public static void main(String[] args) throws IOException {
    System.out.println("Hello world!");
    new Todo();
  }

  // @GET
  // @Path("/todo")
  // public String todo(OpenIdClient openIdClient) {
  //   System.out.println("todo");
  //   UUID sessionId = UUID.randomUUID();
  //   UUID nonce = UUID.randomUUID();
  //   loginSessions.put(sessionId,null);
  //   String result = openIdClient.createRedirectResponse(sessionId, nonce);
  //   System.out.println(result);
  //   return result;
  // }

  @GET
  @Path("/")
  public String donothing() {
    String result = "do nothing";
    System.out.println(result);
    return result;
  }

  // @GET
  // @Path("/login")
  // public String login(@QueryParam("redirect-uri") String clientRedirectUri) {
  //   System.out.println("login");
  //   if (StringUtils.isBlank(clientRedirectUri)) {
  //     System.out.println("status(400) - expected a query param redirect-uri");
  //     return "status(400) - expected a query param redirect-uri";
  //   }
  //
  //   UUID sessionId = UUID.randomUUID();
  //   UUID nonce = UUID.randomUUID();
  //
  //   loginSessions.put(sessionId,null);
  //   return openIdClient.createRedirectResponse(sessionId, nonce);
  // }

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

// public class HelloWorld {
//   public static void main(String[] args) {
//     var app = Javalin.create(/*config*/)
//                      .get("/", ctx -> ctx.result("Hello World"))
// //                      .start(7070);
// //   }
// }