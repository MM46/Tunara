package com.tunara.api.client;

import com.tunara.api.dto.AiGenerateSongRequest;
import com.tunara.api.dto.AiGenerateSongResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import tools.jackson.databind.json.JsonMapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Component
public class TunaraAiClient {

    private final RestClient restClient;
    private final JsonMapper jsonMapper;

    public TunaraAiClient(
        @Value("${tunara.ai.base-url}") String baseUrl,
        JsonMapper jsonMapper
    ) {
        SimpleClientHttpRequestFactory requestFactory =
            new SimpleClientHttpRequestFactory();

        requestFactory.setConnectTimeout(10_000);
        requestFactory.setReadTimeout(900_000);

        this.restClient = RestClient.builder()
            .baseUrl(baseUrl)
            .requestFactory(requestFactory)
            .build();

        this.jsonMapper = jsonMapper;
    }

    public AiGenerateSongResponse generateSong(
        AiGenerateSongRequest request
    ) {
        return restClient
            .post()
            .uri("/api/generate")
            .contentType(MediaType.APPLICATION_JSON)
            .accept(MediaType.APPLICATION_JSON)
            .body(request)
            .exchange((httpRequest, httpResponse) -> {
                byte[] responseBody;

                try {
                    responseBody = httpResponse
                        .getBody()
                        .readAllBytes();
                } catch (IOException exception) {
                    throw new IllegalStateException(
                        "Unable to read the Tunara AI response",
                        exception
                    );
                }

                String rawResponse = new String(
                    responseBody,
                    StandardCharsets.UTF_8
                );

                if (httpResponse.getStatusCode().isError()) {
                    throw new IllegalStateException(
                        "Tunara AI returned HTTP "
                            + httpResponse.getStatusCode().value()
                            + ": "
                            + rawResponse
                    );
                }

                if (responseBody.length == 0) {
                    throw new IllegalStateException(
                        "Tunara AI returned an empty response"
                    );
                }

                try {
                    return jsonMapper.readValue(
                        responseBody,
                        AiGenerateSongResponse.class
                    );
                } catch (RuntimeException exception) {
                    throw new IllegalStateException(
                        "Unable to parse the Tunara AI response: "
                            + rawResponse,
                        exception
                    );
                }
            });
    }
}
