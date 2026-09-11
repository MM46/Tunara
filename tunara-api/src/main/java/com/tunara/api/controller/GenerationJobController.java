package com.tunara.api.controller;

import com.tunara.api.dto.GenerationJobResponse;
import com.tunara.api.service.GenerationJobService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/generation-jobs")
public class GenerationJobController {

    private final GenerationJobService generationJobService;

    public GenerationJobController(GenerationJobService generationJobService) {
        this.generationJobService = generationJobService;
    }

    @GetMapping("/{generationJobId}")
    public ResponseEntity<GenerationJobResponse> getById(
        @PathVariable UUID generationJobId
    ) {
        return ResponseEntity.ok(generationJobService.getGenerationJobById(generationJobId));
    }

    @GetMapping("/song/{songId}")
    public ResponseEntity<GenerationJobResponse> getBySongId(@PathVariable UUID songId) {
        return ResponseEntity.ok(generationJobService.getGenerationJobBySongId(songId));
    }
}
