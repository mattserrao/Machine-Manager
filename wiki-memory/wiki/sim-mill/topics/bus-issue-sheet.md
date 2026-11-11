---
name: bus-issue-sheet
description: The BUS (daily issue) sheet Apr 24 - Oct 16 2026 - 248 issues by asset with owner, count, how each is usually closed, failure-stop issues with WO and lead days, and the open ones; read to see what was on the sheet, who owned it, and what repeated
type: topic
aliases: ["BUS issues", "BUS sheet issues", "BUS issue log", "daily issue sheet", "issue sheet"]
---
See also the earlier and later sheet pages: [[bus-sheet-issues-2025-11-to-2026-05]] (2025-11-01 to 2026-05-03) and [[bus-issues-2026-10-late]] (2026-10-16 to 10-31); stock-prep summary [[stock-prep-recurring-issues]]. Per-asset detail for Apr-Oct 2026 is on the asset pages linked below.

## How to read it
- Each BUS issue = one asset + one problem, with dated status lines "New / Open / Waiting parts / Closed", an owner and often a WO; header gives "on the sheet N days" and "days open". [BUS 2026-04-24 .. BUS 2026-04-25 | issue f80319a8373c5318]
- This page covers 248 issues first seen 2026-04-24 to 2026-10-13 (last entries 2026-10-31). Two were not Closed on their last line: the REF 2 plate item (Open) and the reel drum bearing (Waiting parts), both below. [BUS 2026-10-13 .. BUS 2026-10-31 | issue 31e32f535f07b6a6] [BUS 2026-09-09 .. BUS 2026-10-31 | issue 485d30ef457a8764]
- The same problem is raised again and again as a new issue, often with a new WO each time, so counts of issues below equal repeats. Follow-up Actions raised from these issues: [[bus-follow-up-actions]].
- Some events appear twice (one issue from the maintenance owner with a WO, one from the area engineer without), e.g. 3rd section DS rotary joint 2026-06-23 and 2026-10-02. [BUS 2026-06-23 .. BUS 2026-06-25 | issue f52bb370faa41b40] [BUS 2026-06-23 .. BUS 2026-06-24 | issue 9a965f0ae55b3510]
- Tools: search_records for the issue text; downtime_events for the stop; overdue_actions for follow-ups.

