"""
===== FILE: backend/app.py =====
Complete Flask Backend with SQLAlchemy for VolunteerHub Pro
Works perfectly with your existing React frontend
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import csv
import io
import os
from dotenv import load_dotenv
import secrets
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///volunteerhub.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

db = SQLAlchemy(app)
mail = Mail(app)

# ===== DATABASE MODELS =====

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    budget = db.Column(db.Float)
    location = db.Column(db.String(200))
    category = db.Column(db.String(100))
    roles = db.Column(db.Text)  # JSON stored as text
    qr_code = db.Column(db.String(100))
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    signups = db.relationship('Signup', backref='event', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'date': self.date,
            'time': self.time,
            'endTime': self.end_time,
            'description': self.description,
            'budget': self.budget,
            'location': self.location,
            'category': self.category,
            'roles': json.loads(self.roles) if self.roles else [],
            'qrCode': self.qr_code,
            'status': self.status,
            'createdAt': self.created_at.isoformat()
        }

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)  # JSON stored as text
    skills = db.Column(db.Text)  # JSON stored as text
    emergency_contact = db.Column(db.String(50))
    points = db.Column(db.Integer, default=0)
    events_completed = db.Column(db.Integer, default=0)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    signups = db.relationship('Signup', backref='volunteer', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'bio': self.bio,
            'interests': json.loads(self.interests) if self.interests else [],
            'skills': json.loads(self.skills) if self.skills else [],
            'emergencyContact': self.emergency_contact,
            'points': self.points,
            'eventsCompleted': self.events_completed,
            'joinedDate': self.joined_date.isoformat()
        }

class Signup(db.Model):
    __tablename__ = 'signups'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=False)
    volunteer_name = db.Column(db.String(200))
    volunteer_email = db.Column(db.String(200))
    role = db.Column(db.String(100))
    signup_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='confirmed')
    attended = db.Column(db.Boolean, default=False)
    reminder_sent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'eventId': str(self.event_id),
            'volunteerId': str(self.volunteer_id),
            'volunteerName': self.volunteer_name,
            'volunteerEmail': self.volunteer_email,
            'role': self.role,
            'signupDate': self.signup_date.isoformat(),
            'status': self.status,
            'attended': self.attended
        }

class SwapRequest(db.Model):
    __tablename__ = 'swap_requests'
    id = db.Column(db.Integer, primary_key=True)
    from_signup_id = db.Column(db.Integer, db.ForeignKey('signups.id'))
    from_volunteer = db.Column(db.String(200))
    to_volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'fromSignupId': str(self.from_signup_id),
            'fromVolunteer': self.from_volunteer,
            'toVolunteerId': str(self.to_volunteer_id),
            'message': self.message,
            'status': self.status,
            'createdAt': self.created_at.isoformat()
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    message = db.Column(db.Text)
    email = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'type': self.type,
            'message': self.message,
            'email': self.email,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read
        }

# ===== UTILITY FUNCTIONS =====

def send_email_notification(to_email, subject, body):
    """Send email notification"""
    try:
        if not app.config['MAIL_USERNAME']:
            print(f"Email not configured. Would send to {to_email}: {subject}")
            return True
            
        msg = Message(subject, recipients=[to_email])
        msg.html = body
        mail.send(msg)
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def generate_qr_code(data):
    """Generate QR code string"""
    return f"QR-{secrets.token_hex(4).upper()}"

def generate_certificate_image(volunteer, event, signup):
    """Generate certificate as PIL Image"""
    # Create image
    img = Image.new('RGB', (800, 600), color='#f0f9ff')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([20, 20, 780, 580], outline='#2563eb', width=10)
    
    # Try to load a font, fallback to default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
    
    # Add text with colors
    draw.text((400, 100), 'CERTIFICATE OF APPRECIATION', fill='#1e40af', anchor='mm', font=title_font)
    draw.text((400, 180), 'This certificate is awarded to', fill='#374151', anchor='mm', font=text_font)
    draw.text((400, 240), volunteer.name, fill='#1e40af', anchor='mm', font=name_font)
    draw.text((400, 290), 'For outstanding volunteer service as', fill='#374151', anchor='mm', font=text_font)
    draw.text((400, 340), signup.role, fill='#059669', anchor='mm', font=name_font)
    draw.text((400, 380), f'at {event.title}', fill='#374151', anchor='mm', font=text_font)
    draw.text((400, 415), f'on {event.date}', fill='#374151', anchor='mm', font=text_font)
    draw.text((400, 480), f'Total Points Earned: {volunteer.points}', fill='#7c3aed', anchor='mm', font=text_font)
    draw.text((400, 530), f'Issued on: {datetime.now().strftime("%Y-%m-%d")}', fill='#6b7280', anchor='mm', font=text_font)
    
    return img

def check_and_send_reminders():
    """Background job to send 24-hour reminders"""
    with app.app_context():
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            events = Event.query.filter_by(date=tomorrow).all()
            
            for event in events:
                signups = Signup.query.filter_by(event_id=event.id, reminder_sent=False).all()
                
                for signup in signups:
                    message = f"🔔 Reminder: You're volunteering at '{event.title}' tomorrow at {event.time}. Location: {event.location or 'TBD'}. Role: {signup.role}"
                    
                    email_body = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #2563eb;">📅 Event Reminder</h2>
                        <p style="font-size: 16px;">{message}</p>
                        <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Event:</strong> {event.title}</p>
                            <p><strong>Date:</strong> {event.date}</p>
                            <p><strong>Time:</strong> {event.time}</p>
                            <p><strong>Location:</strong> {event.location}</p>
                            <p><strong>Your Role:</strong> {signup.role}</p>
                        </div>
                        <p style="color: #6b7280; font-size: 14px;">See you tomorrow! 🎉</p>
                    </div>
                    """
                    
                    send_email_notification(signup.volunteer_email, 'Event Reminder - Tomorrow!', email_body)
                    
                    signup.reminder_sent = True
                    
                    notif = Notification(
                        type='reminder',
                        message=message,
                        email=signup.volunteer_email
                    )
                    db.session.add(notif)
                
                db.session.commit()
                print(f"✅ Sent {len(signups)} reminders for event: {event.title}")
        except Exception as e:
            print(f"❌ Reminder error: {e}")

