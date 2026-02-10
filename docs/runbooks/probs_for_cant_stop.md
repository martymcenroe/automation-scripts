# Runbook: probs_for_cant_stop

## Description
A probability calculator for the dice game "Can't Stop". It simulates 1,000,000 dice rolls to calculate the probability of rolling at least one sum of 7 using 4 dice (paired in specific ways).

## Prerequisites
- **Python 3.x:** Must be installed.

## Usage
Run the simulation:
```bash
python tools/probs_for_cant_stop
```

## Logic
- Simulates 4 dice rolls.
- Pairs them as (Dice 1 + Dice 2), (Dice 3 + Dice 4), (Dice 1 + Dice 3), and (Dice 2 + Dice 4).
- Checks if any of these pairs sum to 7.
