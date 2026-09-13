# Assumptions and Simplifications

I made the following choices to keep the project small enough for a take-home
evaluation while still working with real transit operations data.

1. **I focused on the subway.** Bus, commuter rail, ferry, and paratransit
   operate differently enough that including them would have made the metrics
   harder to interpret. The Mattapan Line is also left out so that the live and
   historical route sets stay consistent.

2. **The historical view is intentionally short.** By default, the app loads
   the latest seven complete LAMP service days. That is useful for a working
   example, but it is not a seasonal baseline and should not be used to label a
   route as chronically reliable or unreliable.

3. **“Long gap” and “bunching” are working definitions.** I call a headway a
   long gap when it is more than 150% of the matched scheduled headway, and
   bunched when it is below 50%. These thresholds make the prototype easy to
   explain; they are not official MBTA performance measures.

4. **I only compare usable headway pairs.** Rows with missing, zero, or negative
   observed or scheduled headways are excluded from headway ratios. The same
   principle applies to travel-time comparisons when either side is missing.

5. **Predictions and completed service are kept separate.** The interval
   between two future predictions is only a prediction gap. It is not a
   realized headway, a guaranteed wait, or confirmation that either train will
   arrive at that time.

6. **Today is excluded from the historical download.** A same-day LAMP file may
   still be accumulating. The downloader uses the dates in LAMP's published
   index and selects only completed service dates.

7. **Live data is a snapshot.** Timestamps are handled as timezone-aware values
   and the fetch time is shown in the interface. Vehicle positions, predictions,
   and notices may change immediately after the page loads.

8. **The agent has a narrow tool set.** It can inspect recent network
   reliability, station headways, live line status, and metric definitions. It
   cannot run arbitrary SQL, perform trip planning, or produce a forecast.

9. **Failures remain visible.** If Parley is unavailable, the app returns a
   deterministic evidence summary. If an MBTA source fails and there is no
   cached historical file, the interface reports the problem instead of
   substituting invented data.

10. **This is a local research prototype.** I included caching, timeouts,
    validation, tests, and a reproducible data-preparation step. User accounts,
    production monitoring, persistent conversation storage, and deployment
    infrastructure are outside the scope of this submission.
