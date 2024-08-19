package nl.knaw.huc.di.openidconnect;

import com.nimbusds.oauth2.sdk.token.Tokens;
import io.javalin.http.Context;
import io.javalin.http.HttpStatus;
import nl.knaw.huc.di.todo.exceptions.InvalidTokenException;
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
    LOG.info("ctx:" + ctx.queryParamMap());
    String clientRedirectUri = "/todo"; //ctx.queryParam("redirect-uri");
    if (clientRedirectUri==null || clientRedirectUri.isEmpty()) {
      ctx.status(400).result("expected a query param redirect-uri");
      return;
    }

    UUID sessionId = UUID.randomUUID();
    UUID nonce = UUID.randomUUID();

    loginSessions.put(sessionId, new LoginSessionData(clientRedirectUri, nonce.toString()));
    String result = openIdClient.createRedirectResponse(sessionId, nonce);
    LOG.info("result: "+result);
    ctx.redirect(result, HttpStatus.TEMPORARY_REDIRECT);
    LOG.info("loginSessins.keySet: " + loginSessions.keySet());
    LOG.info("loginSessins.values: " + loginSessions.values());
  }

  public void callback(Context ctx) throws OpenIdConnectException, InvalidTokenException {
    LOG.info("ctx (callback):" + ctx.queryParamMap());
    UUID res = openIdClient.getState();
    LOG.info("uuid: "+res);
    UUID loginSession;
    try {
      loginSession = UUID.fromString(String.valueOf(ctx.queryParam("state")));
    } catch (IllegalArgumentException e) {
      LOG.warn("ctx param 'state' not found!");
      loginSession = res;
    }
    LOG.info("loginSession: "+loginSession);
    String code = ctx.queryParam("code");
    LOG.info("code: "+code);

    if (!loginSessions.containsKey(loginSession)) {
      ctx.status(400).result("Login session unknown");
      return;
    }

    try {
      final LoginSessionData loginSessionData = loginSessions.remove(loginSession);
      final Tokens userTokens = openIdClient.getUserTokens(code, loginSessionData.nonce());
      LOG.info("tokens:"+userTokens);

      String eppn = openIdClient.getUserEppn(userTokens.getBearerAccessToken().toString());
      ctx.sessionAttribute("eppn", eppn);

      final String userUri = loginSessionData.userRedirectUri();
      ctx.redirect(userUri, HttpStatus.TEMPORARY_REDIRECT);
    } catch (OpenIdConnectException | InvalidTokenException e) {
      LOG.error(e.getMessage(), e);
      throw e;
    }
  }

  private record LoginSessionData(String userRedirectUri, String nonce) {
  }
}
