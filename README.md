# live_ars

Arduino based sensors for externally measuring and transmitting RPM and current from rotors. This is necessary when no telemetry from an Electronic Speed Controller (ESC) is available.

## Install
```shell
git clone https://github.com/toopazo/live_ars.git
cd live_ars/
. ./create_venv.sh
```

Make sure you end up with the environment activated indicated by ```(venv) user@host:```
If not, run
```shell
source venv/bin/activate
```
To deactivate it just type
```shell
deactivate
```
## Running the code
```shell
python ars_main.py .
```
