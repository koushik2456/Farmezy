import { Outlet } from "react-router";
import { Navigation } from "../components/Navigation";
import { useState } from "react";
import Login from "./Login";

export default function Root() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation onLogout={handleLogout} />
      <main>
        <Outlet />
      </main>
    </div>
  );
}