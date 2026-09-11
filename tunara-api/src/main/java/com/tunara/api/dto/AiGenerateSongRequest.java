package com.tunara.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.UUID;

public record AiGenerateSongRequest(
    @JsonProperty("song_id") UUID songId,
    String prompt,
    String genre,
    String voice,
    String language,
    @JsonProperty("duration_seconds") Integer durationSeconds
) {
}
