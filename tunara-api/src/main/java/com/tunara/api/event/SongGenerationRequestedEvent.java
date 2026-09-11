package com.tunara.api.event;

import java.util.UUID;

public record SongGenerationRequestedEvent(
    UUID songId,
    UUID generationJobId,
    String prompt,
    String genre,
    String voice,
    String language,
    Integer durationSeconds
) {
}
