package nl.knaw.huc.di.sleutelkast;

import io.javalin.http.UnauthorizedResponse;
import nl.knaw.huc.di.todo.exceptions.SleutelkastUnreachableException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/**
 * SleutelkastClient - An object used for interacting with the Sleutelkast API.
 */
public class SleutelkastClient
{
    private String appName, authKey;

    private final URL endpoint;

    public SleutelkastClient(String appName, String authKey) throws MalformedURLException
    {
        this.appName = appName;
        this.authKey = authKey;
        endpoint = new URL("https://sleutelkast.sd.di.huc.knaw.nl/todo");
    }

    /**
     * Get user data from the api, using a provided API key.
     * @param apiKey The API key of the user to retrieve information for.
     * @return
     */
    public JSONObject getUserData(String apiKey)
    {
        String json;
        try {
            HttpURLConnection con = (HttpURLConnection) endpoint.openConnection();
            con.setRequestMethod("POST");
            String auth = appName + ":" + authKey;
            byte[] encodedAuth = Base64.getEncoder().encode(auth.getBytes(StandardCharsets.UTF_8));
            con.setRequestProperty("Authorization", "Basic " + new String(encodedAuth));
            con.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            con.setRequestProperty("Accept", "application/json");

            String urlParameters = "key=" + apiKey;
            byte[] postData = urlParameters.getBytes(StandardCharsets.UTF_8);
            int postDataLength = postData.length;
            con.setDoOutput(true);
            con.setRequestProperty("Content-Length", Integer.toString(postDataLength));

            try( DataOutputStream wr = new DataOutputStream( con.getOutputStream())) {
                wr.write( postData );
            }

            int responseCode = con.getResponseCode();

            if (400 <= responseCode && responseCode < 500) {
                throw new UnauthorizedResponse("Invalid API key");
            }

            try(BufferedReader in = new BufferedReader(
                    new InputStreamReader(con.getInputStream(), StandardCharsets.UTF_8))) {
                StringBuilder response = new StringBuilder();
                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine.trim());
                }
                json = response.toString();
            }
        } catch (IOException e) {
            throw new SleutelkastUnreachableException();
        }
        return new JSONObject(json);
    }
}
