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
* Copy the `custom_components/axaremote` directory of this repository into the
`config/custom_components/` directory of you Home Assistant installation 