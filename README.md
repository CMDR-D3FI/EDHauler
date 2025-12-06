# EDHauler Plugin for Elite Dangerous Market Connector

EDHauler is a plugin for Elite Dangerous Market Connector (EDMC) that displays Fleet Carrier market data from INARA's public pages.

Are you hauling and require a constant update of the demand of the carrier you are supplying? Do you find yourself constantly checking on INARA what the current demand is? This is the tool that saves you looking up on INARA constantly. It pushes the demand of the carrier to you onscreen as an EDMC overlay. It refreshes every 30 seconds. You can Refresh manually too. You can Dump/Copy to Clipboard in case you need to update your fellow haulers about the current demand easily.

Happy Hauling!

PS. It helps if you pay forward the benefit by logging and uploading your carrier market data to INARA. Fetch your own API key from HERE (https://inara.cz/elite/cmdr-settings-api/) and input it in EDMC Settings for INARA.

<img width="406" height="164" alt="Image" src="https://github.com/user-attachments/assets/a78a052e-8b1b-424c-b020-5fcc0088948f" />

<img width="533" height="216" alt="Image" src="https://github.com/user-attachments/assets/7c39b5ff-edeb-43f0-9997-b4d99a55aab3" />

<img width="773" height="227" alt="Image" src="https://github.com/user-attachments/assets/08828924-ef0b-443e-80af-6497779aeadd" />

## Features

- **No API Key Required**: Fetches data from INARA's public pages
- **Automatic Updates**: Refreshes market data every 30 seconds
- **Manual Refresh**: Click the "Refresh" button to update data on demand
- **🎮 In-Game Overlay**: Display market data directly in Elite Dangerous with EDMCOverlay
- **📋 Clipboard Export**: "Dump" button copies formatted market data to clipboard
- **📊 Table Formatting**: Fixed-width columns for easy reading
- **Live Market Orders**: Displays active buy and sell orders from any Fleet Carrier
- **Simple Interface**: Clean display integrated into the EDMC main window
- **Easy Configuration**: Just enter the carrier name or callsign

## Installation

1. Download or clone this repository
2. Copy the `EDHauler` folder to your EDMC plugins directory:
   - Windows: `%LOCALAPPDATA%\EDMarketConnector\plugins\`
   - Mac: `~/Library/Application Support/EDMarketConnector/plugins/`
   - Linux: `~/.local/share/EDMarketConnector/plugins/`
3. Restart EDMC

## Configuration

1. Open EDMC and go to **File → Settings**
2. Navigate to the **EDHauler** tab
3. Enter your **Fleet Carrier Name, Callsign, or INARA Station ID**:
   - **Name/Callsign**: "CREA" or "Q0G-09K" or "HMS Endeavour"
   - **Station ID**: "1063226" (faster, more reliable)
   - The carrier must be registered on INARA
4. Click **OK** to save

That's it! No API key needed.

### Finding Your Station ID

For the most reliable results, use your carrier's INARA Station ID:

1. Go to [INARA](https://inara.cz/)
2. Search for your carrier name or callsign
3. Open your carrier's page
4. Look at the URL: `https://inara.cz/elite/station-market/1063226/`
5. The number (`1063226`) is your Station ID
6. Enter this number in the EDHauler configuration

**Benefits of using Station ID:**
- ✅ **Faster** - Skips the search step
- ✅ **More reliable** - Direct access to your exact carrier
- ✅ **No ambiguity** - Works even if multiple carriers have similar names

## Usage

Once configured, the plugin will:

- Display your Fleet Carrier's name and callsign
- Show the last update time
- List active buy orders (in green)
- List active sell orders (in blue)
- Automatically refresh every 30 seconds
- Allow manual refresh with the "Refresh" button

### Display Format

```
Carrier: HMS Endeavour (Q0G-09K)
Last updated: 09:30:45    [Refresh] [Dump] [Show Overlay]

=== BUY ORDERS ===
  BUY Tritium: 5,000 @ 50,000 CR
  BUY Platinum: 1,200 @ 280,000 CR

=== SELL ORDERS ===
  SELL Gold: 800 @ 320,000 CR
  SELL Silver: 2,500 @ 180,000 CR
```

### 🎮 In-Game Overlay

EDHauler integrates with EDMCOverlay to display market data directly in Elite Dangerous!

**Requirements:**
- EDMCOverlay plugin must be installed (available in EDMC plugins folder)

**Features:**
- **Yellow text** on **50% opacity black background** for excellent visibility
- **Table format** with fixed-width columns
- **Large headers** for section titles (BUY ORDERS / SELL ORDERS)
- **UPPERCASE commodity names** for emphasis
- Shows up to 8 buy and 8 sell orders
- Auto-updates every 30 seconds
- Toggle on/off with "Show Overlay" / "Hide Overlay" button

**Overlay Format:**
```
=== HMS Endeavour (Q0G-09K) ===

BUY ORDERS:
TRITIUM                  |      5,000 @     50,000 CR
PLATINUM                 |      1,200 @    280,000 CR

SELL ORDERS:
GOLD                     |        800 @    320,000 CR
SILVER                   |      2,500 @    180,000 CR
```

**Position:** Top-left corner of game screen (customizable in code)

### 📋 Clipboard Export (Dump Feature)

Click the **"Dump"** button to copy formatted market data to your clipboard!

**Output Format:**
```
EDHauler Dump : 2025-12-05 14:11:10

=== HMS Endeavour (Q0G-09K) ===

BUY ORDERS:
TRITIUM                  |      5,000 @     50,000 CR
PLATINUM                 |      1,200 @    280,000 CR
CMM COMPOSITE            |     17,212 @     41,018 CR

SELL ORDERS:
GOLD                     |        800 @    320,000 CR
SILVER                   |      2,500 @    180,000 CR
FOOD CARTRIDGES          |        470 @     25,200 CR
```

**Uses:**
- Share market data with your squadron on Discord
- Keep records of carrier inventory
- Paste into trading spreadsheets
- Document market changes over time

**Note:** Includes timestamp and ALL orders (not limited like overlay)

## How It Works

The plugin fetches data from INARA's publicly available Fleet Carrier pages. It:
1. Searches for the carrier by name/callsign
2. Parses the HTML to extract market order information
3. Displays the data in a clean, easy-to-read format
4. Updates automatically every 30 seconds

## Troubleshooting

### "Carrier not found on INARA"
- Check that you entered the correct carrier name or callsign
- **Try using the INARA Station ID instead** (see Configuration section above)
- Make sure the carrier is registered on INARA (visit https://inara.cz/)
- Carriers must have their data synced to INARA (happens automatically when playing)

### "No market orders found or unable to parse data"
- Your carrier may not have any active buy or sell orders
- The carrier page might not have market data visible
- Try clicking the manual "Refresh" button

### Plugin not showing up
- Restart EDMC after installing the plugin
- Check that the plugin folder is in the correct location
- Verify the `load.py` file is present in the EDHauler folder

### "Network Error"
- Check your internet connection
- INARA might be temporarily down or slow
- The plugin will retry automatically after 30 seconds

## Requirements

- Elite Dangerous Market Connector (EDMC) version 4.0 or higher
- Internet connection
- Fleet Carrier registered on INARA (https://inara.cz/)

## Rate Limiting

The plugin is respectful of INARA's servers:
- Automatic refresh: every 30 seconds (not too frequent)
- Uses non-blocking background threads to prevent EDMC freezing
- Includes proper User-Agent header

## Privacy

- No API keys or personal data required
- Only communicates with INARA's public website
- No data is sent to third parties
- Carrier information is stored locally in EDMC's configuration

## Limitations

- Only displays up to 10 buy orders and 10 sell orders (for UI space)
- Requires the carrier to be publicly visible on INARA
- Parsing may break if INARA changes their HTML structure (will be updated if needed)

## Support

For issues, feature requests, or questions:
- Check the troubleshooting section above
- Ensure your carrier is visible on INARA: https://inara.cz/
- Ensure your EDMC is up to date

## Credits

Developed for the Elite Dangerous community.
Data provided by INARA (https://inara.cz/)

## License

MIT License - See [LICENSE](LICENSE) file for details.

This plugin is provided as-is for use with Elite Dangerous Market Connector.

## Changelog

### Version 1.2.0 (2025-12-05)
- **🆔 NEW: Station ID Support** - Use INARA Station ID for direct access
  - Enter station ID (e.g., "1063226") instead of carrier name
  - Faster and more reliable than name search
  - Perfect for carriers with complex names or when search returns wrong results
  - Automatically extracts carrier name and callsign from market page
- **🐛 Bug Fix** - Resolved issues with carriers that have special characters or long names
- **📝 Updated Documentation** - Added guide for finding Station ID

### Version 1.1.0 (2025-12-05)
- **✨ NEW: In-Game Overlay** - Display market data directly in Elite Dangerous
  - Yellow text on 50% opacity black background
  - Table format with fixed-width columns
  - Large section headers (BUY ORDERS / SELL ORDERS)
  - UPPERCASE commodity names for emphasis
  - Toggle on/off with button
- **📋 NEW: Dump/Clipboard Export** - Copy formatted market data to clipboard
  - Includes timestamp
  - Shows ALL orders (not limited like overlay)
  - Perfect for sharing on Discord or keeping records
- **📊 Enhanced Formatting** - Table layout with aligned columns
  - Fixed-width formatting: Commodity (25 chars) | Quantity (10 chars) @ Price (10 chars)
  - Right-aligned numbers for easy comparison
  - Professional appearance
- **🎨 Visual Improvements** - Better readability
  - UPPERCASE commodity names in overlay
  - Large headers for better visibility
  - Improved spacing and alignment

### Version 1.0.1
- Switched to scraping INARA's public pages (no API key required!)
- Simplified configuration (only carrier name needed)
- Improved error messages

### Version 1.0.0
- Initial release
- Auto-refresh every 30 seconds
- Manual refresh button
- Display buy and sell orders
- Configuration through EDMC preferences
