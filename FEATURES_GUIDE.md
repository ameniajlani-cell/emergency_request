# Emergency System - Features Implementation Guide

## Features Implemented

### Feature 1: Improved Location with Google Maps
Users can now select locations using an interactive Google Maps widget instead of plain text input.

**Files Modified:**
- `models.py` - Added `latitude` and `longitude` fields to `Requester` and `EmergencyRequest` models
- `forms.py` - Added latitude/longitude fields and MapWidget class
- `views.py` - Updated `create_request` view to capture and store coordinates
- `templates/create_request.html` - Added map containers for location selection
- `static/core/maps.js` - Google Maps integration script
- `settings.py` - Added GOOGLE_MAPS_API_KEY configuration

**Setup Instructions:**

1. **Get Google Maps API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Maps JavaScript API
   - Create an API key (Credentials > Create Credentials > API Key)
   - Restrict the key to JavaScript origins

2. **Configure API Key:**
   - Open `emergency_project/settings.py`
   - Find the line: `GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'`
   - Replace `'YOUR_GOOGLE_MAPS_API_KEY'` with your actual API key

3. **Usage:**
   - When creating a new emergency request, two interactive maps will be displayed:
     - One for the requester location
     - One for the emergency location
   - Click on the map to select a location
   - The coordinates (latitude/longitude) are automatically captured
   - The location info box shows the selected coordinates

---

### Feature 2: Auto Assignment (Smart System)
When an emergency request is created, the system automatically assigns the appropriate response teams based on the emergency type.

**Files Modified:**
- `models.py` - Added `get_assigned_teams()` method to `EmergencyType` model
- `views.py` - Updated `create_request` view to auto-assign teams

**How It Works:**

1. **Team Assignment Mapping:**
   The following emergency types are automatically mapped to response teams:
   
   | Emergency Type | Assigned Team |
   |---|---|
   | Medical | Ambulance Team |
   | Fire | Firefighters |
   | Robbery / Police | Police Department |
   | Police | Police Department |
   | Accident | Emergency Rescue |
   | Power Outage | Electricity Maintenance |
   | Power | Electricity Maintenance |
   | Hazard | Civil Protection |
   | Infrastructure | Civil Protection |

2. **Assignment Process:**
   - User creates an emergency request and selects an emergency type
   - Upon form submission, the system:
     - Creates/retrieves the requester with coordinates
     - Creates the emergency request with coordinates
     - Automatically queries `EmergencyType.get_assigned_teams()`
     - Creates `Assignment` records linking the request to each matched team
   - The message confirms the request was created successfully

**Configuration:**

To add or modify team assignments:
1. Open `core/models.py`
2. Find the `get_assigned_teams()` method in the `EmergencyType` class
3. Update the `type_to_teams` dictionary with your custom mappings

Example:
```python
type_to_teams = {
    'medical': ['Ambulance Team'],
    'fire': ['Firefighters'],
    'custom_type': ['Team A', 'Team B'],  # Multiple teams for one type
}
```

---

## Database Migrations

The following migration was applied:
- `0005_emergencyrequest_latitude_emergencyrequest_longitude_and_more.py`
  - Adds `latitude` and `longitude` fields to both `Requester` and `EmergencyRequest` models

---

## View Emergency Assignments

To see which teams are assigned to each emergency request:
1. Go to the dashboard (Home page)
2. Click on an emergency request
3. View the assignments in the assignment list page (`/assignment/`)
4. You can also manually add/remove assignments if needed

---

## API Key Security Notes

- **Development:** The placeholder key in `settings.py` is safe for development
- **Production:** Use environment variables to store the API key
  ```python
  import os
  GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY')
  ```
- **Restrict API Key:** Always restrict your API key to specific HTTP referrers and APIs

---

## Troubleshooting

**Map not showing:**
- Check that the Google Maps API key is correctly configured in `settings.py`
- Verify the API key has the Maps JavaScript API enabled
- Check browser console for any JavaScript errors

**No teams assigned:**
- Verify that response teams exist with the exact names in the mapping
- Check that emergency type name matches the mapping dictionary keys
- Visit the Response Teams management page to see available teams

**Coordinates not saving:**
- Ensure you clicked on the map to select a location
- Check that latitude/longitude hidden fields have values before form submission
- Verify browser JavaScript is enabled

---

## API Reference

### EmergencyType.get_assigned_teams()
Returns a QuerySet of `ResponseTeam` objects that should be auto-assigned to this emergency type.

```python
emergency_type = EmergencyType.objects.get(name='Medical')
teams = emergency_type.get_assigned_teams()  # Returns Ambulance Team
```

### Requester Model
```python
requester = Requester.objects.get(id=1)
print(f"Location: {requester.location}")
print(f"Coordinates: {requester.latitude}, {requester.longitude}")
```

### EmergencyRequest Model
```python
request = EmergencyRequest.objects.get(id=1)
print(f"Location: {request.location}")
print(f"Coordinates: {request.latitude}, {request.longitude}")
print(f"Assigned teams: {request.assignments.all()}")
```

---

## Future Enhancements

Potential improvements for these features:
1. Reverse geocoding - show address instead of just coordinates
2. Route optimization - find fastest route for teams to emergency location
3. Real-time team tracking - display team locations on the map
4. Custom assignment rules - allow admins to create conditional assignments
5. Distance-based assignment - automatically assign nearest teams
6. Team capacity management - don't assign teams that are already at capacity
