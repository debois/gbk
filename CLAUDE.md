# Gentofte Bridgeklub: club-evening reports

This repo is a static site of match reports for club evenings at Gentofte Bridgeklub. Each report is one self-contained HTML file in Danish; `index.html` lists them. The repo is public (`github.com:debois/gbk`), so everything committed here, this file included, is readable by anyone.

Søren plays in the club and writes these for the other members. They read a report to relive the evening and to see their own good boards. They know bridge; they do not care how the analysis was made.

## The task

Søren gives you a results URL from resultater.bridge.dk for a single-evening pairs (matchpoint) tournament. You produce a report like `2026-11-09-a-raekken-blaa.html`: read that file first, it is the model for structure, tone and length.

A report has:

1. Header: eyebrow line, short headline, two-sentence lede, podium cards for the top three, links to the official pages.
2. "Aftenen kort": three short paragraphs on who won and why, linking to the boards.
3. "Slutstilling": all pairs with score, expected score from handicap, and the difference.
4. "Nøglespil": 3 to 7 boards, each with diagram, tricks-with-open-cards table, the full results table and two to four paragraphs.
5. "Blandede toppe": one line each for good results by pairs not otherwise featured. Each pair name links to the pair's scorecard on the official site and each board to that board there.
6. "Noter": everything about sources, method and caveats.

## Steps