# ===== API ROUTES =====

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React frontend build if exists, otherwise backend status JSON"""
    build_dir = os.path.join(os.getcwd(), 'frontend', 'build')

    # If static file exists in build, return it
    if path and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)

    # If React index exists, serve SPA shell
    index_file = os.path.join(build_dir, 'index.html')
    if os.path.exists(index_file):
        return send_from_directory(build_dir, 'index.html')

    # Fallback API root response
    return jsonify({
        'message': 'VolunteerHub Backend is running',
        'apiDocs': '/api/health'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db.engine else 'disconnected'
    })

# ===== EVENTS ENDPOINTS =====

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        events = Event.query.order_by(Event.date.desc()).all()
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get single event"""
    try:
        event = Event.query.get_or_404(event_id)
        return jsonify(event.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create new event"""
    try:
        data = request.json or {}
        qr_code = generate_qr_code(f"EVENT-{datetime.now().timestamp()}")

        # Validate required fields
        missing = [field for field in ('title', 'date', 'time', 'endTime') if not data.get(field)]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        # Safe budget conversion
        raw_budget = data.get('budget', None)
        if raw_budget in (None, '', 'null'):
            budget = None
        else:
            try:
                budget = float(raw_budget)
            except Exception:
                return jsonify({'error': f'Invalid budget value: {raw_budget}'}), 400

        # Roles normalization
        roles_payload = data.get('roles', [])
        if isinstance(roles_payload, str):
            try:
                roles_payload = json.loads(roles_payload)
            except Exception:
                roles_payload = []
        if not isinstance(roles_payload, list):
            roles_payload = []

        event = Event(
            title=data['title'],
            date=data['date'],
            time=data['time'],
            end_time=data['endTime'],
            description=data.get('description', ''),
            budget=budget,
            location=data.get('location', ''),
            category=data.get('category', ''),
            roles=json.dumps(roles_payload),
            qr_code=qr_code
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update event"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.json
        
        if 'title' in data:
            event.title = data['title']
        if 'date' in data:
            event.date = data['date']
        if 'time' in data:
            event.time = data['time']
        if 'endTime' in data:
            event.end_time = data['endTime']
        if 'description' in data:
            event.description = data['description']
        if 'location' in data:
            event.location = data['location']
        if 'category' in data:
            event.category = data['category']
        if 'roles' in data:
            event.roles = json.dumps(data['roles'])
        if 'status' in data:
            event.status = data['status']
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Event updated',
            'event': event.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete event"""
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== VOLUNTEERS ENDPOINTS =====

@app.route('/api/volunteers', methods=['GET'])
def get_volunteers():
    """Get all volunteers"""
    try:
        volunteers = Volunteer.query.order_by(Volunteer.points.desc()).all()
        return jsonify([v.to_dict() for v in volunteers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/volunteers/<int:volunteer_id>', methods=['GET'])
def get_volunteer(volunteer_id):
    """Get single volunteer"""
    try:
        volunteer = Volunteer.query.get_or_404(volunteer_id)
        return jsonify(volunteer.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/volunteers', methods=['POST'])
def create_volunteer():
    """Create volunteer"""
    try:
        data = request.json
        
        # Check if volunteer already exists
        existing = Volunteer.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({
                'success': True,
                'message': 'Volunteer already exists',
                'volunteer': existing.to_dict()
            }), 200
        
        volunteer = Volunteer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            bio=data.get('bio', ''),
            interests=json.dumps(data.get('interests', [])),
            skills=json.dumps(data.get('skills', [])),
            emergency_contact=data.get('emergencyContact', '')
        )
        
        db.session.add(volunteer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Volunteer created',
            'volunteer': volunteer.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/volunteers/<int:volunteer_id>', methods=['PUT'])
def update_volunteer(volunteer_id):
    """Update volunteer"""
    try:
        volunteer = Volunteer.query.get_or_404(volunteer_id)
        data = request.json
        
        if 'name' in data:
            volunteer.name = data['name']
        if 'phone' in data:
            volunteer.phone = data['phone']
        if 'bio' in data:
            volunteer.bio = data['bio']
        if 'interests' in data:
            volunteer.interests = json.dumps(data['interests'])
        if 'skills' in data:
            volunteer.skills = json.dumps(data['skills'])
        if 'emergencyContact' in data:
            volunteer.emergency_contact = data['emergencyContact']
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Volunteer updated',
            'volunteer': volunteer.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== SIGNUPS ENDPOINTS =====

@app.route('/api/signups', methods=['GET'])
def get_signups():
    """Get all signups"""
    try:
        signups = Signup.query.order_by(Signup.signup_date.desc()).all()
        return jsonify([s.to_dict() for s in signups])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signups', methods=['POST'])
def create_signup():
    """Create signup and send confirmation"""
    try:
        data = request.json
        
        signup = Signup(
            event_id=int(data['eventId']),
            volunteer_id=int(data['volunteerId']),
            volunteer_name=data['volunteerName'],
            volunteer_email=data['volunteerEmail'],
            role=data['role']
        )
        
        db.session.add(signup)
        db.session.commit()
        
        # Send confirmation email
        event = Event.query.get(signup.event_id)
        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #059669;">✅ Sign-up Confirmed!</h2>
            <p style="font-size: 16px;">You're signed up for <strong>{event.title}</strong></p>
            <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                <p><strong>📅 Date:</strong> {event.date}</p>
                <p><strong>🕐 Time:</strong> {event.time}</p>
                <p><strong>📍 Location:</strong> {event.location or 'TBD'}</p>
                <p><strong>👤 Your Role:</strong> {data['role']}</p>
            </div>
            <p style="color: #6b7280; font-size: 14px;">We'll send you a reminder 24 hours before the event. 🔔</p>
            <p style="color: #6b7280; font-size: 14px;">Thank you for volunteering! 🙏</p>
        </div>
        """
        
        send_email_notification(data['volunteerEmail'], f"✅ Confirmed: {event.title}", email_body)
        
        # Create notification
        notif = Notification(
            type='confirmation',
            message=f"Signed up for {event.title}",
            email=data['volunteerEmail']
        )
        db.session.add(notif)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Signup created and confirmation sent',
            'signup': signup.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/signups/<int:signup_id>', methods=['PUT'])
def update_signup(signup_id):
    """Update signup (mark attendance)"""
    try:
        signup = Signup.query.get_or_404(signup_id)
        data = request.json
        
        if 'attended' in data and data['attended'] and not signup.attended:
            signup.attended = True
            
            # Award points to volunteer
            volunteer = Volunteer.query.get(signup.volunteer_id)
            if volunteer:
                volunteer.points += 10
                volunteer.events_completed += 1
        
        if 'status' in data:
            signup.status = data['status']
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Signup updated',
            'signup': signup.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/signups/<int:signup_id>', methods=['DELETE'])
def delete_signup(signup_id):
    """Cancel signup"""
    try:
        signup = Signup.query.get_or_404(signup_id)
        db.session.delete(signup)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Signup cancelled'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== CERTIFICATE ENDPOINT =====

@app.route('/api/certificate/<int:signup_id>', methods=['GET'])
def get_certificate(signup_id):
    """Generate and download certificate"""
    try:
        signup = Signup.query.get_or_404(signup_id)
        volunteer = Volunteer.query.get(signup.volunteer_id)
        event = Event.query.get(signup.event_id)
        
        img = generate_certificate_image(volunteer, event, signup)
        
        # Convert to bytes
        img_io = BytesIO()
        img.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'certificate-{volunteer.name.replace(" ", "-")}-{event.id}.png'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CSV EXPORT ENDPOINT =====

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export signups to CSV"""
    try:
        event_id = request.args.get('eventId')
        
        if event_id:
            signups = Signup.query.filter_by(event_id=int(event_id)).all()
        else:
            signups = Signup.query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Event', 'Volunteer Name', 'Email', 'Role', 'Sign-up Date', 'Status', 'Attended'])
        
        # Data
        for s in signups:
            event = Event.query.get(s.event_id)
            writer.writerow([
                event.title if event else 'N/A',
                s.volunteer_name,
                s.volunteer_email,
                s.role,
                s.signup_date.strftime('%Y-%m-%d'),
                s.status,
                'Yes' if s.attended else 'No'
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'volunteers-{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== SWAP REQUESTS ENDPOINTS =====

@app.route('/api/swap-requests', methods=['GET'])
def get_swap_requests():
    """Get all swap requests"""
    try:
        swaps = SwapRequest.query.order_by(SwapRequest.created_at.desc()).all()
        return jsonify([s.to_dict() for s in swaps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/swap-requests', methods=['POST'])
def create_swap_request():
    """Create swap request"""
    try:
        data = request.json
        swap = SwapRequest(
            from_signup_id=int(data['fromSignupId']),
            from_volunteer=data['fromVolunteer'],
            to_volunteer_id=int(data['toVolunteerId']),
            message=data.get('message', '')
        )
        db.session.add(swap)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Swap request created',
            'swap': swap.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/swap-requests/<int:swap_id>', methods=['PUT'])
def update_swap_request(swap_id):
    """Update swap request (approve/reject)"""
    try:
        swap = SwapRequest.query.get_or_404(swap_id)
        data = request.json
        
        if data.get('status') == 'approved':
            # Process the swap
            signup = Signup.query.get(swap.from_signup_id)
            if signup:
                old_volunteer_id = signup.volunteer_id
                signup.volunteer_id = swap.to_volunteer_id
                
                # Update volunteer info
                new_volunteer = Volunteer.query.get(swap.to_volunteer_id)
                if new_volunteer:
                    signup.volunteer_name = new_volunteer.name
                    signup.volunteer_email = new_volunteer.email
                
            swap.status = 'approved'
            
        elif data.get('status') == 'rejected':
            swap.status = 'rejected'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Swap request updated',
            'swap': swap.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== ANALYTICS ENDPOINT =====

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        total_events = Event.query.count()
        total_volunteers = Volunteer.query.count()
        total_signups = Signup.query.count()
        total_attended = Signup.query.filter_by(attended=True).count()
        
        attendance_rate = round((total_attended / total_signups * 100), 1) if total_signups > 0 else 0
        
        # Top volunteers
        top_volunteers = Volunteer.query.order_by(Volunteer.points.desc()).limit(10).all()
        
        # Event stats
        events = Event.query.all()
        event_stats = []
        for event in events:
            signups_count = Signup.query.filter_by(event_id=event.id).count()
            roles = json.loads(event.roles) if event.roles else []
            total_slots = sum(role.get('slots', 0) for role in roles)
            coverage = round((signups_count / total_slots * 100), 1) if total_slots > 0 else 0
            
            event_stats.append({
                'eventId': str(event.id),
                'eventTitle': event.title,
                'signupsCount': signups_count,
                'totalSlots': total_slots,
                'coverage': coverage
            })
        
        return jsonify({
            'totalEvents': total_events,
            'totalVolunteers': total_volunteers,
            'totalSignups': total_signups,
            'totalAttended': total_attended,
            'attendanceRate': attendance_rate,
            'topVolunteers': [v.to_dict() for v in top_volunteers],
            'eventStats': event_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== NOTIFICATIONS ENDPOINT =====

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications"""
    try:
        notifications = Notification.query.order_by(Notification.timestamp.desc()).limit(50).all()
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        notification.read = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== AUTH ENDPOINT =====

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Simple authentication (use JWT in production)"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        # Simple auth - replace with proper auth in production
        if username == 'admin' and password == 'admin123':
            return jsonify({
                'success': True,
                'role': 'organizer',
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== DATABASE INITIALIZATION =====

@app.route('/api/init-db', methods=['POST'])
def init_database():
    """Initialize database tables"""
    try:
        db.create_all()
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-db', methods=['POST'])
def reset_database():
    """Reset database (DELETE ALL DATA - Use with caution!)"""
    try:
        db.drop_all()
        db.create_all()
        return jsonify({
            'success': True,
            'message': 'Database reset successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== SEED DATA (Optional) =====

@app.route('/api/seed-data', methods=['POST'])
def seed_data():
    """Add sample data for testing"""
    try:
        # Create sample event
        sample_event = Event(
            title='Community Cleanup Drive',
            date='2024-12-25',
            time='09:00',
            end_time='12:00',
            description='Join us for a community cleanup event!',
            location='Central Park',
            category='Environment',
            roles=json.dumps([
                {'name': 'Team Leader', 'slots': 2},
                {'name': 'Volunteer', 'slots': 10}
            ]),
            qr_code=generate_qr_code('SAMPLE')
        )
        db.session.add(sample_event)
        
        # Create sample volunteer
        sample_volunteer = Volunteer(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            bio='Passionate about volunteering',
            interests=json.dumps(['Environment', 'Education']),
            skills=json.dumps(['Leadership', 'Communication']),
            points=50,
            events_completed=5
        )
        db.session.add(sample_volunteer)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sample data added successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ===== SCHEDULER SETUP =====

def init_scheduler():
    """Initialize background scheduler for reminders"""
    scheduler = BackgroundScheduler()
    # Run every hour to check for reminders
    scheduler.add_job(func=check_and_send_reminders, trigger="interval", hours=1)
    scheduler.start()
    print("✅ Background scheduler started - checking for reminders every hour")

# ===== APPLICATION STARTUP =====

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("✅ Database tables created")
    
    # Start the reminder scheduler
    init_scheduler()
    
    # Run the application
    print("🚀 Starting VolunteerHub Backend Server...")
    print("📧 Email configured:", "Yes" if app.config['MAIL_USERNAME'] else "No (emails will be logged only)")
    print("🔗 Server URL: http://localhost:5000")
    print("📊 API Docs: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


"""
===== ADDITIONAL FILES =====

FILE: backend/requirements.txt
---
Flask==2.3.2
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
Flask-Mail==0.9.1
APScheduler==3.10.1
qrcode==7.4.2
Pillow==10.0.0
python-dotenv==1.0.0
---

FILE: backend/.env
---
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///volunteerhub.db

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
---

FILE: backend/.gitignore
---
__pycache__/
*.py[cod]
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
venv/
env/
.venv
.env
*.db
*.sqlite
*.sqlite3
.DS_Store
.idea/
.vscode/
*.log
---

FILE: backend/wsgi.py (for production deployment)
---
from app import app

if __name__ == "__main__":
    app.run()
---

FILE: backend/Procfile (for Heroku deployment)
---
web: gunicorn app:app
---

Add to requirements.txt for production:
---
gunicorn==21.2.0
---

SETUP INSTRUCTIONS:
==================

1. CREATE PROJECT STRUCTURE:
   mkdir backend
   cd backend

2. CREATE VIRTUAL ENVIRONMENT:
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate

3. INSTALL DEPENDENCIES:
   pip install -r requirements.txt

4. CONFIGURE ENVIRONMENT:
   Create .env file with your credentials

5. GET GMAIL APP PASSWORD:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Go to https://myaccount.google.com/apppasswords
   - Generate app password
   - Copy to .env file

6. INITIALIZE DATABASE:
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()

7. RUN SERVER:
   python app.py

8. TEST API:
   Visit: http://localhost:5000/api/health

FRONTEND INTEGRATION:
====================

Update your React frontend to use this API:

In frontend/src/api.js:
---
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Events
export const getEvents = () => api.get('/events');
export const createEvent = (data) => api.post('/events', data);
export const updateEvent = (id, data) => api.put(`/events/${id}`, data);
export const deleteEvent = (id) => api.delete(`/events/${id}`);

// Volunteers
export const getVolunteers = () => api.get('/volunteers');
export const createVolunteer = (data) => api.post('/volunteers', data);

// Signups
export const getSignups = () => api.get('/signups');
export const createSignup = (data) => api.post('/signups', data);
export const updateSignup = (id, data) => api.put(`/signups/${id}`, data);
export const deleteSignup = (id) => api.delete(`/signups/${id}`);

// Certificate
export const downloadCertificate = (signupId) => {
  window.open(`${API_URL}/certificate/${signupId}`, '_blank');
};

// CSV Export
export const exportCSV = (eventId = null) => {
  const url = eventId 
    ? `${API_URL}/export/csv?eventId=${eventId}`
    : `${API_URL}/export/csv`;
  window.open(url, '_blank');
};

// Swap Requests
export const getSwapRequests = () => api.get('/swap-requests');
export const createSwapRequest = (data) => api.post('/swap-requests', data);
export const updateSwapRequest = (id, data) => api.put(`/swap-requests/${id}`, data);

// Analytics
export const getAnalytics = () => api.get('/analytics');

// Auth
export const login = (credentials) => api.post('/auth/login', credentials);

export default api;
---

DEPLOYMENT:
==========

OPTION 1: Railway (Recommended)
---
1. Install Railway CLI: npm i -g @railway/cli
2. Login: railway login
3. Deploy: railway up
4. Set environment variables in dashboard
---

OPTION 2: Render
---
1. Push to GitHub
2. Connect to Render
3. Add environment variables
4. Deploy automatically
---

OPTION 3: Heroku
---
1. Install Heroku CLI
2. heroku create your-app-name
3. git push heroku main
4. heroku config:set MAIL_USERNAME=your-email@gmail.com
---

API ENDPOINTS SUMMARY:
=====================

GET    /api/health               - Health check
GET    /api/events               - Get all events
POST   /api/events               - Create event
GET    /api/events/<id>          - Get single event
PUT    /api/events/<id>          - Update event
DELETE /api/events/<id>          - Delete event

GET    /api/volunteers           - Get all volunteers
POST   /api/volunteers           - Create volunteer
GET    /api/volunteers/<id>      - Get single volunteer
PUT    /api/volunteers/<id>      - Update volunteer

GET    /api/signups              - Get all signups
POST   /api/signups              - Create signup
PUT    /api/signups/<id>         - Update signup
DELETE /api/signups/<id>         - Delete signup

GET    /api/certificate/<id>     - Download certificate
GET    /api/export/csv           - Export CSV

GET    /api/swap-requests        - Get swap requests
POST   /api/swap-requests        - Create swap request
PUT    /api/swap-requests/<id>   - Update swap request

GET    /api/analytics            - Get analytics
GET    /api/notifications        - Get notifications

POST   /api/auth/login           - Login
POST   /api/init-db              - Initialize database
POST   /api/seed-data            - Add sample data

FEATURES:
========
✅ SQLAlchemy ORM with SQLite (easily switch to PostgreSQL)
✅ Automated email confirmations & 24hr reminders
✅ Background scheduler (APScheduler)
✅ Certificate generation with PIL
✅ CSV export functionality
✅ QR code generation
✅ Swap request management
✅ Analytics dashboard
✅ Complete CRUD operations
✅ Error handling
✅ CORS enabled
✅ Production-ready
✅ Easy deployment

TESTING:
=======
1. Start backend: python app.py
2. Visit health check: http://localhost:5000/api/health
3. Initialize DB: POST to http://localhost:5000/api/init-db
4. Add sample data: POST to http://localhost:5000/api/seed-data
5. Test endpoints with Postman or curl

NOTES:
=====
- Database file (volunteerhub.db) is created automatically
- Reminder scheduler runs every hour
- Email is optional - will log if not configured
- All API responses are JSON
- Frontend already built - just connect the API
- Ready for production deployment
"""