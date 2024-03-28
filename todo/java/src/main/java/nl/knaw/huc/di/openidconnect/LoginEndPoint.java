package nl.knaw.huc.di.openidconnect;

import com.nimbusds.oauth2.sdk.token.Tokens;
import io.javalin.http.Context;
import io.javalin.http.HttpStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

// @Path("/openid-connect")
public class LoginEndPoint {
  public static final Logger LOG = LoggerFactory.getLogger(LoginEndPoint.class);
  private final Map<UUID, LoginSessionData> loginSessions;
  private final OpenIdClient openIdClient;

  public LoginEndPoint(OpenIdClient openIdClient) {
    this.openIdClient = openIdClient;
    loginSessions = new ConcurrentHashMap<>();
  }

  // @GET
  // @Path("/login")
  public void login(Context ctx){ //@QueryParam("redirect-uri") String clientRedirectUri) {
    String clientRedirectUri = ctx.queryParam("redirect-uri");
    if (clientRedirectUri.isEmpty()) {
      ctx.status(400).result("expected a query param redirect-uri");
      return;
    }

    UUID sessionId = UUID.randomUUID();
    UUID nonce = UUID.randomUUID();

    loginSessions.put(sessionId, new LoginSessionData(clientRedirectUri, nonce.toString()));
    String result = openIdClient.createRedirectResponse(sessionId, nonce);
    ctx.redirect(result, HttpStatus.TEMPORARY_REDIRECT);
  }

  public void callback(Context ctx) throws OpenIdConnectException {
    UUID loginSession = UUID.fromString(ctx.queryParam("state"));
    String code = ctx.queryParam("code");

    if (!loginSessions.containsKey(loginSession)) {
      ctx.status(417).result("Login session unknown");
      return;
    }

    try {
      final LoginSessionData loginSessionData = loginSessions.remove(loginSession);
      final Tokens userTokens = openIdClient.getUserTokens(code, loginSessionData.nonce());
      final String userUri = loginSessionData.userRedirectUri()
                                    + "?sessionToken=" + userTokens.getBearerAccessToken().getValue();
      ctx.redirect(userUri, HttpStatus.TEMPORARY_REDIRECT);
    } catch (OpenIdConnectException e) {
      LOG.error(e.getMessage(), e);
      throw e;
    }
  }

  private record LoginSessionData(String userRedirectUri, String nonce) {
  }
}
