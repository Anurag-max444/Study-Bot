"""The single Supabase client instance, shared by every repository module.
Nothing else in the project should call create_client() — always import
`supabase` from here."""
from supabase import create_client, Client

import config

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
