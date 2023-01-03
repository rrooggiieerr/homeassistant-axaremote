[![](https://img.shields.io/github/v/release/rrooggiieerr/homeassistant-axaremote.svg?include_prereleases&style=for-the-badge)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![](https://img.shields.io/badge/MAINTAINER-%40rrooggiieerr-41BDF5?style=for-the-badge)](https://github.com/rrooggiieerr)

# Home Assistant AXA Remote integration

Home Assistant integration to control AXA Remote window openers over the
serial interface.

## Hardware

If you power the AXA Remote using batteries you can connect the Serial 3.3 or
5 Volts to position 1 or 6 of the RJ25 connector, ground to position 2 or 5 of
the RJ25 connector and RX/TX to position 3 or 4.
 
If you power the AXA Remote with the aditional external power adapter you can
use a LIN-bus controller to act as a level converter.

##  Adding a new AXA Remote window opener
- After restarting go to **Settings** then **Devices & Services**
- Select **+ Add Integration** and type in *AXA Remote*
- Select the serial port or enter the path manually
- Select **Submit**

When your wiring is right a new AXA Remote integration and device will now be
added to your Integrations view. If your wiring is not right you will get a
*Failed to connect* error message.

Do you enjoy using this Home Assistant integration? Then consider supporting
my work:\
[<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >](https://www.buymeacoffee.com/rrooggiieerr)  
