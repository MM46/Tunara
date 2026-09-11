package com.tunara.api.dto;
import com.tunara.api.entity.SongStatus;
import java.time.OffsetDateTime; import java.util.UUID;
public record SongResponse(UUID id,String title,String prompt,String lyrics,String genre,String voice,String language,Integer durationSeconds,SongStatus status,String coverUrl,String mp3Url,String wavUrl,String midiUrl,String logicPackUrl,OffsetDateTime createdAt,OffsetDateTime updatedAt){}
