# Agent Evaluation — Parley GPT-5.5

- Run time: `2026-09-15T03:25:50.405701+00:00`
- Model: `gpt-5.5`

## Summary

| Cases | Tool selection | Usable results | Valid citations | Fallback |
|---:|---:|---:|---:|---:|
| 20 | 20/20 | 20/20 | 20/20 | 0 |

## Case overview

| ID | Category | Expected tool | Selected tool | Result | Citation | Pass |
|---|---|---|---|---:|---:|---:|
| hist-network-ranking | historical network | network_reliability | network_reliability | Yes | Yes | Yes |
| hist-red | historical line | network_reliability | network_reliability | Yes | Yes | Yes |
| hist-green | historical line | network_reliability | network_reliability | Yes | Yes | Yes |
| hist-blue | historical line | network_reliability | network_reliability | Yes | Yes | Yes |
| live-orange | live line | live_line_status | live_line_status | Yes | Yes | Yes |
| live-blue | live line | live_line_status | live_line_status | Yes | Yes | Yes |
| live-network | live network | live_line_status | live_line_status | Yes | Yes | Yes |
| station-harvard | historical station | station_headways | station_headways | Yes | Yes | Yes |
| station-kendall | historical station | station_headways | station_headways | Yes | Yes | Yes |
| station-state | historical station | station_headways | station_headways | Yes | Yes | Yes |
| define-gap | methodology | metric_definition | metric_definition | Yes | Yes | Yes |
| define-prediction | methodology | metric_definition | metric_definition | Yes | Yes | Yes |
| compare-orange | multi-tool | live_line_status<br>network_reliability | live_line_status<br>network_reliability | Yes | Yes | Yes |
| live-red-notices | live line | live_line_status | live_line_status | Yes | Yes | Yes |
| define-two-metrics | methodology | metric_definition | metric_definition | Yes | Yes | Yes |
| station-harvard-square | station alias | station_headways | station_headways | Yes | Yes | Yes |
| station-kendall-square | station alias | station_headways | station_headways | Yes | Yes | Yes |
| station-mit | station alias | station_headways | station_headways | Yes | Yes | Yes |
| station-state-street | station alias | station_headways | station_headways | Yes | Yes | Yes |
| station-park-street | dynamic station index | station_headways | station_headways | Yes | Yes | Yes |

## Case details

<details>
<summary><strong>01. Which subway route had the highest long-gap rate in the recent data?</strong></summary>

**Category:** historical network

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>network_reliability({})</code> | <code>network_reliability({})</code> | Yes | Yes | Yes | No |

**Final answer**

Green-D had the highest long-gap rate in the recent MBTA subway reliability data, at 17.6% [E1].

Operationally, this means Green-D had the largest share of measured train-spacing observations classified as long gaps among the subway routes in the evidence. The next highest were Green-E at 17.0% and Green-B at 16.8% [E1], so the highest long-gap issue in this dataset was concentrated on the Green Line branches, especially Green-D.

Limitations: this is route-level reliability evidence only; it does not provide the exact long-gap threshold, time-of-day or direction breakdowns, or passenger arrival data. Therefore, the long-gap rate should be interpreted as irregular train spacing, not as an individual rider’s wait time.

</details>

<details>
<summary><strong>02. How has the Red Line been running recently?</strong></summary>