## Failure stops on the sheet (hours down as written; "N days before" = Bonvoy vibration rising per the sheet text)
- 2026-04-28 [[pulper-rotor]] bearing 4.5 h, 43 days before, WO 26104816, issue d10840ea9aa2dae8. [BUS 2026-04-28 .. BUS 2026-04-30 | issue d10840ea9aa2dae8]
- 2026-05-03 [[p1-felt-bottom]] press felt blown 2.2 h, WO 26104942. [BUS 2026-05-03 .. BUS 2026-05-05 | issue d1aaf49038fbf64d] See [[press-felt-blows]].
- 2026-05-12 [[p2-felt-bottom]] felt plugged (emergency wash) 5.3 h, 16 days of Uhle vacuum climbing, WO 26105138. [BUS 2026-05-12 .. BUS 2026-05-14 | issue 4830ac7d6d730e2a]
- 2026-05-13 [[p1-felt-bottom]] felt plugged 3.6 h, 26 days, WO 26105159. [BUS 2026-05-13 .. BUS 2026-05-15 | issue dc941602601e3655]
- 2026-05-19 [[p2-felt-top]] unplanned felt change 7.5 h, "filled at 3 weeks", Uhle vacuum up 4.6 inHg, 4th section steam at its limit, WO 26105306. [BUS 2026-05-19 .. BUS 2026-05-22 | issue e4a594dc109adcd9]
- 2026-05-28 [[hood-exhaust-fan]] failure 5.1 h, 23 days before, WO 26105509. [BUS 2026-05-28 .. BUS 2026-05-31 | issue 61439c7e8299997d]
- 2026-06-23 [[3rd-section-rotary-joint]] leak 2.9 h, WO 26106237. [BUS 2026-06-23 .. BUS 2026-06-25 | issue f52bb370faa41b40]
- 2026-06-24 [[dryer-drive-lineup]] bearing 5.0 h, 41 days, WO 26106244. [BUS 2026-06-24 .. BUS 2026-06-25 | issue a087f20c8958c226]
- 2026-06-24 [[headbox]] side door blew off 1.3 h, WO 26106258; [[ref-refb]] plates clash, machine slowed 3.5 h, WO 26106272. [BUS 2026-06-24 .. BUS 2026-06-26 | issue abddfa02b117144a] [BUS 2026-06-24 .. BUS 2026-06-25 | issue 42aa519eea9eadaf]
- 2026-06-30 and 2026-08-05 [[p1-felt-top]] HP shower nozzles plugged 3.0 h (24 days before, WO 26106440) and 2.8 h (27 days, WO 26107287). [BUS 2026-06-30 .. BUS 2026-07-01 | issue c322abd4b9113a6e] [BUS 2026-08-05 .. BUS 2026-08-06 | issue 42ca6aa845d8c9e4]
- 2026-07-06 [[pulper-rotor]] rectifier fault 3.9 h, WO 26106545; 2026-09-07 again 3.4 h, WO 26108148 (issue 6aa5467cf4d982bf). [BUS 2026-07-06 .. BUS 2026-07-08 | issue 6409159f2529c7a1] [BUS 2026-09-07 .. BUS 2026-09-09 | issue 6aa5467cf4d982bf] See [[rectifier-fault-mcc-dc-bus]].
- 2026-07-11 [[headbox]] [[slime-buildup]] 5.2 h, "Speed cut to 70%", WO 26106636. [BUS 2026-07-11 .. BUS 2026-07-13 | issue 5fa72e0fecdb1c77]
- 2026-07-18 [[pulper-rotor]] drive trip 4.6 h, WO 26106867 (owner Desmond Pike); 2026-07-20 bearing 5.9 h, 35 days, WO 26106916. [BUS 2026-07-18 .. BUS 2026-07-19 | issue a029410d8bc231f8] [BUS 2026-07-20 .. BUS 2026-07-22 | issue 0afa4d3eb95b62d6]
- 2026-07-20 [[p1-felt-bottom]] felt blown 2.6 h, WO 26106944; 2026-07-21 [[p1-felt-top]] felt plugged 5.8 h, 21 days, WO 26106958; 2026-08-14 [[p1-felt-bottom]] plugged 3.4 h, 19 days, WO 26107469. [BUS 2026-07-20 .. BUS 2026-07-22 | issue 73a73a0256a1c4b0] [BUS 2026-07-21 .. BUS 2026-07-24 | issue 7608f66831922b8a] [BUS 2026-08-14 .. BUS 2026-08-16 | issue a6fc5c5accc64e71] See [[press-felt-plugging]].
- 2026-08-26 [[dryer-drive-lineup]] bearing 6.8 h, 20 days, WO 26107735. [BUS 2026-08-26 .. BUS 2026-08-27 | issue a1678a06376c0002]
- 2026-09-20 [[2nd-press-drive]] bearing 6.9 h, 18 days, WO 26108393. [BUS 2026-09-20 .. BUS 2026-09-22 | issue 72d7c7a1277db71a]
- 2026-10-02 [[3rd-section-rotary-joint]] leak 2.4 h, WO 26108638. [BUS 2026-10-02 .. BUS 2026-10-04 | issue ab19a06e96c87d39]
- 2026-10-14 [[dryer-drive-lineup]] driveshaft snaps 4.8 h, "Millwrights called in", WO 26108981. [BUS 2026-10-14 .. BUS 2026-10-15 | issue 8073fc5c0d602eb1]
- Lead times on the sheet text (43, 35, 41, 20, 18 days) differ from the RCFA "about N days"; both kept on the equipment pages ([[bearing-failed-between-vibration-routes]]).

