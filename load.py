"""
EDHauler Plugin for Elite Dangerous Market Connector
Displays Fleet Carrier market data from INARA (public page)
"""
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

import sys
import re
from datetime import datetime
from threading import Thread

try:
    # Python 3
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
    from urllib.parse import quote
except ImportError:
    # Python 2
    from urllib2 import Request, urlopen, URLError, HTTPError
    from urllib import quote

this = sys.modules[__name__]

try:
    from config import config
except ImportError:
    config = dict()

try:
    import myNotebook as nb
except ImportError:
    nb = None

# Try to import EDMCOverlay
try:
    import sys
    import os
    edmc_overlay_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'EDMCOverlay')
    if edmc_overlay_path not in sys.path:
        sys.path.append(edmc_overlay_path)
    from edmcoverlay import Overlay
    OVERLAY_AVAILABLE = True
except ImportError:
    OVERLAY_AVAILABLE = False
    Overlay = None

# Configuration keys
CFG_CARRIER_NAME = "EDHaulerCarrierName"
CFG_OVERLAY_ENABLED = "EDHaulerOverlayEnabled"

# INARA base URL
INARA_BASE_URL = "https://inara.cz"

# Overlay settings
OVERLAY_X = 50  # pixels from left
OVERLAY_Y = 100  # pixels from top

