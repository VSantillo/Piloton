# Piloton

Piloton is a Raspberry Pi-based digital assistant for **your** spin bike. 
Piloton aims to aggregate and deliver workout-related metrics for 
Bluetooth-enabled spin bikes and heart rate monitors. 

## Installation

While Piloton is targeting Raspberry Pis, this repository and the scripts in it 
could be run from any sufficiently-power, Bluetooth-enabled computer that is 
capable of running Python 3.9.

    git clone https://github.com/VSantillo/Piloton.git

Before continuing, ensure that you have **Influx DB** and **Poetry** installed. 

Install dependencies using Poetry:

    poetry install

To run:

    poetry run python main.py

### External Dependencies
#### Influx DB
Piloton uses [InfluxDB (v1.8.4)](https://www.influxdata.com/). InfluxDB is a 
Time Series Database that Piloton uses to record the data points received from 
your spin bike and heart rate monitor and to report your performance after your 
workout. For now, this information can be visualized using [Grafana](https://grafana.com/oss/grafana/). 

#### Poetry

Piloton uses [Poetry](https://python-poetry.org/docs/). Poetry is a Python 
dependency management and packaging tool.



### Python Dependencies

#### Bleak

[Bleak](https://github.com/hbldh/bleak) is a Bluetooth Low Energy client that is
capable of connecting to devices that broadcast and BLE information. Bleak 
handles the connection to the bike and the heart rate monitor and receiving 
that information. 

#### Rich

[Rich](https://github.com/willmcgugan/rich) is library that enables rich text 
and formatting in the terminal. Rich creates the display and handles most of the
interactions found in Piloton. 

####  Scikit-learn

[Scikit-learn](https://scikit-learn.org/stable/) is library for simple and 
efficient machine learning in Python. Piloton uses scikit-learn to fit and 
predict bike Resistance based on an inputs of Cadence, Power, and Speed. 

## How to Use

While Piloton is still in development, it's usable for most tinkerers. Ideally, 
the Piloton would just idly wait until the Schwinn IC4 started broadcasting data
packets and then to load into the Workout interface. To ease development, it's 
in this application state. 

When loading into Piloton, you'll be presented with a Menu with 5 options: 
Workout, User Settings, Device Settings, Training, and Quit

### Working Out

When working out, Piloton will ask you for how long you'd like to workout. 
Right now, it's indefinite. However, a future goal is to specify a time so that 
the Piloton will automatically stop recording and break connection with the 
devices should they no longer be active. 

![Workout Screen](https://thumbs.gfycat.com/OfficialQuerulousFoxterrier-size_restricted.gif)

There's 5 metrics on this screen:

**Cadence**: Average RPM of flywheel, read directly from bike

**Resistance**: Dimensionless value that reflects how much effort it takes to 
spin the flywheel, predicted from Cadence, Power and Speed

**Power**: Power in Watts, read directly from bike

**Heart Rate**: Heart Rate, read directly from heart rate monitor. 
[Heart Zones](https://www.polar.com/blog/running-heart-rate-zones-basics/) are 
based off of established thresholds determined by maximum heart rate by age. 
**Age** can be adjusted in **User Settings**.

**Power Zone**: Power Zone, interpreted from bike power output. 
[Power Zones](https://blog.onepeloton.com/power-zone-training/) are based off of
established threshold determined by Functional Threshold Power (**FTP**), or the
average power output over an hour. **FTP** can be adjusted in **User Settings**.

When you want to end a workout, press `Ctrl+C`.

### Training

A desired goal of Piloton is that it should be able to be bike agnostic. The 
Schwinn IC4 can have wildly varying factory calibrations, so I wanted to provide
a mechanism that would allow for anyone to train their own resistance scale on 
their own bike. You may retrain the resistance scale however you'd like. 

When you start training, it will ask you for what resistance you'd like to train
on. After providing a value, the Piloton will load up a grid of bars that show 
how many samples have been collected for that given resistance and each 
respective cadence. These values will get fit a Classifier and then predicted 
during a workout. You will need to train on as many values of resistance as you 
want to see.

When you want to end training on a specific cadence, press `Ctrl+C`

![Training Screen](https://thumbs.gfycat.com/ShortSoftEchidna-size_restricted.gif)

I recognize that this process is long and tedious. I don't really know much 
about machine learning and will be the first to admit this is the weakest 
component of the whole project. I will include a full data set collected from my
Schwinn IC4 as I develop more on this project. My immediate goals with this 
training process is to make it faster and to make it more accurate. 


### Device Settings

You can update the bike name and HRM name in the settings. Right now, Piloton 
assumes you will always have a bike and an HRM whenever doing a workout. These 
names should be the names that broadcast from those devices. 

## Motivation

A few months ago, I purchased a Schwinn IC4 spin bike because it connects to the
Peloton digital app (via Bluetooth) that I would run from my phone. This
experience is certainly adequate, however, the bike's display doesn't really 
provide much information that can help me make decisions about progressions 
during my workout. A Redditor (/u/zomrise) posted their 
[Schwinn-to-Peloton Resistance Converter](https://www.reddit.com/r/SchwinnIC4_BowflexC6/comments/l5pgos/i_built_a_schwinntopeloton_resistance_converter/) 
which piqued my interest in what information could be received from the Schwinn 
IC4.  There are apps like Kinetic that provide data collection and visualization
during a workout, however, when you're doing a Peloton digital class on the 
phone, only Kinetic or Peloton can be on screen. My approach was to consider 
Piloton as a pseudo-replacement for the Schwinn IC4 display. However, I felt 
that there was a way to add value such that this information could be aggregated
on any Bluetooth enabled bike.

Developing Piloton also allowed me to work with some new-to-me technology that I
just hadn't found an opportunity to work with in a personal project. This is my 
first Raspberry Pi-based project and my first time doing any Bluetooth work. 
There's a very small "Machine Learning" component which is a Decision Tree 
Classifier for right now. I'm hoping to take a few of the things I've learned 
here, find a few collaborators, and really put some polish into this project. 
