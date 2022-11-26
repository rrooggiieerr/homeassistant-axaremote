# Home Assistant AXA Remote integration

Home Assistant integration to controll AXA Remote window openers over the
serial interface.

## Hardware

If you power the AXA Remote using batteries you can connect the Serial 3.3 or
5 Volts to position 1 or 6 of the RJ25 connector, ground to position 2 or 5 of
the RJ25 connector and RX/TX to position 3 or 4.
 
If you power the AXA Remote with the aditional external power adapter you can
use a LIN-bus controller to act as a level converter.

## Installation

- Copy the `custom_components/axaremote` directory of this repository into the
`config/custom_components/` directory of you Home Assistant installation
- Restart Home Assistant
- After restarting go to **Settings** then **Devices & Services**
- Select **+ Add Integration** and type in *AXA Remote*
- Select the serial port or enter the path manually
- Select **Submit**

When your wiring is right a new AXA Remote integration will now be added to
your Integrations view. If your wiring is not right you will get an *Failed to
connect* error message.