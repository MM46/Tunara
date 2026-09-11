package com.tunara.api.service;

import com.tunara.api.dto.GenerationJobResponse;
import com.tunara.api.entity.GenerationJob;
import com.tunara.api.exception.ResourceNotFoundException;
import com.tunara.api.repository.GenerationJobRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class GenerationJobService {

    private final GenerationJobRepository generationJobRepository;

    public GenerationJobService(GenerationJobRepository generationJobRepository) {
        this.generationJobRepository = generationJobRepository;
    }

    @Transactional(readOnly = true)
    public GenerationJobResponse getGenerationJobById(UUID generationJobId) {
        GenerationJob job = generationJobRepository.findById(generationJobId)
            .orElseThrow(() -> new ResourceNotFoundException(
                "Generation job not found: " + generationJobId
            ));
        return toResponse(job);
    }

    @Transactional(readOnly = true)
    public GenerationJobResponse getGenerationJobBySongId(UUID songId) {
        GenerationJob job = generationJobRepository.findBySongId(songId)
            .orElseThrow(() -> new ResourceNotFoundException(
                "Generation job not found for song: " + songId
            ));
        return toResponse(job);
    }

    private GenerationJobResponse toResponse(GenerationJob job) {
        return new GenerationJobResponse(
            job.getId(), job.getSong().getId(), job.getStatus(), job.getProgress(),
            job.getErrorMessage(), job.getStartedAt(), job.getCompletedAt(), job.getCreatedAt()
        );
    }
}
