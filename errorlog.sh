#!/usr/bin/env bash
# log_errors.sh — run a Python script and log its errors to a file
#
# Features:
#   • Groups multi-line tracebacks into one log entry
#   • Timestamps every error block
#   • Still shows errors live in your terminal
#   • Daily log files, auto-created
#   • Exits with the same code your script did (so CI/cron see failures)
#
# Usage:
#   ./log_errors.sh myscript.py
#   ./log_errors.sh myscript.py --flag value
#   LOG_DIR=/var/log/myapp ./log_errors.sh myscript.py

set -uo pipefail

# config
LOG_DIR="${LOG_DIR:-./logs}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/errors_$(date +%Y-%m-%d).log"

# args
if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <script.py> [args...]" >&2
  exit 64
fi

SCRIPT="$1"
if [ ! -f "$SCRIPT" ]; then
  echo "Error: '$SCRIPT' not found." >&2
  exit 66
fi

# run
{
  echo ""
  echo "═"
  echo "  RUN START   $(date '+%Y-%m-%d %H:%M:%S')"
  echo "  COMMAND     $PYTHON_BIN $*"
  echo "  PWD         $(pwd)"
  echo "═"
} >> "$LOG_FILE"

# -u flag = unbuffered output, so tracebacks appear in real time
"$PYTHON_BIN" -u "$@" 2> >(
  awk -v logfile="$LOG_FILE" '
    BEGIN {
      in_traceback = 0
      buffer = ""
    }

    # Stamp helper
    function ts() {
      cmd = "date \"+%Y-%m-%d %H:%M:%S\""
      cmd | getline t
      close(cmd)
      return t
    }

    function flush_buffer() {
      if (buffer != "") {
        print "[" ts() "] " buffer >> logfile
        fflush(logfile)
        buffer = ""
      }
    }

    # Start of a Python traceback
    /^Traceback \(most recent call last\):/ {
      flush_buffer()
      in_traceback = 1
      buffer = $0
      print $0 > "/dev/stderr"
      next
    }

    # Inside a traceback: indented frames or the final ExceptionType: message
    in_traceback {
      buffer = buffer "\n" $0
      print $0 > "/dev/stderr"
      # The exception line is unindented and contains a colon — end of traceback
      if ($0 !~ /^[[:space:]]/ && $0 ~ /:/) {
        flush_buffer()
        in_traceback = 0
      }
      next
    }

    # Plain stderr lines (warnings, print-to-stderr, etc.)
    {
      print "[" ts() "] " $0 >> logfile
      fflush(logfile)
      print $0 > "/dev/stderr"
    }

    END { flush_buffer() }
  '
)

EXIT_CODE=${PIPESTATUS[0]}

{
  echo "  RUN END     $(date '+%Y-%m-%d %H:%M:%S')   exit=$EXIT_CODE"
  echo "═"
} >> "$LOG_FILE"

exit "$EXIT_CODE"