**Category:** historical line

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>network_reliability({&quot;line&quot;: &quot;Red&quot;})</code> | <code>network_reliability({&quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

The Red Line has recently been running near its scheduled train spacing at the median, but with meaningful unevenness during worse periods. The median headway ratio was 0.985, meaning typical train spacing was slightly shorter than scheduled [E1]. However, the 90th-percentile headway ratio was 1.478, meaning the wider-spacing cases were about 48% longer than scheduled [E1].

Operationally, that suggests service often looks reasonably regular, but riders may still encounter noticeable gaps: the gap rate was 0.094, while the bunching rate was 0.053 [E1]. Median travel-time excess was -50 seconds, indicating trips were slightly faster than the reference/scheduled travel time at the median [E1].

Limitations: this is line-level recent historical performance from 46,555 observations [E1]. It does not show station-by-station, direction, or time-of-day conditions, and train spacing is not the same as an individual rider’s wait without passenger arrival evidence.

</details>

<details>
<summary><strong>03. Which Green Line branch had the most uneven train spacing?</strong></summary>

**Category:** historical line

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>network_reliability({&quot;line&quot;: &quot;Green&quot;})</code> | <code>network_reliability({&quot;line&quot;: &quot;Green&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Finding: **Green-E had the most uneven train spacing by the 90th-percentile headway-ratio metric**, with a p90 headway ratio of **1.748**, narrowly above Green-D at **1.742**, Green-B at **1.698**, and Green-C at **1.652** [E1].

Operationally, that means Green-E’s wider train-spacing episodes were slightly more extreme relative to schedule than the other branches. However, by **gap rate**, Green-D was worst at **0.176**, compared with Green-E at **0.170** [E1]. Green-D and Green-E were tied on **bunching rate** at **0.108** [E1].

Limitations: this is route-level performance evidence, not rider wait-time evidence. It describes train spacing patterns, not what any individual passenger waited. The evidence also does not provide station-, direction-, or time-of-day detail.

</details>

<details>
<summary><strong>04. Summarize recent headway reliability on the Blue Line.</strong></summary>

**Category:** historical line

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>network_reliability({&quot;line&quot;: &quot;Blue&quot;})</code> | <code>network_reliability({&quot;line&quot;: &quot;Blue&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Finding: Recent Blue Line headway reliability was generally strong, with typical train spacing very close to scheduled: the median headway ratio was 1.003 across 27,174 observations [E1].

Operationally, this means the “typical” Blue Line train spacing was nearly on schedule, but reliability degraded in the upper tail: the p90 headway ratio was 1.367, indicating some substantially longer-than-scheduled spacing [E1]. Gaps occurred at a rate of 0.069, while bunching was less common at 0.019 [E1]. Median travel time excess was -34.0 seconds, suggesting trips were not generally running longer than scheduled at the median [E1].

Limitations: this is a line-level aggregate, not broken out by station, direction, time of day, or date. It describes train spacing, not individual rider waits, because no passenger arrival or wait-time evidence is provided.

</details>

<details>
<summary><strong>05. What is happening on the Orange Line right now?</strong></summary>

**Category:** live line

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>live_line_status({&quot;line&quot;: &quot;Orange&quot;})</code> | <code>live_line_status({&quot;line&quot;: &quot;Orange&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

**Finding:** As of **2026-09-15 03:22 UTC**, the Orange Line has **10 tracked vehicles** and **3 active alerts** [E1]. The most operationally significant alert is a **shuttle/service diversion**: riders are told to use Commuter Rail or shuttle buses between **Back Bay and Forest Hills** during Orange Line station improvements and signal upgrades [E1].

**Operational meaning:**
- Service is not simply “normal subway service” end-to-end: the active shuttle alert affects the Back Bay–Forest Hills segment [E1].
- Jackson Square has station-access issues: platform renovation conditions may make boarding/exiting harder for some riders, and a stairway between the lobby and south end of the platform is closed [E1].
- Upcoming prediction spacing is uneven in places. The largest future prediction gap shown is **11.9 minutes** at Back Bay, direction **0**; other large gaps shown are **9.8 minutes** at Wellington, Malden Center, and Oak Grove in direction **1**, plus **6.0 minutes** at Malden Center in direction **0** [E1].

**Limitations:** These are live API observations from the provided snapshot only. The prediction gaps are minutes between consecutive **future predictions** at a stop and direction; they are **not realized headways** and do **not** directly state any individual rider’s wait time [E1].

</details>

<details>
<summary><strong>06. Show me the current Blue Line vehicles, notices, and prediction gaps.</strong></summary>

**Category:** live line

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>live_line_status({&quot;line&quot;: &quot;Blue&quot;})</code> | <code>live_line_status({&quot;line&quot;: &quot;Blue&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

**Finding:** As of **2026-09-15 03:22 UTC**, the Blue Line has **6 vehicles** reported, **1 active alert**, and its largest listed prediction gaps are **10.0 minutes** at several stop/direction pairs [E1].

**Current vehicles**
- Blue Line vehicles reported: **6** [E1]

**Notices / alerts**
- Active alerts: **1** [E1]
- Effect: **Delay** [E1]
- Notice: Blue Line trains will operate on the outbound/eastbound track between Wonderland and Revere Beach during the weekend of **September 26–27** for switch work [E1].

**Largest prediction gaps**
These are gaps between consecutive future predictions at the same stop and direction:

| Stop | Direction ID | Prediction gap |
|---|---:|---:|
| Bowdoin | 1 | 10.0 min [E1] |
| Wonderland | 0 | 10.0 min [E1] |
| Government Center | 1 | 10.0 min [E1] |
| Revere Beach | 0 | 10.0 min [E1] |
| State | 1 | 10.0 min [E1] |

**Operational meaning:** The vehicle count indicates currently reported Blue Line train activity, the alert indicates planned/special operating conditions, and the prediction gaps show where future train predictions are spaced farther apart in the feed.

**Limitations:** Prediction gaps are **not realized headways** and should not be interpreted as an individual rider’s wait time. They only describe spacing between future predictions at a stop and direction [E1].

</details>

<details>
<summary><strong>07. Are there any subway service notices right now?</strong></summary>

**Category:** live network

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>live_line_status({})</code> | <code>live_line_status({})</code> | Yes | Yes | Yes | No |

**Final answer**

Yes. The live MBTA feed shows active subway service notices on Red, Orange, Green, and Blue; the feed summary reports 9 active alerts, while the evidence excerpt lists 8 alert records [E1].

Operationally, riders should expect these impacts:

- **Red Line:** Ashmont Branch shuttle buses are planned to replace train service between JFK/UMass and Ashmont during the weekend of September 19–20 [E1].
- **Orange Line:** Jackson Square has platform/accessibility construction impacts, including unlevel platform sections and a stairway closure until winter 2026 [E1]. Separately, Orange Line work through September 14 involves Commuter Rail or shuttle buses between Back Bay and Forest Hills [E1].
- **Green Line:** C Branch trains are not stopping inbound at Dean Road from September 14 to October 9, and are not stopping at Brandon Hall through October 4 [E1]. A broader Green Line suspension is planned between North Station and Babcock St / Kenmore / Heath St during the weekend of September 19–20, with bus and Orange Line alternatives noted [E1].
- **Blue Line:** Trains are planned to operate on the outbound/eastbound track between Wonderland and Revere Beach during the weekend of September 26–27, which indicates a service-pattern change and possible delays [E1].

Limitations: this is a snapshot from the MBTA live status feed as of 2026-09-15 03:22 UTC [E1]. It reflects published alerts/notices, not confirmation of actual passenger waits or realized train spacing. The prediction-gap data in the evidence is not a service notice and is not a realized headway [E1].

</details>

<details>
<summary><strong>08. How were realized headways at Harvard on the Red Line?</strong></summary>

**Category:** historical station

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;station&quot;: &quot;Harvard&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;Harvard&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Realized headways at Harvard on the Red Line were moderate but uneven: the median train spacing was 10.65 minutes, with the 90th percentile at 16.15 minutes [E1].

Operationally, this means a typical train-to-train interval at Harvard was about 10.65 minutes, while longer spacing reached 16.15 minutes at the high end of observed service [E1]. Gaps occurred in 9.5% of observed headways, and bunching occurred in 5.4% [E1].

Limitations: this describes realized train spacing at Harvard, based on 2,918 observations [E1]. It does not measure individual passenger wait times, passenger arrivals, crowding, or causes of gaps and bunching.

</details>

<details>
<summary><strong>09. Summarize recent train spacing at Kendall/MIT on the Red Line.</strong></summary>

**Category:** historical station

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;station&quot;: &quot;Kendall/MIT&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;Kendall/MIT&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Recent Red Line train spacing at Kendall/MIT was typically about 10.55 minutes, with the 90th-percentile spacing at 16.18 minutes [E1].

Operationally, that means trains generally arrived a little over 10 minutes apart, but wider gaps were not rare: 9.6% of observed spacings were classified as gaps, while 4.9% were classified as bunching [E1]. The dataset includes 2,917 observed realized headways at Kendall/MIT [E1].

Limitations: these are station-level realized train spacings, not individual rider wait times. They do not show passenger arrival patterns, crowding, direction-specific conditions, or causes of gaps and bunching.

</details>

<details>
<summary><strong>10. Were there many long gaps at State on the Orange Line?</strong></summary>

**Category:** historical station

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;station&quot;: &quot;State&quot;, &quot;line&quot;: &quot;Orange&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;State&quot;, &quot;line&quot;: &quot;Orange&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

State on the Orange Line had recurring long gaps, but they were not the norm: the realized station-headway gap rate was 0.062, with 2,597 observations [E1]. Typical train spacing was much shorter, with a median realized headway of 6.18 minutes and a 90th-percentile headway of 9.0 minutes [E1].

Operationally, this means most observed train spacing at State was around the mid-single-digit minutes, but a noticeable minority of observations showed longer-than-desired spacing. This describes realized train spacing at the station, not individual rider wait times.

Limitations: the evidence is aggregated for State on the Orange Line and does not break gaps out by direction, time of day, date range, or cause [E1].

</details>

<details>
<summary><strong>11. How does T-Analyst decide that a gap is unusually long?</strong></summary>

**Category:** methodology

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>metric_definition({})</code> | <code>metric_definition({&quot;metric&quot;: &quot;unusually long gap&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

T-Analyst marks unusually long gaps using the **gap rate**: the share of observed train spacings/headways that are **greater than 1.5× the scheduled headway** [E1].

Operationally, this means T-Analyst compares actual train spacing to the schedule; if trains are spaced much farther apart than planned, that spacing is counted as an unusually long gap. The resulting metric is a share of observed headways exceeding that threshold [E1].

Limitations: the evidence defines the threshold but does not specify aggregation details such as route, station, direction, or time period. It also describes train spacing, not an individual rider’s actual wait.

</details>

<details>
<summary><strong>12. What is the difference between a prediction gap and a realized headway?</strong></summary>

**Category:** methodology

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>metric_definition({})</code> | <code>metric_definition({})</code> | Yes | Yes | Yes | No |

**Final answer**

A **prediction gap** is the time between consecutive **future predictions** for the same stop and direction; it is **not** a realized headway [E1]. A **realized headway** refers to observed train spacing between departures, as reflected in metrics based on observed departure headways [E1].

Operationally, a prediction gap describes spacing in the **prediction feed**, while a realized headway describes spacing in **actual train departures**. So a large prediction gap may indicate a lapse or gap in predicted arrivals, but it should not be treated as proof that trains actually departed that far apart.

Limitation: the evidence defines prediction gap explicitly and describes observed departure headways through related metrics, but it does not provide passenger arrival or wait-time evidence, so this should not be interpreted as an individual rider’s wait [E1].

</details>

<details>
<summary><strong>13. Compare current Orange Line conditions with its recent reliability.</strong></summary>

**Category:** multi-tool

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>live_line_status({&quot;line&quot;: &quot;Orange&quot;}); network_reliability({&quot;line&quot;: &quot;Orange&quot;})</code> | <code>live_line_status({&quot;line&quot;: &quot;Orange&quot;}); network_reliability({&quot;line&quot;: &quot;Orange&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

**Finding:** Current Orange Line conditions look more disrupted than the recent reliability summary would suggest: the live snapshot shows service-impacting alerts, including a shuttle between Back Bay and Forest Hills, while recent aggregate reliability shows typical train spacing was close to scheduled.

- **Current/live conditions:** The Orange Line has **10 vehicles** active and **3 active alerts** [E1]. The alerts include Jackson Square station issues and a shuttle notice between Back Bay and Forest Hills [E1]. The largest listed future prediction gap is **11.9 minutes** at Back Bay, with additional large prediction gaps of **9.8 minutes** at Wellington, Malden Center, and Oak Grove [E1]. These are **prediction gaps**, not realized headways.

- **Recent reliability:** In the recent reliability dataset, the Orange Line has **38,602 observations** [E2]. Its median headway ratio is **0.989**, meaning typical train spacing was very close to scheduled [E2]. The **p90 headway ratio is 1.394**, so the worse end of service had substantially longer spacing than scheduled [E2]. The gap rate is **0.068** and bunching rate is **0.048** [E2]. Median travel time excess is **-45.0 seconds**, indicating trips were slightly faster than the scheduled/reference travel time at the median [E2].

**Operational meaning:** Recent Orange Line reliability appears acceptable at the median, but live conditions currently include a significant service disruption and station-access issues, so riders may experience less reliable service than the aggregate recent metrics imply.

**Limitations:** The live prediction gaps are future prediction spacing at specific stops and directions, not realized headways or individual rider waits [E1]. The reliability data is aggregate recent performance and may not reflect the current disruption [E2].

</details>

<details>
<summary><strong>14. How is the Red Line running right now? Are there any service notices?</strong></summary>

**Category:** live line

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>live_line_status({&quot;line&quot;: &quot;Red&quot;})</code> | <code>live_line_status({&quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Red Line is operating with **15 vehicles reported**, and the feed shows **1 active alert** as of **2026-09-15 03:22 UTC** [E1].

Operationally, the main issue in the live predictions is a **largest prediction gap of 25 minutes** at North Quincy, Wollaston, Quincy Center, Quincy Adams, and Braintree [E1]. That means the feed is showing wider upcoming train spacing at those stops; it is **not** a realized headway or an individual rider’s wait.

Service notice: MBTA lists an alert for the Ashmont Branch: critical bridge work the weekend of **September 19–20**, with accessible shuttle buses replacing Red Line service between JFK/UMass and Ashmont [E1].

Limitations: this is based only on live MBTA API status and prediction gaps. The gap values are between consecutive future predictions at a stop and direction, not observed train spacing after the fact, and no passenger wait-time evidence is provided [E1].

</details>

<details>
<summary><strong>15. How are long gaps and bunching calculated?</strong></summary>

**Category:** methodology

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>metric_definition({})</code> | <code>metric_definition({})</code> | Yes | Yes | Yes | No |

**Final answer**

Finding: **Long gaps** and **bunching** are calculated from observed departure headways compared with scheduled headways.

- **Long gaps / gap rate:** the share of observed headways that are greater than **1.5×** the scheduled headway [E1].
- **Bunching / bunching rate:** the share of observed headways that are below **0.5×** the scheduled headway [E1].
- The underlying comparison is the **headway ratio**: observed departure headway divided by scheduled headway [E1].

Operationally, these metrics describe **train spacing**: long gaps mean trains are spaced much farther apart than scheduled, while bunching means trains are spaced much closer together than scheduled.

Limitations: these are based on observed train headways, not individual rider wait times. Also, **prediction gaps** are minutes between consecutive future predictions and are **not** realized headways [E1].

</details>

<details>
<summary><strong>16. How were realized Red Line headways at Harvard Square?</strong></summary>

**Category:** station alias

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;line&quot;: &quot;Red&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;Harvard Square&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Realized Red Line headways at Harvard Square were moderate but uneven: the median train spacing was 10.65 minutes, with the 90th percentile reaching 16.15 minutes [E1].

Operationally, this means typical train spacing was around 11 minutes, but riders at the station would sometimes see substantially longer gaps between trains. The gap rate was 9.5%, while bunching occurred 5.4% of the time, indicating both delayed spacing and some close-following trains [E1]. The analysis is based on 2,918 observed headways at the Harvard stop, resolved from “Harvard Square” [E1].

Limitations: this describes realized train spacing at the station, not individual passenger wait times. The evidence does not provide direction-specific, time-of-day, or passenger arrival information.

</details>

<details>
<summary><strong>17. Show recent Red Line train spacing at Kendall Square.</strong></summary>

**Category:** station alias

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;line&quot;: &quot;Red&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;Kendall Square&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Recent Red Line train spacing at Kendall/MIT was typically about 10.55 minutes, with the 90th percentile spacing at 16.18 minutes [E1].

Operationally, that means most realized train-to-train gaps at Kendall/MIT were near 10–11 minutes, but larger gaps occurred often enough that 10% of observed spacings were at or above 16.18 minutes [E1]. The measured gap rate was 9.6%, and the bunching rate was 4.9% [E1].

Limitations: this is realized train spacing at the station, not an individual rider’s wait time. The evidence reports 2,917 observed headways for Kendall/MIT on the Red Line, but it does not provide passenger arrival patterns or rider wait-time measurements [E1].

</details>

<details>
<summary><strong>18. What were realized train intervals near MIT on the Red Line?</strong></summary>

**Category:** station alias

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;line&quot;: &quot;Red&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;Kendall/MIT&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Finding: Near MIT, using Kendall/MIT station on the Red Line, realized train spacing had a median headway of 10.55 minutes, with the 90th-percentile headway at 16.18 minutes [E1].

Operationally, that means trains at Kendall/MIT were typically spaced a little over 10 minutes apart, while longer intervals reached about 16 minutes in the upper tail of observed service [E1]. The dataset includes 2,917 observed headways, with a reported gap rate of 0.096 and bunching rate of 0.049 [E1].

Limitations: These are realized train intervals at the station, not individual rider waits. The evidence does not provide passenger arrival times, direction-specific results, or the analysis time window, so it should be interpreted as aggregate train spacing at Kendall/MIT only.

</details>

<details>
<summary><strong>19. Did the Orange Line have many long gaps at State Street?</strong></summary>

**Category:** station alias

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;line&quot;: &quot;Orange&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;State Street&quot;, &quot;line&quot;: &quot;Orange&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Finding: The Orange Line at State Street did not show many long gaps overall; long gaps were present but relatively infrequent, with a gap rate of 6.2% across 2,597 historical realized headway observations [E1].

Operationally, typical train spacing was about 6.18 minutes at the median, and even the 90th-percentile spacing was 9.0 minutes [E1]. That suggests most observed train-to-train intervals at State Street were not especially long, though riders would still have encountered occasional extended spacing.

Limitations: This is station-level realized headway data for State Street on the Orange Line only [E1]. It describes train spacing, not individual rider wait times, and it does not identify causes, direction-specific effects, or time-of-day patterns.

</details>

<details>
<summary><strong>20. Summarize recent Red Line headways at Park Street.</strong></summary>

**Category:** dynamic station index

| Expected tool | Selected tool | Tool correct | Result valid | Citation valid | Fallback |
|---|---|---:|---:|---:|---:|
| <code>station_headways({&quot;line&quot;: &quot;Red&quot;})</code> | <code>station_headways({&quot;station&quot;: &quot;Park Street&quot;, &quot;line&quot;: &quot;Red&quot;})</code> | Yes | Yes | Yes | No |

**Final answer**

Finding: Recent realized Red Line train spacing at Park Street had a median headway of 10.47 minutes, with the 90th percentile at 16.37 minutes across 1,457 observations [E1].

Operational meaning: Typical train spacing was a little over 10 minutes, but the upper-end spacing reached over 16 minutes, indicating some irregularity in service [E1]. The reported gap rate was 0.099 and bunching rate was 0.045, suggesting both longer-than-expected spacing and close train spacing occurred, with gaps more common than bunching [E1].

Limitations: These are realized train headways at Park Street, not individual rider wait times. The evidence does not provide passenger arrival patterns, direction-specific results, or the exact “recent” time window [E1].

</details>

Tool-call order is ignored. Expected arguments must appear in the selected call; the planner may add an optional supported argument.

A fallback is recorded when no API key is used or when the model answer fails citation validation.
