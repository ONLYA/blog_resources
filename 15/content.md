![heading][https://cdn.jsdelivr.net/gh/onlya/blog_resources/15/1.jpg]
# LPC55S69-EVK first impression & Quadcopter initial thoughts

> LPC55S69-EVK contains a chip with two Arm Cortex-M33 Cores. It also features TrustZone technology. With those, a quite powerful quadcopter flight controller can be created. And I will continue on the work towards the final flight controller with a step-by-step learning process.

## Motivation
There was once a time when I was so obsessed with creating a quadcopter on my own after I have watched the video series by [Joop Brokking][u1]. I open the Mouser website as normal to search for the fitted microcontroller for the quadcopter, LPC55S6X series MCUs seem to have a good performance and rich connectivities with a low price. As I had a look at the datasheet of the chip, I was impressed. So I ordered the evaluation board immediately and waited for the delivery.

## First setup of LPC55S69-EVK
During the waiting time, I was eager to develop with the board so I followed [the instructions said on the NXP website][u2] and set up the IDE environment before the delivery arrived. After the environment was set up, I took deep research into the User Manual of the chip. Instead of coding with API given directly, I prefer to play with the registers so that I can have a good understanding and better control of the chip. After days of researching the user guide, API codes and code examples, the development board finally arrived.

As a start, I powered the board up to play with the LED and buttons. It seemed that the LED still blinked when I pressed the button to make it hold at a colour. That's a bit alarming about the program logic. It is evident that the blink is controlled by a standard timer interrupt, which makes the blinking happen all the time.

I connected the board to my laptop and flashed a "Hello_World" demo program into it. It came up with errors with RedlinkServerException that indicates that the redlink server was not open. That's weird. I checked my firewall to enable the server to pass through both private and public network and even added the executed file manually, but those did nothing. After searching on the Internet, from two posts on the NXP forum: [1][u3] and [2][u4], I reinstalled the IDE and make the working directory of the IDE to a completely different folder. Finally, it works like charm.

## What makes LPC55S6x special?
Firstly, this is my first time to develop a dual-core Cortex-M33 microcontroller. Additionally, its high-end structure is a great upgrade for me from ATMega, MSP430 and ATSAMD21 (Cortex-M0+).

Secondly, it contains many features with high performance while the power consumption is low. As shown in the block diagram given in the datasheet,

![LPC55S6x block diagram][1]

There are two Cortex-M33 cores. One is a mainstream core with Floating Point Unit (FPU), Memory Protection Unit (MPU) and a math processing interface. The other one is just a core. A mailbox is used to communicate between two cores. There are independent Nested Vector Interrupt Controllers (NVIC) on both cores. They make the developer distribute the work to different cores according to the workload and types of jobs that the core is capable of. Direct Memory Access (DMA) can make the readings from communication interfaces like I2C, SPI and UART quicker to be accessed by the program. There are 5 standard timers with other types of timers, which makes the chip able to process with PWM or PPM signals. The communication interfaces are flexible so the user does not have to limit their routings and programming for series connections.  SDIO interface makes it able to process files with an SD card.

If we look at the block diagram of Cortex-M33 core,

![Cortex-M33 Block Diagram][2]

TrustZone is included to have wide access control. The use of the TrustZone will be talked about later in my blog.

## Quadcopter Thoughts
Now, I have got a development board. How do I start to develop a quadcopter flight controller?

I draw a diagram for a quadcopter flight controller.

![Quadcopter Block Diagram][3]

From the block diagram and my research in the sensors, there is a list of features that need to be learnt and implemented:
* Timers
  * CAPTURE to read PWM or PPM inputs from the receiver
  * timer interrupts to generate PWM outputs for motor control
* HS-SPI w/ DMA is needed for a 9-DOF IMU (ICM-20948) and Telemetry <- SPI x 2
  * The API library is needed to communicate with the IMU
* I2C w/ DMA is needed for the other chained sensors including temperature, pressor, Time-of-Flight sensors
* DSP features are needed to process the data with low-pass filtering and other techniques
* Multi-core should interact so that one core only to process data and the other only to handle the hardware interface
* SDIO is required to retrieve data from an SD card and log files into the card
* NVIC or FreeRTOS is essential as there are a lot of tasks that need to be processed at the "same" time
* UART interface should be looked at for a GPS module (Hornet ORG1411)
* (Optional) TrustZone is required to protect core program from being accidentally corrupted.

I will learn, understand examples, test with my own examples and build the functionality for each of the features listed above in the following blog posts.

There are not many videos and tutorials to work with LPC55S6x MCUs as it is a relatively new product released by NXP. Most of the developers develop cores from Cortex-M0 to Cortex-M7. So I have to learn it nearly by myself. Luckily, there is a Youtuber called [embeddedpro][u5] who seems to develop NXP products publishing [a list of videos about basic walkthrough and explanation of LPC55S69-EVK board][u6]. 


[1]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/15/2.png "Block diagram of LPC55S6x MCU family"
[2]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/15/3.png "Block diagram of Arm Cortex-M33 Core"
[3]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/15/4.jpg "Block Diagram of a quadcopter"

[u1]:https://www.youtube.com/user/MacPuffdog
[u2]:https://www.nxp.com/document/guide/get-started-with-the-lpc55s69-evk:GS-LPC55S69-EVK
[u3]:https://community.nxp.com/t5/MCUXpresso-General/MCUXpresso-Failing-to-discover-CMISIS-DAP-probe-on-Eval-Boards/m-p/930406
[u4]:https://community.nxp.com/t5/MCUXpresso-General/LPC-Link-Target-Discovery-not-working/m-p/814828
[u5]:https://www.youtube.com/channel/UCGb0cwww_CENTI1wgo6FJTw
[u6]:https://www.youtube.com/playlist?list=PL0zq7qRU_mUvYH4QWqRr8s_iC0JvHr8jX

References:
* [Joop Brokking's Website][https://www.brokking.net/]
* [LPC55S6x product page][https://www.nxp.com/products/processors-and-microcontrollers/arm-microcontrollers/general-purpose-mcus/lpc5500-cortex-m33/high-efficiency-arm-cortex-m33-based-microcontroller-family:LPC55S6x]
* [Arm Cortex-M33 Core][https://www.arm.com/products/silicon-ip-cpu/cortex-m/cortex-m33]
* [embeddedpro's LPC55S69-EVK tutorial][https://www.youtube.com/playlist?list=PL0zq7qRU_mUvYH4QWqRr8s_iC0JvHr8jX]