import aiy.audio
import aiy.voicehat
import time
import audio
import os

led = aiy.voicehat.get_led()


def welcome():
    led.set_state(led.ON)
    audio.play_file('./audio/welcome.wav', 90)
    led.set_state(led.BLINK)

def record_command():
    led.set_state(led.PULSE_QUICK)
    aiy.audio.record_to_wave('./tmp/rec.wav',3)
    audio.play_file('./tmp/rec.wav',100)
    led.set_state(led.BLINK)

def run():
    welcome()
    record_command()

def main():
    # Prepareation
    button = aiy.voicehat.get_button()
    led.set_state(led.BLINK)
    os.makedirs('./tmp/', exist_ok=True)

    button = button.on_press(run)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        led.set_state(led.OFF)
        led.stop()

if __name__ == '__main__':
    main()

