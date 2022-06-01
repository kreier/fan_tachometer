# fan_tachometer
Determination of RPM of a fan or any rotation object with a photo resistor (up to 100 Hz or 6000 rpm). It is inspired by https://github.com/emwdx/fan_tachometer

## Hardware

We use a photoresistor board and take the analog output as input for a STM32F411 black pill board analog input, running Circuitpython.

### Limitations

A photoresistor has a latency of around 10 ms (according to [eepower.com](https://eepower.com/resistor-guide/resistor-types/photo-resistor/#) and [wikipedia](https://en.wikipedia.org/wiki/Photoresistor). So the maximum measureable frequency should be around 10 Hz or 6000 rpm. The ADC needs 1ms to sample a 12 bit signal. The setup:

(picture)

## Software

Written in Circuitpython and the analog value connected to pin A0:

``` py
# light resistor on A0 for optical tachometer

import time
import analogio
from digitalio import DigitalInOut, Direction
from board import *
import gc

pin = analogio.AnalogIn(A0)
led = DigitalInOut(C13)
led.direction = Direction.OUTPUT

FPS        = 100
SAMPLERATE = 2000
POINTSMINMAX = 20


def main():
    print("Start RPM measurement in a second")
    time.sleep(1.0)
    
    # variables to define
    locationAverage = 0
    currentMax = 0
    currentMin = 100000
    counterMinMax = 0
    lastReading = 0
    rpm = 0
    count = 0
    Min = []
    Max = []
    for i in range(POINTSMINMAX):
        Min.append(100000)
        Max.append(0)
    readingsAverage = []
    for i in range(100):
        readingsAverage.append(0)
    printTime = time.monotonic_ns()

    # Sample and output loop
    while True:
        # measure the light intensity
        currentValue = pin.value
        
        # determine the present average value
        readingsAverage[locationAverage] = currentValue
        locationAverage += 1
        if locationAverage > 99:
            locationAverage = 0
        currentAverage = 0
        for i in range(100):
            currentAverage += readingsAverage[i]
        currentAverage = currentAverage / 100
        
        # determine boundaries
        if currentValue > currentMax:
            currentMax = currentValue
        if currentValue < currentMin:
            currentMin = currentValue
        
        if lastReading == 0:
            if currentValue > currentAverage:
                lastReading = 1
                rpm += 1
        else:
            if currentValue < currentAverage:
                lastReading = 0

        # The printout part with FPS
        if (time.monotonic_ns() - printTime) > (1000_000_000 / FPS):
            led.value = False
            Min[counterMinMax] = currentMin
            Max[counterMinMax] = currentMin
            for i in range(POINTSMINMAX):
                if Min[i] < currentMin:
                    currentMin = Min[i]
                if Max[i] > currentMax:
                    currentMax = Max[i]
            range = currentMax - currentMin
            counterMinMax += 1
            if counterMinMax >= POINTSMINMAX:
                counterMinMax = 0
            #print("RPM value: ", rpm, "rounds: ", count, "GC: ", gc.mem_free(), "Current value", currentValue, " - ", currencAverage)
            #print("(",currentValue,",",currencAverage,",",gc.mem_free(),")")
            #print("(", currentValue, ",", currentAverage, ",", rpm, ")",sep="")
            #print("(", currentValue, ",", currentAverage, ")",sep="")
            #print("(", currentValue, ",", currentAverage, ",", currentMin, ",", currentMax, ")",sep="")
            
            # Normalized for plot
            normalized = (currentValue - currentMin) / range * 16000
            print("(", normalized, ")",sep="")


            # Frequency and rpm in longer intervals
            #print("Frequency:", rpm * FPS , "Hz,  RPM value:", rpm * FPS * 60)
            rpm = 0
            count = 0
            currentMax = 0
            currentMin = 100000
            printTime = time.monotonic_ns()
            led.value = True
        #print("(",pin.value,")")
        count += 1
        time.sleep(1/SAMPLERATE)

    pin.deinit()

if __name__ == '__main__':
    main()

```
