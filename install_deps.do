* ============================================================
* install_deps.do
* Install dependencies for the stata-ai-report skill
* Run this once before using the skill on a new machine.
* Usage: do install_deps.do
* ============================================================

* --- 1. Check Stata version ---
local ver = c(version)
di _n "Detected Stata version: `ver'"

if `ver' < 17 {
    di as error "ERROR: Stata 17 or later is required."
    di as error "  Reason: the 'tohtml' command calls Stata's built-in 'markdown' command,"
    di as error "  which was introduced in Stata 17."
    di as error "  Your version: `ver'"
    exit 198
}

* --- 2. Install pathutil (SSC) ---
cap which pathutil
if _rc {
    di _n "Installing pathutil from SSC..."
    cap ssc install pathutil, replace
    if _rc {
        di as error "ERROR: Failed to install pathutil from SSC."
        di as error "  Please ensure you have an internet connection and SSC access."
        exit _rc
    }
    di "  pathutil installed successfully."
}
else {
    di "  pathutil already installed."
}

* --- 3. Install fs (SSC) ---
cap which fs
if _rc {
    di _n "Installing fs from SSC..."
    cap ssc install fs, replace
    if _rc {
        di as error "ERROR: Failed to install fs from SSC."
        di as error "  Please ensure you have an internet connection and SSC access."
        exit _rc
    }
    di "  fs installed successfully."
}
else {
    di "  fs already installed."
}

* --- 4. Install moremata (SSC) ---
* moremata provides mm_outsheet, which tohtml uses extensively.
* We test by trying to call a moremata Mata function.
cap mata: mm_outsheet("", J(0,1,""), "")
if _rc {
    di _n "Installing moremata from SSC (provides mm_outsheet)..."
    cap ssc install moremata, replace
    if _rc {
        di as error "ERROR: Failed to install moremata from SSC."
        di as error "  Please ensure you have an internet connection and SSC access."
        exit _rc
    }
    * Verify installation
    cap mata: mm_outsheet("", J(0,1,""), "")
    if _rc {
        di as error "ERROR: moremata installed but mm_outsheet is still not available."
        di as error "  Try restarting Stata and running this script again."
        exit _rc
    }
    di "  moremata installed successfully."
}
else {
    di "  moremata already installed."
}

* --- 5. Verify markdown command (Stata 17+) ---
cap which markdown
if _rc {
    di as error "ERROR: The 'markdown' command is not available."
    di as error "  This command is built into Stata 17+. If you have Stata 17+,"
    di as error "  please contact Stata technical support."
    exit 198
}
else {
    di "  markdown command verified."
}

* --- 6. Verify core skill commands ---
* These are bundled in the skill's ado/ directory and loaded via adopath ++
local cmdlist "ishere tohtml outreg2e sopen logoute"
foreach cmd of local cmdlist {
    cap which `cmd'
    if _rc {
        di as error "ERROR: `cmd' not found."
        di as error "  Make sure you have copied the ado files from the skill's ado/"
        di as error "  directory to your working directory and run 'adopath ++ \".\"'."
        exit _rc
    }
}
di "  Core skill commands verified: `cmdlist'."

* --- Summary ---
di _n _dup(60) "-"
di "All dependencies are ready. You can now use the stata-ai-report skill."
di _dup(60) "-"