## Planned / alert items (vibration route and Bonvoy)
- 2026-08-13 [[1st-press-drive]] bearing in Alert on the vibration route; WO 26107413 raised and scheduled (Mei Fairbanks); closed 2026-08-19 "Monitoring daily". [BUS 2026-08-13 .. BUS 2026-08-19 | issue 7d66d256db88d021]
- 2026-08-13 [[reel-drum]] DS bearing (asset 00072770) Alert on the Aug 12 route, 0.17 in/s, outer race defect; WO 26107420 for the Aug 19 outage went Waiting parts ("Bearing not in stores; ordering" 2026-08-17); closed 2026-08-20 "Deferred from Aug 19: rescheduled Nov 11, parts on order". [BUS 2026-08-13 .. BUS 2026-08-20 | issue 0f6e407b3446a3de]
- Second reel issue 2026-09-09 -> 2026-10-31 (53 days open, status Waiting parts): daily shift vibration readings, grease per Keel, 2026-09-27 "Keel to re-check weekly", 2026-10-15 "Danger at 0.40 in/s: decide run or stop"; header "bearing for Nov 11 on order, ETA Nov 5". Owner Mei Fairbanks, WO 26107420. [BUS 2026-09-09 .. BUS 2026-10-31 | issue 485d30ef457a8764] See [[out-2026-11-11]].
- 2026-09-10 [[fan-pump]] bearing in Alert; WO 26108169 "Planned stop to change it"; closed 2026-09-11 "Monitoring daily". [BUS 2026-09-10 .. BUS 2026-09-11 | issue 376e6717b36f4ba6]
- 2026-10-13 -> 2026-10-31 [[ref-refb]] (REF 2, asset 00072175) specific energy climbing fast on plates set 2026-09-30; Tobias Renner; 10-20 "Gap OK: plates wearing; Ridgeway to look"; 10-26 "Both refiners due Nov 11: one plate set on hand, order another"; still Open (19 days). [BUS 2026-10-13 .. BUS 2026-10-31 | issue 31e32f535f07b6a6] See [[refiner-plate-wear]].
- 2026-05-04 -> 2026-05-20 [[p2-felt-top]] "filling: Uhle vacuum up, press solids down": raise HP shower pressure; spraywell audit pulled forward to May 13; May 15 "22% nozzles plugged: cleaned; felt still filling"; felt changed May 19 (7.5 h shut). Owner Sunniva Brooks. [BUS 2026-05-04 .. BUS 2026-05-20 | issue b986516cc99abd78]
- 2026-05-09 -> 2026-05-19 [[4th-section-rotary-joint-ds]] "4th section steam at its limit on 34 Super: speed held back ~80 fpm"; "Running slower on 34 Super until the felt is changed"; Eamon Takahashi. [BUS 2026-05-09 .. BUS 2026-05-19 | issue 49269d69211214f3]
- 2026-10-08 [[p1-felt-bottom]] "felt is filling" (Uhle vacuum climbing, solids falling): raise HP shower pressure and check nozzles, WO 26108876, closed 2026-10-09 "Done; running normal". [BUS 2026-10-08 .. BUS 2026-10-09 | issue 8ae05bd2913c8b62]
- 2026-06-24 -> 2026-06-26 and 2026-10-13 -> 2026-10-16 [[4th-section-rotary-joint-ds]] syphon differential falling, "a can is flooding (syphon or joint)": steam and condensate survey, joint seal kit and syphon check planned; WO 26106279 and WO 26108974, both closed "Done; running normal". [BUS 2026-06-24 .. BUS 2026-06-26 | issue 51a8520b6a798d47] [BUS 2026-10-13 .. BUS 2026-10-16 | issue 4966ad93f1acce50]
- 2026-05-23 -> 2026-05-26 [[headbox]] consistency reading drifting with basis weight off target; transmitter recalibrated 05-25, WO 26105369. 2026-07-04 reel moisture reading high but sheet dry at lab (scanner standardization), WO 26106489, Fenna Gallagher. [BUS 2026-05-23 .. BUS 2026-05-26 | issue f0e31db7959d4706] [BUS 2026-07-04 .. BUS 2026-07-05 | issue e9abdff6db41c5c2]

