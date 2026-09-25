import { Link } from "react-router-dom";

function Home({ theme, setTheme }) {
  return (
    <div className={`home-page ${theme}`}>

      {/* =========================
          NAVBAR
      ========================= */}

      <nav className="navbar">

        <div className="logo">

          <div className="logo-icon">
            R
          </div>

          <span>
            ReclaimAI
          </span>

        </div>


        <div className="nav-links">

          <a href="#about">
            About
          </a>

          <a href="#features">
            Features
          </a>

          <a href="#workflow">
            How It Works
          </a>


          {/* THEME BUTTON */}

          <button
            className="home-theme-button"
            onClick={() =>
              setTheme(
                theme === "light"
                  ? "dark"
                  : "light"
              )
            }
          >

            {theme === "light"
              ? "🌙 Dark"
              : "☀ Light"}

          </button>


          <Link
            to="/login"
            className="nav-login"
          >
            Sign In
          </Link>


          <Link
            to="/login"
            className="nav-start"
          >
            Get Started
          </Link>

        </div>

      </nav>


      {/* =========================
          HERO SECTION
      ========================= */}

      <section className="hero">

        <div className="hero-content">


          <div className="hero-badge">
            AI-Powered Digital Recovery
          </div>


          <h1>

            Recover Lost Data.

            <span>
              Understand What Matters.
            </span>

          </h1>


          <p>
            ReclaimAI combines intelligent file recovery
            with AI-assisted analysis to identify,
            reconstruct, classify and prioritize
            recoverable digital information from damaged,
            deleted or partially corrupted storage data.
          </p>


          <div className="hero-buttons">

            <Link
              to="/login"
              className="primary-btn"
            >
              Start Recovery
            </Link>


            <a
              href="#workflow"
              className="secondary-btn"
            >
              See How It Works
            </a>

          </div>


          <div className="hero-stats">


            <div>

              <strong>
                Identify
              </strong>

              <span>
                Recoverable files
              </span>

            </div>


            <div>

              <strong>
                Analyze
              </strong>

              <span>
                File integrity
              </span>

            </div>


            <div>

              <strong>
                Connect
              </strong>

              <span>
                Related fragments
              </span>

            </div>


            <div>

              <strong>
                Prioritize
              </strong>

              <span>
                Important data
              </span>

            </div>


          </div>

        </div>


        {/* HERO VISUAL */}

        <div className="hero-visual">

          <div className="analysis-window">


            <div className="window-header">

              <span></span>
              <span></span>
              <span></span>

              <p>
                Recovery Analysis
              </p>

            </div>


            <div className="scan-area">


              <div className="scan-icon">
                ◈
              </div>


              <h3>
                Storage Analysis
              </h3>


              <p>
                Scanning recoverable digital
                information...
              </p>


              <div className="demo-progress">

                <div></div>

              </div>


              <div className="demo-results">


                <div>

                  <span>
                    Files Detected
                  </span>

                  <strong>
                    24
                  </strong>

                </div>


                <div>

                  <span>
                    Recoverable
                  </span>

                  <strong>
                    15
                  </strong>

                </div>


                <div>

                  <span>
                    Integrity
                  </span>

                  <strong>
                    87%
                  </strong>

                </div>


              </div>


            </div>

          </div>

        </div>

      </section>


      {/* =========================
          ABOUT
      ========================= */}

      <section
        className="about-section"
        id="about"
      >

        <div className="section-label">
          THE PROBLEM
        </div>


        <h2>
          Data recovery should do more than
          simply find files.
        </h2>


        <p className="section-description">

          Traditional recovery tools may recover
          deleted or damaged files, but users still
          need to understand which files are complete,
          which fragments are connected and what
          information can realistically be restored.

        </p>

      </section>


      {/* =========================
          FEATURES
      ========================= */}

      <section
        className="features-section"
        id="features"
      >

        <div className="section-label">
          WHAT RECLAIMAI DOES
        </div>


        <h2>
          Intelligent recovery from start to finish
        </h2>


        <div className="feature-grid">


          {/* FEATURE 1 */}

          <div className="feature-card">

            <div className="feature-icon">
              01
            </div>

            <h3>
              File Identification
            </h3>

            <p>
              Detect recoverable files and fragments
              using file signatures, metadata and
              structural analysis.
            </p>

          </div>


          {/* FEATURE 2 */}

          <div className="feature-card">

            <div className="feature-icon">
              02
            </div>

            <h3>
              Integrity Analysis
            </h3>

            <p>
              Analyze recovered information and
              estimate how complete or damaged each
              recovered artifact is.
            </p>

          </div>


          {/* FEATURE 3 */}

          <div className="feature-card">

            <div className="feature-icon">
              03
            </div>

            <h3>
              Fragment Relationships
            </h3>

            <p>
              AI-assisted similarity analysis helps
              identify fragments that may belong to
              the same original file.
            </p>

          </div>


          {/* FEATURE 4 */}

          <div className="feature-card">

            <div className="feature-icon">
              04
            </div>

            <h3>
              Smart Classification
            </h3>

            <p>
              Automatically organize recovered
              information into documents, images,
              text, videos and other categories.
            </p>

          </div>


          {/* FEATURE 5 */}

          <div className="feature-card">

            <div className="feature-icon">
              05
            </div>

            <h3>
              Recovery Priority
            </h3>

            <p>
              Prioritize highly recoverable information
              so important files can be reviewed first.
            </p>

          </div>


          {/* FEATURE 6 */}

          <div className="feature-card">

            <div className="feature-icon">
              06
            </div>

            <h3>
              AI Recovery Summary
            </h3>

            <p>
              Convert complex recovery information into
              simple and understandable analysis results.
            </p>

          </div>


        </div>

      </section>


      {/* =========================
          HOW IT WORKS
      ========================= */}

      <section
        className="workflow-section"
        id="workflow"
      >

        <div className="section-label">
          HOW IT WORKS
        </div>


        <h2>
          From damaged data to useful information
        </h2>


        <div className="workflow">


          {/* STEP 1 */}

          <div className="workflow-step">

            <div className="step-number">
              1
            </div>

            <h3>
              Upload
            </h3>

            <p>
              Upload damaged, deleted or corrupted
              storage data.
            </p>

          </div>


          <div className="workflow-arrow">
            →
          </div>


          {/* STEP 2 */}

          <div className="workflow-step">

            <div className="step-number">
              2
            </div>

            <h3>
              Recover
            </h3>

            <p>
              Detect recoverable files and digital
              fragments.
            </p>

          </div>


          <div className="workflow-arrow">
            →
          </div>


          {/* STEP 3 */}

          <div className="workflow-step">

            <div className="step-number">
              3
            </div>

            <h3>
              Analyze
            </h3>

            <p>
              Check file integrity, classification
              and fragment relationships.
            </p>

          </div>


          <div className="workflow-arrow">
            →
          </div>


          {/* STEP 4 */}

          <div className="workflow-step">

            <div className="step-number">
              4
            </div>

            <h3>
              Understand
            </h3>

            <p>
              View prioritized recovery results and
              AI-assisted insights.
            </p>

          </div>


        </div>

      </section>


      {/* =========================
          CTA
      ========================= */}

      <section className="cta-section">

        <h2>
          Ready to recover your data?
        </h2>

        <p>
          Start intelligent recovery with ReclaimAI.
        </p>

        <Link
          to="/login"
          className="cta-button"
        >
          Get Started
        </Link>

      </section>


      {/* =========================
          FOOTER
      ========================= */}

      <footer>

        <div className="logo">

          <div className="logo-icon">
            R
          </div>

          <span>
            ReclaimAI
          </span>

        </div>


        <p>
          AI-Assisted Intelligent Data Recovery
        </p>

      </footer>


    </div>
  );
}

export default Home;