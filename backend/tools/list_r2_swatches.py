"""
List all swatch images from R2 bucket.

This script connects to your R2 bucket and lists all PNG files
in the ZEGNA 2025-26 folder, extracting the swatch codes.
"""

import boto3
from app.core.config import settings

def list_r2_swatches():
    """List all swatch files in R2 bucket."""

    # Create S3 client configured for R2
    s3_client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

    print(f"📦 Listing swatches from bucket: {settings.r2_bucket_name}")
    print(f"📁 Folder: ZEGNA 2025-26/\n")

    try:
        # List objects in the ZEGNA 2025-26 folder
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=settings.r2_bucket_name,
            Prefix="ZEGNA 2025-26/"
        )

        swatches = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    # Extract filename from path
                    if key.endswith('.png'):
                        filename = key.split('/')[-1]
                        swatch_code = filename.replace('.png', '')
                        swatches.append({
                            'code': swatch_code,
                            'filename': filename,
                            'key': key,
                            'size': obj['Size']
                        })

        # Sort by code
        swatches.sort(key=lambda x: x['code'])

        # Display results
        print(f"✅ Found {len(swatches)} swatch images:\n")
        print("=" * 80)

        for i, swatch in enumerate(swatches, 1):
            size_kb = swatch['size'] / 1024
            print(f"{i:3d}. {swatch['code']:<20} ({size_kb:>7.1f} KB)")

        print("=" * 80)

        # Save to file for reference
        output_file = "swatch_codes_list.txt"
        with open(output_file, 'w') as f:
            f.write("# List of all swatch codes from R2\n")
            f.write(f"# Total: {len(swatches)} swatches\n\n")
            for swatch in swatches:
                f.write(f"{swatch['code']}\n")

        print(f"\n💾 Swatch codes saved to: {output_file}")

        return swatches

    except Exception as e:
        print(f"❌ Error listing R2 bucket: {e}")
        return []


if __name__ == "__main__":
    print("🎨 R2 Swatch Lister\n")
    swatches = list_r2_swatches()

    if swatches:
        print(f"\n📊 Summary:")
        print(f"   Total swatches: {len(swatches)}")
        print(f"   First code: {swatches[0]['code']}")
        print(f"   Last code: {swatches[-1]['code']}")

    print("\n✨ Done!")
