package nl.knaw.huc.di.todo.middleware;

import io.javalin.http.Context;
import io.javalin.http.InternalServerErrorResponse;
import io.javalin.http.UnauthorizedResponse;
import nl.knaw.huc.di.openidconnect.OpenIdClient;
import nl.knaw.huc.di.sleutelkast.SleutelkastClient;
import nl.knaw.huc.di.todo.Todo;
import nl.knaw.huc.di.todo.exceptions.InvalidTokenException;
import nl.knaw.huc.di.todo.exceptions.SleutelkastUnreachableException;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.MalformedURLException;
import java.net.URL;

public class Authentication
{
    static final Logger LOG = LoggerFactory.getLogger(Todo.class);

    OpenIdClient openIdClient;
    SleutelkastClient sleutelClient;

    public Authentication(OpenIdClient openIdClient, SleutelkastClient sleutelClient)
    {
        this.openIdClient = openIdClient;
        this.sleutelClient = sleutelClient;
    }

    /**
     * A "Before" handler for dealing with authentication.
     * Supports both Satosa and Sleutelkastje api keys, present in the Authentication header or in
     * the sessionToken request parameter.
     * @param ctx The Javalin Context
     */
    public void handleAuthentication(Context ctx)
    {
        String eppn;

        String sessionEppn = ctx.sessionAttribute("eppn");
        if (sessionEppn != null) {
            ctx.attribute("eppn", sessionEppn);
            return;
        }

        String accessToken = getAuthToken(ctx);

        try {
            eppn = getEppnFromToken(accessToken);
        } catch (InvalidTokenException e) {
            throw new UnauthorizedResponse("Unauthorized");
        } catch (MalformedURLException e) {
            throw new InternalServerErrorResponse("Invalid Sleutelkastje URL configuration");
        } catch (SleutelkastUnreachableException e) {
            throw new InternalServerErrorResponse("Sleutelkastje unreachable");
        }

        ctx.attribute("eppn", eppn);
    }

    /**
     * Get the authentication token from the header or request params.
     * @param ctx The Javalin Context
     * @return The authentication token.
     */
    private String getAuthToken(Context ctx)
    {
        String authParam = ctx.queryParam("sessionToken");
        String authHeader = ctx.header("Authorization");

        if (authParam != null) {
            return authParam;
        }
        if (authHeader == null) {
            LOG.info("Trying to connect without an Authorization header.");
            throw new UnauthorizedResponse("Unauthorized");
        }
        return authHeader.replace("Bearer ", "");
    }

    /**
     * Get the user eppn using a sleutelkast api key.
     * @param token The authentication token/api key
     * @return The eppn
     * @throws SleutelkastUnreachableException When we cannot reach the sleutelkast api.
     */
    private String getEppnHuc(String token) throws MalformedURLException, SleutelkastUnreachableException
    {
        // handle sleutelkastje
        LOG.info("Create URL object");
        URL url = new URL("https://sleutelkast.sd.di.huc.knaw.nl/todo");

        JSONObject obj = sleutelClient.getUserData(token);

        return obj.getJSONArray("eppn").getString(0);
    }

    /**
     * Get the EPPN of the user based on a Satosa authentication token.
     * @param token The authentication token.
     * @return The EPPN
     * @throws InvalidTokenException When the token is invalid and no EPPN can be found.
     */
    private String getEppnSatosa(String token) throws InvalidTokenException
    {
        return openIdClient.getUserEppn(token);
    }

    /**
     * Get the EPPN based on the authentication. Deals with both Sleutelkastje tokens and Satosa ones.
     * @param token The authentication token.
     * @return The EPPN of the user.
     * @throws InvalidTokenException When the token is invalid and authentication fails.
     * @throws MalformedURLException When the Sleutelkastje URL is misconfigured.
     */
    private String getEppnFromToken(String token) throws InvalidTokenException, MalformedURLException, SleutelkastUnreachableException
    {
        LOG.info("Trying to get eppn from token: {}", token);
        if (token.startsWith("huc:")) {
            LOG.info("Starts with huc, checking Sleutelkastje");
            return getEppnHuc(token);
        } else {
            LOG.info("Check Satosa");
            return getEppnSatosa(token);
        }
    }
}
