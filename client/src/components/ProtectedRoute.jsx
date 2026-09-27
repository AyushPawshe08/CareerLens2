import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  // While we're verifying a stored token against the backend (happens on
  // every page refresh), don't redirect yet — otherwise a logged-in user
  // refreshing the page gets briefly bounced to /login before /me resolves.
  if (loading) {
    return <div className="page-centered">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}