#!/usr/bin/env python3

import os
import glob
import subprocess
import sys
from datetime import datetime

# 🌻 UKRAINIAN FLOWER HAT GIRL - GALLERY MANAGER 🌻
print("\n🌻 UKRAINIAN FLOWER HAT GIRL - GALLERY MANAGER 🌻")
print("=" * 70)

OUTPUT_DIR = "ComfyUI/output"

def get_collection_stats():
    """Get statistics about the image collection"""
    patterns = {
        "Base Images (1024x1024)": "ukrainian_flower_base_*.png",
        "Fashion Collection (1536x1536)": "ukrainian_flower_fashion_*.png",
        "Efficient Collection (1280x1280)": "ukrainian_flower_efficient_*.png",
        "High-Res (2048x2048)": "ukrainian_flower_hires_*.png",
        "4x Upscaled (4096x4096)": "ukrainian_flower_4x_*.png",
        "Face Enhanced": "ukrainian_flower_enhanced_*.png",
        "Final Combined": "ukrainian_flower_final_*.png"
    }
    
    stats = {}
    total_size = 0
    total_files = 0
    
    print("📊 COLLECTION STATISTICS")
    print("=" * 40)
    
    for category, pattern in patterns.items():
        files = glob.glob(f"{OUTPUT_DIR}/{pattern}")
        count = len(files)
        
        if count > 0:
            # Calculate total size
            category_size = sum(os.path.getsize(f) for f in files) / (1024*1024)  # MB
            total_size += category_size
            total_files += count
            
            latest_file = max(files, key=os.path.getmtime) if files else None
            latest_time = datetime.fromtimestamp(os.path.getmtime(latest_file)).strftime("%H:%M:%S") if latest_file else "N/A"
            
            print(f"📸 {category}: {count} images ({category_size:.1f}MB) - Latest: {latest_time}")
            stats[category] = {"count": count, "size": category_size, "files": files}
        else:
            print(f"📸 {category}: 0 images")
            stats[category] = {"count": 0, "size": 0, "files": []}
    
    print("=" * 40)
    print(f"📊 TOTAL: {total_files} images, {total_size:.1f}MB")
    print()
    
    return stats

def view_category(category_files, category_name):
    """View images from a specific category using feh"""
    if not category_files:
        print(f"❌ No images found in {category_name}")
        return
    
    # Sort by modification time (newest first)
    category_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"👀 Opening {len(category_files)} images from {category_name} in feh...")
    
    try:
        # Open all images in feh slideshow mode
        subprocess.run(["feh", "-F", "-Z", "-D", "3"] + category_files)
    except FileNotFoundError:
        print("❌ feh not installed! Install with: sudo apt install feh")
    except KeyboardInterrupt:
        print("✅ Gallery viewing cancelled")

def view_latest(count=10):
    """View the latest N images from any category"""
    all_patterns = [
        "ukrainian_flower_base_*.png",
        "ukrainian_flower_fashion_*.png",
        "ukrainian_flower_efficient_*.png",
        "ukrainian_flower_hires_*.png",
        "ukrainian_flower_4x_*.png", 
        "ukrainian_flower_enhanced_*.png",
        "ukrainian_flower_final_*.png"
    ]
    
    all_files = []
    for pattern in all_patterns:
        files = glob.glob(f"{OUTPUT_DIR}/{pattern}")
        all_files.extend(files)
    
    if not all_files:
        print("❌ No Ukrainian flower hat girl images found!")
        return
    
    # Sort by modification time (newest first)
    all_files.sort(key=os.path.getmtime, reverse=True)
    latest_files = all_files[:count]
    
    print(f"👀 Opening latest {len(latest_files)} images in feh...")
    print("📁 Latest files:")
    for i, f in enumerate(latest_files, 1):
        file_size = os.path.getsize(f) / (1024*1024)  # MB
        timestamp = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%H:%M:%S")
        print(f"   {i}. {os.path.basename(f)} ({file_size:.1f}MB) - {timestamp}")
    
    try:
        subprocess.run(["feh", "-F", "-Z", "-D", "3"] + latest_files)
    except FileNotFoundError:
        print("❌ feh not installed! Install with: sudo apt install feh")
    except KeyboardInterrupt:
        print("✅ Gallery viewing cancelled")

