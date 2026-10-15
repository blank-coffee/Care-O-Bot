# CareBot Promela Model

This repository contains a Promela model of a care robot interacting with a human and environment. 
It is designed for LTL property mining and comparison with human-written temporal logic.

## Components
- CareObot: robot state machine (idle, fetch, navigate, deliver, wait_human, error)
- Human: nondeterministic movement and proximity detection
- World: obstacle toggling
- Navigator: movement logic
- TaskExec: fetch/deliver execution
- SafetyMonitor: simple safety constraint
- Clock: time progression

## Running SPIN
spin -a CareBot.pml
gcc pan.c -o pan
./pan -v

## Purpose
This model serves as a baseline for generating temporal traces suitable for automated LTL property mining.