class EDHauler(object):
    """
    Main class for the EDHauler plugin
    """
    def __init__(self):
        self.carrier_name = ""
        self.market_data = []
        self.last_update = None
        self.refresh_timer = None
        self.parent = None
        self.is_fetching = False
        self.overlay_enabled = False
        self.overlay_client = None
        
        # UI widgets
        self.carrier_label = None
        self.debug_label = None
        self.status_label = None
        self.market_frame = None
        self.refresh_button = None
        self.overlay_button = None
        self.market_labels = []
        
        # Initialize overlay if available
        if OVERLAY_AVAILABLE:
            try:
                self.overlay_client = Overlay()
            except Exception as e:
                print(f"EDHauler: Could not initialize overlay: {e}")
                self.overlay_client = None

    def load_config(self):
        """Load saved configuration"""
        self.carrier_name = config.get(CFG_CARRIER_NAME) or ""
        self.overlay_enabled = config.get_bool(CFG_OVERLAY_ENABLED) or False

    def save_config(self):
        """Save configuration"""
        config.set(CFG_CARRIER_NAME, self.carrier_name)
        config.set(CFG_OVERLAY_ENABLED, self.overlay_enabled)
    
    def toggle_overlay(self):
        """Toggle overlay on/off"""
        self.overlay_enabled = not self.overlay_enabled
        self.save_config()
        
        if self.overlay_enabled:
            self.update_overlay()
            if self.overlay_button:
                self.overlay_button.config(text="Hide Overlay")
        else:
            self.clear_overlay()
            if self.overlay_button:
                self.overlay_button.config(text="Show Overlay")
    
    def clear_overlay(self):
        """Clear all overlay messages"""
        if not OVERLAY_AVAILABLE or not self.overlay_client:
            return
        
        try:
            # Clear background shape
            self.overlay_client.send_shape("edhauler_bg", "rect", "#000000", "#000000", 0, 0, 1, 1, ttl=1)
            
            # Clear all EDHauler overlay messages
            for i in range(20):  # Clear up to 20 lines
                self.overlay_client.send_message(f"edhauler_{i}", "", "green", 0, 0, ttl=1)
        except Exception as e:
            print(f"EDHauler: Error clearing overlay: {e}")
    
    def update_overlay(self):
        """Update the overlay with current market data"""
        if not self.overlay_enabled or not OVERLAY_AVAILABLE or not self.overlay_client:
            return
        
        if not self.market_data or "error" in self.market_data:
            self.clear_overlay()
            return
        
        try:
            # Format overlay text
            lines = []
            line_sizes = []  # Track which lines should be larger
            
            # Header
            carrier_info = self.market_data.get("carrier_info", {})
            carrier_text = f"{carrier_info.get('name', 'Unknown')} ({carrier_info.get('callsign', 'Unknown')})"
            lines.append(f"=== {carrier_text} ===")
            line_sizes.append("large")  # Header in large size
            lines.append("")
            line_sizes.append("normal")
            
            orders = self.market_data.get("orders", [])
            buy_orders = [o for o in orders if o.get("orderType") == 1]
            sell_orders = [o for o in orders if o.get("orderType") == 2]
            
            if buy_orders:
                lines.append("BUY ORDERS:")
                line_sizes.append("large")  # Section header in large
                for order in buy_orders[:8]:  # Limit to 8 orders for overlay
                    commodity = order.get("commodityName", "Unknown").upper()  # Uppercase for emphasis
                    quantity = order.get("stock", 0)
                    price = order.get("price", 0)
                    # Format as table with fixed-width columns
                    # Commodity: 25 chars, Quantity: 10 chars (right-aligned), Price: 10 chars (right-aligned)
                    lines.append(f"{commodity:<25} | {quantity:>10,} @ {price:>10,} CR")
                    line_sizes.append("normal")
                lines.append("")
                line_sizes.append("normal")
            
            if sell_orders:
                lines.append("SELL ORDERS:")
                line_sizes.append("large")  # Section header in large
                for order in sell_orders[:8]:  # Limit to 8 orders for overlay
                    commodity = order.get("commodityName", "Unknown").upper()  # Uppercase for emphasis
                    quantity = order.get("stock", 0)
                    price = order.get("price", 0)
                    # Format as table with fixed-width columns
                    # Commodity: 25 chars, Quantity: 10 chars (right-aligned), Price: 10 chars (right-aligned)
                    lines.append(f"{commodity:<25} | {quantity:>10,} @ {price:>10,} CR")
                    line_sizes.append("normal")
            
            # Calculate background box dimensions
            # Approximate: 8px per character width, 20px line height
            max_line_length = max(len(line) for line in lines) if lines else 0
            box_width = max(max_line_length * 8, 300)  # Minimum 300px width
            box_height = len(lines) * 20 + 20  # 20px per line + padding
            
            # Draw background box with 50% transparency
            # Fill format: "rgba(0,0,0,0.5)" for black with 50% opacity
            try:
                self.overlay_client.send_shape(
                    "edhauler_bg",
                    "rect",
                    "#000000",  # Black border
                    "rgba(0,0,0,0.5)",  # Black fill with 50% transparency
                    OVERLAY_X - 10,  # Slightly left of text
                    OVERLAY_Y - 10,  # Slightly above text
                    box_width,
                    box_height,
                    ttl=60
                )
            except Exception as e:
                print(f"EDHauler: Could not draw background box: {e}")
            
            # Send text to overlay
            y_offset = OVERLAY_Y
            for i, (line, size) in enumerate(zip(lines, line_sizes)):
                if i < 20:  # Limit total lines
                    self.overlay_client.send_message(
                        f"edhauler_{i}",
                        line,
                        "yellow",
                        OVERLAY_X,
                        y_offset,
                        ttl=60,  # 60 second TTL
                        size=size
                    )
                    # Adjust spacing based on size
                    y_offset += 24 if size == "large" else 20
            
            # Clear any remaining old lines
            for i in range(len(lines), 20):
                self.overlay_client.send_message(f"edhauler_{i}", "", "yellow", 0, 0, ttl=1)
                
        except Exception as e:
            print(f"EDHauler: Error updating overlay: {e}")

    def fetch_market_data(self):
        """Fetch market data from INARA public page"""
        if not self.carrier_name:
            return {"error": "Carrier Name/ID is required"}
        
        if self.is_fetching:
            return {"error": "Already fetching data"}
        
        self.is_fetching = True
        
        try:
            carrier_info = {"name": "", "callsign": ""}
            
            # Check if input is a station ID (all digits)
            if self.carrier_name.strip().isdigit():
                # Direct access using station ID
                station_id = self.carrier_name.strip()
                
                # Fetch the market page directly
                market_url = f"{INARA_BASE_URL}/elite/station-market/{station_id}/"
                
                request = Request(
                    market_url,
                    headers={'User-Agent': 'EDHauler/1.0 (EDMC Plugin)'}
                )
                
                response = urlopen(request, timeout=15)
                market_html = response.read().decode('utf-8')
                
                # Extract carrier name and callsign from the market page
                # HTML structure: <a href="/elite/station/ID/" class="standardcolor">NAME<span class="minor">(CALLSIGN)</span></a>
                
                print(f"EDHauler DEBUG: Station ID: {station_id}")
                
                # Extract name (between <a> tag and <span> tag)
                name_match = re.search(r'<a[^>]*href="/elite/station/\d+/"[^>]*class="standardcolor"[^>]*>([^<]+)<span', market_html, re.DOTALL)
                
                if name_match:
                    carrier_info["name"] = name_match.group(1).strip()
                    print(f"EDHauler DEBUG: Found name: '{carrier_info['name']}'")
                else:
                    print(f"EDHauler DEBUG: name_match failed")
                
                # Extract callsign (inside <span class="minor"> tag)
                callsign_match = re.search(r'<span class="minor">\(([^)]+)\)</span>', market_html)
                
                if callsign_match:
                    carrier_info["callsign"] = callsign_match.group(1).strip()
                    print(f"EDHauler DEBUG: Found callsign: '{carrier_info['callsign']}'")
                else:
                    print(f"EDHauler DEBUG: callsign_match failed")
                
                # Fallback if neither matched
                if not carrier_info["name"]:
                    print(f"EDHauler DEBUG: Using fallback name")
                    carrier_info["name"] = f"Station {station_id}"
                
            else:
                # Step 1: Search for the carrier to get its station ID
                search_url = f"{INARA_BASE_URL}/elite/station/?search={quote(self.carrier_name)}"
                
                request = Request(
                    search_url,
                    headers={'User-Agent': 'EDHauler/1.0 (EDMC Plugin)'}
                )
                
                response = urlopen(request, timeout=15)
                html_content = response.read().decode('utf-8')
                
                # Extract station ID from the market link
                market_link_match = re.search(r'/elite/station-market/(\d+)/', html_content)
                if not market_link_match:
                    self.is_fetching = False
                    return {"error": "Carrier found but no market link available. Market may be disabled."}
                
                station_id = market_link_match.group(1)
                
                # Extract carrier info
                carrier_info = {"name": self.carrier_name, "callsign": ""}
                # Match either XXX-XXX format OR 3-5 letter/digit format (e.g., CREA)
                callsign_match = re.search(r'([A-Z0-9]{3}-[A-Z0-9]{3}|[A-Z0-9]{3,5})', html_content)
                if callsign_match:
                    carrier_info["callsign"] = callsign_match.group(1)
                
                # Step 2: Fetch the actual market page
                market_url = f"{INARA_BASE_URL}/elite/station-market/{station_id}/"
                
                request = Request(
                    market_url,
                    headers={'User-Agent': 'EDHauler/1.0 (EDMC Plugin)'}
                )
                
                response = urlopen(request, timeout=15)
                market_html = response.read().decode('utf-8')
            
            self.is_fetching = False
            
            # Parse market data from the market page
            orders = []
            
            # INARA market table structure:
            # Column 1: Commodity name
            # Column 2: Sell price (station buying FROM players) - if not "-" it's a BUY order
            # Column 3: Demand (quantity for buy orders)
            # Column 4: Buy price (station selling TO players) - if not "-" it's a SELL order
            # Column 5: Supply (quantity for sell orders)
            
            # Find all table rows with commodity data
            # Pattern matches: commodity link, then captures all 4 price/quantity columns
            row_pattern = r'<tr[^>]*>.*?href="/elite/commodity/\d+/">([^<]+)</a>.*?' + \
                         r'<td[^>]*data-order="(\d+)"[^>]*>.*?</td>.*?' + \
                         r'<td[^>]*data-order="(\d+)"[^>]*>.*?</td>.*?' + \
                         r'<td[^>]*data-order="(\d+)"[^>]*>.*?</td>.*?' + \
                         r'<td[^>]*data-order="(\d+)"[^>]*>.*?</td>.*?</tr>'
            
            matches = re.findall(row_pattern, market_html, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                commodity_name = match[0].strip()
                sell_price = int(match[1])      # Station buying (players sell)
                demand = int(match[2])          # Demand quantity
                buy_price = int(match[3])       # Station selling (players buy)
                supply = int(match[4])          # Supply quantity
                
                # If sell_price > 0 and not 99999999999 (that's the subheader), it's a BUY order
                if sell_price > 0 and sell_price < 99999999999 and demand > 0:
                    orders.append({
                        "commodityName": commodity_name,
                        "orderType": 1,  # Buy order (carrier buying from players)
                        "stock": demand,
                        "price": sell_price
                    })
                
                # If buy_price > 0 and not 99999999999, it's a SELL order
                if buy_price > 0 and buy_price < 99999999999 and supply > 0:
                    orders.append({
                        "commodityName": commodity_name,
                        "orderType": 2,  # Sell order (carrier selling to players)
                        "stock": supply,
                        "price": buy_price
                    })
            
            if not orders:
                return {"error": "Market page found but no active orders. Carrier may have empty market."}
            
            return {
                "success": True,
                "orders": orders,
                "carrier_info": carrier_info
            }
            
        except HTTPError as e:
            self.is_fetching = False
            if e.code == 404:
                return {"error": f"Carrier '{self.carrier_name}' not found on INARA"}
            return {"error": f"HTTP Error {e.code}: {e.reason}"}
        except URLError as e:
            self.is_fetching = False
            return {"error": f"Network Error: {str(e.reason)}"}
        except Exception as e:
            self.is_fetching = False
            return {"error": f"Error: {str(e)}"}

    def update_display(self):
        """Update the UI with current market data"""
        # Update overlay if enabled
        if self.overlay_enabled:
            self.update_overlay()
        
        if not self.market_frame or not self.status_label:
            return
        
        # Clear existing market labels
        for label in self.market_labels:
            label.destroy()
        self.market_labels = []
        
        if not self.market_data:
            # Show "no data" message
            label = tk.Label(
                self.market_frame,
                text="No market data available",
                justify=tk.LEFT
            )
            label.pack(anchor=tk.W)
            self.market_labels.append(label)
            self.status_label.config(text="Status: No data")
            return
        
        # Check if it's an error
        if "error" in self.market_data:
            label = tk.Label(
                self.market_frame,
                text=f"Error: {self.market_data['error']}",
                justify=tk.LEFT,
                fg="red"
            )
            label.pack(anchor=tk.W)
            self.market_labels.append(label)
            self.status_label.config(text="Status: Error")
            return
        
        # Display carrier info
        carrier_info = self.market_data.get("carrier_info", {})
        carrier_text = f"{carrier_info.get('name', 'Unknown')} ({carrier_info.get('callsign', 'Unknown')})"
        if self.carrier_label:
            self.carrier_label.config(text=f"Carrier: {carrier_text}")
        
        # Update debug label with raw values
        if self.debug_label:
            debug_text = f"Name: {carrier_info.get('name', 'N/A')} | Callsign: {carrier_info.get('callsign', 'N/A')}"
            self.debug_label.config(text=debug_text)
        
        # Display market orders
        orders = self.market_data.get("orders", [])
        
        if not orders:
            label = tk.Label(
                self.market_frame,
                text="No active market orders",
                justify=tk.LEFT
            )
            label.pack(anchor=tk.W)
            self.market_labels.append(label)
        else:
            # Sort orders by type (buy first, then sell)
            buy_orders = [o for o in orders if o.get("orderType") == 1]
            sell_orders = [o for o in orders if o.get("orderType") == 2]
            
            if buy_orders:
                header = tk.Label(
                    self.market_frame,
                    text="=== BUY ORDERS ===",
                    justify=tk.LEFT,
                    font=("TkDefaultFont", 9, "bold")
                )
                header.pack(anchor=tk.W)
                self.market_labels.append(header)
                
                for order in buy_orders[:10]:  # Limit to 10 orders
                    commodity = order.get("commodityName", "Unknown")
                    quantity = order.get("stock", 0)
                    price = order.get("price", 0)
                    
                    order_text = f"  BUY {commodity}: {quantity:,} @ {price:,} CR"
                    label = tk.Label(
                        self.market_frame,
                        text=order_text,
                        justify=tk.LEFT,
                        fg="green"
                    )
                    label.pack(anchor=tk.W)
                    self.market_labels.append(label)
            
            if sell_orders:
                header = tk.Label(
                    self.market_frame,
                    text="=== SELL ORDERS ===",
                    justify=tk.LEFT,
                    font=("TkDefaultFont", 9, "bold")
                )
                header.pack(anchor=tk.W)
                self.market_labels.append(header)
                
                for order in sell_orders[:10]:  # Limit to 10 orders
                    commodity = order.get("commodityName", "Unknown")
                    quantity = order.get("stock", 0)
                    price = order.get("price", 0)
                    
                    order_text = f"  SELL {commodity}: {quantity:,} @ {price:,} CR"
                    label = tk.Label(
                        self.market_frame,
                        text=order_text,
                        justify=tk.LEFT,
                        fg="blue"
                    )
                    label.pack(anchor=tk.W)
                    self.market_labels.append(label)
        
        # Update status with last update time
        if self.last_update:
            time_str = self.last_update.strftime("%H:%M:%S")
            self.status_label.config(text=f"Last updated: {time_str}")
        else:
            self.status_label.config(text="Status: Ready")

    def fetch_and_update(self):
        """Fetch data and update display (non-blocking)"""
        def fetch_thread():
            result = self.fetch_market_data()
            self.market_data = result
            self.last_update = datetime.now()
            
            # Schedule UI update on main thread
            if self.parent:
                self.parent.after(0, self.update_display)
        
        thread = Thread(target=fetch_thread)
        thread.daemon = True
        thread.start()

    def manual_refresh(self):
        """Handle manual refresh button click"""
        self.fetch_and_update()
    
    def dump_to_clipboard(self):
        """Copy formatted market data to clipboard"""
        if not self.market_data or "error" in self.market_data:
            if self.status_label:
                self.status_label.config(text="Status: No data to dump")
            return
        
        try:
            # Generate formatted text
            lines = []
            
            # Header with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"EDHauler Dump : {timestamp}")
            lines.append("")
            
            # Carrier info
            carrier_info = self.market_data.get("carrier_info", {})
            carrier_text = f"{carrier_info.get('name', 'Unknown')} ({carrier_info.get('callsign', 'Unknown')})"
            lines.append(f"=== {carrier_text} ===")
            lines.append("")
            
            orders = self.market_data.get("orders", [])
            buy_orders = [o for o in orders if o.get("orderType") == 1]
            sell_orders = [o for o in orders if o.get("orderType") == 2]
            
            if buy_orders:
                lines.append("BUY ORDERS:")
                for order in buy_orders:
                    commodity = order.get("commodityName", "Unknown").upper()
                    quantity = order.get("stock", 0)
                    price = order.get("price", 0)
                    lines.append(f"{commodity:<25} | {quantity:>10,} @ {price:>10,} CR")
                lines.append("")
            
            if sell_orders:
                lines.append("SELL ORDERS:")
                for order in sell_orders:
                    commodity = order.get("commodityName", "Unknown").upper()
                    quantity = order.get("stock", 0)
                    price = order.get("price", 0)
                    lines.append(f"{commodity:<25} | {quantity:>10,} @ {price:>10,} CR")
            
            # Join lines and copy to clipboard
            text = "\n".join(lines)
            
            if self.parent:
                self.parent.clipboard_clear()
                self.parent.clipboard_append(text)
                self.parent.update()  # Persist clipboard
                
                if self.status_label:
                    self.status_label.config(text="Status: Copied to clipboard!")
                    # Reset status after 3 seconds
                    self.parent.after(3000, lambda: self.status_label.config(text=f"Last updated: {self.last_update.strftime('%H:%M:%S')}") if self.last_update else None)
        
        except Exception as e:
            print(f"EDHauler: Error copying to clipboard: {e}")
            if self.status_label:
                self.status_label.config(text="Status: Error copying to clipboard")

    def schedule_refresh(self):
        """Schedule automatic refresh every 30 seconds"""
        if self.carrier_name:
            self.fetch_and_update()
        
        # Schedule next refresh
        if self.parent:
            self.refresh_timer = self.parent.after(30000, self.schedule_refresh)

    def stop_refresh(self):
        """Stop automatic refresh timer"""
        if self.refresh_timer and self.parent:
            self.parent.after_cancel(self.refresh_timer)
            self.refresh_timer = None


def plugin_start3(plugin_dir):
    """Plugin start for Python 3"""
    return plugin_start(plugin_dir)


def plugin_start(plugin_dir):
    """Initialize plugin"""
    hauler = EDHauler()
    hauler.load_config()
    this.hauler = hauler
    return "EDHauler"


def plugin_stop():
    """Clean up when plugin stops"""
    if hasattr(this, 'hauler') and this.hauler:
        this.hauler.stop_refresh()


def plugin_app(parent):
    """Create UI for EDMC main window"""
    if not hasattr(this, 'hauler'):
        return None
    
    hauler = this.hauler
    hauler.parent = parent
    
    # Main frame
    frame = tk.Frame(parent)
    frame.columnconfigure(1, weight=1)
    
    # Carrier name label
    hauler.carrier_label = tk.Label(
        frame,
        text="EDHauler: Not configured",
        justify=tk.LEFT
    )
    hauler.carrier_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5)
    
    # Debug label (shows raw name and callsign)
    hauler.debug_label = tk.Label(
        frame,
        text="",
        justify=tk.LEFT,
        fg="gray"
    )
    hauler.debug_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5)
    
    # Status label
    hauler.status_label = tk.Label(
        frame,
        text="Status: Waiting for configuration",
        justify=tk.LEFT
    )
    hauler.status_label.grid(row=2, column=0, sticky=tk.W, padx=5)
    
    # Button frame for Refresh, Dump, and Overlay toggle
    button_frame = tk.Frame(frame)
    button_frame.grid(row=2, column=1, sticky=tk.E, padx=5)
    
    # Refresh button
    hauler.refresh_button = tk.Button(
        button_frame,
        text="Refresh",
        command=hauler.manual_refresh
    )
    hauler.refresh_button.pack(side=tk.LEFT, padx=2)
    
    # Dump button
    hauler.dump_button = tk.Button(
        button_frame,
        text="Dump",
        command=hauler.dump_to_clipboard
    )
    hauler.dump_button.pack(side=tk.LEFT, padx=2)
    
    # Overlay toggle button (only if overlay is available)
    if OVERLAY_AVAILABLE and hauler.overlay_client:
        overlay_text = "Hide Overlay" if hauler.overlay_enabled else "Show Overlay"
        hauler.overlay_button = tk.Button(
            button_frame,
            text=overlay_text,
            command=hauler.toggle_overlay
        )
        hauler.overlay_button.pack(side=tk.LEFT, padx=2)
    
    # Market data frame (scrollable area)
    hauler.market_frame = tk.Frame(frame)
    hauler.market_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)
    
    # Start automatic refresh
    hauler.schedule_refresh()
    
    return frame


