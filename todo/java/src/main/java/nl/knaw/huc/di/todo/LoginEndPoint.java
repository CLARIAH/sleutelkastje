package nl.knaw.huc.di.todo;

import org.apache.commons.lang3.StringUtils;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Response;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Path("/openid-connect")
public class LoginEndPoint {
  private final Map<UUID, LoginSessionData> loginSessions;
  private final OpenIdClient openIdClient;

  public LoginEndPoint(OpenIdClient openIdClient) {
    this.openIdClient = openIdClient;
    loginSessions = new ConcurrentHashMap<>();
  }

  @GET
  @Path("/login")
  public Response login(@QueryParam("redirect-uri") String clientRedirectUri) {
    if (StringUtils.isBlank(clientRedirectUri)) {
      return Response.status(400).entity("expected a query param redirect-uri").build();
    }

    UUID sessionId = UUID.randomUUID();
    UUID nonce = UUID.randomUUID();

    loginSessions.put(sessionId,null);
    return openIdClient.createRedirectResponse(sessionId, nonce);
  }

  @GET
  @Path("/callback")
  public Response callback(@QueryParam("state") UUID loginSession, @QueryParam("code") String code) {
    if (!loginSessions.containsKey(loginSession)) {
      return Response.status(417).entity("Login session unknown").build();
    }
    return null;
  }
    private record LoginSessionData(String userRedirectUri, String nonce) {
    }

}
