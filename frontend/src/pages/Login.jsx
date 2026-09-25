import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  signInWithPopup,
  signInWithEmailAndPassword,
} from "firebase/auth";

import {
  auth,
  googleProvider,
} from "../firebase";

function Login({ theme }) {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [googleLoading, setGoogleLoading] = useState(false);


    const handleLogin = async (event) => {
        event.preventDefault();

        if (!email || !password) {
            alert("Please enter email and password");
            return;
        }

        try {
            const result =
            await signInWithEmailAndPassword(
                auth,
                email,
                password
            );

            const user = result.user;

            localStorage.setItem(
            "reclaimLoggedIn",
            "true"
            );

            localStorage.setItem(
            "currentUser",
            JSON.stringify({
                email: user.email,
            })
            );

            navigate("/dashboard");

        } catch (error) {
            alert(
            "Login failed. Please check your email and password."
            );

            console.error(error);
        }
        };


    const handleGoogleLogin = async () => {
        // Prevent opening more than one popup
        if (googleLoading) return;

        setGoogleLoading(true);

        try {
            const result = await signInWithPopup(
            auth,
            googleProvider
            );

            const user = result.user;

            localStorage.setItem(
            "reclaimLoggedIn",
            "true"
            );

            localStorage.setItem(
            "currentUser",
            JSON.stringify({
                name: user.displayName,
                email: user.email,
                photo: user.photoURL,
            })
            );

            navigate("/dashboard");

        } catch (error) {
            console.error("Google login error:", error);

            if (error.code === "auth/cancelled-popup-request") {
            console.log("Previous Google popup was cancelled.");
            } else if (error.code === "auth/popup-closed-by-user") {
            alert("Google login window was closed.");
            } else {
            alert("Google login failed: " + error.message);
            }

        } finally {
            setGoogleLoading(false);
        }
        };

  return (

    <div className={`login-page ${theme}`}>

      {/* LEFT SIDE */}

      <div className="login-brand">

        <Link to="/" className="login-logo">

          <div className="logo-icon">
            R
          </div>

          ReclaimAI

        </Link>


        <div className="login-brand-content">

          <div className="hero-badge">
            Intelligent Data Recovery
          </div>

          <h1>
            Recover.<br />
            Analyze.<br />
            Understand.
            </h1>

          <p>
            AI-assisted recovery that helps transform
            damaged and fragmented digital data into
            understandable information.
          </p>


          <div className="login-benefits">

            <div>
              <span>✓</span>
              Intelligent file identification
            </div>

            <div>
              <span>✓</span>
              Integrity and recovery scoring
            </div>

            <div>
              <span>✓</span>
              AI-assisted fragment analysis
            </div>

            <div>
              <span>✓</span>
              Smart recovery prioritization
            </div>

          </div>

        </div>

      </div>


      {/* RIGHT SIDE */}

      <div className="login-container">

        <div className="login-card">

          <div className="login-heading">

            <h2>Welcome back</h2>

            <p>
              Sign in to continue to ReclaimAI
            </p>

          </div>


          {/* GOOGLE */}

          <button
            type="button"
            className="google-button"
            onClick={handleGoogleLogin}
            disabled={googleLoading}
            >
            <span className="google-icon">G</span>

            {googleLoading
                ? "Connecting to Google..."
                : "Continue with Google"}
            </button>


          {/* DIVIDER */}

          <div className="login-divider">

            <span></span>

            <p>OR</p>

            <span></span>

          </div>


          {/* EMAIL LOGIN */}

          <form onSubmit={handleLogin}>

            <label>Email address</label>

            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
            />


            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
            />


            <div className="login-options">

              <label className="remember">

                <input type="checkbox" />

                Remember me

              </label>

              <a href="#">
                Forgot password?
              </a>

            </div>


            <button
              type="submit"
              className="login-button"
            >
              Sign In
            </button>

          </form>


          <p className="signup-text">

            Don't have an account?

            <Link to="/signup">
                Create Account
            </Link>

            </p>

        </div>

      </div>

    </div>
  );
}

export default Login;