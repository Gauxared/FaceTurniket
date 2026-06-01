# Diploma Demo Script

1. Start the web server.
2. Open the web UI.
3. Show that the demo user is already registered.
4. Run the allowed photo scenario.
5. Point to the recognition result, similarity, quality score, and decision.
6. Show the mock turnstile command and the event log entry.
7. Run the denied or unknown photo scenario.
8. Explain that the system keeps the turnstile closed when confidence is not enough.
9. Run the video scenario if it is prepared.
10. Explain that the system selects the best frame before recognition.
11. Close with the limitation statement: this is an MVP with a mock turnstile and controlled capture.

Fallback plan:

- If a fresh live upload is unreliable, use the prepared local demo files.
- If the room lighting is bad, use the pre-enrolled allowed photo.
- If video processing is too slow, skip the video step and show the report instead.
- If the optional real provider is unavailable, switch to the mock provider and explain that the demo still proves the system flow.

