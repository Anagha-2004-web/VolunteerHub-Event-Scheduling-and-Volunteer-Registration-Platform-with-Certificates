import React, { useState, useEffect } from 'react';
import { Calendar, Users, Award, Zap, QrCode, Bell, TrendingUp, Plus, X, Check, Download, Clock, MapPin, Star, Brain, Mail, BarChart3, LogIn, LogOut, RefreshCw, ExternalLink, User } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const App = () => {
  const [events, setEvents] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [signups, setSignups] = useState([]);
  const [view, setView] = useState('volunteer');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showEventForm, setShowEventForm] = useState(false);
  const [showSignupForm, setShowSignupForm] = useState(false);
  const [showVolunteerProfile, setShowVolunteerProfile] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showMyProfile, setShowMyProfile] = useState(false);
  const [currentVolunteer, setCurrentVolunteer] = useState(null);
  const [isOrganizerLoggedIn, setIsOrganizerLoggedIn] = useState(false);
  const [swapRequests, setSwapRequests] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const eventsRes = await fetch(`${API_URL}/events`);
      const volunteersRes = await fetch(`${API_URL}/volunteers`);
      const signupsRes = await fetch(`${API_URL}/signups`);
      const swapRes = await fetch(`${API_URL}/swap-requests`);
      
      if (eventsRes.ok) setEvents(await eventsRes.json());
      if (volunteersRes.ok) setVolunteers(await volunteersRes.json());
      if (signupsRes.ok) setSignups(await signupsRes.json());
      if (swapRes.ok) setSwapRequests(await swapRes.json());
    } catch (error) {
      console.log('Error loading data:', error);
    }
  };

  const showNotification = (type, message) => {
    const popup = document.createElement('div');
    popup.className = 'fixed top-4 right-4 bg-white border-2 border-blue-500 rounded-lg p-4 shadow-xl z-50 max-w-md animate-slide-in';
    popup.innerHTML = `
      <div class="flex items-start gap-3">
        <div class="text-2xl">${type === 'confirmation' ? '✅' : '🔔'}</div>
        <div class="flex-1">
          <div class="font-bold text-gray-800 mb-1">${type === 'confirmation' ? 'Success!' : 'Notification'}</div>
          <div class="text-sm text-gray-600">${message}</div>
        </div>
        <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
      </div>
    `;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 5000);
  };

  const addToGoogleCalendar = (event) => {
    const title = encodeURIComponent(event.title);
    const details = encodeURIComponent(event.description);
    const location = encodeURIComponent(event.location || '');
    const startDate = event.date.replace(/-/g, '');
    const startTime = event.time.replace(/:/g, '');
    const endTime = event.endTime.replace(/:/g, '');
    
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&location=${location}&dates=${startDate}T${startTime}00/${startDate}T${endTime}00`;
    window.open(url, '_blank');
  };

  const exportToCSV = (eventId = null) => {
    const url = eventId ? `${API_URL}/export/csv?eventId=${eventId}` : `${API_URL}/export/csv`;
    window.open(url, '_blank');
    showNotification('confirmation', 'CSV file downloaded successfully!');
  };

  const generateCertificate = (signupId) => {
    window.open(`${API_URL}/certificate/${signupId}`, '_blank');
    showNotification('confirmation', 'Certificate downloaded!');
  };

  const cancelSignup = async (signupId) => {
    if (!window.confirm('Are you sure you want to cancel this sign-up?')) return;
    
    try {
      const res = await fetch(`${API_URL}/signups/${signupId}`, { method: 'DELETE' });
      if (res.ok) {
        showNotification('confirmation', 'Sign-up cancelled successfully!');
        loadData();
      }
    } catch (error) {
      alert('Error cancelling signup');
    }
  };

  const LoginForm = () => {
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    
    const handleLogin = async (e) => {
      e.preventDefault();
      try {
        const res = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials)
        });
        const data = await res.json();
        
        if (data.success) {
          setIsOrganizerLoggedIn(true);
          setShowLogin(false);
          setView('organizer');
          showNotification('confirmation', 'Logged in successfully!');
        } else {
          alert('Invalid credentials');
        }
      } catch (error) {
        alert('Login error');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-auto">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-auto" style={{ maxHeight: 'calc(100vh - 40px)', overflowY: 'auto' }}>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Organizer Login</h2>
            <button onClick={() => setShowLogin(false)} className="text-gray-500 hover:text-gray-700">
              <X size={24} />
            </button>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input
                type="text"
                required
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="admin"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="••••••••"
              />
            </div>
            <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
              Demo: username: <strong>admin</strong>, password: <strong>admin123</strong>
            </div>
            <button type="submit" className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
              Login
            </button>
          </form>
        </div>
      </div>
    );
  };

  const AnalyticsDashboard = () => {
    const totalEvents = events.length;
    const totalSignups = signups.length;
    const totalAttended = signups.filter(s => s.attended).length;
    const attendanceRate = totalSignups > 0 ? ((totalAttended / totalSignups) * 100).toFixed(1) : 0;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
        <div className="bg-white rounded-lg p-6 max-w-4xl w-full my-8 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <BarChart3 className="text-blue-600" /> Analytics Dashboard
            </h2>
            <button onClick={() => setShowAnalytics(false)} className="text-gray-500 hover:text-gray-700">
              <X size={24} />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600 mb-1">Total Events</div>
              <div className="text-3xl font-bold text-blue-900">{totalEvents}</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 mb-1">Attendance Rate</div>
              <div className="text-3xl font-bold text-green-900">{attendanceRate}%</div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-purple-600 mb-1">Total Sign-ups</div>
              <div className="text-3xl font-bold text-purple-900">{totalSignups}</div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-sm text-orange-600 mb-1">Total Volunteers</div>
              <div className="text-3xl font-bold text-orange-900">{volunteers.length}</div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-bold text-gray-800 mb-4">Top Volunteers</h3>
            <div className="space-y-2">
              {volunteers.slice(0, 5).map((v, idx) => (
                <div key={v.id} className="flex justify-between items-center border-b pb-2">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-lg text-gray-400">#{idx + 1}</span>
                    <div>
                      <div className="font-medium text-gray-800">{v.name}</div>
                      <div className="text-xs text-gray-500">{v.eventsCompleted} events</div>
                    </div>
                  </div>
                  <div className="font-bold text-blue-600">{v.points} pts</div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6">
            <button onClick={() => exportToCSV()} className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 flex items-center justify-center gap-2">
              <Download size={20} /> Export All Data to CSV
            </button>
          </div>
        </div>
      </div>
    );
  };

  const EventForm = () => {
    const [formData, setFormData] = useState({
      title: '',
      date: '',
      time: '',
      endTime: '',
      description: '',
      budget: '',
      location: '',
      category: '',
      roles: [{ name: '', slots: 1 }]
    });

    const categories = ['Education', 'Environment', 'Health', 'Technology', 'Arts & Culture', 'Sports'];

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const res = await fetch(`${API_URL}/events`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        const data = await res.json();
        if (res.ok) {
          showNotification('confirmation', 'Event created successfully!');
          setShowEventForm(false);
          setView('organizer');
          loadData();
        } else {
          alert(`Create event failed: ${data.error || data.message || 'unknown error'}`);
        }
      } catch (error) {
        alert(`Error creating event: ${error.message || error}`);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
        <div className="bg-white rounded-lg p-6 max-w-2xl w-full my-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Create Event</h2>
            <button onClick={() => setShowEventForm(false)}><X size={24} /></button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Event Title"
            />
            
            <div className="grid grid-cols-1 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Date</span>
                <input
                  type="date"
                  required
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base"
                />
              </label>

              <label className="block">
                <span className="text-sm font-medium text-gray-700">Category</span>
                <select
                  required
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base"
                >
                  <option value="">Category...</option>
                  {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <label className="block">
                  <span className="text-sm font-medium text-gray-700">Start Time</span>
                  <input
                    type="time"
                    required
                    value={formData.time}
                    onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base"
                    placeholder="Start Time"
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-medium text-gray-700">End Time</span>
                  <input
                    type="time"
                    required
                    value={formData.endTime}
                    onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base"
                    placeholder="End Time"
                  />
                </label>
              </div>
            </div>

            <textarea
              required
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              rows="3"
              placeholder="Description"
            />
            
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Location"
            />

            <div>
              <label className="font-medium mb-2 block">Volunteer Roles</label>
              {formData.roles.map((role, idx) => (
                <div key={idx} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    required
                    value={role.name}
                    onChange={(e) => {
                      const newRoles = [...formData.roles];
                      newRoles[idx].name = e.target.value;
                      setFormData({ ...formData, roles: newRoles });
                    }}
                    className="flex-1 px-3 py-2 border rounded-lg"
                    placeholder="Role name"
                  />
                  <input
                    type="number"
                    required
                    min="1"
                    value={role.slots}
                    onChange={(e) => {
                      const newRoles = [...formData.roles];
                      newRoles[idx].slots = parseInt(e.target.value);
                      setFormData({ ...formData, roles: newRoles });
                    }}
                    className="w-20 px-3 py-2 border rounded-lg"
                    placeholder="Slots"
                  />
                </div>
              ))}
              <button
                type="button"
                onClick={() => setFormData({ ...formData, roles: [...formData.roles, { name: '', slots: 1 }] })}
                className="text-blue-600 text-sm flex items-center gap-1"
              >
                <Plus size={16} /> Add Role
              </button>
            </div>

            <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
              Create Event
            </button>
          </form>
        </div>
      </div>
    );
  };

  const VolunteerSignupForm = ({ event }) => {
    const [selectedRole, setSelectedRole] = useState('');
    const [volunteerInfo, setVolunteerInfo] = useState({ name: '', email: '', phone: '' });

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      try {
        // Create or get volunteer
        let volunteerRes = await fetch(`${API_URL}/volunteers`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(volunteerInfo)
        });
        const volunteerData = await volunteerRes.json();
        
        // Create signup
        await fetch(`${API_URL}/signups`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            eventId: event.id,
            volunteerId: volunteerData.volunteer.id,
            volunteerName: volunteerInfo.name,
            volunteerEmail: volunteerInfo.email,
            role: selectedRole
          })
        });
        
        showNotification('confirmation', `Successfully signed up for ${event.title}!`);
        setShowSignupForm(false);
        loadData();
      } catch (error) {
        alert('Error signing up');
      }
    };

    const roles = Array.isArray(event.roles) ? event.roles : [];
    const availableRoles = roles.filter(role => {
      const taken = signups.filter(s => s.eventId === event.id && s.role === role.name).length;
      return taken < (role.slots || 0);
    });

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6 max-w-lg w-full">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Sign Up for {event.title}</h2>
            <button onClick={() => setShowSignupForm(false)}><X size={24} /></button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              required
              value={volunteerInfo.name}
              onChange={(e) => setVolunteerInfo({ ...volunteerInfo, name: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Full Name"
            />
            <input
              type="email"
              required
              value={volunteerInfo.email}
              onChange={(e) => setVolunteerInfo({ ...volunteerInfo, email: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Email"
            />
            <input
              type="tel"
              required
              value={volunteerInfo.phone}
              onChange={(e) => setVolunteerInfo({ ...volunteerInfo, phone: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Phone"
            />
            
            <select
              required
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="">Select Role...</option>
              {availableRoles.map((role, idx) => {
                const taken = signups.filter(s => s.eventId === event.id && s.role === role.name).length;
                return <option key={idx} value={role.name}>{role.name} ({role.slots - taken} available)</option>;
              })}
            </select>

            <button type="submit" className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
              Sign Up
            </button>
          </form>
        </div>
      </div>
    );
  };

  const VolunteerProfileForm = () => {
    const [profileData, setProfileData] = useState({
      name: '', email: '', phone: '', bio: '', interests: [], skills: [], emergencyContact: ''
    });

    const categories = ['Education', 'Environment', 'Health', 'Technology', 'Arts & Culture', 'Sports'];
    const skillsList = ['Communication', 'Leadership', 'Technical', 'Creative', 'Organization', 'Teaching'];

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const res = await fetch(`${API_URL}/volunteers`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profileData)
        });
        const data = await res.json();
        
        setCurrentVolunteer(data.volunteer);
        setShowVolunteerProfile(false);
        showNotification('confirmation', 'Profile created successfully!');
      } catch (error) {
        alert('Error creating profile');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
        <div className="bg-white rounded-lg p-6 max-w-2xl w-full my-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Brain className="text-blue-600" /> Create Volunteer Profile
            </h2>
            <button onClick={() => setShowVolunteerProfile(false)}><X size={24} /></button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              required
              value={profileData.name}
              onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Full Name"
            />
            <input
              type="email"
              required
              value={profileData.email}
              onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Email"
            />
            <input
              type="tel"
              required
              value={profileData.phone}
              onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Phone"
            />
            
            <div>
              <label className="font-medium mb-2 block">Your Interests</label>
              <div className="flex flex-wrap gap-2">
                {categories.map(cat => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => {
                      const newInterests = profileData.interests.includes(cat)
                        ? profileData.interests.filter(i => i !== cat)
                        : [...profileData.interests, cat];
                      setProfileData({ ...profileData, interests: newInterests });
                    }}
                    className={`px-3 py-2 rounded-lg text-sm ${
                      profileData.interests.includes(cat)
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-200'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg hover:from-blue-700 hover:to-purple-700">
              Create Profile
            </button>
          </form>
        </div>
      </div>
    );
  };

  const OrganizerView = () => {
    const handleSwapApproval = async (requestId, approved) => {
      try {
        await fetch(`${API_URL}/swap-requests/${requestId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: approved ? 'approved' : 'rejected' })
        });
        showNotification('confirmation', approved ? 'Swap approved!' : 'Swap rejected!');
        loadData();
      } catch (error) {
        alert('Error processing swap');
      }
    };

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Organizer Dashboard</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowAnalytics(true)}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <BarChart3 size={20} /> Analytics
            </button>
            <button
              onClick={() => setShowEventForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus size={20} /> Create Event
            </button>
            <button
              onClick={() => {
                setIsOrganizerLoggedIn(false);
                setView('volunteer');
              }}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 flex items-center gap-2"
            >
              <LogOut size={20} /> Logout
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="text-blue-600" size={24} />
              <span className="text-sm text-gray-600">Total Events</span>
            </div>
            <div className="text-2xl font-bold text-blue-900">{events.length}</div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Users className="text-green-600" size={24} />
              <span className="text-sm text-gray-600">Total Volunteers</span>
            </div>
            <div className="text-2xl font-bold text-green-900">{volunteers.length}</div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="text-purple-600" size={24} />
              <span className="text-sm text-gray-600">Total Sign-ups</span>
            </div>
            <div className="text-2xl font-bold text-purple-900">{signups.length}</div>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Award className="text-orange-600" size={24} />
              <span className="text-sm text-gray-600">Attended</span>
            </div>
            <div className="text-2xl font-bold text-orange-900">{signups.filter(s => s.attended).length}</div>
          </div>
        </div>

        <div className="space-y-4">
          {events.map(event => {
            const eventSignups = signups.filter(s => s.eventId === event.id);
            const roles = Array.isArray(event.roles) ? event.roles : [];
            const totalSlots = roles.reduce((sum, role) => sum + (role?.slots || 0), 0);
            
            return (
              <div key={event.id} className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{event.title}</h3>
                    <p className="text-gray-600">{event.date} | {event.time} - {event.endTime}</p>
                    <p className="text-sm text-gray-500">{event.location}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{event.category}</span>
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded flex items-center gap-1">
                        <QrCode size={12} /> {event.qrCode}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => addToGoogleCalendar(event)}
                      className="bg-red-100 text-red-700 px-3 py-2 rounded-lg hover:bg-red-200 flex items-center gap-1 text-sm"
                    >
                      <ExternalLink size={16} /> Calendar
                    </button>
                    <button
                      onClick={() => exportToCSV(event.id)}
                      className="bg-green-100 text-green-700 px-3 py-2 rounded-lg hover:bg-green-200 flex items-center gap-1 text-sm"
                    >
                      <Download size={16} /> Export
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Sign-ups Progress</span>
                    <span className="font-medium">{eventSignups.length}/{totalSlots}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min((eventSignups.length / totalSlots) * 100, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-3">
                  {(Array.isArray(event.roles) ? event.roles : []).map((role, idx) => {
                    const roleSignups = eventSignups.filter(s => s.role === role.name);
                    return (
                      <div key={idx} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-semibold text-gray-800">{role.name}</h4>
                          <span className="text-sm text-gray-600">{roleSignups.length}/{role.slots} filled</span>
                        </div>
                        {roleSignups.length > 0 ? (
                          <div className="space-y-2">
                            {roleSignups.map(signup => (
                              <div key={signup.id} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                                <div className="flex items-center gap-2">
                                  {signup.attended && <Check className="text-green-600" size={16} />}
                                  <span className="text-sm">{signup.volunteerName}</span>
                                  <span className="text-xs text-gray-500">{signup.volunteerEmail}</span>
                                </div>
                                <div className="flex gap-2">
                                  {!signup.attended && (
                                    <button
                                      onClick={async () => {
                                        await fetch(`${API_URL}/signups/${signup.id}`, {
                                          method: 'PUT',
                                          headers: { 'Content-Type': 'application/json' },
                                          body: JSON.stringify({ attended: true })
                                        });
                                        showNotification('confirmation', 'Attendance marked!');
                                        loadData();
                                      }}
                                      className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                                    >
                                      Mark Attended
                                    </button>
                                  )}
                                  {signup.attended && (
                                    <button
                                      onClick={() => generateCertificate(signup.id)}
                                      className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 flex items-center gap-1"
                                    >
                                      <Download size={12} /> Certificate
                                    </button>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-400 italic">No volunteers signed up yet</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const VolunteerView = () => {
    const mySignups = currentVolunteer ? signups.filter(s => s.volunteerId === currentVolunteer.id) : [];
    
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Available Events</h2>
          {!currentVolunteer && (
            <button
              onClick={() => setShowVolunteerProfile(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 flex items-center gap-2"
            >
              <Brain size={20} /> Create Profile
            </button>
          )}
        </div>

        {currentVolunteer && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-bold text-purple-900">Welcome back, {currentVolunteer.name}! 👋</h3>
                <p className="text-sm text-purple-700">Points: {currentVolunteer.points} | Events: {currentVolunteer.eventsCompleted}</p>
              </div>
              <button onClick={() => setCurrentVolunteer(null)} className="text-purple-600 hover:text-purple-800">
                Switch Profile
              </button>
            </div>
          </div>
        )}

        {mySignups.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-bold text-blue-900 mb-3">My Upcoming Events</h3>
            <div className="space-y-2">
              {mySignups.map(signup => {
                const event = events.find(e => e.id === signup.eventId);
                if (!event) return null;
                return (
                  <div key={signup.id} className="bg-white p-3 rounded-lg flex justify-between items-center">
                    <div>
                      <p className="font-medium">{event.title}</p>
                      <p className="text-sm text-gray-600">{event.date} at {event.time} - Role: {signup.role}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => addToGoogleCalendar(event)}
                        className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 flex items-center gap-1"
                      >
                        <ExternalLink size={12} /> Calendar
                      </button>
                      <button
                        onClick={() => cancelSignup(signup.id)}
                        className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200">
          <h3 className="text-lg font-bold text-purple-900 mb-2 flex items-center gap-2">
            <Award size={24} /> Top Volunteers Leaderboard
          </h3>
          <div className="space-y-2">
            {volunteers.sort((a, b) => b.points - a.points).slice(0, 5).map((v, idx) => (
              <div key={v.id} className="flex justify-between items-center bg-white p-3 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-lg text-gray-400">#{idx + 1}</span>
                  <div>
                    <p className="font-medium text-gray-800">{v.name}</p>
                    <p className="text-xs text-gray-500">{v.eventsCompleted} events completed</p>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-yellow-600 font-bold">
                  <Zap size={16} fill="currentColor" />
                  {v.points} pts
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {events.length === 0 ? (
            <div className="col-span-full p-4 text-center text-gray-500">No events available yet.</div>
          ) : events.map(event => {
            const eventSignups = signups.filter(s => s.eventId === event.id);
            const roles = Array.isArray(event.roles) ? event.roles : [];
            const totalSlots = roles.reduce((sum, role) => sum + (role?.slots || 0), 0);
            const filledSlots = eventSignups.length;
            const isSignedUp = currentVolunteer && mySignups.some(s => s.eventId === event.id);
            
            return (
              <div key={event.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-bold text-gray-800">{event.title}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${filledSlots >= totalSlots ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {filledSlots >= totalSlots ? 'Full' : 'Open'}
                  </span>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                  <span className="flex items-center gap-1"><Calendar size={14} /> {event.date}</span>
                  <span className="flex items-center gap-1"><Clock size={14} /> {event.time}</span>
                </div>
                
                {event.location && (
                  <p className="text-sm text-gray-600 mb-2 flex items-center gap-1">
                    <MapPin size={14} /> {event.location}
                  </p>
                )}
                
                <p className="text-sm text-gray-600 mb-4">{event.description}</p>

                <div className="flex items-center gap-2 mb-4">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{event.category}</span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded flex items-center gap-1">
                    <QrCode size={12} /> {event.qrCode}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  {(Array.isArray(event.roles) ? event.roles : []).map((role, idx) => {
                    const roleSignups = eventSignups.filter(s => s.role === role.name);
                    const available = (role.slots || 0) - roleSignups.length;
                    return (
                      <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-medium text-gray-800 text-sm">{role.name}</span>
                        <span className={`text-sm ${available > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {available > 0 ? `${available} available` : 'Full'}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {isSignedUp ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                    <p className="text-green-800 font-medium flex items-center justify-center gap-2">
                      <Check size={16} /> You're signed up!
                    </p>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setSelectedEvent(event);
                      setShowSignupForm(true);
                    }}
                    disabled={filledSlots >= totalSlots}
                    className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                      filledSlots >= totalSlots
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {filledSlots >= totalSlots ? 'Event Full' : 'Sign Up Now'}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="bg-white shadow-md border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Calendar className="text-white" size={28} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">VolunteerHub Pro</h1>
                <p className="text-sm text-gray-600">Complete Event Management System</p>
              </div>
            </div>
            
            <div className="flex gap-2">
              {!isOrganizerLoggedIn ? (
                <>
                  <button
                    onClick={() => setView('volunteer')}
                    className={`px-4 py-2 rounded-lg font-medium ${view === 'volunteer' ? 'bg-green-600 text-white' : 'bg-gray-100'}`}
                  >
                    Volunteer
                  </button>
                  <button
                    onClick={() => setShowLogin(true)}
                    className="px-4 py-2 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 flex items-center gap-2"
                  >
                    <LogIn size={20} /> Organizer Login
                  </button>
                </>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isOrganizerLoggedIn ? <OrganizerView /> : <VolunteerView />}
      </div>

      {showLogin && <LoginForm />}
      {showEventForm && <EventForm />}
      {showSignupForm && selectedEvent && <VolunteerSignupForm event={selectedEvent} />}
      {showVolunteerProfile && <VolunteerProfileForm />}
      {showAnalytics && <AnalyticsDashboard />}

      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default App;