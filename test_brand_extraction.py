#!/usr/bin/env python3
"""
Simple test script for brand and product name extraction
"""

import re

def extract_brand_and_product(content):
    """
    Extract brand and product name from document content using regex patterns.
    """
    result = {}

    # Common patterns for brand identification
    brand_patterns = [
        r"Brand:\s*([A-Za-z0-9\s&.-]+)",
        r"Brand Name:\s*([A-Za-z0-9\s&.-]+)",
        r"Company:\s*([A-Za-z0-9\s&.-]+)",
        r"Client:\s*([A-Za-z0-9\s&.-]+)",
        r"(?:^|\n)\s*([A-Z][A-Za-z0-9\s&.-]{1,30})\s+(?:Brand|Company|Corp|Inc|Ltd)",
    ]

    # Common patterns for product identification
    product_patterns = [
        r"Product:\s*([A-Za-z0-9\s&.-]+)",
        r"Product Name:\s*([A-Za-z0-9\s&.-]+)",
        r"Product Title:\s*([A-Za-z0-9\s&.-]+)",
        r"Item:\s*([A-Za-z0-9\s&.-]+)",
        r"Model:\s*([A-Za-z0-9\s&.-]+)",
    ]

    # Extract brand
    for pattern in brand_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            result['brand'] = match.group(1).strip()
            break

    # Extract product name
    for pattern in product_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            result['product_name'] = match.group(1).strip()
            break

    return result

# Test cases
test_documents = [
    """
    Product Brief

    Brand: Adidas
    Product: Moonwalkers Smart Shoes

    Campaign message: Step into the future with our revolutionary smart footwear
    """,

    """
    Marketing Brief

    Company: Nike
    Product Name: Air Max Revolution

    Target demographics: Athletes aged 18-35
    """,

    """
    Brand Brief

    Client: Apple Inc
    Item: iPhone 15 Pro Max

    Launch strategy for Q4 2024
    """
]

print("Testing brand and product name extraction:\n")

for i, doc in enumerate(test_documents, 1):
    print(f"Test Document {i}:")
    print("=" * 40)
    result = extract_brand_and_product(doc)
    print(f"Brand: {result.get('brand', 'Not found')}")
    print(f"Product: {result.get('product_name', 'Not found')}")
    print()