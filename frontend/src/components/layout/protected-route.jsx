import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/auth-context";

export function ProtectedRoute({ children, allowedRoles = [] }) {
  const { isAuthenticated, role } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }
  if (allowedRoles.length > 0 && !role) {
    return <Navigate to="/auth" replace />;
  }
  if (allowedRoles.length > 0 && role && !allowedRoles.includes(role)) {
    return <Navigate to={`/${role}`} replace />;
  }
  return children;
}
