# Home Assistant integration for AXA Remote window openers

![Python][python-shield]
[![GitHub Release][releases-shield]][releases]
[![Licence][license-shield]][license]
[![Maintainer][maintainer-shield]][maintainer]
[![Home Assistant][homeassistant-shield]][homeassistant]
[![HACS][hacs-shield]][hacs]  
[![Github Sponsors][github-shield]][github]
[![PayPal][paypal-shield]][paypal]
[![BuyMeCoffee][buymecoffee-shield]][buymecoffee]
[![Patreon][patreon-shield]][patreon]

## Introduction

Home Assistant integration to control AXA Remote window openers over the serial interface or serial
to network bridges like [esp-link](https://github.com/jeelabs/esp-link).

## Features

- Installation/Configuration through Config Flow UI
- Set the close time of your window opener, the open time is derived from this
- Position the window opener on any position along the way

## Hardware

If you power the AXA Remote using batteries you can connect the Serial 3.3 or 5 Volts to position 1
or 6 of the RJ25 connector, ground to position 2 or 5 of the RJ25 connector and RX/TX to position 3
or 4.
 
If you power the AXA Remote with the additional external power adapter you can use a LIN-bus
controller to act as a level converter.

## Installation

### HACS

The recommended way to install this Home Assistant integration is by using [HACS][hacs].
Click the following button to open the integration directly on the HACS integration page.

[![Install AXA Remote from HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rrooggiieerr&repository=homeassistant-axaremote&category=integration)

Or follow these instructions:

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

## Adding a new AXA Remote window opener

- After restarting go to **Settings** then **Devices & Services**
- Select **+ Add integration** and type in *AXA Remote*
- Select the serial port or enter the path manually
- Set the close time of your device.
- Select **Submit**

When your wiring is right a new AXA Remote integration and device will now be
added to your Integrations view. If your wiring is not right you will get a
*Failed to connect* error message.

## Contributing

If you would like to use this Home Assistant integration in youw own language you can provide me
with a translation file as found in the `custom_components/axaremote/translations` directory.
Create a pull request (preferred) or issue with the file attached.

More on translating custom integrations can be found
[here](https://developers.home-assistant.io/docs/internationalization/custom_integration/).

## Support my work

Do you enjoy using this Home Assistant integration? Then consider supporting my work using one of
the following platforms, your donation is greatly appreciated and keeps me motivated:

[![Github Sponsors][github-shield]][github]
[![PayPal][paypal-shield]][paypal]
[![BuyMeCoffee][buymecoffee-shield]][buymecoffee]
[![Patreon][patreon-shield]][patreon]

## Hire me

If you would like to have a Home Assistant integration developed for your product or are in need
for a freelance Python developer for your project please contact me, you can find my email address
on [my GitHub profile](https://github.com/rrooggiieerr).

---

[python-shield]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[releases]: https://github.com/rrooggiieerr/homeassistant-axaremote/releases
[releases-shield]: https://img.shields.io/github/v/release/rrooggiieerr/homeassistant-axaremote?style=for-the-badge
[license]: ./LICENSE
[license-shield]: https://img.shields.io/github/license/rrooggiieerr/homeassistant-axaremote?style=for-the-badge
[maintainer]: https://github.com/rrooggiieerr
[maintainer-shield]: https://img.shields.io/badge/MAINTAINER-%40rrooggiieerr-41BDF5?style=for-the-badge
[homeassistant]: https://www.home-assistant.io/
[homeassistant-shield]: https://img.shields.io/badge/home%20assistant-%2341BDF5.svg?style=for-the-badge&logo=home-assistant&logoColor=white
[hacs]: https://hacs.xyz/
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[paypal]: https://paypal.me/seekingtheedge
[paypal-shield]: https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white
[buymecoffee]: https://www.buymeacoffee.com/rrooggiieerr
[buymecoffee-shield]: https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black
[github]: https://github.com/sponsors/rrooggiieerr
[github-shield]: https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA
[patreon]: https://www.patreon.com/seekingtheedge/creators
[patreon-shield]: https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white
