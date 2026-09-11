CREATE TABLE app_user (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE song (
    id UUID PRIMARY KEY,
    user_id UUID,
    title VARCHAR(255) NOT NULL,
    prompt TEXT NOT NULL,
    lyrics TEXT,
    genre VARCHAR(100),
    voice VARCHAR(100),
    language VARCHAR(50),
    duration_seconds INTEGER,
    status VARCHAR(50) NOT NULL,
    cover_url TEXT,
    mp3_url TEXT,
    wav_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_song_user
        FOREIGN KEY (user_id)
        REFERENCES app_user(id)
);

CREATE TABLE generation_job (
    id UUID PRIMARY KEY,
    song_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_generation_job_song
        FOREIGN KEY (song_id)
        REFERENCES song(id)
        ON DELETE CASCADE,
    CONSTRAINT chk_generation_job_progress
        CHECK (progress >= 0 AND progress <= 100)
);

CREATE INDEX idx_song_user_id ON song(user_id);
CREATE INDEX idx_song_status ON song(status);
CREATE INDEX idx_generation_job_song_id ON generation_job(song_id);
CREATE INDEX idx_generation_job_status ON generation_job(status);
