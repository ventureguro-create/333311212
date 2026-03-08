/**
 * Radar Page - Geo Intelligence Module
 * Clean layout - no sidebar, no topbar
 */
import { useState, useEffect, useCallback } from 'react';
import {
  MapPin,
  RefreshCw,
  Loader2,
  Radio,
  TrendingUp,
  Eye,
  Sparkles,
  Map,
  List,
  BarChart3
} from 'lucide-react';
import GeoMap from '../components/GeoMap';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

export default function RadarPage() {
  // State
  const [view, setView] = useState('map');
  const [loading, setLoading] = useState(false);
  
  // Channels
  const [channels, setChannels] = useState([]);
  const [channelsLoading, setChannelsLoading] = useState(false);
  
  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  
  // Map data
  const [mapPoints, setMapPoints] = useState([]);
  const [mapLoading, setMapLoading] = useState(false);
  
  // Top places
  const [topPlaces, setTopPlaces] = useState([]);
  const [topLoading, setTopLoading] = useState(false);
  
  // Summary
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  
  // Stats
  const [stats, setStats] = useState(null);
  
  // Filters
  const [days, setDays] = useState(7);
  const [eventType, setEventType] = useState('all');
  
  // Selected marker for highlighting
  const [selectedMarkerId, setSelectedMarkerId] = useState(null);
  const [mapRef, setMapRef] = useState(null);
  
  // Handle marker click from sidebar - fly to location
  const handleMarkerSelect = (point) => {
    setSelectedMarkerId(point.id);
    // Map will handle the fly-to via the selectedMarkerId prop
  };
  
  // Fetch radar channels
  const fetchChannels = useCallback(async () => {
    setChannelsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/geo/channels`);
      const data = await res.json();
      if (data.ok) setChannels(data.items || []);
    } catch (err) {
      console.error('Channels error:', err);
    } finally {
      setChannelsLoading(false);
    }
  }, []);
  
  // Search channels
  const searchChannels = useCallback(async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const res = await fetch(`${API_BASE}/api/geo/search/channels?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (data.ok) setSearchResults(data.items || []);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  }, []);
  
  // Add channel to radar
  const addChannel = async (username) => {
    try {
      const res = await fetch(`${API_BASE}/api/geo/channels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });
      const data = await res.json();
      if (data.ok) {
        fetchChannels();
        setSearchQuery('');
        setSearchResults([]);
      }
    } catch (err) {
      console.error('Add channel error:', err);
    }
  };
  
  // Remove channel from radar
  const removeChannel = async (username) => {
    try {
      await fetch(`${API_BASE}/api/geo/channels/${username}`, { method: 'DELETE' });
      fetchChannels();
    } catch (err) {
      console.error('Remove channel error:', err);
    }
  };
  
  // Toggle channel enabled
  const toggleChannel = async (username, enabled) => {
    try {
      await fetch(`${API_BASE}/api/geo/channels/${username}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !enabled })
      });
      fetchChannels();
    } catch (err) {
      console.error('Toggle error:', err);
    }
  };
  
  // Fetch map points
  const fetchMapPoints = useCallback(async () => {
    setMapLoading(true);
    try {
      const params = new URLSearchParams({ days: days.toString(), limit: '500' });
      if (eventType !== 'all') params.append('type', eventType);
      
      const res = await fetch(`${API_BASE}/api/geo/map?${params}`);
      const data = await res.json();
      if (data.ok) setMapPoints(data.items || []);
    } catch (err) {
      console.error('Map error:', err);
    } finally {
      setMapLoading(false);
    }
  }, [days, eventType]);
  
  // Fetch top places
  const fetchTopPlaces = useCallback(async () => {
    setTopLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/geo/top?days=${days}&limit=30`);
      const data = await res.json();
      if (data.ok) setTopPlaces(data.items || []);
    } catch (err) {
      console.error('Top places error:', err);
    } finally {
      setTopLoading(false);
    }
  }, [days]);
  
  // Fetch summary
  const fetchSummary = useCallback(async () => {
    setSummaryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/geo/summary?days=${days}`);
      const data = await res.json();
      if (data.ok) setSummary(data);
    } catch (err) {
      console.error('Summary error:', err);
    } finally {
      setSummaryLoading(false);
    }
  }, [days]);
  
  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/geo/stats?days=${days}`);
      const data = await res.json();
      if (data.ok) setStats(data);
    } catch (err) {
      console.error('Stats error:', err);
    }
  }, [days]);
  
  // Rebuild events
  const rebuildEvents = async () => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/api/geo/admin/rebuild?days=${days}`, { method: 'POST' });
      fetchMapPoints();
      fetchTopPlaces();
      fetchSummary();
      fetchStats();
    } catch (err) {
      console.error('Rebuild error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load
  useEffect(() => {
    fetchChannels();
    fetchMapPoints();
    fetchTopPlaces();
    fetchSummary();
    fetchStats();
  }, [fetchChannels, fetchMapPoints, fetchTopPlaces, fetchSummary, fetchStats]);
  
  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => searchChannels(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery, searchChannels]);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - только логотип и контролы */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-4">
              <div className="p-2 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-xl">
                <Radio className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Radar</h1>
                <p className="text-sm text-gray-500">Geo Intelligence Module</p>
              </div>
            </div>
            
            {/* View Toggle */}
            <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setView('map')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  view === 'map' ? 'bg-teal-600 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
                data-testid="view-map-btn"
              >
                <Map className="w-4 h-4" /> Map
              </button>
              <button
                onClick={() => setView('list')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  view === 'list' ? 'bg-teal-600 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
                data-testid="view-list-btn"
              >
                <List className="w-4 h-4" /> List
              </button>
              <button
                onClick={() => setView('stats')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  view === 'stats' ? 'bg-teal-600 text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
                data-testid="view-stats-btn"
              >
                <BarChart3 className="w-4 h-4" /> Stats
              </button>
            </div>
            
            {/* Filters */}
            <div className="flex items-center gap-3">
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700"
                data-testid="days-filter"
              >
                <option value={7}>7 days</option>
                <option value={14}>14 days</option>
                <option value={30}>30 days</option>
              </select>
              
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700"
                data-testid="type-filter"
              >
                <option value="all">All Types</option>
                <option value="place">Places</option>
                <option value="food">Food</option>
                <option value="venue">Venues</option>
                <option value="traffic">Traffic</option>
                <option value="infrastructure">Infrastructure</option>
              </select>
              
              <button
                onClick={rebuildEvents}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-sm font-medium disabled:opacity-50"
                data-testid="rebuild-btn"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Rebuild
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-[1800px] mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Sidebar - Markers List */}
          <aside className="col-span-3 space-y-4">
            {/* Markers List - Compact */}
            <div className="bg-white rounded-xl border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-teal-500" />
                  Markers
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-base">🦠</span>
                  <span className="text-xs text-gray-400">/</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="#3b82f6" stroke="none">
                    <path d="M3 6h18v2H3V6zm2 3h14l-1.5 13h-11L5 9zm4-6h6v2H9V3z"/>
                    <rect x="8" y="11" width="2" height="8" rx="1"/>
                    <rect x="11" y="11" width="2" height="8" rx="1"/>
                    <rect x="14" y="11" width="2" height="8" rx="1"/>
                  </svg>
                  <span className="text-xs text-gray-500 ml-1">{mapPoints.length}</span>
                </div>
              </div>
              
              <div className="max-h-[500px] overflow-y-auto">
                {mapLoading ? (
                  <div className="p-8 flex justify-center">
                    <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
                  </div>
                ) : mapPoints.length === 0 ? (
                  <div className="p-6 text-center">
                    <div className="text-3xl mb-2">🦠</div>
                    <p className="text-sm text-gray-500">No markers yet</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {mapPoints.slice(0, 50).map((point, idx) => {
                      const isVirus = ['virus', 'place', 'food', 'venue'].includes(point.eventType);
                      const isSelected = selectedMarkerId === point.id;
                      
                      return (
                        <div
                          key={point.id || idx}
                          onClick={() => handleMarkerSelect(point)}
                          className={`px-3 py-2.5 cursor-pointer transition-colors ${
                            isSelected ? 'bg-teal-50 border-l-2 border-teal-500' : 'hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center gap-2.5">
                            {isVirus ? (
                              <span className="text-base flex-shrink-0">🦠</span>
                            ) : (
                              <svg className="flex-shrink-0" width="16" height="16" viewBox="0 0 24 24" fill="#3b82f6" stroke="none">
                                <path d="M3 6h18v2H3V6zm2 3h14l-1.5 13h-11L5 9zm4-6h6v2H9V3z"/>
                                <rect x="8" y="11" width="2" height="8" rx="1"/>
                                <rect x="11" y="11" width="2" height="8" rx="1"/>
                                <rect x="14" y="11" width="2" height="8" rx="1"/>
                              </svg>
                            )}
                            <div className="min-w-0 flex-1">
                              <p className="text-sm text-gray-900 truncate font-medium">
                                {point.title}
                              </p>
                              <p className="text-xs text-gray-400 truncate">
                                {point.addressText || `${point.lat?.toFixed(4)}, ${point.lng?.toFixed(4)}`}
                              </p>
                            </div>
                            {point.metrics?.views > 0 && (
                              <span className="text-xs text-gray-400 flex items-center gap-1">
                                <Eye className="w-3 h-3" />
                                {point.metrics.views > 1000 
                                  ? `${(point.metrics.views / 1000).toFixed(1)}k` 
                                  : point.metrics.views
                                }
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
              
              {mapPoints.length > 50 && (
                <div className="px-4 py-2 border-t border-gray-100 text-center">
                  <span className="text-xs text-gray-400">
                    Showing 50 of {mapPoints.length} markers
                  </span>
                </div>
              )}
            </div>
          </aside>
          
          {/* Main Content */}
          <div className="col-span-6">
            {view === 'map' && (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                    <Map className="w-4 h-4 text-teal-500" />
                    Geo Events Map
                  </h3>
                  <span className="text-xs text-gray-500">{mapPoints.length} points</span>
                </div>
                
                {mapLoading ? (
                  <div className="h-[500px] flex items-center justify-center">
                    <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
                  </div>
                ) : mapPoints.length === 0 ? (
                  <div className="h-[500px] flex flex-col items-center justify-center bg-gray-50">
                    <MapPin className="w-16 h-16 text-gray-300 mb-4" />
                    <p className="text-gray-500 font-medium">No geo events</p>
                    <p className="text-sm text-gray-400 mt-1">Add channels and rebuild to see events</p>
                  </div>
                ) : (
                  <div className="h-[500px]">
                    <GeoMap points={mapPoints} selectedMarkerId={selectedMarkerId} />
                  </div>
                )}
              </div>
            )}
            
            {view === 'list' && (
              <div className="bg-white rounded-xl border border-gray-200">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                    <List className="w-4 h-4 text-teal-500" />
                    All Events
                  </h3>
                  <span className="text-xs text-gray-500">{mapPoints.length} events</span>
                </div>
                
                <div className="max-h-[600px] overflow-y-auto divide-y divide-gray-100">
                  {mapPoints.length === 0 ? (
                    <div className="p-8 text-center">
                      <List className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">No events yet</p>
                    </div>
                  ) : (
                    mapPoints.map((event, i) => (
                      <div key={event.id || i} className="px-4 py-3 hover:bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">{event.title}</h4>
                            <p className="text-xs text-gray-500 mt-0.5">{event.addressText}</p>
                          </div>
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            event.eventType === 'food' ? 'bg-orange-100 text-orange-700' :
                            event.eventType === 'venue' ? 'bg-purple-100 text-purple-700' :
                            event.eventType === 'traffic' ? 'bg-red-100 text-red-700' :
                            'bg-teal-100 text-teal-700'
                          }`}>
                            {event.eventType}
                          </span>
                        </div>
                        
                        {event.evidenceText && (
                          <p className="text-xs text-gray-500 mt-2 line-clamp-2">{event.evidenceText}</p>
                        )}
                        
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {event.lat?.toFixed(4)}, {event.lng?.toFixed(4)}
                          </span>
                          {event.source?.username && (
                            <span className="text-teal-600">@{event.source.username}</span>
                          )}
                          {event.metrics?.views > 0 && (
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {event.metrics.views}
                            </span>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
            
            {view === 'stats' && (
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 mb-1">Total Events</p>
                    <p className="text-2xl font-bold text-gray-900">{stats?.totalEvents || 0}</p>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 mb-1">Channels</p>
                    <p className="text-2xl font-bold text-gray-900">{stats?.totalChannels || 0}</p>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 mb-1">Active</p>
                    <p className="text-2xl font-bold text-teal-600">{stats?.enabledChannels || 0}</p>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 mb-1">Top Places</p>
                    <p className="text-2xl font-bold text-gray-900">{topPlaces.length}</p>
                  </div>
                </div>
                
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Event Types Distribution</h3>
                  <div className="space-y-2">
                    {(stats?.eventTypes || []).map((et) => (
                      <div key={et.eventType} className="flex items-center gap-3">
                        <span className="text-xs text-gray-500 w-24">{et.eventType}</span>
                        <div className="flex-1 bg-gray-100 rounded-full h-2">
                          <div
                            className="bg-teal-500 h-2 rounded-full"
                            style={{ width: `${Math.min(100, (et.count / (stats?.totalEvents || 1)) * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 w-12 text-right">{et.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Daily Activity</h3>
                  <div className="flex items-end gap-2 h-32">
                    {(stats?.dailyActivity || []).reverse().map((day, i) => (
                      <div key={day.date} className="flex-1 flex flex-col items-center">
                        <div
                          className="w-full bg-teal-500/30 rounded-t"
                          style={{ height: `${Math.max(4, (day.count / Math.max(...(stats?.dailyActivity || []).map(d => d.count))) * 100)}%` }}
                        />
                        <span className="text-[10px] text-gray-500 mt-1">{day.date.slice(-5)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Right Sidebar */}
          <aside className="col-span-3 space-y-4">
            {/* AI Summary */}
            <div className="bg-white rounded-xl border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  AI Summary
                </h3>
                <button onClick={fetchSummary} className="p-1 hover:bg-gray-100 rounded">
                  <RefreshCw className={`w-3.5 h-3.5 text-gray-400 ${summaryLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>
              <div className="p-4">
                {summaryLoading ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 className="w-5 h-5 text-amber-500 animate-spin" />
                  </div>
                ) : summary?.summary ? (
                  <p className="text-sm text-gray-600 leading-relaxed">{summary.summary}</p>
                ) : (
                  <p className="text-sm text-gray-400 text-center py-2">No summary available</p>
                )}
              </div>
            </div>
            
            {/* Top Places */}
            <div className="bg-white rounded-xl border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-teal-500" />
                  Top Places
                </h3>
                <button onClick={fetchTopPlaces} className="p-1 hover:bg-gray-100 rounded">
                  <RefreshCw className={`w-3.5 h-3.5 text-gray-400 ${topLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>
              
              <div className="max-h-[350px] overflow-y-auto divide-y divide-gray-100">
                {topPlaces.length === 0 ? (
                  <div className="p-4 text-center">
                    <p className="text-sm text-gray-400">No places yet</p>
                  </div>
                ) : (
                  topPlaces.slice(0, 15).map((place, i) => (
                    <div key={place.title + i} className="px-4 py-2.5 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="text-xs text-gray-400 w-5">{i + 1}.</span>
                          <span className="text-sm text-gray-900 truncate">{place.title}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">{place.count}x</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                            place.eventType === 'food' ? 'bg-orange-100 text-orange-700' :
                            place.eventType === 'venue' ? 'bg-purple-100 text-purple-700' :
                            'bg-teal-100 text-teal-700'
                          }`}>
                            {place.eventType}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
