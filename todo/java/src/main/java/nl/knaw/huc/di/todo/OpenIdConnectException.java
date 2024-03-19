package nl.knaw.huc.di.todo;

public class OpenIdConnectException extends Exception {
  public OpenIdConnectException(String message) {
    super(message);
  }

  public OpenIdConnectException(String message, Throwable cause) {
    super(message, cause);
  }
}
