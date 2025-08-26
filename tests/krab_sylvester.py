import can
import time

def float_to_uint(x, x_min, x_max, bits):
    span = x_max - x_min
    if x < x_min:
        x = x_min
    elif x > x_max:
        x = x_max
    return int((x - x_min) * ((float((1 << bits) - 1)) / span))

def pack_mit_command(p, v, kp, kd, t):
    # Ranges from your motor's documentation (adjust if needed)
    kv = 80                         # RPM/V
    p_min, p_max = -12.56, 12.56    # rad
    v_min, v_max = -60.0, 60.0      # rad/s
    kp_min, kp_max = 0.0, 500.0
    kd_min, kd_max = 0.0, 5.0
    t_min, t_max = -12.0, 12.0      # Nm

    p_int  = float_to_uint(p,  p_min,  p_max, 16)
    v_int  = float_to_uint(v,  v_min,  v_max, 12)
    kp_int = float_to_uint(kp, kp_min, kp_max, 12)
    kd_int = float_to_uint(kd, kd_min, kd_max, 12)
    t_int  = float_to_uint(t,  t_min,  t_max, 12)

    buffer = [0]*8
    buffer[0] = (kp_int >> 4) & 0xFF
    buffer[1] = ((kp_int & 0xF) << 4) | ((kd_int >> 8) & 0xF)
    buffer[2] = kd_int & 0xFF
    buffer[3] = (p_int >> 8) & 0xFF
    buffer[4] = p_int & 0xFF
    buffer[5] = (v_int >> 4) & 0xFF
    buffer[6] = ((v_int & 0xF) << 4) | ((t_int >> 8) & 0xF)
    buffer[7] = t_int & 0xFF
    return buffer

def pack_velocity_command(velocity, kd):
    # For pure velocity control, set p=0, kp=0, t=0
    return pack_mit_command(0.0, velocity, 0.0, kd, 0.0)

def parse_motor_feedback(data):
    pos_int = int.from_bytes(data[0:2], byteorder='big', signed=True)
    spd_int = int.from_bytes(data[2:4], byteorder='big', signed=True)
    cur_int = int.from_bytes(data[4:6], byteorder='big', signed=True)
    temp = int.from_bytes(data[6:7], byteorder='big', signed=True)
    error = data[7]
    pos = pos_int * 0.1      # degrees
    spd = spd_int * 10.0     # rpm
    cur = cur_int * 0.01     # Amps
    return pos, spd, cur, temp, error

if __name__ == "__main__":
    can_interface = "can0"
    canBus = can.ThreadSafeBus(channel=can_interface, bustype='socketcan')

    arbitration_id = 0x01  # Use your motor's CAN ID (extended frame)
    dt = 0.01

    try:
        for i in range(100):
            # Example: send velocity=3.14 rad/s, kd=2
            data = pack_velocity_command(velocity=3.14, kd=0.5)
            msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=True)
            canBus.send(msg)
            msg = canBus.recv(timeout=0.1)
            if msg is not None and len(msg.data) == 8:
                pos, spd, cur, temp, error = parse_motor_feedback(msg.data)
                print(f"Position: {pos:.1f} deg, Speed: {spd:.1f} rpm, Current: {cur:.2f} A, Temp: {temp}°C, Error: {error}")
            else:
                print("No feedback received.")
            time.sleep(dt)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        canBus.shutdown()
        print("CAN bus closed.")