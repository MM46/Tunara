package com.tunara.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.UUID;

public record AiGenerateSongResponse(
    @JsonProperty("song_id") UUID songId,
    String status,
    Integer progress,
    String message,
    String title,
    String lyrics,
    @JsonProperty("wav_url") String wavUrl
) {
}
