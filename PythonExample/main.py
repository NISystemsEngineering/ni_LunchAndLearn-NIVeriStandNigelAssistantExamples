import time
from niveristand.legacy import NIVeriStand

GATEWAY = "localhost"

ENABLE_POWER = "Aliases/PowerSupply/EnablePower"
SEND_ENABLE_MSG = "Aliases/PowerSupply/SendEnablePowerMessage"
VBATT = "Aliases/Seat ECU/External Measurements/VBATT"
FORWARD = "Aliases/Seat ECU/External Switches/ForwardSwitch"
REVERSE = "Aliases/Seat ECU/External Switches/ReverseSwitch"
POSITION = "Aliases/Seat ECU/External Measurements/SensorPosition"
LOG= "Aliases/Test System/Log"

VBATT_MIN = 14.0
POS_FORWARD_EXPECTED = 100.0
POS_REVERSE_EXPECTED = 0.0
POS_TOL = 0.01


def set_bool(ws, channel, value):
    ws.SetSingleChannelValue(channel, 1.0 if value else 0.0)


def read_value(ws, channel):
    return ws.GetSingleChannelValue(channel)


def approx_equal(a, b, tol=POS_TOL):
    return abs(a - b) <= tol


def main():
    ws = NIVeriStand.Workspace2(GATEWAY)
    failures = []

    try:
        # Power on sequence
        set_bool(ws, LOG, True)
        time.sleep(1.0)

        set_bool(ws, ENABLE_POWER, True)
        set_bool(ws, SEND_ENABLE_MSG, True)

        time.sleep(1.0)

        vbatt = read_value(ws, VBATT)
        print(f"VBATT = {vbatt:.3f} V")

        if vbatt <= VBATT_MIN:
            failures.append(f"VBATT check failed: expected > {VBATT_MIN} V, got {vbatt:.3f} V")
        else:
            # Forward motion
            set_bool(ws, FORWARD, True)
            time.sleep(3.0)
            set_bool(ws, FORWARD, False)

            pos_fwd = read_value(ws, POSITION)
            print(f"Position after forward = {pos_fwd:.3f}")

            if not approx_equal(pos_fwd, POS_FORWARD_EXPECTED):
                failures.append(
                    f"Forward position check failed: expected {POS_FORWARD_EXPECTED}, got {pos_fwd:.3f}"
                )

            # Reverse motion
            set_bool(ws, REVERSE, True)
            time.sleep(3.0)
            set_bool(ws, REVERSE, False)

            pos_rev = read_value(ws, POSITION)
            print(f"Position after reverse = {pos_rev:.3f}")

            if not approx_equal(pos_rev, POS_REVERSE_EXPECTED):
                failures.append(
                    f"Reverse position check failed: expected {POS_REVERSE_EXPECTED}, got {pos_rev:.3f}"
                )


    finally:
        # Leave switches off in all cases
        try:
            set_bool(ws, FORWARD, False)
            set_bool(ws, REVERSE, False)
            set_bool(ws, ENABLE_POWER, False)
            set_bool(ws, SEND_ENABLE_MSG, True)
            time.sleep(1.0)
            set_bool(ws, LOG, False)

        except Exception:
            pass

    print("\n=== TEST RESULT ===")
    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
    else:
        print("PASS")


if __name__ == "__main__":
    main()