# [Phase 1] 011 Read a Joystick with ADC

> In order to control the robot, there should be user input. In this case, it is a joystick. I will show how to get the input and generate the output for the oscilloscope.

The input of the system is a joystick. As shown in the image below.

![Image 1][1]

This joystick has three outputs: X, Y and Switch on press. It can be seen as a variable resistor while the trimmer is the stick. Therefore, the output voltage changes as the user moves the stick.

MSP430G2553 has 10-bit ADC embedded and I will use this module to read the X and Y inputs. In order to represent the reading from the joystick, I will generate PWM signals whose duty cycle depends on the voltage input. The connection is shown below:

![schematic][2]

P1.6 and P1.7 have the analogue input function as said on the user guide. P1.2 and P2.1 are the timer outputs for Timer 1.1 and Timer 2.1 while the Timer 1.0 and Timer 2.0 are the comparison timers to generate the outputs.

The process of continuous ADC reading is described in the official exmaple code. At first, the ADC10 is initialised while set A6 and A7 as the analogue input ports. All detailed settings and initialisation sequences can be found in the official user manual.

```c
void ADC10_init(void){
    ADC10CTL1 |= INCH_7 + CONSEQ_1;                     // INCH7, Enable Single Sequence Conversion
    ADC10CTL0 = ADC10SHT_2 + MSC + ADC10ON + ADC10IE;   // 16xSample&Hold, Multiple sample and conversion, ADCON, Interrupt En
    ADC10DTC1 = 0x02;                                   // 2 conversions
    ADC10AE0 |= BIT7 | BIT6;                            // A6 and A7
}
```

Then the following sequence will be called inside an infinite main loop.

```c
void ADC10_loop(void){
    ADC10SA = (uint16_t)X_Y;        // Data buffer start
    ADC10CTL0 |= ENC + ADC10SC;     // Sampling and conversion start
    while (ADC10CTL1 & ADC10BUSY);  // Wait if ADC10 core is active
    X = X_Y[0]>>2;                  // 10-bit to 8-bit - X
    Y = X_Y[1]>>2;                  // 10-bit to 8-bit - Y
    TA0CCR1 = X;                    // Assign X PWM duty cycle
    TA1CCR1 = Y;                    // Assign Y PEM duty cycle
    __bis_SR_register(GIE);         // Enable Global Interrupt for ADC10 on every cycle
}
```

As the outputs, two timers will be used to generate PWM waveforms for both X and Y inputs. GPIO P1.2 and P2.1 will be set as outputs with the second functionality.

```c
void GPIO_init(void){
    P1DIR |= BIT2;
    P1SEL |= BIT2;
    P2DIR |= BIT1;
    P2SEL |= BIT1;
}
void PWM_init(void){
    /*** Timer0_A Set-Up ***/
    TA0CCR0 |= 0xff - 1;		// Maximum duty cycle
    TA0CCTL1 |= OUTMOD_7;
    TA0CCR1 = 0;                // Init with 0% duty cycle
    TA0CTL |= TASSEL_2 + MC_1;

    /*** Timer1_A Set-Up ***/
    TA1CCR0 |= 0xff - 1;       // Maximum duty cycle
    TA1CCTL1 |= OUTMOD_7;
    TA1CCR1 = 0;                // Init with 0% duty cycle
    TA1CTL |= TASSEL_2 + MC_1;
}
```

Therefore, all the code will be:

```c
#include <msp430.h>
#include <stdint.h>

void ADC10_init(void);
void ADC10_loop(void);

uint8_t X, Y;
uint8_t state = 0;
volatile uint16_t X_Y[2] = {0}; // {X, Y}

void CLK_init(void);
void GPIO_init(void);
void PWM_init(void);

/**
 * main.c
 */
int main(void)
{
	WDTCTL = WDTPW | WDTHOLD;	// stop watchdog timer
	
	CLK_init();
	GPIO_init();
	PWM_init();
	ADC10_init();

	__bis_SR_register(GIE);

	while(1){
	    ADC10_loop();
	}

	return 0;
}

/* Configure the Clock
 * to run it from DCO @16MHz and SMCLK = DCO / 4
 * */
void CLK_init(void){
    BCSCTL1 = CALBC1_16MHZ;
    DCOCTL = CALDCO_16MHZ;
    BCSCTL2 = DIVS_2 + DIVM_0;
}

void GPIO_init(void){
    P1DIR |= BIT2;
    P1SEL |= BIT2;
    P2DIR |= BIT1;
    P2SEL |= BIT1;
}

void PWM_init(void){
    /*** Timer0_A Set-Up ***/
    TA0CCR0 |= 0xff - 1;		// Maximum duty cycle
    TA0CCTL1 |= OUTMOD_7;
    TA0CCR1 = 0;                // Init with 0% duty cycle
    TA0CTL |= TASSEL_2 + MC_1;

    /*** Timer1_A Set-Up ***/
    TA1CCR0 |= 0xff - 1;       // Maximum duty cycle
    TA1CCTL1 |= OUTMOD_7;
    TA1CCR1 = 0;                // Init with 0% duty cycle
    TA1CTL |= TASSEL_2 + MC_1;
}

void ADC10_init(void){
    ADC10CTL1 |= INCH_7 + CONSEQ_1;                     // INCH7, Enable Single Sequence Conversion
    ADC10CTL0 = ADC10SHT_2 + MSC + ADC10ON + ADC10IE;   // 16xSample&Hold, Multiple sample and conversion, ADCON, Interrupt En
    ADC10DTC1 = 0x02;                                   // 2 conversions
    ADC10AE0 |= BIT7 | BIT6;                            // A6 and A7
}

void ADC10_loop(void){
    ADC10SA = (uint16_t)X_Y;        // Data buffer start
    ADC10CTL0 |= ENC + ADC10SC;     // Sampling and conversion start
    while (ADC10CTL1 & ADC10BUSY);  // Wait if ADC10 core is active
    X = X_Y[0]>>2;                  // 10-bit to 8-bit - X
    Y = X_Y[1]>>2;                  // 10-bit to 8-bit - Y
    TA0CCR1 = X;
    TA1CCR1 = Y;
    __bis_SR_register(GIE);         // Enable Global Interrupt for ADC10 on every cycle
}
```

[1]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/16/1.png "The joystick module"
[2]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/16/2.png "Schematic of the joystick example"
