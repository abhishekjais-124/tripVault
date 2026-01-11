from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from .models import SavedTrip
from .logger import get_logger

logger = get_logger('api_views')

@login_required
@require_http_methods(["POST"])
def save_trip(request):
    """Save or update a trip"""
    try:
        user_id = request.user.id
        logger.info(f'Save trip request from user {user_id} ({request.user.username})')
        
        data = json.loads(request.body)
        trip_id = data.get('id')
        trip_name = data.get('trip', {}).get('name', 'Untitled Trip')
        # Store the complete trip data including days and globalCustom
        trip_data = {
            'trip': data.get('trip', {}),
            'days': data.get('days', []),
            'globalCustom': data.get('globalCustom', [])
        }
        
        logger.info(f'Save trip: trip_id={trip_id}, trip_name={trip_name}, is_update={bool(trip_id)}')
        
        if trip_id:
            # Update existing trip
            trip = SavedTrip.objects.get(id=trip_id, user=request.user)
            trip.name = trip_name
            trip.trip_data = trip_data
            trip.save()
            message = f"Trip '{trip_name}' updated successfully!"
            logger.info(f'Trip {trip_id} updated by user {user_id}. Trip name: {trip_name}')
        else:
            # Create new trip
            trip = SavedTrip.objects.create(
                user=request.user,
                name=trip_name,
                trip_data=trip_data
            )
            message = f"Trip '{trip_name}' saved successfully!"
            logger.info(f'New trip created with ID {trip.id} by user {user_id}. Trip name: {trip_name}')
        
        return JsonResponse({
            'success': True,
            'message': message,
            'trip_id': trip.id,
            'trip_name': trip.name
        })
    except SavedTrip.DoesNotExist:
        logger.warning(f'Trip not found for user {request.user.id}. Attempted trip ID: {trip_id}')
        return JsonResponse({'success': False, 'message': 'Trip not found'}, status=404)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in save_trip request from user {request.user.id}: {str(e)}')
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Error saving trip for user {request.user.id}: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@login_required
@require_http_methods(["GET"])
def list_trips(request):
    """List all saved trips for the user"""
    try:
        user_id = request.user.id
        logger.info(f'List trips request from user {user_id} ({request.user.username})')
        
        trips = SavedTrip.objects.filter(user=request.user)
        trip_count = trips.count()
        logger.info(f'Retrieved {trip_count} trips for user {user_id}')
        
        trip_list = [
            {
                'id': trip.id,
                'name': trip.name,
                'created_at': trip.created_at.isoformat(),
                'updated_at': trip.updated_at.isoformat()
            }
            for trip in trips
        ]
        return JsonResponse({
            'success': True,
            'trips': trip_list
        })
    except Exception as e:
        logger.error(f'Error listing trips for user {request.user.id}: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_trip(request, trip_id):
    """Get a specific trip's data"""
    try:
        user_id = request.user.id
        logger.info(f'Get trip request from user {user_id}. Trip ID: {trip_id}')
        
        trip = SavedTrip.objects.get(id=trip_id, user=request.user)
        logger.info(f'Trip {trip_id} retrieved successfully for user {user_id}')
        
        return JsonResponse({
            'success': True,
            'trip': trip.trip_data,
            'trip_name': trip.name
        })
    except SavedTrip.DoesNotExist:
        logger.warning(f'Trip {trip_id} not found or unauthorized access by user {request.user.id}')
        return JsonResponse({'success': False, 'message': 'Trip not found'}, status=404)
    except Exception as e:
        logger.error(f'Error retrieving trip {trip_id} for user {request.user.id}: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@require_http_methods(["DELETE"])
def delete_trip(request, trip_id):
    """Delete a trip"""
    try:
        user_id = request.user.id
        logger.info(f'Delete trip request from user {user_id}. Trip ID: {trip_id}')
        
        trip = SavedTrip.objects.get(id=trip_id, user=request.user)
        trip_name = trip.name
        trip.delete()
        
        logger.info(f'Trip {trip_id} deleted successfully by user {user_id}. Trip name was: {trip_name}')
        
        return JsonResponse({
            'success': True,
            'message': f"Trip '{trip_name}' deleted successfully!"
        })
    except SavedTrip.DoesNotExist:
        logger.warning(f'Trip {trip_id} not found or unauthorized deletion attempt by user {request.user.id}')
        return JsonResponse({'success': False, 'message': 'Trip not found'}, status=404)
    except Exception as e:
        logger.error(f'Error deleting trip {trip_id} for user {request.user.id}: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def update_trip(request, trip_id):
    """Update trip name and data"""
    try:
        user_id = request.user.id
        logger.info(f'Update trip request from user {user_id}. Trip ID: {trip_id}')
        
        data = json.loads(request.body)
        trip = SavedTrip.objects.get(id=trip_id, user=request.user)
        
        if 'name' in data:
            old_name = trip.name
            trip.name = data['name']
            logger.info(f'Trip {trip_id} name updated from "{old_name}" to "{data["name"]}" by user {user_id}')
        
        if 'trip_data' in data:
            trip.trip_data = data['trip_data']
            logger.info(f'Trip {trip_id} data updated by user {user_id}')
        
        trip.save()
        return JsonResponse({
            'success': True,
            'message': 'Trip updated successfully!',
            'trip_name': trip.name
        })
    except SavedTrip.DoesNotExist:
        logger.warning(f'Trip {trip_id} not found or unauthorized update attempt by user {request.user.id}')
        return JsonResponse({'success': False, 'message': 'Trip not found'}, status=404)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in update_trip request from user {request.user.id}: {str(e)}')
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Error updating trip {trip_id} for user {request.user.id}: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
def saved_trips_page(request):
    """Render page to display all saved trips"""
    from django.shortcuts import render
    user_id = request.user.id
    logger.info(f'Saved trips page accessed by user {user_id} ({request.user.username})')
    return render(request, 'trip/saved_trips.html')
