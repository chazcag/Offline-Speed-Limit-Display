# gps_decoder.py - Naza protocol decoder for GPS data

import serial
import time
import math
from config import SERIAL_PORT, BAUD_RATE

class NazaDecoder:
    def __init__(self):
        self.state = 0
        self.message_id = 0
        self.payload_length = 0
        self.payload = []
        self.checksum_a = 0
        self.checksum_b = 0
        self.received_ck_a = 0
        self.received_ck_b = 0

    def decode(self, byte):
        if self.state == 0:  # Wait for header byte 1 (0x55)
            if byte == 0x55:
                self.state = 1
        elif self.state == 1:  # Header byte 2 (0xAA)
            if byte == 0xAA:
                self.state = 2
                self.checksum_a = 0
                self.checksum_b = 0
            else:
                self.state = 0
        elif self.state == 2:  # Message ID
            self.message_id = byte
            self.checksum_a = (self.checksum_a + byte) & 0xFF
            self.checksum_b = (self.checksum_b + self.checksum_a) & 0xFF
            self.state = 3
        elif self.state == 3:  # Payload length
            self.payload_length = byte
            self.checksum_a = (self.checksum_a + byte) & 0xFF
            self.checksum_b = (self.checksum_b + self.checksum_a) & 0xFF
            self.payload = []
            self.state = 4 if self.payload_length > 0 else 5
        elif self.state == 4:  # Payload bytes
            self.payload.append(byte)
            self.checksum_a = (self.checksum_a + byte) & 0xFF
            self.checksum_b = (self.checksum_b + self.checksum_a) & 0xFF
            if len(self.payload) == self.payload_length:
                self.state = 5
        elif self.state == 5:  # Checksum A
            self.received_ck_a = byte
            self.state = 6
        elif self.state == 6:  # Checksum B
            self.received_ck_b = byte
            self.state = 0
            if self.received_ck_a == self.checksum_a and self.received_ck_b == self.checksum_b:
                return self.process_message()
        return None

    def process_message(self):
        if self.message_id != 0x10 or self.payload_length != 0x3A:
            return None

        # Reliable XOR mask (keeps sats, fix=3, seq stable)
        xor_mask = self.payload[24]

        # Unmasked indices
        unmasked_indices = [48, 49, 56, 57]

        # Apply XOR only to masked bytes
        unxor_payload = [b ^ xor_mask if i not in unmasked_indices else b for i, b in enumerate(self.payload)]

        # Stable field extraction
        lon = int.from_bytes(unxor_payload[4:8], 'little', signed=True) / 1e7
        lat = int.from_bytes(unxor_payload[8:12], 'little', signed=True) / 1e7
        num_sats = self.payload[48]
        fix_type = unxor_payload[50]
        seq_num = self.payload[56] + (self.payload[57] << 8)

        # Unfortunately due to the hour being reported as 0-15, hour & day are not usable
        # There is no reliable way to distinguish between hours 00-07 and 16-23 making this section somewhat useless

        # Date/time from indices 0:4 after unxor
        dt_raw = int.from_bytes(unxor_payload[0:4], 'little')

        # Bit unpacking
        second = (dt_raw >> 0) & 0x3F   # bits 0-5
        minute = (dt_raw >> 6) & 0x3F   # bits 6-11
        hour   = (dt_raw >> 12) & 0x0F  # bits 12-15 (reported 0-15)
        day    = (dt_raw >> 16) & 0x1F  # bits 16-20
        month  = (dt_raw >> 21) & 0x0F  # bits 21-24
        year   = (dt_raw >> 25) & 0x7F  # bits 25-31 (7-bit offset)

        # Change base to 2000
        full_year = 2000 + year
        """
        # Quirk correction? (add 1 day if reported hour >7)
        if hour > 7:
            day += 1
            if day > 31:  # Rough carry-over
                day = 1
                month += 1
                if month > 12:
                    month = 1
                    full_year += 1
        """

        return {
            'lat': lat,
            'lon': lon,
            'sats': num_sats,
            'fix_type': fix_type,
            'seq_num': seq_num,
            'date': f"{full_year}-{month:02d}-{day:02d}",
            'time': f"{hour:02d}:{minute:02d}:{second:02d}"
        }

# Get a decoded message from serial
def get_decoded_message(ser, decoder):
    while True:
        data = ser.read(ser.in_waiting or 1)  # Read available bytes or at least 1
        for byte in data:
            result = decoder.decode(byte)
            if result:
                return result
        time.sleep(0.1)


if __name__ == "__main__":
    # Test the decoder standalone
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    decoder = NazaDecoder()
    result = get_decoded_message(ser, decoder)
#    print(f"Decoded GPS: Lat: {result['lat']:.7f}, Lon: {result['lon']:.7f}, Sats: {result['sats']}, Fix: {result['fix_type']}, Seq: {result['seq_num']}")
    print(f"Decoded GPS: Lat: {result['lat']:.7f}, Lon: {result['lon']:.7f}, "
          f"Sats: {result['sats']}, Fix: {result['fix_type']}, Seq: {result['seq_num']}, "
          f"Date: {result['date']} Time: {result['time']}")
    ser.close()