def compare_versions():
    """Compare the same image across different processing stages"""
    base_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_base_*.png")
    
    if not base_files:
        print("❌ No base images found to compare!")
        return
    
    print("🔍 COMPARING PROCESSING STAGES")
    print("=" * 40)
    
    # Get the latest base image
    latest_base = max(base_files, key=os.path.getmtime)
    base_name = os.path.basename(latest_base)
    base_number = base_name.split('_')[-1].replace('.png', '_')
    
    print(f"📸 Using base image: {base_name}")
    
    # Find corresponding processed versions
    versions = {
        "Base (1024x1024)": latest_base
    }
    
    # Look for 4x upscaled version
    upscaled_pattern = f"{OUTPUT_DIR}/ukrainian_flower_4x_{base_number}*.png"
    upscaled_files = glob.glob(upscaled_pattern)
    if upscaled_files:
        versions["4x Upscaled (4096x4096)"] = max(upscaled_files, key=os.path.getmtime)
    
    # Look for enhanced version
    enhanced_pattern = f"{OUTPUT_DIR}/ukrainian_flower_enhanced_{base_number}*.png"
    enhanced_files = glob.glob(enhanced_pattern)
    if enhanced_files:
        versions["Face Enhanced"] = max(enhanced_files, key=os.path.getmtime)
    
    # Look for final version
    final_pattern = f"{OUTPUT_DIR}/ukrainian_flower_final_{base_number}*.png"
    final_files = glob.glob(final_pattern)
    if final_files:
        versions["Final Combined"] = max(final_files, key=os.path.getmtime)
    
    print(f"🎯 Found {len(versions)} processing stages to compare:")
    comparison_files = []
    
    for stage, filepath in versions.items():
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / (1024*1024)  # MB
            print(f"   • {stage}: {os.path.basename(filepath)} ({file_size:.1f}MB)")
            comparison_files.append(filepath)
    
    if len(comparison_files) > 1:
        print(f"\n👀 Opening {len(comparison_files)} versions for comparison in feh...")
        try:
            subprocess.run(["feh", "-F", "-Z"] + comparison_files)
        except FileNotFoundError:
            print("❌ feh not installed! Install with: sudo apt install feh")
        except KeyboardInterrupt:
            print("✅ Comparison viewing cancelled")
    else:
        print("❌ Need at least 2 processing stages to compare!")

def interactive_menu():
    """Interactive menu for gallery management"""
    while True:
        print("\n🌻 UKRAINIAN FLOWER HAT GIRL GALLERY MENU")
        print("=" * 50)
        print("1. 📊 Show Collection Statistics")
        print("2. 👀 View Latest Images (10)")
        print("3. 📸 View Base Images (1024x1024)")
        print("4. 👗 View Fashion Collection (1536x1536)")
        print("5. ⚡ View Efficient Collection (1280x1280)")
        print("6. 🚀 View High-Res Images (2048x2048)")
        print("7. 🔍 Compare Processing Stages")
        print("8. 🌻 View ALL Images (Slideshow)")
        print("9. ❌ Exit")
        
        choice = input("\n🎯 Choose option (1-9): ").strip()
        
        if choice == "1":
            get_collection_stats()
            
        elif choice == "2":
            view_latest(10)
            
        elif choice == "3":
            stats = get_collection_stats()
            view_category(stats["Base Images (1024x1024)"]["files"], "Base Images")
            
        elif choice == "4":
            stats = get_collection_stats()
            view_category(stats["Fashion Collection (1536x1536)"]["files"], "Fashion Collection")
            
        elif choice == "5":
            stats = get_collection_stats()
            view_category(stats["Efficient Collection (1280x1280)"]["files"], "Efficient Collection")
            
        elif choice == "6":
            stats = get_collection_stats()
            view_category(stats["High-Res (2048x2048)"]["files"], "High-Res Images")
            
        elif choice == "7":
            compare_versions()
            
        elif choice == "8":
            # View ALL images
            all_patterns = [
                "ukrainian_flower_base_*.png",
                "ukrainian_flower_fashion_*.png",
                "ukrainian_flower_efficient_*.png",
                "ukrainian_flower_hires_*.png",
                "ukrainian_flower_4x_*.png",
                "ukrainian_flower_enhanced_*.png", 
                "ukrainian_flower_final_*.png"
            ]
            
            all_files = []
            for pattern in all_patterns:
                files = glob.glob(f"{OUTPUT_DIR}/{pattern}")
                all_files.extend(files)
            
            if all_files:
                all_files.sort(key=os.path.getmtime, reverse=True)
                print(f"👀 Opening ALL {len(all_files)} Ukrainian flower hat girl images...")
                try:
                    subprocess.run(["feh", "-F", "-Z", "-D", "4"] + all_files)
                except FileNotFoundError:
                    print("❌ feh not installed! Install with: sudo apt install feh")
                except KeyboardInterrupt:
                    print("✅ Slideshow cancelled")
            else:
                print("❌ No images found!")
                
        elif choice == "9":
            print("🌻 Thank you for viewing your Ukrainian flower hat girl collection!")
            break
            
        else:
            print("❌ Invalid choice! Please enter 1-9.")

def main():
    print("🎯 Ukrainian Flower Hat Girl Gallery Manager")
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"❌ Output directory not found: {OUTPUT_DIR}")
        return 1
    
    # Check if we have any images
    all_patterns = [
        "ukrainian_flower_base_*.png",
        "ukrainian_flower_fashion_*.png",
        "ukrainian_flower_efficient_*.png",
        "ukrainian_flower_hires_*.png",
        "ukrainian_flower_4x_*.png",
        "ukrainian_flower_enhanced_*.png",
        "ukrainian_flower_final_*.png"
    ]
    
    total_images = 0
    for pattern in all_patterns:
        total_images += len(glob.glob(f"{OUTPUT_DIR}/{pattern}"))
    
    if total_images == 0:
        print("❌ No Ukrainian flower hat girl images found!")
        print("🔄 Run the generation pipeline first:")
        print("   • python3 ukrainian_flower_girl_pipeline.py")
        return 1
    
    # Run interactively if no arguments, or show stats by default
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        get_collection_stats()
    
    return 0

if __name__ == "__main__":
    exit(main())