#################################################
# Import Dependencies
#################################################
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import timedelta
#################################################
# Create the engine for the Hawaii SQLIte database
engine = create_engine('sqlite://///Users/almulldreyer/Desktop/sqlalchemy-challenge/Instructions/Resources/hawaii.sqlite')
# Reflect Database into ORM classes
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# print(Base.classes.keys())
# Save references to the tables as "Measurement" and "Station"
measurement = Base.classes.measurement
station = Base.classes.station
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
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start_date<br>"
        f"/api/v1.0/start_date/end_date"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # session.query(Base.classes.measurement.date)
    # """Return a list of dates and precipitations"""
    # # Query all precipitations
    results = session.query(measurement.date,measurement.prcp).filter(
        measurement.date >= '2016-08-23').filter(measurement.date <= '2017-08-23').all()
    session.close()
    # Convert raw data into list
    all_date_prcp = []
    for date,precip in results:
        date_dict = {}
        date_dict["date"] = precip
        date_dict["prcp"] = precip
        all_date_prcp.append(date_dict)
    return jsonify(all_date_prcp)
@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the database
    session = Session(engine)
    """Return a list of stations"""
    # Query all stations
    results = session.query(Base.classes.measurement.station, func.count(Base.classes.measurement.station)).group_by(
        Base.classes.measurement.station).order_by(func.count(Base.classes.measurement.station).desc()).all()
    session.close()
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)
#query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)
    """Return a list of tobs (temperature observations) for the last year of data in the table"""
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #print()
    results = session.query(measurement.tobs).\
        filter(measurement.date >= query_date).all()
    session.close()
        
    # Convert to normal list
    all_tobs = list(np.ravel(results))
    return jsonify(all_tobs=all_tobs)
# Formatting YYYY-MM-DD
def validate(date_text):
    try:
        dt.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):
    session = Session(engine)
  # start_date = dt.datetime(start_date, '%Y-%m-%d')                   
    start_results = session.query(measurement,func.avg(measurement.tobs).label('TAVG'),func.max(measurement.tobs).label('TMAX'),func.min(measurement.tobs).label('TMIN')).filter(measurement.date >= start_date).first()
    session.close()
    start_tobs_list = []   
    dict = {}
    dict["TMIN"] = start_results.TMIN           
    dict["TMAX"] = start_results.TMAX   
    dict["TAVG"] = start_results.TAVG   
    start_tobs_list.append(dict)
    return jsonify(start_tobs_list)                 
                            
@app.route("/api/v1.0/<start_date>/<end_date>")
def date_range_temps(start_date, end_date):
    session = Session(engine)
    # end_date = dt.datetime(end_date,'%Y-%m-%d')   
    start_end_results = session.query(measurement,func.min(measurement.tobs).label('TMIN'),func.max(measurement.tobs).label('TMAX'),func.avg(measurement.tobs).label('TAVG')).filter((measurement.date >= start_date) & (measurement.date <= end_date)).first()
    session.close()
    start_end_results_list = []
    dict = {}
    dict['TMIN'] = start_end_results.TMIN  
    dict['TMAX'] = start_end_results.TMAX
    dict['TAVG'] = start_end_results.TAVG
    start_end_results_list.append(dict)
    return jsonify(start_end_results_list)
if __name__ == '__main__':
    app.run(debug=True)
    
    
 