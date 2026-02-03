"""
Browser-based file downloader for Salesforce pages that require JavaScript execution.
Uses Playwright to handle pages that need button clicks or form submissions.
"""

import tempfile
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import settings

class BrowserDownloader:
    """
    Downloads files from pages that require browser interaction.
    Specifically designed for Salesforce download pages that use JavaScript redirects.
    """
    
    def download_file(self, url: str, timeout_ms: int = 60000) -> bytes:
        """
        Downloads a file using a headless browser.
        
        Args:
            url: The Salesforce download page URL
            timeout_ms: Maximum time to wait for download (default 60s)
            
        Returns:
            bytes: The downloaded file content
            
        Raises:
            Exception: If download fails or times out
        """
        print(f"   🌐 Iniciando navegador headless...")
        
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']  # Avoid detection
            )
            
            try:
                context = browser.new_context(
                    accept_downloads=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Set up download handler
                download_promise = None
                
                def handle_download(download):
                    nonlocal download_promise
                    download_promise = download
                
                page.on('download', handle_download)
                
                # Navigate to the page (this triggers the automatic POST)
                print(f"   📄 Carregando página Salesforce...")
                
                # Set up network monitoring to catch download redirects
                download_url_from_network = None
                
                def handle_response(response):
                    nonlocal download_url_from_network
                    # Look for responses that might be the actual file
                    if response.status == 200 and 'content-disposition' in response.headers:
                        download_url_from_network = response.url
                
                page.on('response', handle_response)
                
                page.goto(url, wait_until='networkidle', timeout=timeout_ms)
                
                # Wait for page to fully load
                print(f"   ⏳ Aguardando página carregar...")
                page.wait_for_timeout(3000)
                
                # Try to find and click download button
                print(f"   🔍 Procurando botão de download...")
                
                # Salesforce-specific selectors first (most specific)
                selectors = [
                    'button.downloadbutton',  # Exact class from Salesforce
                    'button[title="Fazer download"]',  # Exact title
                    'button.bare.downloadbutton',  # Full class chain
                    'button[aria-label*="download"]',
                    'button:has-text("Fazer download")',
                    # Generic download selectors
                    'button:has-text("Download")',
                    'a:has-text("Download")',
                    'button:has-text("Baixar")',
                    'a:has-text("Baixar")',
                    'button[title*="Download"]',
                    'a[title*="Download"]',
                    'button[aria-label*="Download"]',
                    'a[download]',
                    '.downloadButton',
                    '#downloadButton',
                    'a[href*="download"]',
                    'button[onclick*="download"]',
                    'input[type="button"][value*="Download"]',
                    'input[type="submit"][value*="Download"]',
                    # Generic button/link if nothing else works
                    'button',
                    'a[href]'
                ]
                
                button_clicked = False
                for selector in selectors:
                    try:
                        count = page.locator(selector).count()
                        if count > 0:
                            print(f"   ✅ Elemento encontrado: {selector} ({count} elementos)")
                            # Click the first one
                            page.locator(selector).first.click(timeout=5000)
                            button_clicked = True
                            print(f"   🖱️ Clique executado, aguardando download...")
                            page.wait_for_timeout(10000)  # Wait for download to start
                            break
                    except Exception as e:
                        continue
                
                if not button_clicked:
                    # Take screenshot for debugging
                    screenshot_path = os.path.join(tempfile.gettempdir(), f"salesforce_no_button_{int(time.time())}.png")
                    page.screenshot(path=screenshot_path)
                    print(f"   📸 Screenshot salvo: {screenshot_path}")
                    raise Exception(f"Nenhum botão de download encontrado na página.")
                
                # Check if we got a download from network monitoring
                if download_url_from_network and not download_promise:
                    print(f"   🌐 URL de download capturada via rede: {download_url_from_network[:50]}...")
                    # Try to download directly
                    import requests
                    resp = requests.get(download_url_from_network, timeout=60)
                    resp.raise_for_status()
                    return resp.content
                
                # Wait for download to complete
                if download_promise:
                    print(f"   ⬇️ Download iniciado, aguardando conclusão...")
                    
                    # Save to temp file
                    temp_dir = tempfile.mkdtemp()
                    file_path = os.path.join(temp_dir, download_promise.suggested_filename)
                    download_promise.save_as(file_path)
                    
                    # Read file bytes
                    with open(file_path, 'rb') as f:
                        file_bytes = f.read()
                    
                    # Debug: Check file signature
                    if len(file_bytes) > 0:
                        # ZIP files start with 'PK' (0x50 0x4B)
                        if file_bytes[:2] != b'PK':
                            # Not a ZIP, might be HTML
                            preview = file_bytes[:500].decode('utf-8', errors='ignore')
                            print(f"   ⚠️ Arquivo baixado não é ZIP. Primeiros bytes: {preview[:100]}")
                            raise Exception(f"Arquivo baixado não é ZIP válido. Pode ser HTML ou erro da Salesforce.")
                    
                    # Cleanup
                    os.remove(file_path)
                    os.rmdir(temp_dir)
                    
                    print(f"   ✅ Download concluído: {len(file_bytes)} bytes")
                    return file_bytes
                else:
                    # No download detected - save page screenshot for debugging
                    screenshot_path = os.path.join(tempfile.gettempdir(), f"salesforce_debug_{int(time.time())}.png")
                    page.screenshot(path=screenshot_path)
                    print(f"   📸 Screenshot salvo em: {screenshot_path}")
                    raise Exception("Nenhum download foi iniciado. A página pode ter mudado de estrutura.")
                    
            except PlaywrightTimeoutError as e:
                raise Exception(f"Timeout ao carregar página Salesforce: {e}")
            except Exception as e:
                raise Exception(f"Erro no download via navegador: {e}")
            finally:
                browser.close()
