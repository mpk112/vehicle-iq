#!/usr/bin/env python3
"""Quick test script to verify price prediction endpoint is registered."""

import sys
sys.path.insert(0, '.')

from app.main import app

# Check if price router is registered
print("Checking registered routes...")
print()

price_routes = [route for route in app.routes if '/price' in str(route.path)]

if price_routes:
    print("✓ Price prediction routes found:")
    for route in price_routes:
        print(f"  - {route.methods} {route.path}")
    print()
    print("SUCCESS: Price prediction API endpoint is registered!")
    sys.exit(0)
else:
    print("✗ No price prediction routes found")
    print()
    print("FAILURE: Price prediction API endpoint is NOT registered!")
    sys.exit(1)
