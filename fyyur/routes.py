from flask import Flask, render_template, request, Response, flash, redirect, url_for
from fyyur import app, db
from fyyur.models import Venue, Artist, Show
from fyyur.forms import *
import sys
from sqlalchemy import func
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # get data in my local database
  all_areas  = db.session.query(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []
  for area in all_areas :
    a_veunes = db.session.query(Venue).filter(Venue.state == area.state, Venue.city == area.city).all()
    venue_data = []
    for venue in a_veunes:
      upcoming_shows_count = db.session.query(func.count(Show.id)).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).scalar()
      venue_data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming_shows_count
      })
    data.append({
        "city": area.city,
        "state": area.state,
        "venues": venue_data
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # post sershing and get data in database
  search_term = request.form.get('search_term', '')
  search_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in search_result:
    upcoming_shows_count = db.session.query(func.count(Show.id)).filter(Show.venue_id == result.id, Show.start_time > datetime.now()).scalar()
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": upcoming_shows_count
    })

  response = {
    "count": len(search_result),
    "data": data
}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # post sershing and get data in database
  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('pages/home.html')
  
  upcoming_shows = []
  past_shows = []

  for show in venue.shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
    else:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # add data in database
  done = True
  try: 
    if request.form['seeking_talent'] == 'y' :
      seeking_talent = True
    else :
      seeking_talent = False

    venue = Venue(name= request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], facebook_link=request.form['facebook_link'], image_link=request.form['image_link'], website_link = request.form['website_link'], genres = request.form.getlist('genres'), seeking_description = request.form['seeking_description'], seeking_talent = seeking_talent)
    db.session.add(venue)
    db.session.commit()
  except: 
    done = False
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    if done :
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # delete venue in database
  done = True
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    done = False
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if done :
      flash(f'Venue {venue_id} was successfully deleted.')
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  #get data artist in database
  data= db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # post sershing and get data in database
  search_term = request.form.get('search_term', '')
  search_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in search_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count": len(search_result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = db.session.query(Artist).get(artist_id)

  if not artist:
    return render_template('pages/home.html')
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
  past_shows_count = db.session.query(func.count()).filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).scalar()

  past_shows = []

  for show in past_shows_query:
    past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).all()
  upcoming_shows_count = db.session.query(func.count()).filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).scalar()

  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # get data in databade for user
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_talent
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # update data in databade for user
  done = True
  artist = Artist.query.get(artist_id)

  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    done = False
    flash('An error occurred. Artist could not be changed.')
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    if done :
      flash('Artist was successfully updated!')
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # get data in databade for user
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # update data in databade for user
  done = True
  venue = Venue.query.get(venue_id)

  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    flash(f'An error occurred. Venue could not be changed.')
    done = False
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    if done :
      flash(f'Venue was successfully updated!')
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # add data in database
  done = True
  try:
    artist = Artist( name=request.form['name'], city=request.form['city'], state=request.form['state'], seeking_talent =True if 'seeking_venue' in request.form else False , phone=request.form['phone'], facebook_link=request.form['facebook_link'], image_link=request.form['image_link'], website_link = request.form['website_link'], genres = request.form.getlist('genres'), seeking_description = request.form['seeking_description'])
    db.session.add(artist)
    db.session.commit()
  except: 
    done = False
    flash('An error occurred. Artis ' + request.form['name']+ ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    if done:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # get data in database
  shows = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in shows: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # add data in database
  done = True
  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except: 
    done = False
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    if done :
      flash('Show was successfully listed')
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