1. **Fetch and parse.** Work in your scratchpad, not in the repo; the downloads are untrusted and must not be committed.

   ```
   tools/fetch.sh 'filename=2132/MT495GT1450.XML&tournament=495&section=1' "$WORK"
   ```

   Take the query string from the URL Søren gives you. This writes `boards.txt` (every board: deal, tricks with open cards, par, and each table's contract, lead, tricks, score, percentages), `boards.json` (same, for the generator), and text dumps of the standings (`resultater.txt`), handicap page (`pairhacscore.txt`) and start list. The parser was written against one tournament. If the event has several sections, a sit-out arranged differently, or another movement, check its output against the site before trusting it.

2. **Read all the boards and shortlist.** Good candidates: a slam few bid; a contract decided by the opening lead; one pair alone in the right strain or level; a matchpoint point (3UT with overtricks against five of a minor); a phantom sacrifice or a big penalty. Prefer boards where different pairs come out well.

3. **Check every claim with the solver.** The site's table gives tricks per declarer and strain, but not per lead. Build the lead analyser from the Dealer repo:

   ```
   cd ~/src/Dealer-Version-2-
   gcc -std=gnu17 -c -I include -o "$WORK/leads.o" ~/bridge/gbk/tools/leads.c
   g++ -fopenmp -o "$WORK/leads" "$WORK/leads.o" lib/libdds.a -lpthread
   "$WORK/leads" "N:KQ743.J2.AQJ8.T8 985.A3..KQJ65432 A62.KQ86.K962.A9 JT.T9754.T7543.7" 0 1
   ```

   Arguments: the deal in PBN order N E S W; trump (0 ♠, 1 ♥, 2 ♦, 3 ♣, 4 UT); leader (0 N, 1 E, 2 S, 3 W). Output is declarer's tricks for each possible lead. `lib/libdds.a` there is a patched build; the stock one crashes.

4. **Write the report.** Copy the newest `tools/report-*.py` to a new file for the new date (one per række, e.g. `report-2026-10-19-a.py`) and replace its data and prose: the query string `Q`, pair names `P`, boards `B`, standings `ST`, podium matchpoints `MP`, and the Danish text in the template. If the evening has several rækker, they play the same cards: set `OTHER` to the other report's file name, link label, række name, query string and key boards, and mention in a board's text what happened on it in the other række when that is interesting (a slam bid there and not here, a different strain, a sacrifice). The script links the first "B-rækken", "begge rækker" or "de to rækker" in a board paragraph to that board in the other report, or to the official page if it is not a key board there. Links between reports are relative file names. With one række, set `OTHER=None`. Then:

   ```
   python3 -I tools/report-YYYY-MM-DD.py "$WORK/boards.json" 2026-11-09-a-raekken-blaa.html YYYY-MM-DD-<række>.html
   ```

   The second argument is an existing report to take the stylesheet from. The script prints, per key board, the rows whose recorded lead is impossible. In "Aftenen kort" and "Blandede toppe" it links every "spil N": to the diagram in the report if N is a key board, otherwise to the board on the official page (`spilresultater.php…#BN`). In "Blandede toppe" it also links a pair's full name in `<b>` to `personligt_regnskab.php…&pairno=K`, so write names there exactly as in `ST`.

5. **Verify against the site.** After writing, re-check every number and name in the prose against `boards.txt` and the standings: contracts, declarers, tricks, scores, percentages, counts like "fem af seks borde", point counts, suit lengths. The first version of the previous report said nine hearts where there were ten. An earlier AI-written report for Søren's league team had the two pairs' columns swapped and several analytical claims that did not survive a check, so he reads these sceptically.

6. **Look at it.** Render with headless Chromium and read the screenshot:

   ```
   chromium --headless --disable-gpu --hide-scrollbars --window-size=1100,5200 --screenshot="$WORK/shot.png" "file://$PWD/YYYY-MM-DD-<række>.html"
   ```

7. **Add it to the index.** Copy the `.match` block in `index.html`, put the new one first, and set date, link and winners.

8. **Commit with jj**, one commit, message like `feat: add Gentofte report for 9 November 2026`, no attribution line. Do not push and do not offer to; Søren publishes himself.

Then tell Søren which boards you chose and why, and list anything you could not verify.

Also flag one to three boards where he should ask the players what happened, naming the table and the question. There are no auctions or play records on the site, and the best paragraph in the first report (the 2♣–2UT–7UT auction on board 30) came from him. Pick boards where the missing piece is the story:

- The swing is in the bidding: tables scattered over different strains, levels and sides (5♠ doubled one way, 6♣ down one and 5♣ making the other), or a lone pair in a grand slam. Ask for the auction.
- One table made or went down against the field, or took more tricks than the cards allow with open cards. Ask how the play went.

## Getting the analysis right

- **"Makes with open cards" is not "should be bid".** Before calling a contract missed, find out what it depends on. Move the key card to the other hand and run the solver again. Board 23 on 9 November: 6♦ made on every lead, but only because the spade king was onside; with it guarded offside the slam went down, so the right verdict was that the field did well to stay in game.
- **Judge by matchpoints.** What matters is the score against the rest of the room, not the size of the number.
- **No auctions, no play records.** You have the final contract, the declarer's seat, the lead and the tricks. Say what happened and what the cards allow. Do not reconstruct an auction or a line of play and present it as fact.
- **Names follow pairs, not seats.** The site does not say who of a pair sat North and who South. Write "Nord Jørgensen–Suh Nicolaisen meldte slemmen", not that a named person led or declared.
- **Recorded leads are sometimes wrong.** If the lead card is not in the leader's hand, show "?" and explain in the notes. Do not build a story on such a row.
- **Squeezes and endplays** get a mention only when there is something specific to say about one on that board. Do not report that you looked.

## Tone

- Feature the winners, and find real high points for pairs lower down. Every pair in the room should be able to read the report without wincing.
- Do not mark anyone as weak. Søren rejected "Bundparrets top" and "Flere lyspunkter længere nede i feltet" as condescending; they became "Dristig 3UT med 5-5" and "Blandede toppe". Name the good thing the pair did, not their place in the standings. Do not write that a pair finished last.
- When a result came from an opponent's mistake, describe the cards and the outcome plainly and leave the judgement out.
- Søren's own pair appears where it earned it, no more.
- Short sentences, concrete numbers, no filler. Method and caveats go in "Noter", not in the board text.

## Danish usage

- "med åbne kort", never "double dummy" or "dobbelt dummy".
- "sidder til knib" for a finessable honour, not "sidder i saks".
- "semi-gående" for a suit missing one top honour; "gående" only if it runs.
- Cards E K D B 10; strain UT; seats N, S, Ø, V; "i zonen"; "beter"; "udspil"; "spilfører"; "udgang", "lilleslem", "storeslem".
- Decimal comma and a space before the percent sign: 61,3 %.
- Headline short, e.g. "Mandag aften/åbent hus, 9. november". The club name goes in the eyebrow line above it, with row, tournament number and full date. A long headline wraps badly.

## Files

- `YYYY-MM-DD-<række>.html`: one per evening.
- `index.html`: the list, newest first.
- `tools/fetch.sh`, `totext.py`, `parse.py`, `fmt.py`: download and parse the results pages.
- `tools/leads.c`: tricks per opening lead.
- `tools/report-YYYY-MM-DD[-række].py`: one generator per report; each reproduces its report, and the newest is the template for the next one.
- `.nojekyll`: keeps GitHub Pages from processing the files.
