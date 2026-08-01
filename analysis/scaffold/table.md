<h3>Prompt-scaffolding division (bash only) — SWE-bench Verified hard, Sonnet 5</h3>
<table style="border-collapse:collapse">
<tbody>
  <tr>
    <th rowspan="1" colspan="2" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888">Hard — 45 <i>Python</i> events (1+ h human effort)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — bash (control)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — minimal prompt (pen-down fallback)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — no ritual (pen-down only)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — exec tool, no ritual (pen-down only)</th>
  </tr>
  <tr>
    <th rowspan="4" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top">Results</th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Resolved</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 34</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 34</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥇 <b>38</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥉 33</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Resolved %</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 76%</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 76%</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥇 <b>84%</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥉 73%</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Total cost</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥉 $39.63</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 $33.84</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥇 <b>$33.22</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$40.51</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">$/resolved</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥉 $1.17</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 $1.00</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥇 <b>$0.87</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$1.23</td>
  </tr>
  <tr>
    <th rowspan="14" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top;border-top:1px solid #888">Stats</th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888">Steps (total)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">2,206</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">2,111</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">2,045</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888;border-top:1px solid #888">2,067</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Turns/instance (avg)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">49.0</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">46.9</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">45.4</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">45.9</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Cost/turn (avg)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$0.018</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$0.016</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$0.016</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">$0.020</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Output tokens</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">725k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">628k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">631k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">804k</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Thinking (output)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">—</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">—</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">—</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">—</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Input tokens</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">71.86M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">59.17M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">57.11M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">69.12M</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">— non-cached</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4k</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">— cache read</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">69.78M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">57.23M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">55.19M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">66.89M</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">— cache write</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">2.08M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">1.93M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">1.91M</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">2.23M</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Failed tool calls (FormatError)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">0</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">0</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">0</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">0</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Input tokens/turn (avg)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">32,575</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">28,029</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">27,925</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">33,442</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Output tokens/turn (avg)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">329</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">297</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">309</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">389</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Context window (peak, single turn)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">134k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">93k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">117k</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">127k</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">Wall-clock (12-way parallel)</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">3.5 h</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">2.4 h</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">2.4 h</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">2.7 h</td>
  </tr>
</tbody>
<tbody>
  <tr>
    <th rowspan="1" colspan="2" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888">Medal tally — per instance (45 events, 4 unsolved by every model)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — bash (control)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — minimal prompt (pen-down fallback)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — no ritual (pen-down only)</th>
    <th colspan="1" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;border-top:1px solid #888;border-bottom:1px solid #888;border-left:1px solid #888">Sonnet 5 — exec tool, no ritual (pen-down only)</th>
  </tr>
  <tr>
    <th rowspan="4" style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold;vertical-align:top"></th>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">🥇 gold</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">12</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">12</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">11</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">6</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">🥈 silver</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">8</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">7</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">15</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">8</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">🥉 bronze</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">8</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">10</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">9</td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">7</td>
  </tr>
  <tr>
    <th style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;font-weight:bold">placing</th>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥇 <b>1</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥈 <b>2</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">🥉 <b>3</b></td>
    <td style="padding:3px 10px;text-align:left;white-space:nowrap;border:none;border-left:1px solid #888">4</td>
  </tr>
</tbody>
</table>

Verdicts from the pinned swebench judges. Full caveats in report.md.
