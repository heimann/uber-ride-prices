# Uber Ride Prices

A little tool to grab price estimates from the Uber API and store the results in a SQLite database.

## Configuration

Set the following environment variables:

```bash
UBER_SERVER_TOKEN=
```

You can get a server token from the [Uber Developer Portal](https://developer.uber.com/dashboard/).

## Setup

The app will look for location names provided as arguments on runtime. In order for the locations to exist in the SQLite database, you need to create the database at data/uber_rides.db, you also need to seed it with some locations.

## Usage

```bash
>> pipenv shell
>> python app.py home work
```