import argparse
from hoverboard.toolchains import get_tool
from hoverboard.programmers.avrdude import AVRDude


def main():
    """
    Main entry point of the avrdude example
    """
    # Locate avrdude
    avrdude = get_tool('avrdude')
    assert isinstance(avrdude, AVRDude), "Wrong tool returned from get_tool"

    # Parse arguments
    parser = argparse.ArgumentParser(description="A mock example that uses avrdude to read an Uno's flash, and then "
                                                 "reprogram it back to the flash.")
    parser.add_argument('port', help='The serial port the Arduino Uno is connected to')
    args = parser.parse_args()

    arduino = avrdude.create_arduino_target(args.port)

    # Read and program
    data = arduino.read('flash')
    arduino.program('flash', data)


if '__main__' == __name__:
    main()
