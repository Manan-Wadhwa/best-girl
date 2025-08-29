import requests
import os
from pathlib import Path
import json
import time

# Character image URLs (using more reliable sources)
CHARACTER_IMAGES = {
    "Asuna Yuuki": "https://cdn.myanimelist.net/images/characters/4/275825.jpg",
    "C.C.": "https://cdn.myanimelist.net/images/characters/7/75332.jpg", 
    "Emilia": "https://cdn.myanimelist.net/images/characters/11/289717.jpg",
    "Erza Scarlet": "https://cdn.myanimelist.net/images/characters/11/52048.jpg",
    "Hinata Hyūga": "https://cdn.myanimelist.net/images/characters/16/81907.jpg",
    "Holo": "https://cdn.myanimelist.net/images/characters/5/17318.jpg",
    "Kurisu Makise": "https://cdn.myanimelist.net/images/characters/11/310711.jpg",
    "Mai Sakurajima": "https://cdn.myanimelist.net/images/characters/2/371669.jpg",
    "Maki Zenin": "https://cdn.myanimelist.net/images/characters/5/423533.jpg",
    "Marin Kitagawa": "https://cdn.myanimelist.net/images/characters/6/457127.jpg",
    "Mitsuri Kanroji": "https://cdn.myanimelist.net/images/characters/8/386902.jpg",
    "Nezuko Kamado": "https://cdn.myanimelist.net/images/characters/3/386910.jpg",
    "Nico Robin": "https://cdn.myanimelist.net/images/characters/9/310307.jpg",
    "Nobara Kugisaki": "https://cdn.myanimelist.net/images/characters/7/398043.jpg",
    "Power": "https://cdn.myanimelist.net/images/characters/13/425804.jpg",
    "Rem": "https://cdn.myanimelist.net/images/characters/5/299015.jpg",
    "Rias Gremory": "https://cdn.myanimelist.net/images/characters/2/310364.jpg",
    "Shinobu Kocho": "https://cdn.myanimelist.net/images/characters/8/378254.jpg",
    "Shinobu Oshino": "https://cdn.myanimelist.net/images/characters/5/310712.jpg",
    "Tohru": "https://cdn.myanimelist.net/images/characters/8/383335.jpg",
    "Tsunade": "https://cdn.myanimelist.net/images/characters/2/4960.jpg",
    "Yor Forger": "https://cdn.myanimelist.net/images/characters/3/457745.jpg",
    "Yoruichi Shihōin": "https://cdn.myanimelist.net/images/characters/8/75348.jpg",
    "Yukino Yukinoshita": "https://cdn.myanimelist.net/images/characters/2/280607.jpg",
    "Zero Two": "https://cdn.myanimelist.net/images/characters/7/357062.jpg"
}

def create_images_directory():
    """Create images directory if it doesn't exist"""
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    return images_dir

def download_image(url, filename, max_retries=3):
    """Download image from URL with retry logic"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"❌ URL doesn't point to an image: {url}")
                return False
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(filename)
            if file_size < 1024:  # Less than 1KB, probably an error
                os.remove(filename)
                print(f"❌ Downloaded file too small: {filename}")
                return False
                
            print(f"✅ Downloaded: {filename} ({file_size/1024:.1f}KB)")
            return True
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed for {filename}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            
    return False

def get_file_extension(url):
    """Get file extension from URL"""
    if '.jpg' in url.lower():
        return '.jpg'
    elif '.png' in url.lower():
        return '.png'
    elif '.jpeg' in url.lower():
        return '.jpeg'
    elif '.webp' in url.lower():
        return '.webp'
    else:
        return '.jpg'  # Default to jpg

def fetch_all_images():
    """Download all character images"""
    images_dir = create_images_directory()
    downloaded = []
    failed = []
    
    print("🎭 Starting character image download...")
    print("=" * 50)
    
    for character, url in CHARACTER_IMAGES.items():
        # Clean filename
        safe_name = "".join(c for c in character if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        extension = get_file_extension(url)
        filename = images_dir / f"{safe_name}{extension}"
        
        # Skip if already exists
        if filename.exists():
            print(f"⏭️  Already exists: {filename}")
            downloaded.append(str(filename))
            continue
        
        print(f"📥 Downloading {character}...")
        if download_image(url, filename):
            downloaded.append(str(filename))
        else:
            failed.append(character)
            print(f"💥 Failed to download: {character}")
        
        # Small delay to be nice to servers
        time.sleep(1)
    
    # Save download status
    status = {
        "downloaded": downloaded,
        "failed": failed,
        "total": len(CHARACTER_IMAGES),
        "success_count": len(downloaded),
        "timestamp": time.time()
    }
    
    with open(images_dir / "download_status.json", 'w') as f:
        json.dump(status, f, indent=2)
    
    print("\n" + "=" * 50)
    print(f"🎉 Download complete!")
    print(f"✅ Successfully downloaded: {len(downloaded)}/{len(CHARACTER_IMAGES)}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print("\n💥 Failed downloads:")
        for character in failed:
            print(f"   - {character}")
    
    print(f"\n📁 Images saved to: {images_dir.absolute()}")
    return status

def get_local_image_path(character_name):
    """Get local path for character image"""
    images_dir = Path("images")
    safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    
    # Try different extensions
    for ext in ['.jpg', '.png', '.jpeg', '.webp']:
        filename = images_dir / f"{safe_name}{ext}"
        if filename.exists():
            return str(filename)
    
    return None

if __name__ == "__main__":
    print("🎭 Character Image Fetcher")
    print("=" * 30)
    
    choice = input("Download all images? (y/n): ").lower().strip()
    if choice in ['y', 'yes']:
        fetch_all_images()
    else:
        print("Download cancelled.")
