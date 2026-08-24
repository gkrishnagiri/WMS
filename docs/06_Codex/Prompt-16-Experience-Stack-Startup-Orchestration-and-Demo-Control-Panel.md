# Prompt 16 – Experience Stack Startup Orchestration and Demo Control Panel

Prompt 16 adds PID-owned startup, status, validation, and shutdown scripts for
the local EOS infrastructure, backend/BFF processes, and frontend experiences.
It also adds a read-only demo control panel at `/demo-control` in the full UI.

The implementation preserves all existing ports and uses `/tmp/eos-demo` for
PID records and logs. Shutdown validates PID ownership using process start time
and expected command markers; it does not use broad `pkill`, `killall`, or
process-name termination. Existing healthy unmanaged processes are reused and
left untouched.

The demo control API provides summary, component, URL, and readiness endpoints.
The UI displays topology, links, readiness, and terminal commands only; it
never executes shell commands or starts/stops local processes.

Prompt 16 does not change Docker Compose, database schema, authentication,
ServiceNow integration, external LLM behavior, or autonomous remediation.
