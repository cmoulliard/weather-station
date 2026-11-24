#!/usr/bin/env python3
"""
led_circuit_calculator.py
=========================
Circuit: 9V Battery → R1 → LED → GND

Calculates and validates:
  1. Voltage across the resistor  (V_R)
  2. Current through the circuit  (I)
  3. Whether the resistor value is safe for the LED

Usage
-----
  python led_circuit_calculator.py               # use built-in defaults
  python led_circuit_calculator.py --r 330       # custom resistor
  python led_circuit_calculator.py --help        # full option list

Exit codes
----------
  0  — all checks passed
  1  — one or more checks failed (resistor too low, current too high, etc.)
"""

import argparse
import sys
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LEDSpec:
    """Electrical characteristics of the LED."""
    name: str                   # friendly label
    vf: float                   # forward voltage  [V]
    if_typ: float               # typical forward current [A]
    if_max: float               # absolute maximum forward current [A]
    if_min: float = 0.001       # minimum visible current [A] (~1 mA)


@dataclass
class CircuitResult:
    """Computed values and pass/fail flags."""
    v_battery: float            # [V]
    r_ohm: float                # [Ω]
    led: LEDSpec

    v_resistor: float           # voltage drop across R  [V]
    i_circuit: float            # current through circuit [A]
    p_resistor: float           # power dissipated in R  [W]

    ok_min_current: bool        # current ≥ LED minimum visible threshold
    ok_max_current: bool        # current ≤ LED absolute maximum
    ok_resistor_power: bool     # resistor power ≤ safety margin of rated wattage
    r_ideal: float              # ideal R for typical current [Ω]
    r_min: float                # minimum R to stay below If_max [Ω]

    @property
    def is_safe(self) -> bool:
        return self.ok_min_current and self.ok_max_current and self.ok_resistor_power


# ─────────────────────────────────────────────────────────────────────────────
# Core calculation
# ─────────────────────────────────────────────────────────────────────────────

