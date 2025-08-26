#self.id = int(321 + motor_id) 
import can
import core.CANHelper
import time

if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    # Adjust the range as needed (e.g., 0x01 to 0x7F for 7-bit IDs, or 0x00 to 0x7FF for full standard CAN)
    id_range = range(0x01, 0x7F)
    # read_cmd = [0x9C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Example: RMD-style read state
    msg_data = [0x9A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    # self._single_send(msg_data)
    found_ids = set()
    print("Active scan: sending read command to each CAN ID...")

    for can_id in id_range:

        msg = can.Message(arbitration_id=can_id, data=msg_data, is_extended_id=False)
        try:
            can0.send(msg)
        except can.CanError:
            print(f"Send failed for CAN ID {hex(can_id)}")
            continue

        response = can0.recv(timeout=0.1)
        if response and response.arbitration_id == can_id:
            found_ids.add(can_id)
            print(f"Found device with CAN ID: {can_id} (0x{can_id:02x})")
        time.sleep(0.01)  # Small delay to avoid flooding the bus

    print("Active scan complete.")
    print("All detected CAN IDs:", sorted(found_ids))
    can0.shutdown()