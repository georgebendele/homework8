import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON of rainfall dict"""
    # Query precipitation
    max_date = session.query(func.max(Measurement.date)).all()[0][0]
    mx_date = dt.datetime.strptime(max_date, "%Y-%m-%d")
    one_year_ago = mx_date - dt.timedelta(days=365)
    one_year_ago
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > one_year_ago).all()

    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip.append(precip_dict)

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations"""
    # Query stations
    results = session.query(Station.id, Station.station, Station.name).all()

    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Query tobs
    max_date = session.query(func.max(Measurement.date)).all()[0][0]
    mx_date = dt.datetime.strptime(max_date, "%Y-%m-%d")
    one_year_ago = mx_date - dt.timedelta(days=365)
    one_year_ago
    results = session.query(Measurement.date, Measurement.tobs)\
            .filter(Measurement.station == "USC00519281").filter(Measurement.date > one_year_ago)\
            .all()

    lastYtobs = []
    for date, tobs in results:
        lastYtobs_dict = {}
        lastYtobs_dict["date"] = date
        lastYtobs_dict["tobs"] = tobs
        lastYtobs.append(lastYtobs_dict)

    return jsonify(lastYtobs)



@app.route("/api/v1.0/<start_date>")
def starter(start_date):
    
    """Return a min, max and avg for all dates greater than and equal to the start date"""
    # Query after date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    start_temps = []
    for min, avg, max in results:
        start_temps_dict = {}
        start_temps_dict["min"] = min
        start_temps_dict["avg"] = avg
        start_temps_dict["max"] = max
        start_temps.append(start_temps_dict)

    return jsonify(start_temps)

@app.route("/api/v1.0/<start_date>/<end_date>")
def ender(start_date, end_date):
    
    """Return a min, max and avg for all dates greater than and equal to the start date"""
    # Query date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    start_temps = []
    for min, avg, max in results:
        start_temps_dict = {}
        start_temps_dict["min"] = min
        start_temps_dict["avg"] = avg
        start_temps_dict["max"] = max
        start_temps.append(start_temps_dict)

    return jsonify(start_temps)




if __name__ == '__main__':
    app.run(debug=True)
