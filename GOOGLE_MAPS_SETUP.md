# Quick Setup Guide - Google Maps Integration

## Option 1: Using Google Maps (Interactive Maps)

### Get Your Free API Key:

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a Project" → "New Project"
   - Enter project name and click Create

2. **Enable Maps API:**
   - In the Console, go to **APIs & Services** → **Library**
   - Search for "Maps JavaScript API"
   - Click it and press **Enable**

3. **Create API Key:**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **API Key**
   - Copy the generated key

4. **Restrict Your Key (Recommended):**
   - Click on your API key
   - Under "Application restrictions", select "HTTP referrers (web sites)"
   - Add your localhost: `http://localhost:8000/*`
   - Under "API restrictions", select "Maps JavaScript API"
   - Click Save

5. **Add to Django Settings:**
   - Open `emergency_project/settings.py`
   - Find: `GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'`
   - Replace with your key: `GOOGLE_MAPS_API_KEY = 'AIzaSyD....'`
   - Save file and restart Django server

## Option 2: Using Fallback Coordinate Picker (No API Key Needed)

If you don't have an API key yet, the system automatically provides a simple coordinate picker.

**To find coordinates:**
1. Go to [OpenStreetMap](https://www.openstreetmap.org/)
2. Search for your location
3. Click on the location to see coordinates at the bottom
4. Copy latitude and longitude into the form

## Testing:

1. Start your Django server: `python manage.py runserver`
2. Go to: http://localhost:8000/emergency/create/
3. Fill in requester info
4. Enter or select coordinates using the map/picker
5. Fill in emergency info
6. Submit

## Troubleshooting:

- **Map still not showing after adding API key?**
  - Restart Django: `python manage.py runserver`
  - Clear browser cache (Ctrl+Shift+Del)
  - Check browser console for errors (F12)

- **"API key not valid" error?**
  - Verify key is copied correctly (no extra spaces)
  - Check Maps JavaScript API is enabled
  - Wait a few minutes for API to activate

- **Coordinates not saving?**
  - Make sure you select a location (enter or click map)
  - Check hidden fields have values before submitting
  - Try entering coordinates manually in the coordinate picker

## Free Tier Limits:

Google Maps API free tier includes:
- 1,000 requests per day
- $200/month free credit
- Great for development and small deployments

More details: [Google Maps Pricing](https://developers.google.com/maps/billing-and-pricing)