def calculate(
    v_battery: float,
    r_ohm: float,
    led: LEDSpec,
    r_watt_rating: float = 0.25,   # ¼ W resistor (standard)
    power_derate: float = 0.5,     # operate at ≤ 50 % of rated wattage
) -> CircuitResult:
    """
    Perform all electrical calculations for the series circuit.

    Parameters
    ----------
    v_battery       : supply voltage [V]
    r_ohm           : resistor value [Ω]
    led             : LED specification
    r_watt_rating   : rated wattage of the resistor [W]
    power_derate    : maximum allowed fraction of watt rating (safety margin)
    """
    if r_ohm <= 0:
        raise ValueError(f"Resistor value must be > 0, got {r_ohm} Ω")
    if v_battery <= led.vf:
        raise ValueError(
            f"Battery voltage ({v_battery} V) must be greater than LED Vf ({led.vf} V)"
        )

    v_resistor = v_battery - led.vf          # Kirchhoff: V_R = V_bat - V_f
    i_circuit  = v_resistor / r_ohm          # Ohm's law
    p_resistor = v_resistor * i_circuit       # P = V × I  (= I² × R)

    r_ideal = (v_battery - led.vf) / led.if_typ
    r_min   = (v_battery - led.vf) / led.if_max

    return CircuitResult(
        v_battery        = v_battery,
        r_ohm            = r_ohm,
        led              = led,
        v_resistor       = v_resistor,
        i_circuit        = i_circuit,
        p_resistor       = p_resistor,
        ok_min_current   = i_circuit >= led.if_min,
        ok_max_current   = i_circuit <= led.if_max,
        ok_resistor_power= p_resistor <= r_watt_rating * power_derate,
        r_ideal          = r_ideal,
        r_min            = r_min,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Report formatting
# ─────────────────────────────────────────────────────────────────────────────

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def _chk(ok: bool) -> str:
    return PASS if ok else FAIL


def print_report(res: CircuitResult, r_watt_rating: float = 0.25) -> None:
    """Print a human-readable analysis report."""
    sep = "─" * 60

    print()
    print("╔" + "═" * 58 + "╗")
    print("║  LED Circuit Calculator — Analysis Report              ║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("  CIRCUIT PARAMETERS")
    print(sep)
    print(f"  Battery voltage   : {res.v_battery:.2f} V")
    print(f"  Resistor R1       : {res.r_ohm:.0f} Ω")
    print(f"  LED               : {res.led.name}")
    print(f"    Forward voltage   Vf        = {res.led.vf:.2f} V")
    print(f"    Typical current   If_typ    = {res.led.if_typ * 1000:.1f} mA")
    print(f"    Maximum current   If_max    = {res.led.if_max * 1000:.1f} mA")
    print()
    print("  MEASURED / CALCULATED VALUES")
    print(sep)
    print(f"  Voltage across R1 : {res.v_resistor:.3f} V")
    print(f"    = Vbat − Vf  = {res.v_battery:.2f} − {res.led.vf:.2f}")
    print()
    print(f"  Current (I)       : {res.i_circuit * 1000:.2f} mA")
    print(f"    = V_R / R  = {res.v_resistor:.3f} / {res.r_ohm:.0f}")
    print()
    print(f"  Power in R1       : {res.p_resistor * 1000:.2f} mW  "
          f"(rated {r_watt_rating * 1000:.0f} mW, limit 50 % = "
          f"{r_watt_rating * 500:.0f} mW)")
    print()
    print("  RESISTOR SIZING GUIDE")
    print(sep)
    print(f"  Ideal R (for If_typ {res.led.if_typ*1000:.0f} mA) : "
          f"{res.r_ideal:.1f} Ω  → use {_nearest_e24(res.r_ideal):.0f} Ω (E24)")
    print(f"  Minimum R (for If_max {res.led.if_max*1000:.0f} mA) : "
          f"{res.r_min:.1f} Ω  → any R ≥ this value is safe")
    print(f"  Chosen R1 = {res.r_ohm:.0f} Ω  "
          f"({'≥ R_min ✅' if res.r_ohm >= res.r_min else '< R_min ❌'})")
    print()
    print("  SAFETY CHECKS")
    print(sep)
    print(f"  Current ≥ If_min  ({res.led.if_min*1000:.1f} mA) : {_chk(res.ok_min_current)}"
          f"  ({res.i_circuit*1000:.2f} mA)")
    print(f"  Current ≤ If_max  ({res.led.if_max*1000:.1f} mA) : {_chk(res.ok_max_current)}"
          f"  ({res.i_circuit*1000:.2f} mA)")
    print(f"  R1 power ≤ 50 %   ({r_watt_rating*500:.0f} mW)  : {_chk(res.ok_resistor_power)}"
          f"  ({res.p_resistor*1000:.2f} mW)")
    print()
    overall = _chk(res.is_safe)
    print(f"  OVERALL  : {overall}")
    print()
    if not res.is_safe:
        print("  ⚠  RECOMMENDATIONS")
        if not res.ok_max_current:
            print(f"     Increase R1 to at least {res.r_min:.0f} Ω  "
                  f"(E24 suggestion: {_nearest_e24(res.r_min):.0f} Ω)")
        if not res.ok_min_current:
            print(f"     Decrease R1 so current exceeds {res.led.if_min*1000:.1f} mA")
        if not res.ok_resistor_power:
            print(f"     Use a ½W (or higher) resistor instead of ¼W")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# E24 nearest-value helper
# ─────────────────────────────────────────────────────────────────────────────

_E24 = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4,
    2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2,
    6.8, 7.5, 8.2, 9.1,
]


def _nearest_e24(r: float) -> float:
    """Return the nearest E24 standard resistor value to *r* [Ω]."""
    import math
    decade = 10 ** math.floor(math.log10(r))
    normalised = r / decade
    best = min(_E24, key=lambda v: abs(v - normalised))
    return best * decade


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="led_circuit_calculator",
        description=(
            "Calculate and validate a 9 V battery + resistor + LED series circuit.\n"
            "Default component values match the KiCad schematic in this project."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python led_circuit_calculator.py
  python led_circuit_calculator.py --r 470
  python led_circuit_calculator.py --vbat 5 --vf 2.0 --if-typ 0.02 --if-max 0.025 --r 150
        """,
    )
    p.add_argument("--vbat",   type=float, default=9.0,    metavar="V",
                   help="Battery voltage in Volts (default: 9.0)")
    p.add_argument("--r",      type=float, default=330.0,  metavar="Ω",
                   help="Resistor value in Ohms (default: 330)")
    p.add_argument("--vf",     type=float, default=2.0,    metavar="V",
                   help="LED forward voltage in Volts (default: 2.0)")
    p.add_argument("--if-typ", type=float, default=0.020,  metavar="A",
                   help="LED typical forward current in Amps (default: 0.020)")
    p.add_argument("--if-max", type=float, default=0.025,  metavar="A",
                   help="LED max forward current in Amps (default: 0.025)")
    p.add_argument("--if-min", type=float, default=0.001,  metavar="A",
                   help="LED minimum visible current in Amps (default: 0.001)")
    p.add_argument("--r-watt", type=float, default=0.25,   metavar="W",
                   help="Resistor power rating in Watts (default: 0.25)")
    p.add_argument("--led-name", type=str, default="LED Red 5mm",
                   help="Friendly name for the LED (default: 'LED Red 5mm')")
    return p


def main(argv: Optional[list] = None) -> int:
    args = _build_parser().parse_args(argv)

    led = LEDSpec(
        name   = args.led_name,
        vf     = args.vf,
        if_typ = args.if_typ,
        if_max = args.if_max,
        if_min = args.if_min,
    )

    try:
        result = calculate(
            v_battery    = args.vbat,
            r_ohm        = args.r,
            led          = led,
            r_watt_rating= args.r_watt,
        )
    except ValueError as exc:
        print(f"\n  ERROR: {exc}\n", file=sys.stderr)
        return 1

    print_report(result, r_watt_rating=args.r_watt)
    return 0 if result.is_safe else 1


if __name__ == "__main__":
    sys.exit(main())
