![heading][https://cdn.jsdelivr.net/gh/onlya/blog_resources/15/1.png]
# LPC55S69-EVK first impression & Quadcopter plan

> LPC55S69-EVK contains a chip with two Arm Cortex-M33 Cores. It also features Secure Zone technology. With those, a quite powerful quadcopter flight controller can be created. And I will continue on the work towards the final flight controller with a step-by-step learning process.

## Motivation
There was once a time when I was so obsessed with creating a quadcopter on my own after I have watched the video series by [Joop Brokking][u1]. I open the Mouser website as normal to search for the fitted microcontroller for the quadcopter, LPC55S6X series MCUs seem to have a good performance and rich connectivities with a low price. As I had a look at the datasheet of the chip, I was impressed. So I ordered the evaluation board immediately and waited for the delivery.

## First setup of LPC55S69-EVK
During the waiting time, I was eager to develop with the board so I followed [the instructions said on the NXP website][u2] and set up the IDE environment before the delivery arrived. After the environment was set up, I took deep research into the User Manual of the chip. Instead of coding with API given directly, I prefer to play with the registers so that I can have a good understanding and better control of the chip. After days of researching the user guide, API codes and code examples, the development board finally arrived.

As a start, I powered the board up to play with the LED and buttons. It seemed that the LED still blinked when I pressed the button to make it hold at a colour. That's a bit alarming about the program logic. It is evident that the blink is controlled by a standard timer interrupt, which makes the blinking happen all the time.

I connected the board to my laptop and flashed a "Hello_World" demo program into it. It came up with errors with RedlinkServerException that indicates that the redlink server was not open. That's weird. I checked my firewall to enable the server to pass through both private and public network and even added the executed file manually, but those did nothing. After searching on the Internet, from two posts on the NXP forum: [1][u3] and [2][u4], I reinstalled the IDE and make the working directory of the IDE to a completely different folder. Finally, it works like charm.

## What makes LPC55S6x special?
Firstly, this is my first time to develop a dual-core Cortex-M33 microcontroller. Additionally, its high-end structure is a great upgrade for me from ATMega, MSP430 and ATSAMD21 (Cortex-M0+).

Secondly, it contains many features with high performance while the power consumption is low. As shown in the block diagram,

![LPC55S6x block diagram][1]



[1]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/15/2.png "Block diagram of LPC55S6x MCU family"

[u1]:https://www.youtube.com/user/MacPuffdog
[u2]:https://www.nxp.com/document/guide/get-started-with-the-lpc55s69-evk:GS-LPC55S69-EVK
[u3]:https://community.nxp.com/t5/MCUXpresso-General/MCUXpresso-Failing-to-discover-CMISIS-DAP-probe-on-Eval-Boards/m-p/930406
[u4]:https://community.nxp.com/t5/MCUXpresso-General/LPC-Link-Target-Discovery-not-working/m-p/814828