"""Generate sample images for testing VehicleIQ."""

from PIL import Image, ImageDraw, ImageFont
import random
from pathlib import Path


def generate_odometer_image(reading: int, output_path: str):
    """Generate synthetic odometer image with reading."""
    img = Image.new('RGB', (800, 600), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    
    # Draw odometer display background
    draw.rectangle([150, 200, 650, 400], fill=(40, 40, 40), outline=(100, 100, 100), width=3)
    
    # Draw reading
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    reading_text = f"{reading:06d}"
    draw.text((200, 250), reading_text, fill=(255, 200, 0), font=font)
    
    # Add "KM" label
    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
    except:
        small_font = ImageFont.load_default()
    draw.text((550, 320), "KM", fill=(200, 200, 200), font=small_font)
    
    # Add some noise for realism
    for _ in range(200):
        x, y = random.randint(0, 800), random.randint(0, 600)
        color = random.randint(0, 50)
        draw.point((x, y), fill=(color, color, color))
    
    img.save(output_path)
    print(f"✅ Generated odometer image: {output_path}")


def generate_vin_plate_image(vin: str, output_path: str):
    """Generate synthetic VIN plate image."""
    img = Image.new('RGB', (1000, 300), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    
    # Draw plate background
    draw.rectangle([50, 50, 950, 250], fill=(220, 220, 220), outline=(100, 100, 100), width=5)
    
    # Draw VIN
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 120), vin, fill=(0, 0, 0), font=font)
    
    # Add label
    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
    except:
        small_font = ImageFont.load_default()
    draw.text((100, 70), "VEHICLE IDENTIFICATION NUMBER", fill=(80, 80, 80), font=small_font)
    
    img.save(output_path)
    print(f"✅ Generated VIN plate image: {output_path}")


def generate_registration_image(reg_number: str, owner_name: str, output_path: str):
    """Generate synthetic registration document image."""
    img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([50, 50, 1150, 750], outline=(0, 0, 0), width=3)
    
    # Title
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 48)
        label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)
        value_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
    except:
        title_font = label_font = value_font = ImageFont.load_default()
    
    draw.text((400, 100), "REGISTRATION CERTIFICATE", fill=(0, 0, 0), font=title_font)
    
    # Registration number
    draw.text((100, 250), "Registration No:", fill=(80, 80, 80), font=label_font)
    draw.text((500, 250), reg_number, fill=(0, 0, 0), font=value_font)
    
    # Owner name
    draw.text((100, 350), "Owner Name:", fill=(80, 80, 80), font=label_font)
    draw.text((500, 350), owner_name, fill=(0, 0, 0), font=value_font)
    
    # Registration date
    draw.text((100, 450), "Registration Date:", fill=(80, 80, 80), font=label_font)
    draw.text((500, 450), "15/03/2020", fill=(0, 0, 0), font=value_font)
    
    img.save(output_path)
    print(f"✅ Generated registration image: {output_path}")


def generate_placeholder_image(angle: str, output_path: str):
    """Generate placeholder image for other angles."""
    img = Image.new('RGB', (1024, 768), color=(100, 100, 120))
    draw = ImageDraw.Draw(img)
    
    # Draw placeholder text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    text = f"Vehicle Photo\n{angle.replace('_', ' ').title()}"
    
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1024 - text_width) // 2
    y = (768 - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font, align='center')
    
    # Add border
    draw.rectangle([10, 10, 1014, 758], outline=(200, 200, 200), width=5)
    
    img.save(output_path)
    print(f"✅ Generated placeholder image: {output_path}")


def generate_all_sample_images():
    """Generate all sample images for testing."""
    print("🖼️  Generating sample images for VehicleIQ...")
    print("=" * 60)
    
    # Create storage directory
    storage_path = Path("backend/storage/samples")
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Generate odometer images (various readings)
    for reading in [15000, 45000, 75000, 120000]:
        generate_odometer_image(reading, str(storage_path / f"odometer_{reading}.jpg"))
    
    # Generate VIN plate images
    vins = [
        "1HGBH41JXMN109186",
        "2HGFG12648H542890",
        "3VWFE21C04M000001"
    ]
    for i, vin in enumerate(vins):
        generate_vin_plate_image(vin, str(storage_path / f"vin_plate_{i+1}.jpg"))
    
    # Generate registration images
    registrations = [
        ("DL01AB1234", "Rajesh Kumar"),
        ("MH02CD5678", "Priya Sharma"),
        ("KA03EF9012", "Amit Patel")
    ]
    for i, (reg, owner) in enumerate(registrations):
        generate_registration_image(reg, owner, str(storage_path / f"registration_{i+1}.jpg"))
    
    # Generate placeholder images for other angles
    angles = [
        "front", "rear", "left_side", "right_side",
        "front_left_diagonal", "front_right_diagonal",
        "rear_left_diagonal", "rear_right_diagonal",
        "interior_dashboard"
    ]
    for angle in angles:
        generate_placeholder_image(angle, str(storage_path / f"{angle}.jpg"))
    
    print("=" * 60)
    print("✅ Sample image generation completed!")
    print(f"📁 Images saved to: {storage_path}")
    print("\n📊 Generated:")
    print("  - 4 odometer images (various readings)")
    print("  - 3 VIN plate images")
    print("  - 3 registration document images")
    print("  - 9 placeholder images (vehicle angles)")
    print("\n💡 These images can be used for:")
    print("  - Testing photo upload API")
    print("  - Testing quality gate validation")
    print("  - Testing OCR extraction")
    print("  - Demo purposes")


if __name__ == "__main__":
    generate_all_sample_images()
