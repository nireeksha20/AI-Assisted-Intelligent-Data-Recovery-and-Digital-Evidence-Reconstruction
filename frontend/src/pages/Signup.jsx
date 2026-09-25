import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  createUserWithEmailAndPassword,
  updateProfile,
} from "firebase/auth";

import { auth } from "../firebase";
function Signup({ theme }) {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSignup = async (event) => {
    event.preventDefault();

    if (
      !name ||
      !email ||
      !password ||
      !confirmPassword
    ) {
      alert("Please fill all fields");
      return;
    }

    if (password.length < 6) {
      alert(
        "Password must contain at least 6 characters"
      );
      return;
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      const result =
        await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );

      await updateProfile(
        result.user,
        {
          displayName: name,
        }
      );

      alert(
        "Account created successfully"
      );

      navigate("/login");

    } catch (error) {
      console.error(error);

      alert(
        "Account creation failed: " +
        error.message
      );
    }
  };

  return (
    <div className={`login-page ${theme}`}>

      <div className="login-brand">

        <Link to="/" className="login-logo">
          <div className="logo-icon">R</div>
          ReclaimAI
        </Link>

        <div className="login-brand-content">

          <div className="hero-badge">
            Intelligent Data Recovery
          </div>

          <h1>
            Start your
            recovery journey.
          </h1>

          <p>
            Create your ReclaimAI account to analyze,
            recover and manage digital recovery sessions.
          </p>

          <div className="login-benefits">

            <div>
              <span>✓</span>
              Intelligent recovery analysis
            </div>

            <div>
              <span>✓</span>
              Recovery history
            </div>

            <div>
              <span>✓</span>
              AI-assisted fragment analysis
            </div>

            <div>
              <span>✓</span>
              Light and dark themes
            </div>

          </div>

        </div>

      </div>

      <div className="login-container">

        <div className="login-card">

          <div className="login-heading">
            <h2>Create account</h2>
            <p>Get started with ReclaimAI</p>
          </div>

          <button
            className="google-button"
            onClick={() =>
              alert("Google authentication will be connected later")
            }
          >
            <span className="google-icon">G</span>
            Continue with Google
          </button>

          <div className="login-divider">
            <span></span>
            <p>OR</p>
            <span></span>
          </div>

          <form onSubmit={handleSignup}>

            <label>Full Name</label>

            <input
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
            />

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
              placeholder="Minimum 6 characters"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
            />

            <label>Confirm Password</label>

            <input
              type="password"
              placeholder="Enter password again"
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
            />

            <button
              type="submit"
              className="login-button"
            >
              Create Account
            </button>

          </form>

          <p className="signup-text">

            Already have an account?

            <Link to="/login">
              Sign In
            </Link>

          </p>

        </div>

      </div>

    </div>
  );
}

export default Signup;