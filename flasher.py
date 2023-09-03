import serial
import time

# Define your commands, just like in the C code
CMD_IAP_ERASE = 0x81
CMD_IAP_PROM = 0x80
CMD_IAP_VERIFY = 0x82
CMD_IAP_END = 0x83

CHUNK_LEN = 32
# Initialize serial port
ser = serial.Serial('/dev/ttyACM0', 460800, timeout=5)


def send_command(cmd, data=[]):
    packet = [0x57, 0xab, cmd, len(data), 0x00, 0x00]
    if len(data) > 0:
        packet += data
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    ser.write(bytearray(packet))


def read_response():
    buff = ser.read(2)
    print(buff)
    return buff


def send_firmware(firmware_path):
    with open(firmware_path, 'rb') as f:
        firmware_data = f.read()

    # Erase the flash
    send_command(CMD_IAP_ERASE)
    if read_response() != b'\x00\x00':
        print("Failed to erase flash!")
        return

    # Program the flash
    for i in range(0, len(firmware_data), CHUNK_LEN):
        chunk = firmware_data[i:i + CHUNK_LEN]
        send_command(CMD_IAP_PROM, list(chunk))
        if read_response() != b'\x00\x00':
            print(f"Failed to program chunk at {i}!")
            return

    # Verify the flash
    for i in range(0, len(firmware_data), CHUNK_LEN):
        chunk = firmware_data[i:i + CHUNK_LEN]
        send_command(CMD_IAP_VERIFY, list(chunk))
        if read_response() != b'\x00\x00':
            print(f"Failed to verify chunk [{i}-{i+CHUNK_LEN}]!")
            return

    # End the programming
    send_command(CMD_IAP_END)
    #if read_response() != b'\x00\x00':
    #    print("Failed to end programming!")
     #    return

    print("Firmware successfully sent!")


if __name__ == "__main__":
    firmware_path = "firmware.bin"
    send_firmware(firmware_path)
