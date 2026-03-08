/**
 * GeoMap Component - Production Leaflet Map
 * Real map with markers, clusters, fullscreen
 */
import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, ZoomControl, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Maximize2, Minimize2, MapPin, Eye, ExternalLink } from 'lucide-react';

// Fix default marker icon issue with webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icons - small colored dots with emoji/svg centers
const createVirusIcon = () => {
  return L.divIcon({
    className: '',
    html: `<span style="font-size:14px;line-height:1;">🦠</span>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    popupAnchor: [0, -7],
  });
};

const createTrashIcon = () => {
  return L.divIcon({
    className: '',
    html: `<svg width="14" height="14" viewBox="0 0 24 24" fill="#3b82f6" stroke="none"><path d="M3 6h18v2H3V6zm2 3h14l-1.5 13h-11L5 9zm4-6h6v2H9V3z"/></svg>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    popupAnchor: [0, -7],
  });
};

const getEventIcon = (eventType) => {
  if (eventType === 'virus' || eventType === 'place' || eventType === 'food' || eventType === 'venue') {
    return createVirusIcon();
  }
  return createTrashIcon();
};

// Component to fit bounds to markers
function FitBounds({ points }) {
  const map = useMap();
  
  useEffect(() => {
    if (points.length > 0) {
      const validPoints = points.filter(p => p.lat && p.lng);
      if (validPoints.length > 0) {
        const bounds = L.latLngBounds(validPoints.map(p => [p.lat, p.lng]));
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
      }
    }
  }, [points, map]);
  
  return null;
}

// Component to fly to selected marker
function FlyToMarker({ points, selectedMarkerId }) {
  const map = useMap();
  
  useEffect(() => {
    if (selectedMarkerId && points.length > 0) {
      const point = points.find(p => p.id === selectedMarkerId);
      if (point && point.lat && point.lng) {
        map.flyTo([point.lat, point.lng], 16, { duration: 1 });
      }
    }
  }, [selectedMarkerId, points, map]);
  
  return null;
}

// Custom cluster icon
const createClusterCustomIcon = (cluster) => {
  const count = cluster.getChildCount();
  let dimension = 26;
  let fontSize = '11px';
  
  if (count >= 100) {
    dimension = 36;
    fontSize = '13px';
  } else if (count >= 10) {
    dimension = 30;
    fontSize = '12px';
  }
  
  return L.divIcon({
    html: `<div style="
      background: linear-gradient(135deg, #14b8a6, #06b6d4);
      color: white;
      width: ${dimension}px;
      height: ${dimension}px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: ${fontSize};
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
      border: 2px solid white;
    ">${count}</div>`,
    className: '',
    iconSize: L.point(dimension, dimension, true),
  });
};

export default function GeoMap({ points = [], onPointClick, selectedMarkerId, onMapReady }) {
  const [fullscreen, setFullscreen] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const mapRef = useRef(null);
  
  // Default center (Kyiv)
  const defaultCenter = [50.4501, 30.5234];
  const defaultZoom = 11;
  
  // Calculate center from points
  const getCenter = () => {
    if (points.length === 0) return defaultCenter;
    const validPoints = points.filter(p => p.lat && p.lng);
    if (validPoints.length === 0) return defaultCenter;
    
    const avgLat = validPoints.reduce((sum, p) => sum + p.lat, 0) / validPoints.length;
    const avgLng = validPoints.reduce((sum, p) => sum + p.lng, 0) / validPoints.length;
    return [avgLat, avgLng];
  };

  const handleMarkerClick = (point) => {
    setSelectedPoint(point);
    if (onPointClick) onPointClick(point);
  };

  return (
    <div className={`relative ${fullscreen ? 'fixed inset-0 z-50 bg-white' : 'h-full'}`}>
      {/* Fullscreen toggle */}
      <button
        onClick={() => setFullscreen(!fullscreen)}
        className="absolute top-3 right-3 z-[1000] bg-white shadow-md px-3 py-2 rounded-lg flex items-center gap-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
      >
        {fullscreen ? (
          <>
            <Minimize2 className="w-4 h-4" />
            Exit
          </>
        ) : (
          <>
            <Maximize2 className="w-4 h-4" />
            Fullscreen
          </>
        )}
      </button>
      
      {/* Points counter */}
      <div className="absolute top-3 left-3 z-[1000] bg-white shadow-md px-3 py-2 rounded-lg text-sm font-medium text-gray-700">
        <MapPin className="w-4 h-4 inline mr-1 text-teal-500" />
        {points.length} events
      </div>

      <MapContainer
        ref={mapRef}
        center={getCenter()}
        zoom={defaultZoom}
        zoomControl={false}
        style={{ height: fullscreen ? '100vh' : '100%', width: '100%', minHeight: '500px' }}
        className="rounded-b-xl"
      >
        <ZoomControl position="bottomright" />
        
        {/* OpenStreetMap tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Fit bounds to markers */}
        {points.length > 0 && <FitBounds points={points} />}
        
        {/* Fly to selected marker */}
        {selectedMarkerId && <FlyToMarker points={points} selectedMarkerId={selectedMarkerId} />}
        
        {/* Clustered markers */}
        <MarkerClusterGroup
          chunkedLoading
          iconCreateFunction={createClusterCustomIcon}
          maxClusterRadius={25}
          disableClusteringAtZoom={13}
          spiderfyOnMaxZoom={true}
          showCoverageOnHover={false}
        >
          {points.map((point, index) => {
            if (!point.lat || !point.lng) return null;
            
            const icon = getEventIcon(point.eventType);
            
            return (
              <Marker
                key={point.id || `point-${index}`}
                position={[point.lat, point.lng]}
                icon={icon}
                eventHandlers={{
                  click: () => handleMarkerClick(point)
                }}
              >
                <Popup className="custom-popup" maxWidth={300}>
                  <div className="p-1">
                    <h3 className="font-semibold text-gray-900 text-sm mb-1">
                      {point.title}
                    </h3>
                    
                    {point.addressText && point.addressText !== point.title && (
                      <p className="text-xs text-gray-500 mb-2">{point.addressText}</p>
                    )}
                    
                    <div className="flex items-center gap-3 text-xs text-gray-500 mb-2">
                      <span className={`px-2 py-0.5 rounded ${
                        point.eventType === 'food' ? 'bg-orange-100 text-orange-700' :
                        point.eventType === 'venue' ? 'bg-purple-100 text-purple-700' :
                        point.eventType === 'traffic' ? 'bg-red-100 text-red-700' :
                        'bg-teal-100 text-teal-700'
                      }`}>
                        {point.eventType}
                      </span>
                      
                      {point.metrics?.views > 0 && (
                        <span className="flex items-center gap-1">
                          <Eye className="w-3 h-3" />
                          {point.metrics.views}
                        </span>
                      )}
                    </div>
                    
                    {point.evidenceText && (
                      <p className="text-xs text-gray-600 line-clamp-3 mb-2">
                        {point.evidenceText}
                      </p>
                    )}
                    
                    {point.source?.username && (
                      <a
                        href={`https://t.me/${point.source.username}/${point.source.messageId || ''}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-teal-600 hover:underline flex items-center gap-1"
                      >
                        <ExternalLink className="w-3 h-3" />
                        @{point.source.username}
                      </a>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MarkerClusterGroup>
      </MapContainer>
    </div>
  );
}
