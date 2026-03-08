import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Suspense, lazy } from "react";

// Loading component
const PageLoader = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 border-4 border-gray-200 border-t-teal-500 rounded-full animate-spin" />
      <p className="text-sm text-gray-500 font-medium">Loading...</p>
    </div>
  </div>
);

// Radar Page - main and only page
const RadarPage = lazy(() => import("./pages/RadarPage"));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Radar is the only page - no sidebar, no topbar */}
          <Route path="/" element={<RadarPage />} />
          <Route path="/radar" element={<RadarPage />} />
          <Route path="/*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
