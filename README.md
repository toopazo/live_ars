# live_ars

Arduino based sensors for externally measuring and transmitting RPM and current from rotors. This is necessary when no telemetry from an Electronic Speed Controller (ESC) is available.



## Running the code

### Individual tests
Running `ars_parser.py`

```
source venv/bin/activate
python --version
python ars_parser.py --testnum 1
...
python ars_parser.py --testnum 12
python ars_parser.py --testall
source deactivate
```

There are two classes of importance:
- `ArsDec22Data`: This class contains static data about about .ulg and .ars files and timestamps
- `ArsParser`: This class can read and parse the data, plot it and write a .pkl file

### Summary of tetsts
Running `ars_dec22_data.py`

```
source venv/bin/activate
python --version
python ars_dec22_data.py
source deactivate
```
This file reads all previously generated .pkl files and plots a summary for all tests

