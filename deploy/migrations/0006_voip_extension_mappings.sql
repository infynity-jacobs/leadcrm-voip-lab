CREATE TABLE IF NOT EXISTS voip_extension_mappings (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(80) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    extension_number VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_voip_mapping_provider_user UNIQUE (provider, user_id),
    CONSTRAINT uq_voip_mapping_provider_extension UNIQUE (provider, extension_number)
);
CREATE INDEX IF NOT EXISTS ix_voip_extension_mappings_provider ON voip_extension_mappings(provider);
CREATE INDEX IF NOT EXISTS ix_voip_extension_mappings_user_id ON voip_extension_mappings(user_id);
