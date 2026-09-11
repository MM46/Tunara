package com.tunara.api.repository;

import com.tunara.api.entity.Song;
import com.tunara.api.entity.SongStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface SongRepository extends JpaRepository<Song, UUID> {

    Page<Song> findByUserIdOrderByCreatedAtDesc(
        UUID userId,
        Pageable pageable
    );

    List<Song> findByStatusOrderByCreatedAtAsc(SongStatus status);

    long countByUserId(UUID userId);
}