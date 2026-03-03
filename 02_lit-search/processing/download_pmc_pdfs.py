import os
import subprocess
import sys
import time

def install_requests():
    """Installs the requests package using pip."""
    try:
        print("Installing requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing requests: {e}")
        sys.exit(1)

try:
    import requests
except ImportError:
    install_requests()
    import requests

def download_pdf(pmcid, output_dir):
    """Downloads a PDF from PMC given its PMCID."""
    # Ensure PMCID starts with 'PMC'
    if not pmcid.startswith("PMC"):
        pmcid = f"PMC{pmcid}"
    
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    output_path = os.path.join(output_dir, f"{pmcid}.pdf")
    
    if os.path.exists(output_path):
        print(f"File already exists: {output_path}")
        return True

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    print(f"Downloading {pmcid} from {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30, allow_redirects=True, headers=headers)
        print(f"  Final URL: {response.url}")
        print(f"  Status Code: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'None')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully downloaded: {output_path}")
                return True
            else:
                print(f"Skipped {pmcid}: Not a PDF (Content-Type: {content_type}).")
                # If it's a small HTML file, it might be an error page or a landing page
                return False
        else:
            print(f"Failed to download {pmcid}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {pmcid}: {e}")
        return False

def main():
    input_file = "pmcids.txt"
    output_dir = "pdfs"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r") as f:
        pmcids = [line.strip() for line in f if line.strip()]

    print(f"Found {len(pmcids)} PMCIDs in {input_file}")
    
    success_count = 0
    for pmcid in pmcids:
        if download_pdf(pmcid, output_dir):
            success_count += 1
        # Be nice to NCBI servers
        time.sleep(1)

    print(f"\nFinished. Successfully downloaded {success_count}/{len(pmcids)} PDFs.")

if __name__ == "__main__":
    main()
