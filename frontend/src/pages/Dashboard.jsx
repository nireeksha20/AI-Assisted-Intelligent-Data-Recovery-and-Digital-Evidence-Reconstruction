import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  onAuthStateChanged,
  signOut,
} from "firebase/auth";

import { auth } from "../firebase";


function Dashboard({ theme, setTheme }) {
  const navigate = useNavigate();


  /* =====================================
     BASIC STATES
  ===================================== */

  const [activePage, setActivePage] =
    useState("overview");

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [showResults, setShowResults] =
    useState(false);

  const [authLoading, setAuthLoading] =
    useState(true);


  /* =====================================
     SETTINGS STATES
  ===================================== */

  const [saveHistory, setSaveHistory] =
    useState(
      localStorage.getItem("saveHistory") !== "false"
    );

  const [aiSummary, setAiSummary] =
    useState(
      localStorage.getItem("aiSummary") !== "false"
    );

  const [notifications, setNotifications] =
    useState(
      localStorage.getItem("notifications") === "true"
    );

  const [compactView, setCompactView] =
    useState(
      localStorage.getItem("compactView") === "true"
    );


  /* =====================================
     USER INFORMATION
  ===================================== */

  const storedCurrentUser = JSON.parse(
    localStorage.getItem("currentUser") || "{}"
  );

  const storedUser = JSON.parse(
    localStorage.getItem("reclaimUser") || "{}"
  );


  const [profileName, setProfileName] =
    useState(
      storedUser.name ||
      storedCurrentUser.name ||
      "ReclaimAI User"
    );

  const [profileEmail, setProfileEmail] =
    useState(
      storedCurrentUser.email ||
      storedUser.email ||
      ""
    );

  const [profilePhoto, setProfilePhoto] =
    useState(
      storedCurrentUser.photo || ""
    );

  const [editingProfile, setEditingProfile] =
    useState(false);


  /* =====================================
     RECOVERY HISTORY
  ===================================== */

  const [recoveryHistory, setRecoveryHistory] =
    useState(() => {

      const savedHistory =
        localStorage.getItem("recoveryHistory"); 

      return savedHistory
        ? JSON.parse(savedHistory)
        : [];

    });


  /* =====================================
     SAMPLE RECOVERY DATA
     Will be replaced by backend later
  ===================================== */

  const recoveredFiles = [
    {
      name: "project_report.pdf",
      type: "PDF",
      integrity: 92,
      status: "Highly Recoverable",
    },

    {
      name: "family_photo.jpg",
      type: "Image",
      integrity: 81,
      status: "Recoverable",
    },

    {
      name: "notes_fragment.txt",
      type: "Text",
      integrity: 64,
      status: "Partially Recoverable",
    },

    {
      name: "damaged_video.mp4",
      type: "Video",
      integrity: 31,
      status: "Severely Damaged",
    },
  ];


  /* =====================================
     FIREBASE LOGIN CHECK
  ===================================== */

  useEffect(() => {

    const unsubscribe =
      onAuthStateChanged(auth, (user) => {

        if (user) {

          const userData = {
            name:
              user.displayName ||
              "ReclaimAI User",

            email:
              user.email || "",

            photo:
              user.photoURL || "",
          };


          localStorage.setItem(
            "currentUser",
            JSON.stringify(userData)
          );


          setProfileName(
            user.displayName ||
            storedUser.name ||
            "ReclaimAI User"
          );

          setProfileEmail(
            user.email ||
            storedUser.email ||
            ""
          );

          setProfilePhoto(
            user.photoURL || ""
          );

          setAuthLoading(false);

        } else {

          setAuthLoading(false);

          navigate("/login");
        }

      });


    return () => unsubscribe();

  }, [navigate]);


  /* =====================================
     SAVE HISTORY
  ===================================== */

  useEffect(() => {

    localStorage.setItem(
      "recoveryHistory",
      JSON.stringify(recoveryHistory)
    );

  }, [recoveryHistory]);


  /* =====================================
     SAVE SETTINGS
  ===================================== */

  useEffect(() => {

    localStorage.setItem(
      "saveHistory",
      saveHistory
    );

    localStorage.setItem(
      "aiSummary",
      aiSummary
    );

    localStorage.setItem(
      "notifications",
      notifications
    );

    localStorage.setItem(
      "compactView",
      compactView
    );

  }, [
    saveHistory,
    aiSummary,
    notifications,
    compactView,
  ]);


  /* =====================================
     OVERVIEW CALCULATIONS
  ===================================== */

  const totalSessions =
    recoveryHistory.length;


  const totalFilesRecovered =
    recoveryHistory.reduce(
      (total, item) =>
        total +
        Number(item.recoverable || 0),

      0
    );


  const averageIntegrity =
    recoveryHistory.length > 0

      ? Math.round(

          recoveryHistory.reduce(
            (total, item) =>
              total +
              Number(item.integrity || 0),

            0
          ) / recoveryHistory.length

        )

      : 0;


  const totalFilesFound =
    recoveryHistory.reduce(
      (total, item) =>
        total +
        Number(item.filesFound || 0),

      0
    );


  /* =====================================
     FILE SELECTION
  ===================================== */

  const handleFileChange = (event) => {

    const file =
      event.target.files[0];

    setSelectedFile(file || null);

    setShowResults(false);
  };


  /* =====================================
     ANALYZE FILE
     Demo version until backend arrives
  ===================================== */

  const handleAnalyze = () => {

    if (!selectedFile) {

      alert(
        "Please select a file first"
      );

      return;
    }


    setLoading(true);

    setShowResults(false);


    setTimeout(() => {

      setLoading(false);

      setShowResults(true);


      const newHistoryItem = {

        id: Date.now(),

        fileName:
          selectedFile.name,

        date:
          new Date().toLocaleString(),

        filesFound: 24,

        recoverable: 15,

        integrity: 82,

        status: "Completed",

      };


      if (saveHistory) {

        setRecoveryHistory(
          (oldHistory) => [
            newHistoryItem,
            ...oldHistory,
          ]
        );

      }


      if (notifications) {

        alert(
          "Recovery analysis completed successfully."
        );

      }

    }, 2000);

  };


  /* =====================================
     SAVE PROFILE
  ===================================== */

  const handleSaveProfile = () => {

    if (
      !profileName.trim() ||
      !profileEmail.trim()
    ) {

      alert(
        "Name and email cannot be empty."
      );

      return;
    }


    const updatedUser = {

      name:
        profileName,

      email:
        profileEmail,

      photo:
        profilePhoto,

    };


    localStorage.setItem(
      "reclaimUser",
      JSON.stringify(updatedUser)
    );


    localStorage.setItem(
      "currentUser",
      JSON.stringify(updatedUser)
    );


    setEditingProfile(false);


    alert(
      "Profile updated successfully"
    );

  };


  /* =====================================
     LOGOUT
  ===================================== */

  const handleLogout = async () => {

    try {

      await signOut(auth);

      localStorage.removeItem(
        "currentUser"
      );

      localStorage.removeItem(
        "reclaimLoggedIn"
      );

      navigate("/");

    } catch (error) {

      console.error(
        "Logout error:",
        error
      );

    }

  };


  /* =====================================
     AUTHENTICATION LOADING
  ===================================== */

  if (authLoading) {

    return (

      <div className="auth-loading">

        <div className="spinner"></div>

        <p>
          Loading your workspace...
        </p>

      </div>

    );

  }


  /* =====================================
     MAIN DASHBOARD
  ===================================== */

  return (

    <div
      className={`dashboard-page ${theme}`}
    >


      {/* ==========================
          SIDEBAR
      ========================== */}

      <aside className="sidebar">


        <div className="sidebar-logo">

          <div className="logo-icon">
            R
          </div>

          <span>
            ReclaimAI
          </span>

        </div>


        <p className="menu-title">
          WORKSPACE
        </p>


        <button
          className={
            activePage === "overview"
              ? "sidebar-item active-menu"
              : "sidebar-item"
          }

          onClick={() =>
            setActivePage("overview")
          }
        >
          Overview
        </button>


        <button
          className={
            activePage === "recover"
              ? "sidebar-item active-menu"
              : "sidebar-item"
          }

          onClick={() =>
            setActivePage("recover")
          }
        >
          Recover Data
        </button>


        <button
          className={
            activePage === "history"
              ? "sidebar-item active-menu"
              : "sidebar-item"
          }

          onClick={() =>
            setActivePage("history")
          }
        >
          Recovery History
        </button>


        <button
          className={
            activePage === "profile"
              ? "sidebar-item active-menu"
              : "sidebar-item"
          }

          onClick={() =>
            setActivePage("profile")
          }
        >
          Profile
        </button>


        <button
          className={
            activePage === "settings"
              ? "sidebar-item active-menu"
              : "sidebar-item"
          }

          onClick={() =>
            setActivePage("settings")
          }
        >
          Settings
        </button>


        <div className="sidebar-bottom">


          <button
            className="theme-button"

            onClick={() =>
              setTheme(
                theme === "light"
                  ? "dark"
                  : "light"
              )
            }
          >

            {theme === "light"
              ? "🌙 Dark Mode"
              : "☀ Light Mode"}

          </button>


          <button
            className="logout-link"
            onClick={handleLogout}
          >
            Logout
          </button>


        </div>

      </aside>


      {/* ==========================
          MAIN AREA
      ========================== */}

      <div className="dashboard-main">


        {/* TOP BAR */}

        <header className="dashboard-topbar">

          <h2>

            {activePage === "overview" &&
              "Dashboard"}

            {activePage === "recover" &&
              "Data Recovery"}

            {activePage === "history" &&
              "Recovery History"}

            {activePage === "profile" &&
              "Profile"}

            {activePage === "settings" &&
              "Settings"}

          </h2>


          <div className="system-status">

            <span className="status-dot"></span>

            System Online

          </div>

        </header>


        <main className="dashboard-content">


          {/* ==================================
              OVERVIEW
          ================================== */}

          {activePage === "overview" && (

            <div>


              <div className="dashboard-heading">

                <p className="dashboard-label">
                  OVERVIEW
                </p>

                <h1>
                  Welcome to ReclaimAI
                </h1>

                <p>
                  Monitor recovery activity
                  and start a new intelligent
                  data analysis session.
                </p>

              </div>


              <div className="overview-cards">


                <div className="overview-card">

                  <span>
                    Recovery Sessions
                  </span>

                  <h2>
                    {totalSessions}
                  </h2>

                  <p>
                    Total analyses performed
                  </p>

                </div>


                <div className="overview-card">

                  <span>
                    Files Recovered
                  </span>

                  <h2>
                    {totalFilesRecovered}
                  </h2>

                  <p>
                    Recoverable files detected
                  </p>

                </div>


                <div className="overview-card">

                  <span>
                    Average Integrity
                  </span>

                  <h2>
                    {averageIntegrity}%
                  </h2>

                  <p>
                    Across recovery sessions
                  </p>

                </div>


                <div className="overview-card">

                  <span>
                    Files Detected
                  </span>

                  <h2>
                    {totalFilesFound}
                  </h2>

                  <p>
                    Total files identified
                  </p>

                </div>


              </div>


              <div className="overview-grid">


                <div className="overview-panel">

                  <h2>
                    Start New Recovery
                  </h2>

                  <p>
                    Upload damaged or corrupted
                    storage data and begin
                    intelligent recovery analysis.
                  </p>

                  <button
                    className="primary-dashboard-button"

                    onClick={() =>
                      setActivePage("recover")
                    }
                  >
                    Start Recovery
                  </button>

                </div>


                <div className="overview-panel">

                  <h2>
                    Recent Activity
                  </h2>


                  {recoveryHistory.length === 0 ? (

                    <p>
                      No recovery activity yet.
                    </p>

                  ) : (

                    recoveryHistory
                      .slice(0, 3)
                      .map((item) => (

                        <div
                          className="activity-item"
                          key={item.id}
                        >

                          <div>

                            <strong>
                              {item.fileName}
                            </strong>

                            <span>
                              {item.date}
                            </span>

                          </div>


                          <span>
                            {item.integrity}%
                          </span>

                        </div>

                      ))

                  )}

                </div>


              </div>

            </div>

          )}


          {/* ==================================
              RECOVER DATA
          ================================== */}

          {activePage === "recover" && (

            <>


              <div className="dashboard-heading">

                <p className="dashboard-label">
                  RECOVERY WORKSPACE
                </p>

                <h1>
                  Analyze Storage Data
                </h1>

                <p>
                  Upload damaged, corrupted
                  or partially recoverable
                  digital information for
                  intelligent analysis.
                </p>

              </div>


              <div className="dashboard-upload">

                <h2>
                  Upload Storage Data
                </h2>

                <p>
                  Select a damaged file
                  or storage sample for
                  recovery analysis.
                </p>


                <div className="file-select-area">


                  <input
                    id="recovery-file"
                    className="hidden-file-input"
                    type="file"
                    onChange={handleFileChange}
                  />


                  <label
                    htmlFor="recovery-file"
                    className="choose-file-button"
                  >
                    Choose File
                  </label>


                  <div className="chosen-file-info">

                    {selectedFile ? (

                      <>

                        <span>
                          Selected File
                        </span>

                        <strong>
                          {selectedFile.name}
                        </strong>

                      </>

                    ) : (

                      <span>
                        No file selected
                      </span>

                    )}

                  </div>


                </div>


                <button
                  className="primary-dashboard-button"

                  onClick={handleAnalyze}

                  disabled={loading}
                >

                  {loading
                    ? "Analyzing..."
                    : "Start Analysis"}

                </button>


              </div>


              {loading && (

                <div className="loading-box">

                  <div className="spinner"></div>

                  <h3>
                    Analyzing Storage Data
                  </h3>

                  <p>
                    Identifying files,
                    checking integrity
                    and analyzing fragments...
                  </p>

                </div>

              )}


              {showResults && (

                <div
                  className={
                    compactView
                      ? "results-section compact-results"
                      : "results-section"
                  }
                >


                  <h2>
                    Recovery Overview
                  </h2>


                  <div className="summary-cards">


                    <div className="summary-card">

                      <h3>
                        Files Found
                      </h3>

                      <p>24</p>

                    </div>


                    <div className="summary-card">

                      <h3>
                        Recoverable
                      </h3>

                      <p>15</p>

                    </div>


                    <div className="summary-card">

                      <h3>
                        Partial
                      </h3>

                      <p>6</p>

                    </div>


                    <div className="summary-card">

                      <h3>
                        Damaged
                      </h3>

                      <p>3</p>

                    </div>


                  </div>


                  <div className="table-card">

                    <h2>
                      Recovered Files
                    </h2>


                    <table>


                      <thead>

                        <tr>

                          <th>
                            File Name
                          </th>

                          <th>
                            Type
                          </th>

                          <th>
                            Integrity
                          </th>

                          <th>
                            Status
                          </th>

                        </tr>

                      </thead>


                      <tbody>


                        {recoveredFiles.map(
                          (file, index) => (

                            <tr key={index}>


                              <td>
                                {file.name}
                              </td>


                              <td>
                                {file.type}
                              </td>


                              <td>

                                <div className="integrity-row">

                                  <div className="integrity-bar">

                                    <div
                                      className="integrity-fill"

                                      style={{
                                        width:
                                          `${file.integrity}%`,
                                      }}
                                    ></div>

                                  </div>

                                  <span>
                                    {file.integrity}%
                                  </span>

                                </div>

                              </td>


                              <td>

                                <span
                                  className={
                                    file.integrity >= 80
                                      ? "status high-status"

                                      : file.integrity >= 50
                                      ? "status medium-status"

                                      : "status low-status"
                                  }
                                >

                                  {file.status}

                                </span>

                              </td>


                            </tr>

                          )
                        )}


                      </tbody>


                    </table>

                  </div>


                  {aiSummary && (

                    <div className="ai-card">

                      <h2>
                        AI Fragment Analysis
                      </h2>

                      <p>
                        Fragment_07 and
                        Fragment_12 appear
                        to contain related
                        information and may
                        belong to the same
                        original document.
                      </p>

                      <p>
                        Similarity Confidence:
                        <strong> 89%</strong>
                      </p>

                      <button
                        className="primary-dashboard-button"
                      >
                        Attempt Reconstruction
                      </button>

                    </div>

                  )}


                </div>

              )}

            </>

          )}


          {/* ==================================
              HISTORY
          ================================== */}

          {activePage === "history" && (

            <div>


              <div className="history-heading-row">


                <div className="dashboard-heading">

                  <p className="dashboard-label">
                    PREVIOUS ANALYSIS
                  </p>

                  <h1>
                    Recovery History
                  </h1>

                  <p>
                    View your previously
                    completed recovery sessions.
                  </p>

                </div>


                {recoveryHistory.length > 0 && (

                  <button
                    className="clear-history-button"

                    onClick={() => {

                      const confirmClear =
                        window.confirm(
                          "Are you sure you want to clear recovery history?"
                        );

                      if (confirmClear) {
                        setRecoveryHistory([]);
                      }

                    }}
                  >

                    Clear History

                  </button>

                )}


              </div>


              {recoveryHistory.length === 0 ? (

                <div className="empty-history">


                  <div className="empty-history-icon">
                    ↺
                  </div>


                  <h2>
                    No Recovery History
                  </h2>


                  <p>
                    Your completed recovery
                    sessions will appear here.
                  </p>


                  <button
                    className="primary-dashboard-button"

                    onClick={() =>
                      setActivePage("recover")
                    }
                  >
                    Start Recovery
                  </button>


                </div>

              ) : (

                <div className="table-card">


                  <table>


                    <thead>

                      <tr>

                        <th>
                          File Name
                        </th>

                        <th>
                          Date
                        </th>

                        <th>
                          Files Found
                        </th>

                        <th>
                          Recoverable
                        </th>

                        <th>
                          Integrity
                        </th>

                        <th>
                          Status
                        </th>

                        <th>
                          Action
                        </th>

                      </tr>

                    </thead>


                    <tbody>


                      {recoveryHistory.map(
                        (item) => (

                          <tr key={item.id}>


                            <td>
                              <strong>
                                {item.fileName}
                              </strong>
                            </td>


                            <td>
                              {item.date}
                            </td>


                            <td>
                              {item.filesFound}
                            </td>


                            <td>
                              {item.recoverable}
                            </td>


                            <td>

                              <div className="integrity-row">

                                <div className="integrity-bar">

                                  <div
                                    className="integrity-fill"

                                    style={{
                                      width:
                                        `${item.integrity}%`,
                                    }}
                                  ></div>

                                </div>

                                <span>
                                  {item.integrity}%
                                </span>

                              </div>

                            </td>


                            <td>

                              <span className="status high-status">
                                {item.status}
                              </span>

                            </td>


                            <td>

                              <button
                                className="delete-history-button"

                                onClick={() =>
                                  setRecoveryHistory(
                                    recoveryHistory.filter(
                                      (historyItem) =>
                                        historyItem.id !==
                                        item.id
                                    )
                                  )
                                }
                              >
                                Delete
                              </button>

                            </td>


                          </tr>

                        )
                      )}


                    </tbody>


                  </table>


                </div>

              )}


            </div>

          )}


          {/* ==================================
              PROFILE
          ================================== */}

          {activePage === "profile" && (

            <div>


              <div className="dashboard-heading">

                <p className="dashboard-label">
                  ACCOUNT
                </p>

                <h1>
                  Your Profile
                </h1>

                <p>
                  View and manage your
                  ReclaimAI account information.
                </p>

              </div>


              <div className="profile-card">


                <div className="profile-header">


                  {profilePhoto ? (

                    <img
                      src={profilePhoto}
                      alt="Profile"
                      className="profile-avatar"
                    />

                  ) : (

                    <div className="profile-avatar">

                      {profileName
                        ? profileName
                            .charAt(0)
                            .toUpperCase()
                        : "U"}

                    </div>

                  )}


                  <div>

                    <h2>
                      {profileName}
                    </h2>

                    <p>
                      {profileEmail}
                    </p>

                  </div>


                </div>


                <div className="profile-form">


                  <label>
                    Full Name
                  </label>

                  <input
                    type="text"

                    value={profileName}

                    disabled={!editingProfile}

                    onChange={(event) =>
                      setProfileName(
                        event.target.value
                      )
                    }
                  />


                  <label>
                    Email Address
                  </label>

                  <input
                    type="email"

                    value={profileEmail}

                    disabled={!editingProfile}

                    onChange={(event) =>
                      setProfileEmail(
                        event.target.value
                      )
                    }
                  />


                </div>


                {!editingProfile ? (

                  <button
                    className="primary-dashboard-button"

                    onClick={() =>
                      setEditingProfile(true)
                    }
                  >
                    Edit Profile
                  </button>

                ) : (

                  <div className="profile-buttons">


                    <button
                      className="primary-dashboard-button"

                      onClick={handleSaveProfile}
                    >
                      Save Changes
                    </button>


                    <button
                      className="cancel-button"

                      onClick={() =>
                        setEditingProfile(false)
                      }
                    >
                      Cancel
                    </button>


                  </div>

                )}


                <div className="profile-details">


                  <div>

                    <span>
                      Account Type
                    </span>

                    <strong>
                      Standard User
                    </strong>

                  </div>


                  <div>

                    <span>
                      Recovery Sessions
                    </span>

                    <strong>
                      {totalSessions}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Account Status
                    </span>

                    <strong>
                      Active
                    </strong>

                  </div>


                </div>


              </div>


            </div>

          )}


          {/* ==================================
              SETTINGS
          ================================== */}

          {activePage === "settings" && (

            <div>


              <div className="dashboard-heading">

                <p className="dashboard-label">
                  PREFERENCES
                </p>

                <h1>
                  Settings
                </h1>

                <p>
                  Customize appearance,
                  recovery and AI preferences.
                </p>

              </div>


              {/* APPEARANCE */}

              <div className="settings-card">


                <h3>
                  Appearance
                </h3>

                <p>
                  Select your preferred
                  application theme.
                </p>


                <div className="theme-options">


                  <button
                    className={
                      theme === "light"
                        ? "theme-option selected-theme"
                        : "theme-option"
                    }

                    onClick={() =>
                      setTheme("light")
                    }
                  >

                    <span className="theme-symbol">
                      ☀
                    </span>

                    <strong>
                      Light Mode
                    </strong>

                    <span>
                      Light background
                      with dark text
                    </span>

                  </button>


                  <button
                    className={
                      theme === "dark"
                        ? "theme-option selected-theme"
                        : "theme-option"
                    }

                    onClick={() =>
                      setTheme("dark")
                    }
                  >

                    <span className="theme-symbol">
                      🌙
                    </span>

                    <strong>
                      Dark Mode
                    </strong>

                    <span>
                      Dark background
                      with light text
                    </span>

                  </button>


                </div>


              </div>


              {/* RECOVERY SETTINGS */}

              <div className="settings-card">


                <h3>
                  Recovery Preferences
                </h3>


                <div className="setting-row">


                  <div>

                    <strong>
                      Save Recovery History
                    </strong>

                    <p>
                      Save completed
                      recovery sessions.
                    </p>

                  </div>


                  <label className="switch">

                    <input
                      type="checkbox"

                      checked={saveHistory}

                      onChange={() =>
                        setSaveHistory(
                          !saveHistory
                        )
                      }
                    />

                    <span className="slider"></span>

                  </label>


                </div>


                <div className="setting-row">


                  <div>

                    <strong>
                      Compact Results View
                    </strong>

                    <p>
                      Use a smaller
                      recovery results layout.
                    </p>

                  </div>


                  <label className="switch">

                    <input
                      type="checkbox"

                      checked={compactView}

                      onChange={() =>
                        setCompactView(
                          !compactView
                        )
                      }
                    />

                    <span className="slider"></span>

                  </label>


                </div>


              </div>


              {/* AI SETTINGS */}

              <div className="settings-card">


                <h3>
                  AI Preferences
                </h3>


                <div className="setting-row">


                  <div>

                    <strong>
                      AI Recovery Summary
                    </strong>

                    <p>
                      Show AI-assisted
                      recovery explanations.
                    </p>

                  </div>


                  <label className="switch">

                    <input
                      type="checkbox"

                      checked={aiSummary}

                      onChange={() =>
                        setAiSummary(
                          !aiSummary
                        )
                      }
                    />

                    <span className="slider"></span>

                  </label>


                </div>


                <div className="setting-row">


                  <div>

                    <strong>
                      Analysis Notifications
                    </strong>

                    <p>
                      Notify when analysis
                      has completed.
                    </p>

                  </div>


                  <label className="switch">

                    <input
                      type="checkbox"

                      checked={notifications}

                      onChange={() =>
                        setNotifications(
                          !notifications
                        )
                      }
                    />

                    <span className="slider"></span>

                  </label>


                </div>


              </div>


              {/* SYSTEM INFO */}

              <div className="settings-card">


                <h3>
                  System Information
                </h3>


                <div className="system-info-row">

                  <span>
                    Application
                  </span>

                  <strong>
                    ReclaimAI
                  </strong>

                </div>


                <div className="system-info-row">

                  <span>
                    Recovery Engine
                  </span>

                  <strong>
                    Online
                  </strong>

                </div>


                <div className="system-info-row">

                  <span>
                    AI Analysis
                  </span>

                  <strong>
                    Enabled
                  </strong>

                </div>


                <div className="system-info-row">

                  <span>
                    Version
                  </span>

                  <strong>
                    1.0
                  </strong>

                </div>


              </div>


            </div>

          )}


        </main>

      </div>

    </div>

  );
}


export default Dashboard;