package nl.knaw.huc.di.sleutelkast;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.javalin.http.UnauthorizedResponse;
import nl.knaw.huc.di.todo.dataclasses.UserData;
import nl.knaw.huc.di.todo.exceptions.SleutelkastUnreachableException;

import java.io.IOException;
import java.net.*;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

/**
 * SleutelkastClient - An object used for interacting with the Sleutelkast API.
 */
public class SleutelkastClient
{
    private final String appName, authKey;

    private final URI endpoint;

    public SleutelkastClient(String appName, String authKey) throws URISyntaxException
    {
        this.appName = appName;
        this.authKey = authKey;
        endpoint = new URI("https://sleutelkast.sd.di.huc.knaw.nl/todo");
    }

    /**
     * Get user data from the api, using a provided API key.
     * @param apiKey The API key of the user to retrieve information for.
     * @return A json object containing the retrieved user data.
     */
    public UserData getUserData(String apiKey)
    {
        HttpResponse<String> response;
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        String urlParameters = "key=" + apiKey;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(endpoint)
                .POST(HttpRequest.BodyPublishers.ofString(urlParameters))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .build();

        try (HttpClient client = HttpClient.newBuilder()
                .authenticator(getAuthenticator())
                .build()) {
            response = client.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException | InterruptedException e) {
            throw new SleutelkastUnreachableException();
        }

        if (response.statusCode() != 200) {
            throw new UnauthorizedResponse();
        }

        try {
            return objectMapper.readValue(response.body(), UserData.class);
        } catch (JsonProcessingException e) {
            throw new SleutelkastUnreachableException();
        }
    }

    /**
     * Get basic auth authenticator for the request.
     * @return The authenticator
     */
    private Authenticator getAuthenticator()
    {
        return new Authenticator() {
            @Override
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication(appName, authKey.toCharArray());
            }
        };
    }
}
