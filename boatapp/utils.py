from datetime import datetime, timedelta
import pytz

def voltage_to_percent(voltage):
    # Ensure voltage is a float
    voltage = float(voltage)
    
    # Define a mapping table based on provided data points
    voltage_map = {
        29.5: 100,
        27.2: 100,
        26.8: 99,
        26.6: 90,
        26.4: 70,
        26.2: 40,
        26.0: 30,
        25.8: 20,
        25.6: 17,
        25.0: 14,
        24.0: 9,
        20.0: 0
    }
    
    # Check for direct matches
    if voltage in voltage_map:
        return voltage_map[voltage]
    
    # Sort table by voltage descending
    sorted_voltages = sorted(voltage_map.keys(), reverse=True)
    
    # Find the two points for interpolation
    for i in range(len(sorted_voltages)-1):
        high_v, low_v = sorted_voltages[i], sorted_voltages[i+1]
        
        if high_v >= voltage >= low_v:
            high_p, low_p = voltage_map[high_v], voltage_map[low_v]
            # Linear interpolation
            percentage = low_p + ((voltage - low_v) * (high_p - low_p) / (high_v - low_v))
            return round(percentage)  # Round to the nearest integer
        
    if voltage < 20.0:
        return -1
        
    # If voltage is out of range
    raise ValueError("Voltage is out of predefined range.")

def minutes_since_last_transmission(transmission_time, local_tz_str="America/New_York"):
    # Ensure transmission_time is a datetime
    transmission_time = datetime.strptime(str(transmission_time), "%Y-%m-%d %H:%M:%S")
    
    # Make the naive datetime object aware in GMT timezone
    transmission_time = pytz.utc.localize(transmission_time)
    
    # Convert to the local timezone
    local_tz = pytz.timezone(local_tz_str)
    transmission_time_local = transmission_time.astimezone(local_tz)
    
    # Get the current time in local timezone
    current_time_local = datetime.now(local_tz)
    
    # Calculate the difference
    time_delta = current_time_local - transmission_time_local
    
    # Return the difference in minutes
    minutes = time_delta.total_seconds() / 60

    return round(minutes)