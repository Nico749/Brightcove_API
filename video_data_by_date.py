import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
account_id = os.getenv('ACCOUNT_ID')

def get_access_token():
    url = 'https://oauth.brightcove.com/v4/access_token'
    auth = (client_id, client_secret)
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, auth=auth, data=data)
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get access token: {response.text}")

def get_video_views_by_date(video_id, access_token, start_date, end_date):
    url = f'https://analytics.api.brightcove.com/v1/data?accounts={account_id}&dimensions=video,date&where=video=={video_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    params = {
        'fields': 'video_view,video_name,video_impression,daily_unique_viewers,play_rate',
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d')
        
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  
        analytics_data = response.json()
        return analytics_data.get('items', [])
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []

def get_video_metadata(video_id, access_token):
    url = f'https://cms.api.brightcove.com/v1/accounts/{account_id}/videos/{video_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {}

def get_all_videos_metadata(access_token):
    url = f'https://cms.api.brightcove.com/v1/accounts/{account_id}/videos'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []

def main():
    try:
        access_token = get_access_token()
        
        today = datetime.now()
        start_date = today - timedelta(days=2)
        end_date = today - timedelta(days=2)
        
        # Get all video metadata
        videos_metadata = get_all_videos_metadata(access_token)
        
        if isinstance(videos_metadata, list):
            for video in videos_metadata:
                video_id = video.get('id')
                brand = video.get('custom_fields', {}).get('brand', 'N/A')
                
                # Get video views grouped by date
                views_by_date = get_video_views_by_date(video_id, access_token, start_date, end_date)
                
                for item in views_by_date:
                    print(f"Video ID: {video_id}, "
                          f"Video Name: {item.get('video_name', 'N/A')}, "
                          f"Brand: {brand}, " 
                          f"Date: {item.get('date', 'N/A')}, "
                          f"Views: {item.get('video_view', 'N/A')}, "
                          f"Impressions: {item.get('video_impression', 'N/A')}, "
                          f"Unique Viewers: {item.get('daily_unique_viewers', 'N/A')}, "
                          f"Play Rate: {item.get('play_rate', 'N/A')*100}%"
                    )
        else:
            print("Expected a list of video metadata but received something else.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
