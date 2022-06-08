# A light resistor on A0 for optical tachometer
# 2022-06-08
# https://github.com/kreier/fan_tachometer
#
# Edition: 4 segments on a hand powered centrifuge

import time
import analogio
from digitalio import DigitalInOut, Direction
from board import *
import gc

pin = analogio.AnalogIn(A0)
led = DigitalInOut(C13)
led.direction = Direction.OUTPUT

FPS        = 1
SAMPLERATE = 2000
POINTSMINMAX = 20
THRESHOLD    = 40


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
    countOutput = 0
    plotOutput = []
    for i in range(50):
        plotOutput.append(0)
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
            if currentValue > currentAverage + THRESHOLD:
                lastReading = 1
                rpm += 1
        else:
            if currentValue < currentAverage - THRESHOLD:
                lastReading = 0

        # Prepare for 100Hz output with 2000 sample rate
        if count < 10:
            pass
        elif count < 50:
            plotOutput[count-10] = currentValue
        elif count < 60:
            plotOutput[count-10] = currentAverage

        # The printout part with FPS
        if (time.monotonic_ns() - printTime) > (1_000_000_000 / FPS):
            led.value = False

            # Calculate boundaries
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

            # Some output options
            #print("RPM value: ", rpm, "rounds: ", count, "GC: ", gc.mem_free(), "Current value", currentValue, " - ", currencAverage)
            #print("(",currentValue,",",currencAverage,",",gc.mem_free(),")")
            #print("(", currentValue, ",", currentAverage, ",", rpm, ")",sep="")
            #print("(", currentValue, ",", currentAverage, ")",sep="")
            #print("(", currentValue, ",", currentAverage, ",", currentMin, ",", currentMax, ")",sep="")

            # Normalized for plot
            normalized = (currentValue - currentMin) / range * 16000
            #print("(", normalized, ")",sep="")

            # Frequency and rpm in longer intervals
            #print("Frequency:", rpm * FPS , "Hz,  RPM value:", rpm * FPS * 60)
            print("({0})".format(rpm/4*60))

            # Output the first 40 samples from 2000
            #plotValue = plotOutput[countOutput]
            #plotValue = (plotOutput[countOutput] - currentMin) / range * 15000
            #print("(", plotValue, ")", sep="")
            #print("(", plotValue, ",", (currentAverage - currentMin) / range * 15000, ",", (currentMax - currentMin) / range * 15000, ")",sep="")
            countOutput += 1
            if countOutput >= 50:
                countOutput = 0
                count = 0

            rpm = 0
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