## Recurring nuisance subjects (issues on the sheet, first-last, asset no., owner, usual closing text)
- [[dryer-can-13]] condensate flooding (cold can): 10 issues, 2026-05-01 to 2026-10-07; asset 00072581; Eamon Takahashi; "Syphon reset at the outage" each time.
- [[machine-chest]] level control hunting: 10; 2026-04-27 to 2026-10-15; asset 00072140; Fenna Gallagher; "Retuned; steady" (WO each time).
- Dryer can 4 doctor blade worn: 10; 2026-05-17 to 2026-10-04; asset 00072406; Gloria Nakamura; "Changed" after 2 to 10 days ("change blade on the next break"). [[dryer-cans]]
- [[dryer-can-4]] (see Dryer can 4 above) and [[forming-hp-shower]] oscillator stalling: 9; 2026-04-26 to 2026-09-27; asset 00072224; Gloria Nakamura; "Oscillator motor coupling replaced" every time.
- [[steam-header]] pressure dips at grade changes: 9; 2026-05-26 to 2026-10-12; asset 00072154; Eamon Takahashi; "Ramp rate changed".
- Thickener shower nozzles plugging: 9; 2026-04-29 to 2026-09-25; asset 00072126; Ingrid Solberg; "Cleaned".
- Flat box cover wear at the TS edge: 9; 2026-04-29 to 2026-10-03; asset 00072217; Curtis Lindahl; closed "Added to outage scope" every time (WOs 26105026, 26106153, 26106188, 26107070, 26107931, 26108652, 26108680; others no WO on the sheet) - check outage_scope that the flat box inspection is in [[out-2026-11-11]].
- 1st press top roll doctor chatter: 9; 2026-05-17 to 2026-10-07; asset 00072294; Gloria Nakamura; "Blade changed; chatter gone". [[p1-roll-top]]
- [[reel-drive]] turn-up missed twice on nights: 8; 2026-04-24 to 2026-08-26; asset 00072777; Desmond Pike; "Timing adjusted".
- Wire guide palm drifting to the TS: 8; 2026-05-02 to 2026-09-15; asset 00072231; Fenna Gallagher; "Regulator replaced" (guide air supply) every time.
- Fine screens DP creeping up: 8; 2026-04-26 to 2026-10-13; asset 00072105; Ingrid Solberg; "Flushed; DP normal" at grade change.
- 2nd section PV fan amps low: 6 (2026-04-26 to 2026-08-09), asset 00072553, Gloria Nakamura, "Belts tensioned"; none after 2026-08-10.
- Hood exhaust humidity high: 8 (2026-05-05 to 2026-09-19), asset 00072756, Fenna Gallagher, "Damper linkage repaired". [[hood-exhaust-fan]]
- Hood supply fan bearing noisy: 6 (2026-04-29 to 2026-09-02), asset 00072749, Gloria Nakamura, "Grease and monitor" then "Quiet after greasing". [[hood-supply-fan]]
- Vacuum pump seal water temperature high: 7 (2026-05-13 to 2026-09-23), asset 00072238, Gloria Nakamura, "Strainer cleaned". [[vacuum-pump]]
- Couch roll seal strip water low: 4 (2026-06-01 to 2026-08-26), asset 00072210, Tobias Renner, "Strainer cleaned". [[couch-roll]]
- Fan pump packing leaking: 5 (2026-04-27 to 2026-09-27), asset 00072196, Gloria Nakamura, "Leak down to a drip". [[fan-pump]]
- 1st press top felt conditioning low: 7 (2026-07-12 to 2026-10-10), asset 00072252, Sunniva Brooks, "Raise Uhle vacuum setpoint 0.5 inHg" then "Holding". [[p1-felt-top]]
- 2nd press bottom felt guide hunting: 6 (2026-06-05 to 2026-09-21), asset 00072336, Sunniva Brooks, "Paddle cleaned". [[p2-felt-bottom]]
- Winder slitter dust 6 (asset 00072798, Dolores Vance, "Changed" blades) and winder telescoping rolls 6 (asset 00072784, "Taper adjusted"). [[winder-drums]]
- Ragger rope breaking: 6 (2026-06-30 to 2026-10-02), asset 00072147, Ingrid Solberg, "Rethreaded; new rope ordered"; one issue ran 42 days on the sheet (2026-06-30 to 2026-08-01) with 4 re-thread cycles. [BUS 2026-06-30 .. BUS 2026-08-01 | issue 710e122c18496e89]
- Coarse screen rejects high 6 (asset 00072098, "Basket OK; reject rate back down"); HD cleaner reject valve sticking 5 (asset 00072091, Fenna Gallagher, "Valve rebuilt"); LC cleaner tips plugging 4 (asset 00072112, "Cleaned"); Headbox edge flow streak at the FS 5 (asset 00072189, Tobias Renner, "Streak gone on the scanner"); Pulper rotor amps swinging with bale feed 3 (asset 00072077, Ingrid Solberg, "Feed rate steadied; watch"); spool bar damage at the reel 4 (asset 00072763, Harlan Mbeki, "Spool sent for repair").
- Break-tape reviews ("N sheet breaks in 24 h, mostly at ..."; owner Tobias Renner, closed "Watching" the next day): Dryer can 6 6 issues (4-5 breaks, 2026-04-24 to 2026-09-17); [[p2-felt-top]] 7 issues (4-6 breaks, 2026-05-02 to 2026-09-15; 6 breaks on 2026-07-10); reel drum 4 issues (4-8 breaks; 8 breaks on 2026-05-07). Tool: downtime_summary group=location kind=break; see [[breaks-by-location]].
- RCFAs: the failure-stop issues above map to RCFAs on the equipment pages; no RCFA for the nuisance subjects is mentioned in the BUS text ([[rcfa-register]]).
