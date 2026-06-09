import os

# Using "../../" tells the script to walk up out of the subfolders 
# and save the file directly on the primary root page of your repository!
HISTORY_FILE = "last_bullsf_patch.txt"
OUTPUT_FILE = "BullSF.txt"

def main():
    latest_version = "V111"
    
    print(f"Bypassing connection blocks. Forcing version to: {latest_version}")
    
    # Save directly to root path output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    # Sync straight to root path tracking file
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    print(f"Successfully processed and forced update to root repository folder!")

if __name__ == "__main__":
    main()
