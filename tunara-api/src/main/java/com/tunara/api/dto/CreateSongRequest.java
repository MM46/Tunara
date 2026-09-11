package com.tunara.api.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateSongRequest(

    @NotBlank(message = "Prompt is required")
    @Size(max = 2000, message = "Prompt cannot exceed 2000 characters")
    String prompt,

    @NotBlank(message = "Genre is required")
    @Size(max = 100, message = "Genre cannot exceed 100 characters")
    String genre,

    @NotBlank(message = "Voice is required")
    @Size(max = 100, message = "Voice cannot exceed 100 characters")
    String voice,

    @NotBlank(message = "Language is required")
    @Size(max = 50, message = "Language cannot exceed 50 characters")
    String language,

    @Min(value = 30, message = "Duration must be at least 30 seconds")
    @Max(value = 600, message = "Duration cannot exceed 600 seconds")
    Integer durationSeconds
) {
}