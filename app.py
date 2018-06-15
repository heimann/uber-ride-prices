import datetime
import os
import sys

from sqlalchemy import (
    Column,
    create_engine,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from uber_rides.session import Session as UberSession
from uber_rides.client import UberRidesClient

uber_session = UberSession(server_token=os.environ.get('UBER_SERVER_TOKEN'))

client = UberRidesClient(uber_session)

engine = create_engine('sqlite:///data/uber_rides.db')

Base = declarative_base()

starting_location_name = sys.argv[1]
ending_location_name = sys.argv[2]

def get_price_estimates_for_locations(start_loc, end_loc):
    """
    Gets the Uber price estimates for a set of locations. Creates an Estimate object and returns the Estimate.
    
    params:
        start_loc (obj Location): Starting Location of Ride
        end_loc (obj Location): Ending Location of Ride
    
    return:
        estimate (obj Estimate): Estimates for Ride
    """
    estimate = client.get_price_estimates(
        start_latitude=start_loc.latitude,
        start_longitude=start_loc.longitude,
        end_latitude=end_loc.latitude,
        end_longitude=end_loc.longitude,
        seat_count=1
    )
    estimates = estimate.json['prices']
    uber_x_data = [i for i in estimates if i['localized_display_name'] == 'UberX'][0]
    uber_pool_data = [i for i in estimates if i['localized_display_name'] == 'UberPool'][0]
    
    estimate = Estimate(
        starting_location=start_loc,
        ending_location=end_loc,
        pool_min=uber_pool_data['low_estimate'],
        pool_max=uber_pool_data['high_estimate'],
        x_min=uber_x_data['low_estimate'],
        x_max=uber_x_data['high_estimate']
    )
    
    return estimate

class Location(Base):
    __tablename__ = 'location'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    def __repr__(self):
        return f"<Location(name={self.name}, latitude={self.latitude}, longitude={self.longitude})>"

class Estimate(Base):
    __tablename__ = 'estimate'
    
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    starting_location_id = Column(Integer, ForeignKey('location.id'))
    ending_location_id = Column(Integer, ForeignKey('location.id'))
    pool_min = Column(Float)
    pool_max = Column(Float)
    x_min = Column(Float)
    x_max = Column(Float)
    
    starting_location = relationship("Location", foreign_keys=starting_location_id, backref="starting_location")
    ending_location = relationship("Location", foreign_keys=ending_location_id, backref="ending_location")
    
    def pool_average(self):
        return (self.pool_min + self.pool_max) / 2.0

    def x_average(self):
        return (self.x_min + self.x_max) / 2.0
    
    def __repr__(self):
        return f"<Estimate(created={self.created}, pool_average={self.pool_average()}, x_average={self.x_average()})>"

Session = sessionmaker(bind=engine)
session = Session()

sl = session.query(Location).filter_by(name=starting_location_name).first()
el = session.query(Location).filter_by(name=ending_location_name).first()

estimate = get_price_estimates_for_locations(sl, el)
session.add(estimate)
session.commit()
print( (
    f"""Generated new estimate from {sl.name} to {el.name}.
    Current Uber Pool Average: {estimate.pool_average()}
    Current Uber X Average: {estimate.x_average()}
    """)
)