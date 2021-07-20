# live_ars
Arduino based sensors for externally measuring and transmitting RPM and current from rotors. This is necessary when no telemetry from an Electronic Speed Controller (ESC) is available

## Running the code
Running `ars_parser.py`
```
source venv/bin/activate
python --version
python ars_parser.py --testnum 1
..
python ars_parser.py --testnum 12
python ars_parser.py --testall
```

There are two classes of importance:
- `ArsDec22Data`: This class contains static data about about .ulg and .ars files and timestamps
- `ArsParser`: This class can read and parse the data, plots it and write a .pkl file

