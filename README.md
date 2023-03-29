# Home Assistant AXA Remote integration

Home Assistant integration to control AXA Remote window openers over the
serial interface.

## Hardware

If you power the AXA Remote using batteries you can connect the Serial 3.3 or
5 Volts to position 1 or 6 of the RJ25 connector, ground to position 2 or 5 of
the RJ25 connector and RX/TX to position 3 or 4.
 
If you power the AXA Remote with the aditional external power adapter you can
use a LIN-bus controller to act as a level converter.

## Installation

### HACS
- Go to your **HACS** view in Home Assistant and then to **Integrations**
- Open the **Custom repositories** menu
- Add this repository URL to the **Custom repositories** and select
**Integration** as the **Category**
- Click **Add**
- Close the **Custom repositories** menu
- Select **+ Explore & download repositories** and search for *AXA Remote*
- Select **Download**
- Restart Home Assistant

### Manually
- Copy the `custom_components/axaremote` directory of this repository into the
`config/custom_components/` directory of your Home Assistant installation
- Restart Home Assistant

##  Adding a new AXA Remote window opener
- After restarting go to **Settings** then **Devices & Services**
- Select **+ Add integration** and type in *AXA Remote*
- Select the serial port or enter the path manually
- Select **Submit**

When your wiring is right a new AXA Remote integration and device will now be
added to your Integrations view. If your wiring is not right you will get a
*Failed to connect* error message.

Do you enjoy using this Home Assistant integration? Then consider supporting
my work:\
[<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >](https://www.buymeacoffee.com/rrooggiieerr)  
