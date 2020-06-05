# klmodel

This is a small model of COVID transmission and detection dynamics in a small, mostly isolated group.
The model has few parameters, and it is not intended to be precise. It may be useful to help determine
a sufficient testing cadence to prevent excessive transmission once COVID has been introduced to the
group.

This model is for relatively short time periods so it does not model "removal" (i.e. recovering and
becoming immune) or changes in group size. It assumes that entrance criteria are established to ensure
there are no infections at the beginning of the time period.

To set it up:

<pre>
sudo apt-get install python3-venv
python3 -m venv ./klmodel
cd klmodel/
. bin/activate
pip install plotly
pip install pandas
# now bring model.py from this repository into the current directory
python3 model.py
# your browser should show plots of the cumulative histograms
</pre>
