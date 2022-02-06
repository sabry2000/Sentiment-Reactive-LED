import asyncio
import socket

import time
from rpi_ws281x import PixelStrip, Color
import argparse

import RPi.GPIO as GPIO 

# LED strip configuration:
LED_COUNT = 16        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
ENGAGE_PIN = 17
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
GPIO.setup(ENGAGE_PIN, GPIO.IN)    # set GPIO25 as input (button) 

colors = []
starts = []
ends = []
durations = []

async def receiver():
    global colors, starts, ends

    print('Waiting for connection')
    websocket = await websockets.connect('https://192.168.0.24:8765')
    print('Established Connection')
    await websocket.send("RPi")

    numOfElements = int(await websocket.recv())
    print('Number of Elements is' + numOfElements)
    await websocket.send("OK")
    for _ in range(numOfElements):
        color = await websocket.recv()
        start = int(await websocket.recv())
        end = int(await websocket.recv())
        duration = start - end

        colors.append(color)
        starts.append(start)
        ends.append(end)
        durations.append(duration)

def adjustColors(color, R, G, B):
    if color == 'r':
        [R, G, B] = adjust(R,G,B)
    elif color == 'g':
        [G, R, B] = adjust(G,R,B)
    else:
        [B, R, G] = adjust(B,R,G)
    return R, G, B

def adjust(plus,minus,zero):
    if plus < 255:
        plus = plus+1
    else:
        if minus > 0:
            minus = minus - 1
        elif zero > 0:
            zero = zero - 1
        else:
            plus = plus - 10

    return plus,minus,zero


# Define functions which animate LEDs in various ways.
def colorWipe(i, strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    print("Putting color {0} on LED #{1}".format(str(color),i))
    strip.setPixelColor(i, color)
    strip.show()
    time.sleep(wait_ms / 1000.0)

# Main program logic follows:
if __name__ == '__main__':
    try:
        while True:            # this will carry on until you hit CTRL+C  
            if GPIO.input(ENGAGE_PIN):
                # Process arguments
                parser = argparse.ArgumentParser()
                parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
                args = parser.parse_args()


                # asyncio.get_event_loop().run_until_complete(receiver())

                host='192.168.0.30' #client ip
                port = 4005

                server = ('192.168.0.24', 4000)

                print('Waiting for connection')
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind((host,port))
                print('Established Connection')

                s.sendto("RPi".encode('utf-8'), server)
                print("Sent RPi");

                data, addr = s.recvfrom(1024)
                numOfElements = int(data.decode('utf-8'))
                print('Number of Elements is ' + str(numOfElements))
                s.sendto("OK".encode('utf-8'), server)

                for i in range(numOfElements):
                    data, addr = s.recvfrom(1024)
                    color = data.decode('utf-8')
                    print("Received " + color)

                    #s.sendto("OK".encode('utf-8'), server)

                    data, addr = s.recvfrom(1024)
                    data = data.decode('utf-8')
                    start = int(data)
                    print("Received " + data)

                    #s.sendto("OK".encode('utf-8'), server)

                    data, addr = s.recvfrom(1024)
                    data = data.decode('utf-8')
                    end = int(data)
                    print("Received " + data)

                    #s.sendto("OK".encode('utf-8'), server)

                    duration = end - start

                    colors.append(color)
                    starts.append(start)
                    ends.append(end)
                    durations.append(duration)
                    print(i)

                    #time.sleep(500)
                    s.sendto("OK".encode('utf-8'), server)

                s.close()

                # Create NeoPixel object with appropriate configuration.
                strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
                # Intialize the library (must be called once before other functions).
                strip.begin()

                print('Press Ctrl-C to quit.')
                if not args.clear:
                    print('Use "-c" argument to clear LEDs on exit')

                try:
                    R = 255
                    G = 255
                    B = 255
                    time.sleep(starts[0] / 1000.0)
                    print(durations)
                    for i, color in enumerate(colors):
                        [R, G, B] = adjustColors(color, R, G, B)
                        colorWipe(i % (LED_COUNT+1), strip, Color(R, G, B), durations[i])

                except KeyboardInterrupt:
                    if args.clear:
                        colorWipe(strip, Color(0, 0, 0), 10)
    finally:                   # this block will run no matter how the try block exits  
        GPIO.cleanup()         # clean up after yourself  





