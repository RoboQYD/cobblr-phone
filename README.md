A Phone application for written for the [Cobblr framework](http://github.com/TheQYD/cobblr).

![PiPhone](https://raw.githubusercontent.com/TheQYD/cobblr/master/photos/cobblr_phone.jpg)

# Hardware
Here's a list of hardware necessary to make the phone work:

 - 1 [Raspberry Pi](https://www.adafruit.com/products/2358)
 - 1 [Adafruit 2.8in PiTFT](https://www.adafruit.com/products/1601)
 - 1 [(Optional) Adafruit Powerboost 1000C](https://www.adafruit.com/products/2465)
 - 1 [(Optional) Adafruit Lipo Battery 2500mAh](https://www.adafruit.com/products/328)
 
The phone software is based on Dave Hunt's [PiPhone](http://www.davidhunt.ie/piphone-a-raspberry-pi-based-smartphone). The wiring is the same, and it can be found [here](https://learn.adafruit.com/piphone-a-raspberry-pi-based-cellphone/pi-setup?view=all). I was inspired by Dave's work, and wanted to add some features. I ended up writing a small framework around the core of the code. Some of Cobblr's improvements include:
 
 - It's faster.
 - It can receive calls.
 - The framework itself supports multiple apps.
 - It can be extended a bit easier.
 
Dave inspired me, so I want to make sure I mention him. I wouldn't have thought of it on my own.

# How to Install

Follow the directions to install the [Cobblr framework](http://github.com/TheQYD/cobblr). The PiTFT should be configured in portrait mode (no rotation). Once that's finished, and the framework is installed, execute this command:

```
sudo cobblr install cobblr-phone
```

# More

Though not required, I've made a polycarbonate and aluminum body for it. The CADs are avaliable [here](https://github.com/TheQYD/CAD/tree/master/cobblr-phone). Other applications were made to work with the cobblr-phone:

- [cobblr-calculator](http://gihub.com/TheQYD/cobblr-calculator)
- [cobblr-music](http://gihub.com/TheQYD/cobblr-calculator)

# License
PiPhone is available under the MIT license. See the LICENSE file for more info. Make it better!
