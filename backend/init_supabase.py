"""
Initialize Supabase table and add the first world.

Run this script once to set up the database:
    python init_supabase.py
"""
import os
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://casjsrxyujujmygemutg.supabase.co"
SUPABASE_KEY = "sb_publishable_9UnJsuOI58b4i670LZkghg_fefZ7Lgw"


def main():
    print("Connecting to Supabase...")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # The table should be created via Supabase dashboard with this SQL:
    # CREATE TABLE worlds (
    #     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    #     world_id TEXT,
    #     viewer_url TEXT NOT NULL,
    #     thumbnail_url TEXT,
    #     splat_urls JSONB,
    #     place_name TEXT,
    #     lat DOUBLE PRECISION,
    #     lng DOUBLE PRECISION,
    #     text_prompt TEXT,
    #     created_at TIMESTAMPTZ DEFAULT NOW()
    # );

    # Add the first world
    first_world = {
        "world_id": "a99f96c3-49b1-4362-9472-db709155d2ae",
        "viewer_url": "https://marble.worldlabs.ai/world/a99f96c3-49b1-4362-9472-db709155d2ae",
        "place_name": "First World",
    }

    print("Inserting first world...")
    try:
        result = client.table("worlds").insert(first_world).execute()
        print(f"Success! Inserted: {result.data}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you've created the 'worlds' table in Supabase first.")
        print("Go to Supabase Dashboard > SQL Editor and run:")
        print("""
CREATE TABLE IF NOT EXISTS worlds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id TEXT,
    viewer_url TEXT NOT NULL,
    thumbnail_url TEXT,
    splat_urls JSONB,
    place_name TEXT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    text_prompt TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
        """)


if __name__ == "__main__":
    main()