def plugin_prefs(parent, cmdr, is_beta):
    """Create preferences UI"""
    if not hasattr(this, 'hauler'):
        return None
    
    hauler = this.hauler
    
    # Create frame
    if nb:
        frame = nb.Frame(parent)
    else:
        frame = tk.Frame(parent)
    
    frame.columnconfigure(1, weight=1)
    
    # Title
    if nb:
        title_label = nb.Label(frame, text="EDHauler Configuration")
    else:
        title_label = tk.Label(frame, text="EDHauler Configuration")
    title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
    
    # Carrier Name or Station ID
    if nb:
        carrier_label = nb.Label(frame, text="Fleet Carrier Name/ID:")
    else:
        carrier_label = tk.Label(frame, text="Fleet Carrier Name/ID:")
    carrier_label.grid(row=1, column=0, sticky=tk.W, padx=10)
    
    this.carrier_name_var = tk.StringVar(value=hauler.carrier_name)
    if nb:
        carrier_entry = nb.Entry(frame, textvariable=this.carrier_name_var, width=30)
    else:
        carrier_entry = tk.Entry(frame, textvariable=this.carrier_name_var, width=30)
    carrier_entry.grid(row=1, column=1, sticky=tk.EW, padx=10)
    
    # Overlay enabled checkbox (only if overlay is available)
    if OVERLAY_AVAILABLE:
        this.overlay_enabled_var = tk.IntVar(value=1 if hauler.overlay_enabled else 0)
        if nb:
            overlay_check = nb.Checkbutton(
                frame,
                text="Enable in-game overlay (yellow text)",
                variable=this.overlay_enabled_var
            )
        else:
            overlay_check = tk.Checkbutton(
                frame,
                text="Enable in-game overlay (yellow text)",
                variable=this.overlay_enabled_var
            )
        overlay_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
    
    # Help text
    if nb:
        help_label = nb.Label(
            frame,
            text="Enter your Fleet Carrier's name, callsign, or INARA station ID.\n• Name/Callsign: 'CREA' or 'Q0G-09K'\n• Station ID: '1063226' (faster, more reliable)\nData is fetched from INARA's public pages - no API key needed!\nUpdates automatically every 30 seconds."
        )
    else:
        help_label = tk.Label(
            frame,
            text="Enter your Fleet Carrier's name, callsign, or INARA station ID.\n• Name/Callsign: 'CREA' or 'Q0G-09K'\n• Station ID: '1063226' (faster, more reliable)\nData is fetched from INARA's public pages - no API key needed!\nUpdates automatically every 30 seconds."
        )
    help_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
    
    return frame


def prefs_changed(cmdr, is_beta):
    """Handle preference changes"""
    if not hasattr(this, 'hauler'):
        return
    
    hauler = this.hauler
    
    # Update configuration
    if hasattr(this, 'carrier_name_var'):
        hauler.carrier_name = this.carrier_name_var.get()
    
    # Update overlay setting if available
    if OVERLAY_AVAILABLE and hasattr(this, 'overlay_enabled_var'):
        old_overlay_state = hauler.overlay_enabled
        hauler.overlay_enabled = bool(this.overlay_enabled_var.get())
        
        # Update overlay button text if it changed
        if old_overlay_state != hauler.overlay_enabled:
            if hauler.overlay_button:
                button_text = "Hide Overlay" if hauler.overlay_enabled else "Show Overlay"
                hauler.overlay_button.config(text=button_text)
            
            # Update overlay display
            if hauler.overlay_enabled:
                hauler.update_overlay()
            else:
                hauler.clear_overlay()
    
    hauler.save_config()
    
    # Update display
    if hauler.carrier_name:
        hauler.fetch_and_update()
