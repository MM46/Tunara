package com.tunara.api.dto;

import com.tunara.api.entity.GenerationJobStatus;
import java.time.OffsetDateTime;
import java.util.UUID;

public record GenerationJobResponse(
    UUID id,
    UUID songId,
    GenerationJobStatus status,
    Integer progress,
    String errorMessage,
    OffsetDateTime startedAt,
    OffsetDateTime completedAt,
    OffsetDateTime createdAt
) {
}
