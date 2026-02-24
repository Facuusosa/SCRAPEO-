
import requests
import json
import re

# Since mapping categories is hard, we will rely on SEARCH for specific keywords (which user likely wants anyway)
# OR we can iterate through known slugs using the inline list approach I tried earlier but it failed with 'NoneType'.
# Wait! verify_inline.py failed with "NoneType object is not subscriptable" inside Python, likely because response.json()
# returned None or 'data' was None.
# BUT, the first call with ["celulares-y-telefonos", "celulares-liberados"] SUCCEEDED with Total: 0.
# Total 0 means valid query but no results found for those "IDs".
# This confirms "categories" filter expects the internal IDs (like 5a30...), NOT the slugs.

# PLAN B: Use the Search query (keywords) but pass the slug as keyword?
# Or query "samsung" and filter results by category? No, too broad.

# PLAN C: Reverse engineer how the frontend gets products for /l/celulares/
# It MUST make an API call.
# In `next_data.json` analysis I saw:
# items({"filtering":{"active":true,"availableStock":{"includeThousands":true},"category":{"id":["celulares-y-telefonos","celulares-liberados"]},"tags":[]}})
# Wait! `category` field inside filtering!
# introspection showed `categories` (plural) as [String].
# But `next_data.json` shows `category` (singular) with `id` list inside?
# Let's check `ItemFilteringInput` introspection again.
# schema_details.json:
# "categories": { "kind": "LIST", "ofType": "NON_NULL" -> "String" }
# "brands": ...
# No "category" singular field in `ItemFilteringInput`!
# BUT `next_data.json` has `category: { id: ... }`.
# Maybe `ItemFilteringInput` has a field `category` that I missed or introspection didn't show because of depth?
# Or `categories` argument in `items` query is OLD?
# Wait, let's look at schema_details.json again.
# Fields: ids, skus, keywords, brands, categories, collections, sellers, attributes...
# It DOES NOT show `category`.
# However, next_data shows:
# `items(filtering: { ..., category: { id: [...] } })`
# This contradictory!
# Maybe `categories` is the name of the argument in the API but it processes it differently?
# Or maybe the type `ItemFilteringInput` has dynamic fields? No.
# Maybe I am looking at the wrong Input Type? `items` uses `filtering: ItemFilteringInput`.
# Let's try to trust `next_data.json` structure and try to constructing a query that matches what the FRONTEND sends precisely, 
# even if introspection seems to say otherwise (maybe I missed a type extension).

# The Frontend sends:
# filtering: {
#   active: true,
#   category: { id: ["slug"] }  <-- TRICKY PART
# }

# But my introspection said `categories` is a List of Strings.
# Maybe `categories` IS the field but it accepts slugs?
# I tried `categories: ["slug"]` and got 0 results.
# Maybe I need to use `category` as a field name?
# Let's try to query with `category` field despite introspection not showing it explicitly (or maybe I missed it).
# Wait, if introspection didn't show it, GraphQL validation should fail if I use it.
# UNLESS `ItemFilteringInput` has a field that I missed?
# Let's try running a query with `category` field.

query_magic = """
query ProductListing {
  items(
    filtering: {
      category: {
        id: ["celulares-y-telefonos", "celulares-liberados"]
      },
      active: true
    }
  ) {
    total
    results { title }
  }
}
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://www.fravega.com/"
}

def verify_magic_query():
    print("Testing 'category' field (Magic Query)...")
    try:
        response = requests.post("https://www.fravega.com/api/v1", json={'query': query_magic}, headers=HEADERS)
        print(response.text[:500])
        # If this works, we found the hidden door.
    except Exception as e:
        print(e)

if __name__ == "__main__":
    verify_magic_query()
