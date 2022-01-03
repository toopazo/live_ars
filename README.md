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

## Saving data to a log file
To run the code and start saving data to a log file in the 
current directory, type
```shell
python ars_log.py .
```

## Plotting data from a log file
To plot data this repo makes us of 
[pandas](https://pandas.pydata.org/docs/index.html). 
Therefore, we need to indicate a filename to parse but also
an index for our dataframe.
```shell
python ars_plot.py filename index_col
```
Another option is to choose ```None``` and let 
pandas generate and index.

E.g.
```buildoutcfg
python ars_plot_log.py logs/log_5_2021-10-14-19-22-46.ars None


```