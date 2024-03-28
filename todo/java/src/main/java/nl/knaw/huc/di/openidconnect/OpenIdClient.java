package nl.knaw.huc.di.openidconnect;


import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.proc.BadJOSEException;
import com.nimbusds.oauth2.sdk.AuthorizationCode;
import com.nimbusds.oauth2.sdk.AuthorizationCodeGrant;
import com.nimbusds.oauth2.sdk.ParseException;
import com.nimbusds.oauth2.sdk.TokenRequest;
import com.nimbusds.oauth2.sdk.TokenResponse;
import com.nimbusds.oauth2.sdk.auth.ClientAuthentication;
import com.nimbusds.oauth2.sdk.auth.ClientSecretBasic;
import com.nimbusds.oauth2.sdk.auth.Secret;
import com.nimbusds.oauth2.sdk.id.ClientID;
import com.nimbusds.oauth2.sdk.id.Issuer;
import com.nimbusds.oauth2.sdk.token.BearerAccessToken;
import com.nimbusds.oauth2.sdk.token.Tokens;
import com.nimbusds.openid.connect.sdk.Nonce;
import com.nimbusds.openid.connect.sdk.OIDCTokenResponseParser;
import com.nimbusds.openid.connect.sdk.UserInfoRequest;
import com.nimbusds.openid.connect.sdk.UserInfoResponse;
import com.nimbusds.openid.connect.sdk.claims.UserInfo;
import com.nimbusds.openid.connect.sdk.op.OIDCProviderConfigurationRequest;
import com.nimbusds.openid.connect.sdk.op.OIDCProviderMetadata;
import com.nimbusds.openid.connect.sdk.validators.IDTokenValidator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.UUID;

public class OpenIdClient {
  public static final Logger LOG = LoggerFactory.getLogger(OpenIdClient.class);

  private final OIDCProviderMetadata metadata;
  private final URI redirectUrl;
  private final String clientId;
  private final String clientSecret;
  private final String scope;
  private final String claims;

  public OpenIdClient(String discoveryUrl,
                      String clientId,
                      String clientSecret,
                      String scope,
                      String claims,
                      String baseUri) throws OpenIdConnectException {
    try {
      final Issuer issuer = new Issuer(discoveryUrl);
      final OIDCProviderConfigurationRequest configurationRequest = new OIDCProviderConfigurationRequest(issuer);

      this.metadata = OIDCProviderMetadata.parse(configurationRequest.toHTTPRequest().send().getBodyAsJSONObject());
      this.redirectUrl = new URI(baseUri + "/callback");
      this.clientId = clientId;
      this.clientSecret = clientSecret;
      this.scope = scope;
      this.claims = claims;
    } catch (IOException | ParseException e) {
      throw new OpenIdConnectException("Couldn't read metadata from OIDC provider!");
    } catch (URISyntaxException e) {
        throw new RuntimeException(e);
    }
  }

  public Optional<UserInfo> getUserInfo(String accessToken) throws IOException, ParseException, URISyntaxException {
    final URI userInfoUri =  metadata.getUserInfoEndpointURI();
    final UserInfoRequest userInfoRequest = new UserInfoRequest(userInfoUri, new BearerAccessToken(accessToken));
    final UserInfoResponse userInfoResponse = UserInfoResponse.parse(userInfoRequest.toHTTPRequest().send());

    if (userInfoResponse.indicatesSuccess()) {
      return Optional.of(userInfoResponse.toSuccessResponse().getUserInfo());
    } else {
      LOG.warn("User info request failed: {}", userInfoResponse.toErrorResponse().getErrorObject());
      return Optional.empty();
    }
  }

  public String createRedirectResponse(UUID sessionId, UUID nonce) {
    final String openIdServer = metadata.getAuthorizationEndpointURI()
                                       + "?response_type=code"
                                       +"&client_id="+clientId
                                       +"redirect_uri="+redirectUrl
                                       +"scope="+scope
                                       +"claims="+ URLEncoder.encode(claims, StandardCharsets.UTF_8)
                                       +"state="+sessionId
                                       +"nonce="+nonce;
    return openIdServer;
    // return Response.temporaryRedirect(openIdServer).build();
  }

  public Tokens getUserTokens(String code, String nonce) throws OpenIdConnectException {
    try {
      final IDTokenValidator validator = new IDTokenValidator(metadata.getIssuer(), new ClientID(clientId),
          metadata.getIDTokenJWSAlgs().get(0), metadata.getJWKSetURI().toURL());
      final ClientAuthentication basicAuth = new ClientSecretBasic(new ClientID(clientId), new Secret(clientSecret));
      final URI redirectUri = redirectUrl;
      final AuthorizationCodeGrant authzGrant = new AuthorizationCodeGrant(new AuthorizationCode(code), redirectUri);
      final TokenRequest tokenRequest = new TokenRequest(metadata.getTokenEndpointURI(), basicAuth, authzGrant);
      final TokenResponse response = OIDCTokenResponseParser.parse(tokenRequest.toHTTPRequest().send());

      if (response.indicatesSuccess()) {
        final Tokens tokens = response.toSuccessResponse().getTokens();
        validator.validate(tokens.toOIDCTokens().getIDToken(), new Nonce(nonce));
        return tokens;
      } else {
        throw new OpenIdConnectException("Could not retrieve client token: " +
            response.toErrorResponse().getErrorObject());
      }
    } catch (ParseException | IOException | BadJOSEException | JOSEException e) {
      throw new OpenIdConnectException("Retrieval of tokens failed!", e);
    }
  }
}
