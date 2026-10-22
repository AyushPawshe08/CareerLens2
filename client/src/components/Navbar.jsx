import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="navbar-wrapper">
      <nav className="navbar">
        <Link to="/" className="navbar-brand">
          <img className="brand-icon" src="/Logo.png" alt="" />
          <span className="brand-text">CareerLens</span>
        </Link>

        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <NavLink
                to="/analyze"
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
              >
                Analyze
              </NavLink>
              <NavLink
                to="/history"
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
              >
                History
              </NavLink>
              <div className="nav-divider" aria-hidden="true" />
              {user?.email && (
                <div className="user-badge" title={user.email}>
                  <span className="user-avatar">
                    {user.email.charAt(0).toUpperCase()}
                  </span>
                  <span className="user-email-text">{user.email}</span>
                </div>
              )}
              <button
                type="button"
                className="btn-nav-logout"
                onClick={handleLogout}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
              >
                Log in
              </NavLink>
              <Link to="/register" className="btn-nav-signup">
                Sign up
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}