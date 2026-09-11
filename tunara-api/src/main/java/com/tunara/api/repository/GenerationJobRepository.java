package com.tunara.api.repository;

import com.tunara.api.entity.GenerationJob;
import com.tunara.api.entity.GenerationJobStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface GenerationJobRepository
    extends JpaRepository<GenerationJob, UUID> {

    Optional<GenerationJob> findBySongId(UUID songId);

    List<GenerationJob> findByStatusOrderByCreatedAtAsc(
        GenerationJobStatus status
    );
}