package com.tunara.api.client;

import com.tunara.api.dto.AiGenerateSongRequest;
import com.tunara.api.dto.AiGenerateSongResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class TunaraAiClient {

    private final RestClient restClient;

    public TunaraAiClient(
        @Value("${tunara.ai.base-url}") String baseUrl
    ) {
        SimpleClientHttpRequestFactory requestFactory =
            new SimpleClientHttpRequestFactory();

        requestFactory.setConnectTimeout(10_000);
        requestFactory.setReadTimeout(30_000);

        this.restClient = RestClient.builder()
            .baseUrl(baseUrl)
            .requestFactory(requestFactory)
            .build();
    }

    public AiGenerateSongResponse generateSong(
        AiGenerateSongRequest request
    ) {
        return restClient
            .post()
            .uri("/api/generate")
            .header("Content-Type", "application/json")
            .body(request)
            .retrieve()
            .body(AiGenerateSongResponse.class);
    }
}